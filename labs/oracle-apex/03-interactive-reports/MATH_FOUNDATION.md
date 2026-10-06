# Lab 03: Interactive Reports — Math Foundation

## 1. The Base Query Cost Model

An Interactive Report on page N issues, on every render:

```
SELECT (page 1, rows shown)          1
SELECT COUNT(*)  (pagination)        1
  -- only when "Row Count" is set to
  -- "Count All" or "Count Range"
```

```
Base query, 2,000,000-row orders table, date filter of 1 month:
  Rows in last month:              62,000  (0.62% selectivity)
  Index on order_date:            62,000 index entries + 62,000 rows read
  Index range scan + fetch:        ~48 ms
  No index: full scan + top-N:    ~1,150 ms
```

| Filter | Selectivity | Rows read | Elapsed |
|--------|-------------|-----------|---------|
| No filter | 100% | 2,000,000 | ~1,150 ms |
| `status = 'SHIPPED'` | 62% | 1,240,000 | ~820 ms |
| `order_date >= :d` | 3% | 62,000 | ~48 ms |
| Date + status | 1.9% | 38,000 | ~34 ms |
| Date + status + region | 0.4% | 8,000 | ~11 ms |

```
Every additional selective predicate multiplies down.
Every additional low-selectivity predicate barely moves.
```

## 2. Sargability — Index Used or Lost

```sql
-- NON-SARGABLE: function applied to the INDEXED COLUMN
WHERE TRUNC(o.order_date) = :p_date
WHERE TO_CHAR(o.order_date,'YYYY-MM') = :p_month
WHERE UPPER(o.customer_name) = UPPER(:p_name)

-- SARGABLE: the column is compared to a value, functions applied to the bind
WHERE o.order_date >= :p_date AND o.order_date < :p_date + 1
WHERE o.order_date >= ADD_MONTHS(:p_month,1)
WHERE UPPER(o.customer_name) = UPPER(:p_name)  -- only if index is on UPPER(...)
```

```
Non-sargable month equality, 1 month matching out of 24:
  Rows read: 2,000,000 (whole table scanned, function applied per row)
  Elapsed:   ~1,800 ms

Sargable month range:
  Rows read: 83,000 (1/24 of the table, straight from the index)
  Elapsed:   ~62 ms

Ratio: ~29×
```

**This is the highest-return change available in a slow APEX report, and it is
free.** It changes nothing about the user experience.

## 3. Selectivity Estimation and Misestimate Impact

```
Table: 2,000,000 rows. Last analysed at 1,000,000 rows (before a bulk load).
num_distinct on order_date: stale

Actual rows matching a 1-month range:  62,000
Estimated rows matching:               31,000
Misestimate factor: 2.0×
```

| Optimiser decision | At 31,000 est. | At 62,000 actual |
|-------------------|----------------|------------------|
| Join to customers | Nested loops (25k probes) | Hash join (1 scan) |
| Sort strategy | Full sort of estimate | Top-N via index |
| Elapsed | ~890 ms | ~48 ms |

```
A 2× misestimate can flip the join method entirely.
Nested loops instead of hash: 18.6× slower on this shape.
```

Check `last_analyzed` before concluding the query is badly written:

```sql
SELECT table_name, num_rows, last_analyzed
  FROM user_tables WHERE table_name = 'ORDERS';
```

## 4. Bind Variables and Plan Stability

The IR base query executes on every render, every filter change, every sort,
every page click. That is dozens of executions per user session:

```
One session, 40 IR interactions:
  Literal SQL:  40 distinct statements, 40 hard parses × 1.8 ms = 72 ms
  Bind SQL:      1 statement, 1 hard parse + 40 soft parses      =  2.0 ms
```

```
Rule: never concatenate into the query.

  WHERE region = '&P1_REGION'      -- hard parse per value, injection risk
  WHERE region = :P1_REGION        -- one parse, safe
```

```
Shared pool footprint:
  Distinct literal statements: 500 region values × ~4 KB = 2 MB per IR,
                               never evicted while the cursor is hot
  Bind version:                 1 statement × 4 KB = 4 KB
```

## 5. Row-Count-Driven Rendering Cost

```
IR render cost ≈ 0.02 ms per rendered row (25 columns, plain text)
              + ~2 ms fixed per column for formatting
```

| Rows on page | Render | Total region cost | Note |
|--------------|--------|-------------------|------|
| 25 | 0.5 ms | ~51 ms | Default, query-bound |
| 100 | 2 ms | ~54 ms | Still query-bound |
| 1,000 | 20 ms | ~75 ms | Getting visible |
| 10,000 | 200 ms | ~290 ms | **Now rendering-bound** |
| 50,000 | 1,000 ms | ~1,400 ms | Unusable |

```
Break-even where rendering exceeds SQL:
  SQL ~48 ms / 0.02 ms per row ≈ 2,400 rows

Below 2,400 rows on the page, optimise the query.
Above it, reduce the page size.
```

## 6. Pagination Is Not a Filter

```sql
-- APEX sends this for page 400 of a 10,000-row report
SELECT ... WHERE <filters>
ORDER BY order_date DESC
OFFSET 9750 ROWS FETCH NEXT 25 ROWS ONLY
```

```
Rows read = offset + page_size

Page    1   ->     25 rows read
Page   10   ->    250 rows read
Page  100   ->  2,500 rows read
Page  400   ->  9,775 rows read
```

```
Cost on the unfiltered 2M-row table (full scan + sort each time):
  Page 1:    ~1,150 ms
  Page 400:  ~1,480 ms
```

### Keyset pagination

```sql
WHERE (order_date, order_id) < (:last_date, :last_id)
ORDER BY order_date DESC, order_id DESC
FETCH FIRST 25 ROWS ONLY
```

```
Keyset cost is flat: ~48 ms at page 1 and at page 400.
Offset cost grows linearly with depth.
```

Set **Pagination Type = Cursor** on the IR and the framework uses keyset.

## 7. Maximum Row Count

```
IR "Maximum Rows to Fetch":
  0 / unlimited  -> COUNT(*) over the full range, and export of everything
  50,000         -> COUNT capped, export capped, memory bounded

COUNT(*) on 2,000,000 rows:                ~95 ms
COUNT of a capped 50,000-row range:        ~18 ms
```

```
Export cost, set-based (APEX_DATA_EXPORT):
   50,000 rows  ≈   6 s
  500,000 rows  ≈  62 s
  2,000,000 rows ≈ 250 s  -- exceeds a 60 s HTTP timeout

A cap is not a limitation. It is a refusal to attempt work that cannot finish.
```

## 8. Export and Email Cost

```
Download (browser, current filters):   bounded by export rows
CSV via APEX_DATA_EXPORT:              ~120 µs per row
XLSX (multiple sheets):                ~1.4 ms per row
PDF (paginated, 50 rows/page):         ~9 ms per row
```

| Format | 50,000 rows | Timeout risk at 60 s |
|--------|-------------|-----------------------|
| CSV | 6 s | None |
| XLSX | 70 s | **Yes** |
| PDF | 450 s | **Yes, badly** |

```
Email attach: 50,000 rows × 120 µs = 6 s to build
              + APEX_MAIL queue submit
Subscriptions must be capped or they will queue forever.
```

## 9. Session State and Report Memory

```
IR row-count cache, session state item:
  Value stored: the count as text        ~12 bytes
  Without it:  COUNT(*) re-run every render: ~95 ms

Filter state persisted in session state (4 filters):
  ~200 bytes per session. Deserialisation: < 0.1 ms.
```

```
IR "Report" attribute used to cache region attributes in session state:
  Region with 6 attributes ≈ 1.2 KB
  Cost of mis-using it as a data cache: a 1.2 KB JSON blob
  parsed on every render ≈ 0.4 ms — and stale data nobody expects
```

**`apex_application.report` is for report configuration, never for row data.**
Caching rows in it is the most common misuse of the feature.

## 10. Search on All Columns

```
"Search on All Columns" = LIKE '%' || :SEARCH || '%' across every column

Indexes are not usable for a leading-wildcard LIKE.
Cost = full scan + per-row LOWER/UPPER evaluation.

25 searchable columns, 2,000,000 rows:
  Indexed, filtered search:        ~50 ms
  Search-on-all-columns search:  ~2,400 ms
```

```
Searchable column count is a direct cost multiplier:
  5 columns  ->  ~700 ms
  10 columns -> ~1,050 ms
  25 columns -> ~2,400 ms
```

Disable search on large tables, or add a generated indexed search column.

## 11. Filtered Report Counts

```sql
-- Declarative column filters rewrite the base query; each distinct filter
-- combination is a different SQL shape and a different plan.
```

```
Users/day:            400
Sessions/day:         960
Distinct filter combos a user builds per session:  ~5
Distinct combos/day:  4,800

Hard parses:  4,800 × 1.8 ms = 8.6 s/day   (with binds in the base query,
                                          these are soft parses of ONE cursor)
Without binds on filters:  4,800 hard parses
```

## 12. Before/After Summary

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Base query (date filter) | 1,150 ms | 48 ms | 24× |
| Month filter form | 1,800 ms | 62 ms | 29× |
| Page 400 render | 1,480 ms | 48 ms | 31× |
| Hard parses per session | 40 | 1 | 40× |
| Export rows capped | 2,000,000 | 50,000 | bounded |
| All-columns search | 2,400 ms | 700 ms | 3.4× |
| Rows rendered per page | 10,000 | 25 | 400× |

Every row is attributable to one change: a sargable predicate, a cursor, a bind,
a cap, or a narrower search. Measure them separately so a regression can be
traced to a specific edit.
