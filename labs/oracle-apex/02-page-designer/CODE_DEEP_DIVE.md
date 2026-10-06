# Lab 02: APEX Page Designer — Code Deep Dive

## 1. Layout Definition

```
Page 2 — Sales Dashboard
Layout:  Grid (12 columns)
  Row 1: new row, height auto
  Row 2: new row, height auto
  Row 3: new row, height auto
```

| Region | New Row | Start Col | Col Span | Height |
|--------|---------|-----------|----------|--------|
| FilterBar (Static Content) | Yes | 1 | 12 | auto |
| Sales IR | Yes | 1 | 12 | auto |
| Pie — By Category | Yes | 1 | 6 | 300px |
| Pie — By Channel | No | 7 | 6 | 300px |
| Bar — Revenue by Month | Yes | 1 | 12 | 350px |

**Never absolute-position a region.** Spans and rows are what make the layout
responsive.

## 2. Shared Filter Items

```
Static Content region "Dashboard Filters"
  P1_FROM_DATE   Date Picker, default via computation
  P1_TO_DATE     Date Picker
  P1_REGION      Select List (LOV), optional (NULL = all)
  P1_CATEGORY    Select List (LOV), optional
```

## 3. Computation — Default Date Range (runs every render)

```sql
-- Computation: "Default Date Range"
-- Point: Before Header
-- Type:   SQL Expression
CASE WHEN :P1_FROM_DATE IS NULL THEN
       TO_CHAR(TRUNC(SYSDATE) - 30, 'YYYY-MM-DD')
     ELSE :P1_FROM_DATE END
```

```sql
-- Second computation for the end date
CASE WHEN :P1_TO_DATE IS NULL THEN
       TO_CHAR(TRUNC(SYSDATE), 'YYYY-MM-DD')
     ELSE :P1_TO_DATE END
```

## 4. Region Queries — Every One Binds the Filters

### Sales Interactive Report

```sql
SELECT so.order_id,
       so.order_number,
       so.order_date,
       so.customer_name,
       so.region_name,
       so.category_name,
       so.channel_name,
       ROUND(so.net_amount, 2) net_amount
  FROM sales_order so
 WHERE so.order_date >= :P1_FROM_DATE          -- sargable range
   AND so.order_date <  :P1_TO_DATE + 1
   AND (:P1_REGION   IS NULL OR so.region_id   = :P1_REGION)
   AND (:P1_CATEGORY IS NULL OR so.category_id = :P1_CATEGORY)
 ORDER BY so.order_date DESC, so.order_id DESC;
```

### Pie — Revenue by Category

```sql
SELECT so.category_name AS label,
       ROUND(SUM(so.net_amount), 2) AS value
  FROM sales_order so
 WHERE so.order_date >= :P1_FROM_DATE
   AND so.order_date <  :P1_TO_DATE + 1
   AND (:P1_REGION IS NULL OR so.region_id = :P1_REGION)
 GROUP BY so.category_name
 ORDER BY 2 DESC;
```

### Pie — Revenue by Channel

```sql
SELECT so.channel_name AS label,
       ROUND(SUM(so.net_amount), 2) AS value
  FROM sales_order so
 WHERE so.order_date >= :P1_FROM_DATE
   AND so.order_date <  :P1_TO_DATE + 1
   AND (:P1_CATEGORY IS NULL OR so.category_id = :P1_CATEGORY)
 GROUP BY so.channel_name
 ORDER BY 2 DESC;
```

### Bar — Revenue by Month (the drill-through source)

```sql
-- Return the month KEY, not just the label, so drill-down can pass an ID
SELECT so.region_id                 AS region_id,     -- for drill-through
       TO_CHAR(so.order_date, 'YYYY-MM') AS month_key, -- for drill-through
       TO_CHAR(so.order_date, 'Mon YYYY') AS label,   -- for display
       ROUND(SUM(so.net_amount), 2) AS value
  FROM sales_order so
 WHERE so.order_date >= :P1_FROM_DATE
   AND so.order_date <  :P1_TO_DATE + 1
   AND (:P1_CATEGORY IS NULL OR so.category_id = :P1_CATEGORY)
 GROUP BY so.region_id, TO_CHAR(so.order_date, 'YYYY-MM'), TO_CHAR(so.order_date,'Mon YYYY')
 ORDER BY MIN(so.order_date);
```

> **Both charts bind `P1_CATEGORY` but only the category chart binds
> `P1_REGION`.** This is deliberate: a pie split by category *within* the
> selected region is meaningful; splitting by channel *within* a category is not.
> Deciding this per chart is part of designing the filter set, not a detail.

## 5. Region Display Conditions — Empty States

```
-- Region: Pie — By Category
-- When:  "region is not null" AND the region's own query returned 0 rows
-- Use a SQL Expression condition:
(SELECT COUNT(*) FROM sales_order so
  WHERE so.order_date >= :P1_FROM_DATE
    AND so.order_date <  :P1_TO_DATE + 1
    AND (:P1_REGION IS NULL OR so.region_id = :P1_REGION)) > 0
```

Add a companion Static Content region "No data" with the inverse condition:

```sql
(SELECT COUNT(*) FROM sales_order so
  WHERE so.order_date >= :P1_FROM_DATE
    AND so.order_date <  :P1_TO_DATE + 1) = 0
```

## 6. Dynamic Action — Filter Refresh

```
Dynamic Action: "Refresh dashboard on date change"

  Event:
    Trigger Type: Item
    Item:         P1_FROM_DATE
    Condition:    "is not null"
    (Create a second DA with identical settings on P1_TO_DATE,
     or use Event "Change" on a container)

  True Action:
    Action:  Refresh
    Target:  Regions → Sales IR, Pie Category, Pie Channel, Bar Month
    Wait:    Until element exists (prevent double-fire on date picker)
```

**`Wait: Until element exists`** is required for date pickers. Without it, the
change event fires mid-population and the regions refresh with a half-set value.

### Container-level alternative

```
Static Content region "Dashboard Filters"
  →  Dynamic Action on region: Event "Change" targeting any child item
```

One action instead of four; scales as items are added.

## 7. Drill-Through Dynamic Action on the Bar Chart

```sql
-- Dynamic Action: "Open order detail"
--   Trigger Type: Region
--   Region:       Bar — Revenue by Month
--   Condition:    Selection has a value
--
--   True Action: Execute JavaScript
--   JavaScript:
--   var d = $v(this.data);
--   var row = (d.row && d.row.length) ? d.row[0] : (d.row || d);
--   apex.util.getPageValue('P2_REGION_ID', function(v) {
--     apex.item.submit('P2_REGION_ID', row.region_id, true, false, false, function() {
--       apex.item.submit('P2_MONTH_KEY', row.month_key, true, false, false, function() {
--         apex.submit('GO_TO_DETAIL');
--       });
--     });
--   });
```

Then a Branch:

```
Branch: "Go to order detail"
  When:      "Page is" = "is not null on page load"
  Target:    Page 3 (Order Detail)
  Condition: :GO_TO_DETAIL = 'Y'
```

**`region_id` and `month_key` are IDs/keys, not labels.** Page 3 binds them:

```sql
SELECT order_id, order_number, order_date, customer_name, net_amount
  FROM sales_order
 WHERE region_id          = :P2_REGION_ID
   AND TO_CHAR(order_date,'YYYY-MM') = :P2_MONTH_KEY
 ORDER BY order_date;
```

## 8. Detail Page — Lazy-Loaded Region

```
Region: Order Detail
  Loading: "Lazy load" with a trigger of "Region Display Selector"

Static Content region "Show orders"
  DA: On Click → set :P2_LOADED = 'Y' → Refresh → Order Detail
```

Query starts with the guard:

```sql
SELECT /* existing query */
  FROM sales_order
 WHERE :P2_LOADED = 'Y'          -- no query cost until requested
   AND region_id = :P2_REGION_ID ...
```

## 9. Page Process with a Condition

```sql
-- Page Process: "Log dashboard usage"
-- Point:   On Page Load
-- Condition: :P1_REGION IS NOT NULL
-- Source:
BEGIN
  INSERT INTO dashboard_usage_log (user_name, from_date, to_date, region_id)
  VALUES (APEX_UTIL.SESSION_STATE('MY_CTX_USERNAME'),
          :P1_FROM_DATE, :P1_TO_DATE, :P1_REGION);
END;
/
```

Note the condition. Without it, the process logs a row on every render including
the initial defaults, which makes the log useless for measuring filter usage.

## 10. Server-Side Condition Guard on Invalid Ranges

```sql
-- Add to every region query, or better, a single validation before the regions:
-- Page Validation "End date after start date"
-- Condition (when displayed):
WHEN :P1_FROM_DATE IS NOT NULL
 AND :P1_TO_DATE IS NOT NULL
 AND TO_DATE(:P1_FROM_DATE,'YYYY-MM-DD') > TO_DATE(:P1_TO_DATE,'YYYY-MM-DD')
-- Message:
'Start date must be on or before end date. You entered ' ||
:P1_FROM_DATE || ' to ' || :P1_TO_DATE || '.'
```

## 11. LOV Definitions (Scoped)

```sql
-- P1_REGION
SELECT region_id, region_name FROM sales_region WHERE active_flag='Y' ORDER BY 2;

-- P1_CATEGORY — restrict to categories present in the selected region
SELECT DISTINCT c.category_id, c.category_name
  FROM category c
  JOIN sales_order so ON so.category_id = c.category_id
 WHERE :P1_REGION IS NULL OR so.region_id = :P1_REGION
 ORDER BY 2;
```

```sql
-- Cascading LOV needs the parent value on the parent item
-- Set "Cascading LOV Parent Item" = P1_REGION on P1_CATEGORY
```

## 12. Row-Level Security in Every Region Query

Every region query above needs the scoping predicate. Dashboard regions are the
most frequently forgotten place for it, because each query looks self-contained.

```sql
 AND so.region_id = current_user_region()     -- NULL → -1, fails closed
```

Add it to all four. A dashboard whose IR is scoped and whose charts are not
leaks the same data you just protected.

## 13. Query Count Verification

```sql
-- After building, enable APEX Debug and count:
SELECT region_name, sql_text FROM v$sql
 WHERE sql_text LIKE '%SALES_ORDER%'
   AND sql_id IN (/* statement ids from the Debug run */);
```

```sql
-- Confirm no literal dates crept in
SELECT sql_id, sql_text FROM v$sql
 WHERE sql_text LIKE '%SALES_ORDER%'
   AND sql_text NOT LIKE '%:P1_FROM_DATE%';
```

A `TO_DATE(:P1_FROM_DATE...)` in the SQL is fine — what matters is that the
column comparison stays sargable.

## 14. Index Support

```sql
CREATE INDEX ix_sales_date   ON sales_order (order_date);
CREATE INDEX ix_sales_region ON sales_order (region_id, order_date);
CREATE INDEX ix_sales_cat    ON sales_order (category_id, order_date);
```

```sql
-- Aggregations over 5M rows benefit from an index supporting the group
CREATE INDEX ix_sales_date_region ON sales_order (order_date, region_id, net_amount);
```

## 15. Page Performance Summary Query

```sql
-- Once monitoring is available
SELECT page_id, ROUND(AVG(elapsed_time),1) avg_ms, MAX(elapsed_time) max_ms,
       COUNT(*) executions
  FROM apex_user_activity_log
 WHERE application_id = 100
   AND page_id = 2
   AND view_time > SYSDATE - 7
 GROUP BY page_id;
```