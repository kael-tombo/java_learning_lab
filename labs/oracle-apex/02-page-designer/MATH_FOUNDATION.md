# Lab 02: APEX Page Designer — Math Foundation

## 1. Unfiltered vs Filtered Region Cost

The 11-second problem, quantified.

### Before: four independent unfiltered queries over 5M rows

```
SELECT category_name, SUM(net_amount) FROM sales_order GROUP BY category_name;
  Full scan + hash group by       →  3,200 ms

SELECT channel_name, SUM(net_amount) FROM sales_order GROUP BY channel_name;
  Full scan + hash group by       →  3,100 ms

SELECT region_id, TO_CHAR(order_date,'YYYY-MM'), SUM(net_amount)
  FROM sales_order GROUP BY ...   →  3,000 ms

SELECT ... detail list           →  1,600 ms
                                    -----------
                                     10,900 ms  ≈ 11 seconds
```

### After: filtered with matching indexes

```
Same four queries with order_date >= :P1_FROM_DATE AND < :P1_TO_DATE + 1
Date range: last 30 days of a 5M-row / 24-month table ≈ 6% of rows ≈ 310,000

Index range scan + group by      →    210 ms each
                                  ->   840 ms SQL
Framework + rendering            ->   420 ms
                                    --------
Total page load                    ~1,260 ms
```

```
Improvement: 11,000 ms → 1,260 ms = 8.7x
SQL time:      10,900 ms →    840 ms = 13x
```

**The filtering is the whole fix.** No amount of PL/SQL optimisation would have
helped a query that has to aggregate five million rows every page load.

## 2. Filter Selectivity — the Number That Matters

```
Sales table: 5,000,000 rows over 24 months
Rows per month:                    ~208,000
Rows per day:                        ~6,900
```

| Filter | Rows matched | Relative cost |
|--------|-------------|---------------|
| None | 5,000,000 | 1.00x |
| 1 month | 208,000 | 24x faster |
| 30 days | 208,000 | 24x faster |
| 7 days | 48,300 | 104x faster |
| 1 day | 6,900 | 725x faster |
| 1 region + 30 days | 26,000 | 192x faster |
| 1 region + 7 days | 6,000 | 833x faster |

```
Aggregation cost ∝ rows matched
```

**This is why default filters matter more than any query optimisation.** A
dashboard that opens with no date filter costs 24× more than one defaulting to
30 days — which is why the default belongs in a Computation, not left empty.

## 3. Index Support for Aggregation

Grouping `SUM(net_amount)` by month still reads every matching row:

```
Rows read for the group:            208,000
Without a covering index:           208,000 table + index row reads
With (order_date, region_id, net_amount):
                                    208,000 index-only reads (no table access)
```

| Index type | Buffers | Notes |
|-----------|---------|-------|
| `order_date` only | ~1,600 | Table lookups for `net_amount` |
| `(order_date, region_id, net_amount)` covering | ~480 | Index-only scan |

```
Reduction: 3.3x from making the index covering
```

The table lookups eliminated are the expensive part — a logical read of a wide
table row costs several times a narrow index entry.

## 4. Region Count and Page Load

```
Framework overhead (fixed):     ~400 ms
SQL per region (filtered):       ~210 ms
```

| Regions | SQL time | Total load |
|---------|----------|------------|
| 1 | 210 ms | ~610 ms |
| 4 | 840 ms | ~1,240 ms |
| 8 | 1,680 ms | ~2,080 ms |
| 12 | 2,520 ms | ~2,920 ms |

**Framework overhead stops dominating around 2 regions.** Past that, every region
added is nearly linear cost, which is what makes "reduce region count" a real
lever on a heavy page.

### Comparing removal strategies

```
Remove a chart region (210 ms of a 1,240 ms page):     saves 210 ms  (17%)
Remove a region and share the query via a collection:
  4 regions → 1 shared query                          saves 630 ms  (51%)
Lazy-load the 2 charts until expanded                  saves 420 ms  (34%)
```

**Sharing the query via a collection is the highest-return option**, and it is
covered in Lab 07.

## 5. Page Submit vs Dynamic Action

A filter change on a 4-region page.

| | Page submit | Dynamic Action (AJAX refresh) |
|---|---|---|
| Queries run | 4 regions + any processes | 4 regions (or fewer) |
| Processes run | all | none |
| HTML re-rendered | full page | targeted regions |
| Framework overhead | ~400 ms | ~120 ms |
| Scroll/focus preserved | no | yes |
| Perceived latency | high | low |

```
Page submit:   840 ms SQL + 400 ms framework = 1,240 ms + flicker
AJAX refresh:  840 ms SQL + 120 ms overhead  =   960 ms, no flicker
```

The SQL is identical — **the AJAX win is the overhead and the interaction
quality, not the queries.** On a page where only 2 of 4 regions depend on the
changed item:

```
Targeted refresh of 2 regions: 420 ms SQL + 120 ms = 540 ms
```

That is where the real gain appears: **target the action at only what depends on
the change.**

## 6. Layout Span Math

12-column grid.

| Region | Columns | % width | Desktop behaviour |
|--------|---------|---------|-------------------|
| IR detail | 12 | 100% | Full width |
| Pie category | 6 | 50% | Half |
| Pie channel | 6 | 50% | Half (adjacent) |
| Bar month | 12 | 100% | Full |

### Responsive reflow

```
1440 px:  [ Pie A (6) ][ Pie B (6) ]      side by side
768 px:   [ Pie A (6) ][ Pie B (6) ]      still side by side
375 px:   [ Pie A        ]                stacked
          [ Pie B        ]
```

**Spans let the theme decide when to stack.** Fixed pixel widths do not:

```
Fixed 480px region at 375px viewport → 105px horizontal scroll on every page
```

## 7. Chart Data Volume

Rendering a chart with too many points is a rendering cost, not a query cost.

| Data points | Render time | Readable? |
|--------------|-------------|-----------|
| 6 (months) | ~40 ms | Yes |
| 12 | ~60 ms | Yes |
| 52 (weeks) | ~180 ms | Marginal |
| 365 (days) | ~900 ms | No |

**Bar by month over a 2-year range is 24 points** — within the readable band. The
same chart un-aggregated by day over the same range would be 730 points and would
add a second of rendering time for less insight.

```
Aggregation is a rendering optimisation as well as a query one.
```

## 8. Drill-Through Key Design

```
Passing a label:   "Mar 2026"          → editable, non-unique, breaks on rename
Passing a key:     "2026-03"          → stable, sortable, compact
Passing an ID:     region_id = 4      → referentially stable
```

```
Label in URL:  ~10 chars, fragile
Month key:      7 chars, sortable, survives a display-name change
Region ID:      1 char, referentially stable
```

The label is 3 characters longer and infinitely more fragile. The saving is
negligible; the robustness is not.

## 9. Lazy Loading Math

```
Charts not visible on load: 2 of 4 regions

Eager:    4 queries × 210 ms = 840 ms
Lazy:     2 queries × 210 ms = 420 ms
Saving:   420 ms (34% of page load)
```

Cost when the user *does* expand them:

```
Expanded: 4 queries × 210 ms + 120 ms overhead = 960 ms
```

**Lazy loading trades a guaranteed cost for a conditional one.** Correct when most
sessions do not open every panel — which is true for a dashboard where two of
four charts are usually not needed.

## 10. Default Filter Value

```
Dashboard opened with no date filter:   11,000 ms
Dashboard defaulting to 30 days:         1,260 ms
```

A single computation changes the default experience by 8.7×. This is the
highest-value single change on the page and it is four lines of PL/SQL.

## 11. Cascading LOV Cost

```
P1_CATEGORY LOV without cascading:
  Categories for ALL regions          ~40 options
P1_CATEGORY LOV with P1_REGION parent:
  Categories in the selected region   ~8 options
```

```
Database work for a cascading LOV: roughly 1 extra query per change
Usability gain: 40 options → 8, and no impossible combinations
```

Worth one query. **Impossible filter combinations** (a category that does not
exist in the selected region) are the real justification — they produce empty
regions and confuse users.

## 12. Empty-State Cost

| Approach | Query cost | User experience |
|----------|-----------|-----------------|
| No handling | Full query, empty chart | Confusing: "is it broken?" |
| Region condition | **Query skipped** | Clean: chart hidden |
| Static "no data" region | Full query | Explicit |

```
Region display condition with a COUNT subquery: +1 count query (~30 ms)
Avoided: the chart's own query (~210 ms)
Net: saves ~180 ms when empty; costs 30 ms when populated
```

Worth it. And the UX benefit is the real return.

## 13. Full Before/After Summary

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Page load | 11,000 ms | 1,260 ms | 8.7x |
| SQL time | 10,900 ms | 840 ms | 13x |
| Filter change | ~1,900 ms | ~540 ms | 3.5x |
| Queries per render | 4 unfiltered | 4 filtered | same count, 13x cheaper each |
| Rows read per render | 20,000,000 | 2,480,000 | 8x |
| Flicker on filter | yes | no | — |

```
Rows read: 4 regions × 5M = 20M  →  4 regions × 310k = 1.24M (per region share)
The number that moved most is rows read, and no code changed — only the predicate.
```