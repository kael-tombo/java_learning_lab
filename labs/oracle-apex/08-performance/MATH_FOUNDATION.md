# Lab 08: APEX Performance — Math Foundation

## 1. Attribution — Where 12 Seconds Live

| Component | Time | % |
|-----------|------|---|
| Region: Orders | 3,214 ms | 27% |
| Rendering | 3,008 ms | 25% |
| Region: Chart Revenue by Category | 1,020 ms | 9% |
| PL/SQL processing | 912 ms | 8% |
| Region: Chart Revenue by Channel | 840 ms | 7% |
| Region: Customers | 1,802 ms | 15% |
| Session state | 604 ms | 5% |
| Charts: Revenue by Region | 260 ms | 2% |
| Regions 5–8 | ~20 ms | <1% |
| Dynamic Actions | 200 ms | 2% |

### The two findings that matter

```
Region: Orders alone       = 27% of total
Rendering                 = 25% of total
Together                  = 52%

Regions 5-8 combined      = <1% of total
```

**Optimising the seven small regions would address less than 1% of the problem.**
The seven largest changes address 94%.

## 2. Sargability — The 24× Effect

```
Table: orders, 5,000,000 rows over 24 months
Rows per month: ~208,000
```

| Predicate form | Index used | Rows examined | Time |
|----------------|-----------|---------------|------|
| `TRUNC(order_date) = :d` | No | 5,000,000 | 3,214 ms |
| `order_date >= :d AND < :d+1` | Yes | 208,000 | 190 ms |

```
Reduction: 24x for a one-line change and one index.
```

### Why the function defeats the index

```
order_date >= :d
  → compares the INDEXED COLUMN to a value → index range scan

TRUNC(order_date) = :d
  → applies a FUNCTION to the INDEXED COLUMN → the index does not contain
    computed values → full scan
```

**Rule: functions go on the right-hand side, never the left.**

## 3. Pagination Is Not a Filter — The Cost

```
Developer believes:  25 rows displayed → 25 rows read
Actually happens:     scan until 25 MATCHING rows are found

Best case (highly selective filter):   25 rows examined    → pagination works
Worst case (low selectivity):          5,000,000 examined  → pagination useless
```

### In this lab

```
Filter: last 30 days, no additional filter
Rows matching: 208,000 of 5,000,000 = 4.2% selectivity

Rows examined to produce the first page: ~600
   (database stops once it has 25 matches)
```

That looks good — but only because the date filter is selective. Without it:

```
Filter: none (the state before the fix)
Selectivity: 100%
Rows examined for page 1: 25 (cheap) but ORDER BY requires a full sort
Full scan + sort: 3,214 ms
```

**The killer is the `ORDER BY net_amount DESC` with no supporting index** — a top-N
sort over 5M rows requires scanning everything to be sure the top 25 are found.

```sql
-- The actual fix: a covering index that supports the sort
CREATE INDEX ix_orders_date ON orders (order_date, net_amount);
-- Now: index range scan, rows already ordered, no sort step
```

## 4. Bind Variables — Hard Parse Cost

```
Distinct status values in the application: 8
Users:                                    200
Working days per year:                    250
```

| Approach | Distinct statements | Hard parses/year |
|----------|--------------------|------------------|
| Literal built by concatenation | 8 | up to 8 × sessions |
| Static SQL with bind | 1 | **1** |

```
Reduction in hard parses: from thousands to one, ever.
```

### The library cache latch effect — non-linear

```
Sleep percentage on library cache latches:
  < 1%     healthy
  1-5%     noticeable contention
  > 5%     severe — degrades every session on the instance
```

This is why an APEX hard-parse problem is reported as "the database got slow":
the latch is shared, so an APEX application can impair unrelated workloads.

**The cost is not the CPU of parsing. It is the contention on a shared resource.**

## 5. Cache Layer Selection

| Problem | Wrong answer | Right answer |
|---------|--------------|--------------|
| Slow order list, per-user filters | Page cache | **Region cache** |
| Personalised dashboard | Page cache | Region cache per region |
| 40 KB lookup list used on 10 pages | Session state | **Region cache or function result cache** |
| Expensive monthly aggregate | Region cache | **Function result cache** |

### Why page cache is dangerous here

```
Distinct sessions over 7 days: 240
Total views:                    3,500
Sessions per view:              14.6

Page content: depends on P1_REGION, P1_CUSTOMER — set per user
→ Page cache would serve user A's HTML to user B
→ That is a data disclosure bug, not a performance decision
```

## 6. Cache Hit Rate and Effective Cost

```
Region: Charts (3 combined, 2,120 ms)
TTL: 60 seconds
Requests/hour at peak: 400

Requests per TTL window: 400 / 60 = 6.7
Misses per window:       1
Hit rate:                5.7/6.7 = 85.1%

Effective cost = (1 - 0.851) × 2,120 = 316 ms
Saving:                    1,804 ms (85%)
```

### Hit rate is highly sensitive to request rate

| Requests/hour | Requests per 60 s window | Hit rate | Worth it? |
|---------------|-------------------------|----------|-----------|
| 2,400 | 40 | 97.5% | **Yes** |
| 400 | 6.7 | 85% | Yes |
| 60 | 1 | 0% | **No** |
| 6 | 0.1 | 0% | **No** |

**At 60 requests/hour a 60-second TTL produces no hits at all.** The cache adds
invalidation complexity and delivers nothing.

## 7. Session State Cost

```
Unnecessary lookup blob: 40 KB
Requests per day:        3,500

Serialisation: 40 KB × 3,500 = 140 MB/day of serialise/deserialise work
```

### Measured impact

| Session state size | Per-request overhead |
|-------------------|---------------------|
| 2 KB | ~5 ms |
| 40 KB | ~170 ms |
| 200 KB | ~850 ms |

```
Removing the 40 KB blob:  604 ms → 90 ms   = 514 ms saved
```

**A 5× reduction on a component that was only 5% of total** — still worth doing
because it is one line of change.

## 8. PL/SQL Bulk Access

| Approach | 500 rows | 10,000 rows |
|----------|---------|-------------|
| Cursor loop with per-row SQL | 900 ms | 18,000 ms |
| `BULK COLLECT` + FORALL | 30 ms | 320 ms |
| Single MERGE | 15 ms | 145 ms |

```
FORALL vs row loop:   30x
MERGE vs row loop:    60x
```

In the breakdown, PL/SQL was 912 ms. Converting to FORALL gives ~120 ms — a 792 ms
saving from 8% of the problem. Worth doing, but only **after** the 27% region.

## 9. Rendering — Dynamic Action Cost

```
10 dynamic actions, no page caching: 3,008 ms

Per-action overhead (event binding, condition evaluation, potential AJAX):
  ~250 ms per action with a complex condition

Consolidating 10 → 3 actions, with precomputed flags:
  3 × 90 ms = 270 ms, plus base render
```

```
Rendering: 3,008 ms → 1,410 ms   = 1,598 ms saved (53%)
```

**Consolidating actions on the same element is one of the cheapest wins
available** — no SQL changes, no cache, no schema change.

## 10. Theme Assets — The Invisible 2.5 Seconds

```
Universal Theme CSS + JavaScript: ~1.8 MB uncompressed
Client connection:                5 Mbps = 625 KB/s

Transfer time: 1.8 MB / 625 KB/s = 2.9 s
```

**This happens before the first region renders.** It does not appear in APEX Debug
because Debug measures server time.

| Configuration | Size | Transfer at 5 Mbps |
|---------------|------|--------------------|
| Uncompressed | 1.8 MB | 2.9 s |
| Minified | 0.8 MB | 1.3 s |
| Minified + gzip | 0.25 MB | **0.4 s** |

```
Saving: 2.5 s of pre-render time.

Comparison: the entire server-side optimisation (12 s → 2.75 s) saved 9.25 s.
Theme assets are 27% of the total user-visible improvement, from a checkbox.
```

**This is why "measure everything the user experiences", not only what the server
reports.**

## 11. Combined User-Visible Timeline

### Before

```
Theme assets transfer    2,900 ms
Server processing      11,100 ms   (12,000 total minus rendering overlap)
Rendering               1,400 ms
-----------------------------------------
Total                ~14,600 ms
```

### After

```
Theme assets transfer      400 ms
Server processing        1,750 ms
Rendering                 600 ms
-----------------------------------------
Total                  ~2,750 ms
```

```
5.3x improvement.

Server-measured p95:  14.6 s → 2.75 s
User-perceived:        14.6 s → 2.75 s   (both improved, but the user felt more,
                                         because the asset transfer was invisible)
```

## 12. Attribution Order — Effort Versus Return

| Rank | Component | Time | Fix effort | Return |
|------|-----------|------|-----------|--------|
| 1 | Region: Orders | 3,214 ms | 2 hrs | 3,024 ms |
| 2 | Theme assets | 2,900 ms | 15 min | 2,500 ms |
| 3 | Rendering | 3,008 ms | 3 hrs | 1,598 ms |
| 4 | Charts (cache) | 2,120 ms | 1 hr | 1,804 ms |
| 5 | Session state | 604 ms | 30 min | 514 ms |
| 6 | PL/SQL | 912 ms | 4 hrs | 792 ms |
| 7 | Regions 5-8 | 20 ms | — | ~0 |

**The 15-minute theme fix ranks second by return.** This is why attribution must
include transfer time, not only server timings.

## 13. Is It Even the Application?

```
If db file sequential read dominates:
  → The application IS partly responsible (more selective SQL = less I/O)
  → But the root cause is storage latency. Escalate.

If library cache latch dominates:
  → Application. Fix hard parses. Fully within reach.

If CPU is saturated from all tenants:
  → Infrastructure. Application work will not help.
```

```
Before escalating, confirm with v$system_event which class dominates.
Escalating a storage problem as "APEX is slow" wastes weeks.
```

## 14. p95 Reporting

```
Distribution across 3,500 views:
  Average:  3,240 ms   ← "acceptable"
  p50:      2,100 ms
  p95:     14,600 ms   ← "unacceptable"
  p99:     31,200 ms
```

**The average passes and p95 fails.** 5% of sessions — 175 per week — cannot work.

```
Requirement: under 3 seconds p95
Reported:    under 3 seconds p95   ← the only number that satisfies the requirement
```

**Measure and report the same statistic the requirement names.**

## 15. Full Before/After

| Component | Before | After | Fix |
|-----------|--------|-------|-----|
| Region: Orders | 3,214 ms | 190 ms | Sargable predicate + covering index |
| Region: Customers | 1,802 ms | 180 ms | Bind variable |
| 3 charts | 2,120 ms | 340 ms | Region cache, 60 s TTL, 85% hit rate |
| PL/SQL | 912 ms | 120 ms | FORALL |
| Rendering | 3,008 ms | 1,410 ms | 10 DAs consolidated to 3 |
| Session state | 604 ms | 90 ms | Lookup blob removed |
| Regions 5–8 | 20 ms | 20 ms | — |
| Theme assets | 2,900 ms | 400 ms | Minify + gzip |
| **Total** | **14,580 ms** | **2,750 ms** | **5.3×** |

**Every row is attributable to one specific change.** That is what makes the result
defensible and each fix independently reversible.