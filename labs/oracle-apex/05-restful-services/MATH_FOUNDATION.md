# Lab 05: RESTful Services (ORDS + APEX integration) — Math Foundation

## 1. HTTP Status as a Contract

Each status code carries a cost decision and a retry decision:

| Status | Meaning | Client may retry? | Correct response |
|--------|---------|-------------------|------------------|
| 200 | Success | n/a | `{"items":[...]}` |
| 400 | Malformed request | No — fix the caller | error body with the field |
| 401 | Not authenticated | After refresh | `WWW-Authenticate` header |
| 403 | Authenticated, not allowed | No | never leak the reason |
| 404 | Not found | No | same body as 403 for private data |
| 409 | Conflict / duplicate | After re-read | current state in the body |
| 429 | Rate limited | Yes, after `Retry-After` | `Retry-After: 30` |
| 500 | Server fault | Yes, with backoff | correlation id, no stack trace |

```
Returning 200 with {"error":"..."}:
  Client code:  if (status == 200) { parse and use data }   → wrong data used
  MTTR:         hours, because the failure looks like success

Returning 500 with a stack trace:
  Attack surface: internal class names, SQL, file paths leaked
  Recovery:       correct status, but information disclosed
```

**Status code correctness is not pedantry — it is the client's error handling
mechanism.** A 200 with an error body breaks every client that follows the
contract.

## 2. Pagination Contract Mathematics

```
Unpaginated endpoint, orders table, 1,240,000 rows:
  Response: ~520 MB JSON
  Transfer at 100 Mbit/s:  ~42 s
  Parse:                  ~17 s
  Client memory:          ~1.4 GB as objects
  Result: unusable

Paginated at 100 rows, hasMore + totalCount:
  Response per page: ~42 KB
  Transfer:           ~3.4 ms
  Parse:              ~1.1 ms
  Pages needed:      12,400 for a full scan — but no client does that
```

```
Contract fields that make pagination composable:
  items, limit, offset (or cursor), hasMore, totalCount (optional)

totalCount is optional precisely because COUNT(*) on 1.24M rows costs ~60 ms
on every page request. Trade a cheap contract for an expensive convenience.
```

| Approach | Cost per page | Client cost to read all |
|----------|--------------|------------------------|
| `hasMore` only | ~1 ms | Must page until exhausted |
| `totalCount` always | ~61 ms | Knows the size up front |
| Cursor/keyset | ~1 ms | Cannot jump to page 500 |

**Offset vs cursor on the server side:**

```
OFFSET 9750 FETCH NEXT 25:  reads 9,775 rows, ~9 ms with an index
Keyset (created_at, id):    reads 25 rows,     ~0.3 ms
                           -> 30× cheaper at page depth
```

## 3. Payload Design — Envelope Size

```
Naive envelope, 1 record:
  {"id":1024,"cust":"ACME Ltd","status":"SHIPPED","total":1234.56,"date":"2026-10-01"}
  ~104 bytes

With names, links, and metadata:
  ~610 bytes

Ratio: 5.9× for zero additional information
```

```
1,240,000 rows:
  Naive:      129 MB
  Verbose:    756 MB
  Saving:     627 MB per full scan
```

**gzip compresses the difference away for text-heavy JSON** (~8-10× on
repeated keys), which is why content negotiation matters more than field naming:

```
Verbose JSON uncompressed: 756 MB
Verbose JSON + gzip:       ~85 MB   (8.9×)
Content-Encoding: gzip costs ~1 ms/MB to compress, ~40 ms/MB for a
naive client that ignores it
```

## 4. Rate Limiting Arithmetic

```
Token bucket: capacity 600, refill 10/sec

Burst of 800 requests in 1 second:
  Available: min(600, 10 + 800) = 600 granted
  Rejected: 200 -> 429 with Retry-After

Client with exponential backoff:
  200 retries × ~2 s average backoff, spread over ~20 minutes
  Successful after: ~6 minutes
```

```
Headers that make this workable:
  X-RateLimit-Limit:     600
  X-RateLimit-Remaining: 0
  Retry-After:           30

Without Retry-After, well-behaved clients guess. Guessing clients
synchronise and create the thundering herd the limit was meant to prevent.
```

## 5. Authentication Cost and Token Lifetime

```
OAuth2 client credentials:
  Token lifetime:        3,600 s
  Clients:                40
  Token requests/hour:    40 (one per client per lifetime, amortised)

Token validation per API call: ~0.05 ms (local signature verification)
```

| Validation | Cost | Revocation |
|------------|------|------------|
| Self-contained JWT (RS256) | ~0.05 ms | None until expiry |
| Opaque token + DB lookup | ~1.2 ms | Immediate |
| Introspection endpoint | ~4 ms | Immediate |

```
Latency budget for a 50 ms endpoint:
  JWT:        0.05 ms  (0.1% of budget)
  Opaque:     1.2 ms   (2.4%)
  Introspect: 4.0 ms   (8.0%)   <- a third of the budget on authorisation alone
```

**Self-contained tokens are fast precisely because revocation is deferred.** That
is a real trade-off, not an oversight: for read APIs with short lifetimes the
latency wins; for permission changes you need revocation and pay for it.

## 6. Fencing Tokens for Concurrent Writes

Concurrent updates to the same resource need ordering, not locking:

```
Fencing token = monotonically increasing integer from the store.

PUT /orders/1024  with If-Match: "41"

Token 41 held:      write accepted, token becomes 42
Token 40 (stale):   write REJECTED with 412 Precondition Failed
```

```
Why this is safe under failover:
  Node A gets token 41, then stalls (GC, network partition).
  Lease expires. Node B gets token 42 and writes.
  Node A wakes and writes with token 41.
  Store rejects 41 < 42.   No lost update, no double charge.
```

```
Without fencing:
  Double-write probability per stalled operation:
    P(lease expires) × P(another client acquires) × P(both complete)
  With 60 s lease and 10 s stall:
    P ≈ 0.167 × 0.9 × 0.95 ≈ 14%
```

**A lock without fencing is a hope; a lock with fencing is a guarantee.** At 10%
probability per event and 5,000 events/day that is 500 corrupted writes/day.

## 7. Response Size Drives Client Memory

```
Endpoint returning 1,240,000 rows as one array:
  Raw JSON:              129 MB
  As Java objects:       ~1.4 GB  (11 bytes overhead per field minimum)
  JVM default heap:      512 MB  -> OutOfMemoryError

Paginated 100-row pages:
  Per page as objects:   ~1.2 MB
  Peak client memory:    ~4 MB (page + accumulation for display)
```

```
Server memory for the same endpoint:
  Streaming JSON writer:  O(chunk size) ≈ 64 KB, independent of row count
  Buffering the whole result: 129 MB per concurrent request
  20 concurrent requests: 2.6 GB of buffers on the server
```

**Streaming on the server is a memory decision, not a performance one.** It makes
peak memory proportional to concurrency rather than to data volume.

## 8. Error Handling Over the Wire

```
Errors per 10,000 calls at a 0.5% failure rate:  50

Retries without backoff:
  All 50 retry immediately -> the failing dependency sees a 100× burst

Retries with exponential backoff + full jitter:
  attempt k delay ~ U(0, min(cap, base * 2^k))
  Expected additional wall clock: ~4 s
  Peak retry concurrency: ~1-2 instead of 50
```

| Pattern | Effect on the dependency | Effect on the client |
|---------|--------------------------|----------------------|
| No retry | Fast failure | User sees an error |
| Immediate retry | 100× burst, likely worse | Still fails |
| Bounded backoff | Load smoothed | Slightly slower success |
| Circuit breaker | Zero load while open | Fast, clear failure |

```
Circuit breaker thresholds, derived:
  failure_rate_threshold = 50% over rolling 20 requests
  Requests needed to evaluate: 20
  At 10 req/sec that is 2 seconds of traffic per decision
```

## 9. Local Database Cost of the Tables Behind the Endpoints

ORDS auto-generated endpoints query Oracle directly, so Oracle performance rules
apply unchanged:

```sql
-- Sargable: the index is usable
WHERE status = :status AND created_at >= :from_date

-- Non-sargable: function on the indexed column
WHERE TO_CHAR(created_at,'YYYY-MM') = :month
WHERE UPPER(email) = :email          -- unless the index is on UPPER(email)
```

```
orders table: 1,240,000 rows

status = 'SHIPPED':                 62%   ~1,240 ms unindexed
+ created_at last 30 days:         4.1%  ~92 ms
+ region = 3:                       0.3%  ~11 ms

Same query with TRUNC(created_at) = :d:
                                     100%  ~1,340 ms  -> 122× worse
```

## 10. Bind Variables — Plan Stability Behind Every Endpoint

```
Endpoints sharing one query with binds:   1 cursor
Endpoints built by string concatenation: N cursors, N plans

Distinct filter combinations across clients: ~800/day

Literal SQL:
  800 × 4 KB cursor = 3.2 MB of shared pool, 800 hard parses/day
  800 × 1.8 ms = 1.44 s of parse time/day

Bind SQL:
  1 × 4 KB, 1 hard parse, 800 soft parses
  1.8 ms + 800 × 0.02 ms ≈ 1.82 s -> but no cursor growth and no stale plans
```

**Injection risk and plan instability are the same bug.** Concatenating a filter
into SQL is both an attack surface and a hard-parse generator.

## 11. Backward Compatibility Cost

```
Response consumers:                6 (3 internal, 3 partner)
Versions of the response shape:   3 (v1, v2, v3)
Fields added in v2:               3
Fields removed in v3:             2

Consumers on v1 that break when a field is removed:  2 of 6 = 33%

Alternative: additive-only change
  Fields added in v2:             3
  Fields removed:                 0
  Consumers broken:               0 of 6 = 0%
```

```
Deprecation window math:
  consumers_to_migrate = 6
  migration_rate = 2 per month
  months_to_clear = 6 / 2 = 3 months

Zero-downtime removal requires:
  deprecation announcement + 3 months + 0 remaining consumers
Anything shorter forces a version break on someone.
```

## 12. Before/After API Budget

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Unpaginated response | 520 MB | 42 KB/page | 12,400× |
| Pagination cost | n/a | ~1 ms (hasMore) | flat |
| Offset page 400 (server) | ~9 ms | ~0.3 ms | 30× |
| Auth per call | 4.0 ms | 0.05 ms | 80× |
| Concurrent write corruption risk | ~14% | 0% | fencing token |
| Server memory per request | 129 MB | ~64 KB | streaming |
| Distinct cursors/day | 800 | 1 | 800× |
| Error bodies with status 200 | 100% | 0% | contract honoured |

Every improvement here comes from making the contract explicit — status codes,
pagination, fencing tokens, streaming — rather than from adding hardware.
