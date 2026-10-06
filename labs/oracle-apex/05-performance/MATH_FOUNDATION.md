# Lab 05: APEX Performance — Math Foundation

## 1. Attribution — Where 30 Seconds Live

From the APEX Debug breakdown:

| Component | Time | % |
|-----------|------|---|
| IR #1 — Order Summary | 9,240 ms | 31% |
| IR #2 — Revenue by Region | 6,410 ms | 21% |
| IR #3 — Top Products | 4,120 ms | 14% |
| 6 charts combined | 2,570 ms | 9% |
| 8 small regions | 180 ms | 1% |
| PL/SQL processing | 840 ms | 3% |
| Processes | 320 ms | 1% |
| **Rendering** | **4,020 ms** | **13%** |
| **Session state** | **1,760 ms** | **6%** |

### What this tells you

```
Two regions = 15,650 ms = 52% of total
SQL total    = 22,340 ms = 74% of total
Rendering    =  4,020 ms = 13% of total
```

**If you optimise rendering you address 13% of the problem.** Optimising the two
slowest regions addresses 52%. The attribution is the whole point.

## 2. Collection — Query Reduction

```
Regions on the dashboard: 16
Before:  16 queries over 5M rows        = 22,340 ms
After:   1 collection query              =  ~2,400 ms
         + 16 collection reads (in-memory)
```

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Queries | 16 | 1 (+16 in-memory reads) | 16× fewer |
| SQL time | 22,340 ms | 2,400 ms | 9.3× |
| Total page | 29,960 ms | ~8,200 ms | 3.7× |

### The aggregation cost remains

```
The collection does not make aggregation free:
  16 regions each doing SUM/GROUP BY over the collection
  Collection has 200,000 elements
  Each aggregation pass: ~40 ms
  6 charts × 40 ms = 240 ms
```

```
Collection population:  2,400 ms
Collection reads:         480 ms
Total:                   2,880 ms
```

**Sharing removes redundant scanning, not the work itself.** That is still the
largest single win available.

## 3. Cache Hit Rate — the Whole Argument

```
Dashboard views/day:        50,000
Active hours/day:           8
Requests/hour:              6,250
Region cache TTL:           30 seconds

Requests per TTL window:    6,250 / 120 = 52
Misses per window:          1  (the first request)
Hit rate:                   51/52 = 98.1%
```

### Effective cost with and without cache

```
Cached query cost:          6,000 ms
Effective cost = (1 - 0.981) × 6,000 = 114 ms
Saving per request:          5,886 ms (98.1%)
```

### Hit rate is a function of request rate

| Requests/hour | Requests per 30s window | Hit rate | Worth it? |
|---------------|--------------------------|----------|-----------|
| 6,250 | 52 | 98.1% | **Yes** |
| 600 | 3 | 67% | Marginal |
| 120 | 0.6 | ~0% | **No** — added complexity for nothing |
| 12 | 0.06 | 0% | **No** |

**Caching an application with low traffic is pure overhead.** The hit rate must be
measured, not assumed:

```sql
SELECT region_id, COUNT(DISTINCT session_id) sessions,
       COUNT(*) requests, MAX(view_time) last_view
  FROM apex_user_activity_log
 WHERE view_time > SYSDATE - 1
 GROUP BY region_id;
```

## 4. Cache vs Collection — Which One

These solve different problems.

| Problem | Solution |
|---------|----------|
| Multiple regions read the same rows | **Collection** |
| Expensive query, slow-changing data, many users | **Cache** |
| Small stable lookup list, used on many pages | Session state cache |
| Expensive aggregate, survives sessions | Function result cache |

### Combined effect

```
Base:                          29,960 ms
+ collection (16 queries → 1)   8,200 ms
+ cache the 2 slow regions
  (2 regions × 98.1% hit rate):
  saving = 15,650 × 0.981 = 15,353 ms    →  ~2,850 ms of SQL
+ session state cleanup          1,760 → 200 ms

Total:                          ~3,050 ms
```

```
29,960 ms → 3,050 ms = 9.8x improvement
Target was 3,000 ms p95. Achieved, with each change attributable.
```

## 5. Row-by-Row vs Set-Based

### The cost model

```
Row-by-row:
  Network round trip:     ~1.5 ms
  PL/SQL overhead/row:    ~0.3 ms
  Total/row:              ~1.8 ms

Set-based:
  Parse + optimise:       ~5 ms (fixed)
  Per row processed:      ~0.015 ms
```

### Comparison

| Rows | Row-by-row | Set-based | Ratio |
|------|-----------|-----------|-------|
| 100 | 180 ms | 7 ms | 26× |
| 1,000 | 1,800 ms | 20 ms | 90× |
| 10,000 | 18,000 ms | 155 ms | 116× |
| 100,000 | 180,000 ms | 1,500 ms | **120×** |
| 1,000,000 | 1,800,000 ms (30 min) | 15,000 ms | 120× |

**The ratio converges to ~120×** once the fixed set-based cost amortises. It
does not improve further with volume — the per-row cost is what differs.

### The practical consequence

```
CSV import of 100,000 rows:
  Row-by-row:  180,000 s = 50 hours      ← unacceptable
  Set-based:     1,500 s = 25 minutes    ← acceptable
```

## 6. Export — Bounded vs Unbounded

### The APEX default export path

```
Default Interactive Report export:
  May fetch beyond the displayed page
  Framework processing per row
  No explicit row bound
```

```
100,000 rows through the default path: ~90-140 s  → FAILS the 30 s target
100,000 rows via set-based custom export: ~8-15 s    → MEETS the target
```

### The design decision

```
Bounded export (ROWS <= 100,000):
  Predictable time, predictable memory
  User told the limit in the UI

Unbounded export:
  Time unknown until it runs
  May exceed the HTTP timeout
  User discovers the limit when it fails
```

**Refusing a 500,000-row export in one second is better than attempting it and
timing out after four minutes.**

## 7. Cascading Filters — Combination Reduction

```
Regions: 12
Categories: 40
Reachable combinations without cascading: 480
Valid combinations (category exists in region): ~96
```

### Cost of an invalid combination

```
Query: region = 12 AND category = 37 (no orders in that pair)
Rows scanned before proving emptiness: full 30-day range
Daily rows: ~208,000
```

```
Invalid combinations reachable:  480 - 96 = 384
Requests hitting an invalid combination (est. 10%):
  50,000 views × 10% = 5,000/day
Cost each: ~180 ms (scan of 208,000 rows, no result)

Wasted work: 5,000 × 180 ms = 900 s/day = 15 minutes/day of database CPU
```

With cascading, users cannot select those combinations at all. **Cascading is
a performance control as much as a usability one.**

## 8. p95 vs Average — Reporting the Wrong Number

```
Before optimisation, page load distribution:
  Average:  4,200 ms
  p50:      2,900 ms
  p95:     30,000 ms   ← timeouts live here
  p99:     48,000 ms
  Max:     120,000 ms
```

**The average says 4.2 seconds — acceptable. The p95 says 30 seconds — unusable.**
Users experience the distribution, not the mean, because they encounter the
slow tail regularly.

```
Users hitting p95+ per day:  ~2.5% of sessions
Users per day:                 1,200
Users experiencing a timeout:  30/day
```

**Report p95 for the requirement, and always look at p99** — p99 is where the
genuinely broken cases are.

## 9. Peak-Hour Database Impact

```
Daily dashboard views:        50,000
Share in the 9-10 AM peak:    15%  = 7,500 requests/hour

Before:  7,500 × 4,200 ms avg = 31,500 s of work in one hour
After:   7,500 × 2,900 ms avg = 21,750 s
```

```
CPU seconds in peak hour: 31,500 → 21,750 = 31% reduction
```

### Scheduling batch work out of the peak

```
Batch jobs currently at 9:30 AM (in peak):
  Refresh aggregations      300 s
  Nightly exports queued     180 s
  Cache pre-warm             120 s
  Total batch in peak:      600 s

Move to 6:00 AM:
  Batch work in peak:          0 s
```

```
600 s of batch removed from the peak hour = 2% of peak load
```

Worth doing, but note it is 2% — **the 31% reduction from per-request
optimisation is 15× larger.** Reducing work per request comes first; scheduling
is a second-order improvement.

## 10. Statistics Staleness — The Silent Regression

```
Table:            5,000,000 rows
Statistics last analyzed: before a 2,000,000-row load
num_rows in stats:         3,000,000

Error in cardinality estimate: 40%
```

**A 40% misestimate can flip a join from a hash join to a nested loops join.**
On 5M rows the difference is minutes.

```
Nested loops instead of hash join:  ~90 s
Hash join:                        ~1.2 s
Ratio: 75x, from statistics alone
```

This is the failure mode that looks like "the database got slower overnight"
with no code change. Check `last_analyzed` before investigating anything else.

## 11. Undo and Batching

```
Single DELETE of 10,000,000 rows:
  Undo generated:        ~40 GB
  Lock duration:         minutes
  Concurrent DML on the table: blocked
  ORA-1555 risk:         real

Batched (50,000 rows × 200 iterations, 0.2 s sleep):
  Undo per batch:        ~200 MB
  Lock duration:         ~2 s per batch
  Concurrent DML:        proceeds between batches
```

```
Peak undo:  40 GB  →  200 MB   (200x reduction)
Blocking:   minutes → seconds
```

**Batching does not reduce total work; it reduces peak resource consumption.**
That is the entire point — the database stays responsive for everyone else.

## 12. Combined Before/After

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Page load p95 | 30,000 ms | 2,950 ms | **10.2×** |
| SQL queries per render | 16 | 1 | 16× |
| SQL time | 22,340 ms | 2,400 ms | 9.3× |
| Session state | 1,760 ms | 200 ms | 8.8× |
| Peak-hour DB CPU | 31,500 s | 21,750 s | 31% less |
| 100K export | 120 s | 12 s | 10× |
| 100K CSV import | 50 hours | 25 min | 120× |
| Cache hit rate | — | 98.1% | — |

**Every number is attributable to one change**, measured separately. That is what
makes the result defensible in review and reversible if one change regresses.