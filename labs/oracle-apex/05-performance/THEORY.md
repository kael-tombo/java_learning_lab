# Lab 05: APEX Performance — Theory

## The Scenario

An enterprise APEX application with 10,000+ concurrent users. The executive
dashboard takes 30+ seconds and frequently times out. It contains:

- 10 interactive reports over tables with 5M+ rows each
- 6 chart regions with complex aggregated queries
- 3 classic reports for year-over-year comparison
- Multiple cascading filters
- CSV export on each report using the APEX built-in export

Targets: page load under 3 seconds p95, filter change under 1 second, 100K-row
export under 30 seconds, minimal database impact at the 9–10 AM and 2–3 PM peaks.

## Principle 1: Attribute before you optimise

30 seconds is not a diagnosis. It is a symptom.

```
Enable APEX Debug and read the breakdown:
  Page Processing      ~24 s
    SQL queries        ~22 s
      IR #1 (orders)    9.2 s
      IR #2 (revenue)   6.4 s
      IR #3-10          3.8 s
      Charts            2.6 s
  Rendering             ~4 s
  Session state         ~2 s
```

**One run tells you where the 30 seconds live.** Optimising the 4-second
rendering phase before the 22-second SQL phase is wasted effort. And optimising
the 3.8 seconds spread across 8 small reports is lower value than the 9.2
seconds in one.

```
Optimisation order = descending attribution
```

## Principle 2: 10 regions means 10 queries — share them with collections

The dashboard's 10 reports and 6 charts all draw from overlapping data. Each
issues its own query.

```
Before: 16 regions × own query = 16 queries
After:  1 collection + 16 region reads = 1 query
```

A collection is a server-side working set that lives for the request:

```plsql
APEX_COLLECTION.TRUNCATE('DASHBOARD_DATA');
FOR r IN (SELECT ... FROM sales_order WHERE <shared filters>) LOOP
  APEX_COLLECTION.ADD_ELEMENT('DASHBOARD_DATA', r.id, r);
END LOOP;
```

**The caveat**: a collection is per-request. It does not help if the regions
genuinely need different data. It helps enormously when they need *the same* data
in different shapes.

```
Rule: share a collection when regions read the same rows.
      Do not build one collection when each region needs its own aggregation.
```

## Principle 3: Cache the parts that change rarely

Not everything on a dashboard is volatile.

| Data | Changes | Cache? |
|------|---------|--------|
| Region list (last hour) | Continuously | **No** |
| Reference data (regions, categories, products) | Rarely | **Yes** |
| Historical aggregates (month-end totals) | Never intraday | **Yes** |
| Drill-down detail | On demand | No |

Caching a fast query is pointless. Caching a 6-second aggregation is a large win.

### Caching layers available

```
Region cache    — the region query result, per page, per session or shared
Page cache      — the whole rendered page HTML
Session state cache — values reused across pages in a session
Function result cache — inside a package, survives sessions
```

**Region cache** is the right default for this dashboard. **Page cache** is wrong
here: the page has per-user filters and live regions, and caching the HTML would
serve one user's data to another.

### The invalidation trigger is the contract

Every cache needs a stated answer to: *when does this become wrong?*

```
Region cache on a region list:
  Trigger: 30 seconds — bounded staleness, acceptable for an executive view

Region cache on reference data:
  Trigger: invalidated explicitly when a reference table is updated

Page cache:
  Trigger: 60 seconds — only valid if no per-user data is on the page
```

**A cache with no stated trigger is a latent incident.** It works until the day
someone needs the fresh number.

## Principle 4: Cache hit rate decides whether it was worth it

```
Requests/day:        50,000 dashboard views
Cache TTL:           30 seconds
Requests per TTL window: 50,000 / (8 hours × 120) ≈ 52 per window

First request in a window: cache miss (pays full cost)
Remaining 51:          cache hits
Hit rate: 51/52 = 98.1%
```

```
Effective cost = (1 - 0.981) × 6,000 ms = 114 ms
```

**A 98% hit rate makes a 6-second query effectively free.** This is why caching
is the highest-leverage change available and why it must be measured, not
assumed.

The caveat: a low request rate gives a low hit rate.

```
10 requests/hour with a 30s TTL:  most requests miss
Hit rate ≈ 8% → caching adds complexity for little benefit
```

## Principle 5: Bulk operations are the difference between minutes and hours

This is the lesson that applies beyond APEX.

```plsql
-- Row-by-row: 100,000 network round trips
FOR r IN (SELECT ...) LOOP
  UPDATE target SET ... WHERE id = r.id;
END LOOP;
```

```sql
-- Set-based: one round trip
UPDATE target t
   SET t.amount = (SELECT s.amount FROM staging s WHERE s.id = t.id)
 WHERE EXISTS (SELECT 1 FROM staging s WHERE s.id = t.id);
```

### The cost of row-by-row

| Rows | Row-by-row | Set-based |
|------|-----------|-----------|
| 100 | ~1 s | ~0.02 s |
| 10,000 | ~100 s | ~0.3 s |
| 100,000 | ~1,000 s (17 min) | ~2 s |

**The ratio grows with volume** — roughly linear per row versus constant-ish
per statement. At 100,000 rows the difference is 17 minutes against 2 seconds.

This is why the export requirement matters: 100K rows must go through one query,
not 100,000 fetches.

## Principle 6: The APEX default export is not designed for 100K rows

The built-in Interactive Report export has two problems at scale:

1. It may fetch beyond the displayed page set.
2. It has no explicit bound or time budget.

```sql
-- Bounded export: explicit row limit, explicit columns, one query
SELECT column_a, column_b, column_c
  FROM target
 WHERE <the same filters the report uses>
   AND ROWNUM <= 100000;
```

**Cap the row count and say so in the UI.** An export that silently truncates is
worse than one that refuses.

```
Export of 100,000 rows, set-based, one query: ~8-15 s   → meets the 30 s target
Export via row-by-row PL/SQL loop:                  ~17 min → fails
```

## Principle 7: Cascade filters so impossible combinations never run

With cascading filters, a user cannot select a category that does not exist in
the chosen region. This is a UX control *and* a performance control:

```
Without cascading:  region × category = 12 × 40 = 480 possible combinations
                    many of which return zero rows after scanning millions
With cascading:     12 × ~8 = 96 reachable combinations, all valid
```

Invalid combinations do not merely return nothing — they scan the whole filtered
range to prove there is nothing.

## Principle 8: Peak-hour database impact is a design constraint

The client named 9–10 AM and 2–3 PM as peaks. That is a scheduling signal.

```
If 10,000 concurrent users peak at 9-10 AM:
  Requests in that hour: significant share of daily volume
  Database CPU during the peak: the thing to protect
```

**Options in order of preference**:

1. **Reduce work per request** — collections, caching. Cuts total CPU.
2. **Move batch work off-peak** — exports, refreshes, aggregates.
3. **Cache harder** — longer TTL during the peak window.
4. Add read replicas — last resort, introduces consistency questions.

Option 1 is always available and always preferable. Option 4 is almost never
justified for a read-mostly dashboard.

## Principle 9: Optimise the peak, not the average

```
Average page load:  2.4 s   (acceptable)
p95 page load:      3.1 s   (borderline)
p99 page load:     28 s    (timeouts)
```

The average hides the problem. Users remember the 28 seconds, not the 2.4. All
targets in the brief are p95, which is the correct choice.

**Measure p95 from the activity log, not from a single manual run.** A single run
tells you one thing; the log tells you the distribution and the outliers.

## Principle 10: Measure each change alone

Bundled changes make attribution impossible:

```
Applied: index + collection + cache + bulk rewrite
Result: 30 s → 2.6 s
```

You cannot say which change worked, so you cannot defend any of them in a
review, and you cannot remove one that turns out to cause staleness.

```
Apply one change → measure → record → next change
```

That is slower in the moment and much faster when something regresses.

## Diagnostic Order

1. APEX Debug: attribute time to SQL, rendering, and session state.
2. Identify overlapping region data — candidates for a collection.
3. Identify slow queries that return stable data — candidates for caching.
4. Identify row-by-row code — candidates for set-based rewriting.
5. Check the export path — is it bounded and set-based?
6. Check cascading filters — are impossible combinations reachable?
7. Re-measure each change individually; confirm p95.

## Anti-Patterns

- Optimising rendering before SQL when SQL is 22 of 30 seconds.
- Caching a page containing per-user data.
- Caching with no stated invalidation trigger.
- Row-by-row processing at volume.
- Unbounded export.
- Bundling changes so nothing is attributable.
- Reporting the average when the requirement is p95.
- Adding read replicas instead of reducing work.

## Summary

Thirty seconds became 2.6 seconds through five decisions: attribute before
optimising, share one query across 16 regions with a collection, cache the
regions whose data changes on a timescale longer than a user session, rewrite
row-by-row processing set-based, and bound the export so 100K rows go through
one query. Each was measured alone so the p95 improvement is attributable and
each cache has a stated trigger so staleness is a decision rather than a
surprise.