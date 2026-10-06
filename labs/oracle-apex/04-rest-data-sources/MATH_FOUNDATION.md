# Lab 04: REST Data Sources — Math Foundation

## 1. The Network Is the Cost Model

An APEX region backed by a REST source spends almost all its time waiting on the
network, not on the database:

```
Loopback call (same host):        ~2 ms
Same datacenter:                   ~5-15 ms
Same region, cross-AZ:             ~20-40 ms
Cross-continent:                  ~120-250 ms
Caller timeout:                     2,000 ms (default)
```

```
Interactive region over REST, 25 rows:
  APEX overhead:                ~400 ms
  1 REST call:                    ~15 ms
  25 rows over HTTP (JSON):      ~25 ms
  Total:                        ~440 ms

Same region over a local view:
  APEX overhead:                ~400 ms
  1 SQL call:                     ~10 ms
  Total:                        ~410 ms
```

**On a healthy network the two are nearly indistinguishable.** Performance
problems appear when the call count rises, when the remote API is slow, or when
payloads are large — which is exactly what happens in bulk processing.

## 2. Call Count Multiplier — The Dominant Factor

```
One page, 6 regions each with its own REST source:
  6 sequential HTTP calls × 15 ms = 90 ms of pure wait
  Framework: 400 ms

One page, 6 regions sharing ONE collection:
  1 HTTP call = 15 ms
  6 collection reads = ~1 ms
  Framework: 400 ms
```

| Regions | Sequential REST | One call + collection | Saving |
|---------|-----------------|------------------------|--------|
| 3 | 45 ms | 16 ms | 29 ms |
| 6 | 90 ms | 16 ms | 74 ms |
| 12 | 180 ms | 18 ms | 162 ms |

```
At 12 regions the call count, not the payload, is the problem.
Each call has fixed overhead: DNS, TLS handshake reuse, auth header,
parse, error handling. Fixed overhead ~12 ms; payload cost ~0.4 ms/row.
```

## 3. Payload Size — Rows per KB

```
JSON record, typical order:      ~420 bytes
XML record, same data:           ~610 bytes
REST source with a 10,000-row response:  4.2 MB JSON

Transfer at 100 Mbit/s effective:  4.2 MB ≈ 336 ms
Parse with APEX_JSON:            ~1.1 ms per 100 records -> 110 ms
```

```
Per-record overhead:
  JSON:  parse 1.1 ms/100 rows + transfer 0.34 ms/100 rows
        ≈ 14.4 µs per row end to end

10,000 rows:  parse 110 ms + transfer 336 ms = 446 ms
```

**A single unbounded REST region can exceed the request timeout by itself.** Set
a page-size limit on the source and request server-side pagination from the API.

## 4. Pagination and Offset Cost Across the Wire

```
Remote API with offset pagination:
  GET /orders?offset=9750&limit=25

Rows transferred for page 400:
  With server-side pagination:            25 rows  ≈ 10 KB
  API that ignores limit and returns all:  10,000 rows ≈ 4.2 MB

Ratio: 420× more data for the same visible rows
```

```
Remote API sorting 10,000 rows per request, 40 page clicks per session:
  40 × 30 ms server-side sort = 1,200 ms of remote CPU per session
  400 users × 40 = 16,000 requests -> 480 s of remote CPU per day
```

**Ask the API for keyset pagination if it offers it.** Offset cost grows with
depth on the remote side too, and you pay that cost in someone else's database.

## 5. Bind Variables and Plan Stability — Local Database Side

REST sources that land in a local staging table reintroduce every Oracle
performance problem:

```sql
-- Landing table populated per refresh
INSERT INTO rest_order_staging (...)
SELECT ... FROM dual CONNECT BY LEVEL <= :n;
```

```
Rows staged per refresh:            10,000
Distinct literal INSERTs:           1 (binds used) -> 1 hard parse
Without binds:                     10,000 distinct statements

Without binds:
  10,000 hard parses × 1.8 ms = 18 s of pure parse overhead
With binds:
  1 hard parse + 10,000 executions ≈ 1.8 s total
```

**Batching is the second half of the answer.** Never call the API once per row:

```
Row-by-row API calls (10,000 rows):
  10,000 × 15 ms network = 150 s
  Serial:                  150 s
  With 20 concurrent workers: 150 / 20 = 7.5 s  (rate-limit permitting)

Bulk endpoint (one call, 10,000 rows):
  1 × 15 ms + 336 ms transfer = 351 ms
```

## 6. Retry and Backoff Arithmetic

```
Remote API error rate:                0.5% per call
Calls per bulk job:                   10,000
Expected failures without retry:      50

Retry with exponential backoff + jitter:
  attempt delay:  1s, 2s, 4s, 8s   (capped), ±20% jitter
  max attempts:   5

Expected total time for 10,000 calls at p95 latency 15 ms:
  10,000 × 15 ms = 150 s
  + 50 retries × ~4 s of backoff (mostly overlapping) ≈ +20 s wall clock
  Total: ≈ 170 s
```

**Jitter is not optional.** Without it, all failed callers retry at the same
instant and the recovering API is immediately knocked over again:

```
Without jitter: 50 clients retry at t=1s -> thundering herd on a system
                already at 100% CPU
With jitter:    retries spread over ±0.2s -> ~1 effective concurrent retry
```

## 7. Rate Limiting Arithmetic

```
Remote API limit:        600 requests/minute (10/sec)

Consumption if the APEX page calls 6 sources per render:
  Users:                 400
  Renders/user/hour:     24
  Requests/hour:         400 × 24 × 6 = 57,600
  Requests/minute:        57,600 / 60 = 960  →  EXCEEDS 960/min by 6%

Required: 600/min. Available: 600/min. Utilisation: 160%.
```

```
Fix options, in order of preference:
  1. Share one call via a collection:      960 -> 160/min  (util 27%)
  2. Cache the response for 60 s:          160 -> ~2.7/min  (util 0.5%)
  3. Reduce page loads:                    depends
```

**Rate limits turn an architectural decision into arithmetic.** A page that works
in testing and 429s in production is almost always this calculation done wrong.

## 8. Timeout Budget

```
Total page budget:                    2,000 ms
  Framework:                            400 ms
  6 REST calls at 15 ms:                90 ms
  Remaining:                          1,510 ms

But one source has a p99 of 400 ms (the partner ERP):
  p99 page: 400 + (5 × 15 + 400) = 875 ms
  One source at 2,000 ms: page = 400 + 2,000 = 2,400 ms  → timeout
```

```
Timeout allocation rule:
  per_source_timeout <= (page_budget - framework_overhead) / number_of_sources
                     = 1,510 / 6 ≈ 250 ms

A single source given 2,000 ms can consume the entire page budget.
Set per-source timeouts below the budget share and fail fast.
```

## 9. Row-Count-Driven Rendering Cost

```
REST region, rows returned:      25      500      2,000
  Render at 0.02 ms/row:          0.5 ms    10 ms     40 ms
  JSON parse at 14.4 µs/row:      0.4 ms    7 ms      29 ms
  Transfer at 34 µs/row:          0.9 ms   17 ms      68 ms
  APEX render:                    0.2 ms    0.2 ms    0.2 ms
  Total:                         ~2 ms     34 ms    137 ms
```

```
Below ~500 rows the network dominates.
Above ~2,000 rows the payload dominates.
The knee is around 500 rows — set the source page size there or below.
```

## 10. File Upload and Download Arithmetic

```
Upload, 5 MB PDF, 10 MB/s upload from a remote user:
  Transfer:            500 ms
  DBMS_LOB write:      ~120 ms
  APEX processing:      ~80 ms
  Total:               ~700 ms

Download, 5 MB, served from a LOB through APEX:
  LOB read:            ~90 ms
  Stream to client:    ~500 ms  (user's link, not the DB)
  Server memory:       streamed, not buffered — O(1) in file size
```

```
Buffering the whole file instead of streaming:
  5 MB  -> 5 MB × concurrent downloads (say 20) = 100 MB session memory
  50 MB -> 1 GB of session memory, and ORA-04090
Stream the LOB in chunks. Memory must be independent of file size.
```

## 11. Session State for Cached REST Responses

```
Cached response: 500 rows × 420 bytes JSON = 210 KB
Session state limit reality:               1 serialised value per item
Deserialisation per render:                ~4 ms

Alternative: cache into a local table with a TTL column
  Storage: 210 KB (identical)
  Read cost: 1 indexed query ~0.3 ms
  Refresh: explicit, auditable, shared across sessions
```

| Cache | Storage | Read cost | Shared across sessions | Auditable |
|-------|---------|-----------|------------------------|-----------|
| Session state collection | 210 KB | ~4 ms | No | No |
| Local table + TTL | 210 KB | ~0.3 ms | **Yes** | **Yes** |
| No cache | 0 | 15 ms + render | — | — |

**Session-state caching helps one user. A table helps everyone.** With 400 users
at 24 renders/hour the table saves 9,500 remote calls per hour.

## 12. Before/After Integration Budget

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| REST calls per page render | 6 | 1 | 6× |
| Requests/minute against the API | 960 | 160 | 6× |
| API utilisation | 160% | 27% | inside limit |
| Bulk job of 10,000 rows | 150 s | 0.35 s | 428× |
| Payload for page 400 | 4.2 MB | 10 KB | 420× |
| Per-source timeout | 2,000 ms | 250 ms | bounded |
| Cached read cost | 15 ms | 0.3 ms | 50× |

The recurring theme: **the expensive part of REST integration is the number of
calls, not the size of any one of them.** Fix the call count first; the payload
sizes follow.
