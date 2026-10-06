# Lab 05: APEX Performance — Code Deep Dive

## 1. Attribution First — What APEX Debug Shows

```
Executive Dashboard — APEX Debug timing breakdown

  Page Processing                    24,180 ms
    SQL queries                      22,340 ms
      Region: Order Summary              9,240 ms
      Region: Revenue by Region          6,410 ms
      Region: Top Products               4,120 ms
      Region: Charts (6 combined)        2,570 ms
      Regions 11-16 (small)               180 ms
    PL/SQL processing                    840 ms
    Processes                            320 ms
  Rendering                             4,020 ms
  Session state                         1,760 ms
  -----------------------------------------------
  Total                                29,960 ms   ← the 30 seconds
```

**Optimisation order follows this table.** Two regions hold 70% of the time.

## 2. Collection — One Query, Many Regions

```sql
-- Page process: "Populate dashboard collection"
-- Point: Before Header (runs every render, before any region queries)

APEX_COLLECTION.TRUNCATE('DASHBOARD_ORDERS');

FOR r IN (
  SELECT so.order_id,
         so.order_date,
         so.region_id,
         sr.region_name,
         so.category_id,
         sc.category_name,
         so.product_id,
         sp.product_name,
         so.quantity,
         so.unit_price,
         ROUND(so.quantity * so.unit_price, 2) AS net_amount
    FROM sales_order so
    JOIN sales_region   sr ON sr.region_id   = so.region_id
    JOIN sales_category sc ON sc.category_id = so.category_id
    JOIN sales_product  sp ON sp.product_id  = so.product_id
   WHERE so.order_date >= :P1_FROM_DATE
     AND so.order_date <  :P1_TO_DATE + 1
     AND (:P1_REGION   IS NULL OR so.region_id   = :P1_REGION)
     AND (:P1_CATEGORY IS NULL OR so.category_id = :P1_CATEGORY)
) LOOP
  APEX_COLLECTION.ADD_ELEMENT('DASHBOARD_ORDERS', r.order_id, r);
END LOOP;
```

```sql
-- Every region now reads the SAME collection. No further table access.

-- Region: Order Summary (Interactive Report)
SELECT c.c001 order_id,
       TO_DATE(SUBSTR(c.c002,1,4)||'-'||SUBSTR(c.c002,6,2)||'-'||SUBSTR(c.c002,9,2),'YYYY-MM-DD') order_date,
       c.c004 region_name,
       c.c006 category_name,
       c.c010 quantity,
       c.c011 net_amount
  FROM apex_collection c
 WHERE c.collection_name = 'DASHBOARD_ORDERS'
   AND c.seq_key IS NOT NULL
 ORDER BY 2 DESC
```

```sql
-- Region: Revenue by Region (Chart)
SELECT c.c004 AS label, ROUND(SUM(c.c012), 2) AS value
  FROM apex_collection c
 WHERE c.collection_name = 'DASHBOARD_ORDERS'
   AND c.seq_key IS NOT NULL
 GROUP BY c.c004
 ORDER BY 2 DESC
```

```sql
-- Region: Top Products (Interactive Report)
SELECT * FROM (
  SELECT c.c008 AS label, ROUND(SUM(c.c012), 2) AS value
    FROM apex_collection c
   WHERE c.collection_name = 'DASHBOARD_ORDERS'
     AND c.seq_key IS NOT NULL
   GROUP BY c.c008
   ORDER BY 2 DESC
) WHERE ROWNUM <= 10
```

### Collection index layout

```sql
-- c001..cN follow the SELECT list order in the collection population
SELECT collection_name, c001, c002, c003, seq_key
  FROM apex_collection
 WHERE collection_name = 'DASHBOARD_ORDERS'
   AND ROWNUM <= 3;
```

**`c001`…`cNN` is positional.** Adding a column to the population query shifts
every subsequent index and silently corrupts every region. Treat the column list
as a contract and comment it.

### Collection sizing caveat

```sql
-- Collections live in the session's shared pool. Size them deliberately.
SELECT collection_name, COUNT(*) rows_collected
  FROM apex_collection
 GROUP BY collection_name
 ORDER BY 2 DESC;
```

For a very large result set, the collection itself becomes the cost. Filter
before populating.

## 3. Region Cache — Reference Data

```
Region: Product Filter List ( LOV)
  Source: SELECT product_id, product_name FROM sales_product WHERE active_flag='Y'
  Region Cache: 
    Type:       CACHE
    Time to Live: 3600 seconds
    Dependency: sales_product
    Session:    Shared
```

### Explicit invalidation when reference data changes

```sql
-- Page process on the reference-data maintenance page
APEX_REGION_CACHE.clear_cache(
  p_application_id => 100,
  p_region_id      => NULL,        -- all regions in the app
  p_sub_id         => NULL);

-- Or clear by dependency
APEX_REGION_CACHE.clear_cache(
  p_application_id => 100,
  p_region_id      => NULL,
  p_dependency     => 'sales_product');
```

**Every cached region needs an owner who knows when to invalidate.** Without
that, someone discovers the staleness in production.

## 4. Session State Cache — Reused Across Pages

```sql
-- Populate once per session
IF APEX_UTIL.SESSION_STATE('CTX_REGION_LIST') IS NULL THEN
  APEX_UTIL.SET_SESSION_STATE(
    'CTX_REGION_LIST',
    APEX_UTIL.json_encode(
      (SELECT JSON_ARRAYAGG(JSON_OBJECT('id'   VALUE region_id,
                                        'name' VALUE region_name)
                               RETURNING CLOB)
         FROM sales_region WHERE active_flag = 'Y')));
END IF;
```

**Good for small, stable lookup sets.** Bad for anything large — session state is
serialised per request, so a big value is a per-request cost.

## 5. Function Result Cache — Survives Sessions

```sql
CREATE OR REPLACE PACKAGE dashboard_cache_pkg AS
  -- Cached for 10 minutes; applies across ALL sessions
  FUNCTION monthly_revenue(p_from DATE, p_to DATE) RETURN NUMBER
    RESULT_CACHE RELIES_ON (sales_order);
END;
/
```

```sql
CREATE OR REPLACE PACKAGE BODY dashboard_cache_pkg AS

  FUNCTION monthly_revenue(p_from DATE, p_to DATE) RETURN NUMBER IS
    l_total NUMBER;
  BEGIN
    SELECT SUM(quantity * unit_price) INTO l_total
      FROM sales_order
     WHERE order_date >= p_from AND order_date < p_to + 1;
    RETURN l_total;
  END monthly_revenue;

END;
/
```

**Invalidate manually when data changes, not on a timer alone:**

```sql
-- After a bulk load, invalidate rather than waiting for TTL
DBMS_RESULT_CACHE.invalidate(
  user     => USER,
  status   => DBMS_RESULT_CACHE.STATUS_INVALIDATED,
  result_id => (SELECT cache_id FROM dbms_result_cache_result_name
                 WHERE result_name LIKE '%monthly_revenue%'));
```

## 6. Bulk Update — Set-Based

```sql
-- BEFORE: row-by-row. 100,000 rows ≈ 17 minutes.
FOR r IN (SELECT id, new_price FROM price_update_staging) LOOP
  UPDATE sales_product SET unit_price = r.new_price WHERE product_id = r.id;
  n := n + 1;
  IF MOD(n, 1000) = 0 THEN COMMIT; END IF;
END LOOP;
```

```sql
-- AFTER: one statement. 100,000 rows ≈ 2 seconds.
MERGE INTO sales_product t
USING price_update_staging s
   ON (t.product_id = s.product_id)
 WHEN MATCHED THEN UPDATE SET t.unit_price = s.new_price
 WHEN NOT MATCHED THEN INSERT (product_id, unit_price) VALUES (s.product_id, s.new_price);

COMMIT;
```

```sql
-- Bulk insert: INSERT ... SELECT, not a loop
INSERT INTO sales_order_archive (order_id, order_date, net_amount)
  SELECT order_id, order_date, quantity * unit_price
    FROM sales_order
   WHERE order_date < ADD_MONTHS(TRUNC(SYSDATE), -24);
```

```sql
-- Bulk delete
DELETE FROM price_update_staging WHERE processed_flag = 'Y';
```

### Bulk collection load — the anti-pattern

```sql
-- NEVER: one INSERT per row
FOR r IN staging LOOP
  INSERT INTO history VALUES (...);
END LOOP;
-- 100,000 round trips

-- ALWAYS: INSERT ... SELECT with validation in the WHERE
INSERT INTO history (id, value)
  SELECT s.id, s.value
    FROM staging s
   WHERE s.valid_flag = 'Y'
     AND NOT EXISTS (SELECT 1 FROM history h WHERE h.id = s.id);
```

## 7. Bounded Export

```sql
-- Custom export: explicit limit, explicit columns, one query
DECLARE
  CURSOR c_export IS
    SELECT c.c004 region_name,
           c.c006 category_name,
           c.c008 product_name,
           c.c010 quantity,
           c.c011 net_amount
      FROM apex_collection c
     WHERE c.collection_name = 'DASHBOARD_ORDERS'
       AND c.seq_key IS NOT NULL
       AND (:P1_REGION   IS NULL OR c.c003 = TO_NUMBER(:P1_REGION))
       AND (:P1_CATEGORY IS NULL OR c.c005 = TO_NUMBER(:P1_CATEGORY))
       AND ROWNUM <= 100000;         -- BOUND, and communicated to the user
BEGIN
  FOR r IN c_export LOOP
    APEX_CSV := APEX_CSV || '"' || r.region_name || '","' || r.product_name
             || '",' || r.quantity || ',' || r.net_amount || CRLF;
  END LOOP;
END;
```

**Bypassing APEX CSV entirely** and writing the string yourself is faster for
large sets because it avoids the framework's per-row processing. Use
`APEX_APPLICATION.GZIP` for very large payloads:

```sql
APEX_APPLICATION.GZIP(
  p_content => UTL_RAW.CAST_TO_RAW(APEX_CSV),
  p_dest    => 'BLOB',
  p_content_type => 'text/csv',
  p_filename      => 'dashboard_export.csv');
```

### Export with a timeout guard

```sql
-- Reject rather than time out
IF :P1_EXPORT_ROWS > 100000 THEN
  RAISE_APPLICATION_ERROR(-20100,
    'Export limited to 100,000 rows. Narrow your filters and try again.');
END IF;
```

**Refusing is better than truncating silently.** A truncated export produces a
spreadsheet that reconciles to nothing and takes an hour to diagnose.

## 8. Bulk CSV Import with Reject Log

```sql
CREATE TABLE price_import_staging (
  load_id       NUMBER,
  sku           VARCHAR2(40),
  new_price     NUMBER(12,2),
  valid_flag    CHAR(1),
  reject_reason VARCHAR2(200)
);

-- 1. Validate in bulk, not row by row
UPDATE price_import_staging s
   SET valid_flag = 'Y', reject_reason = NULL
 WHERE s.new_price > 0
   AND s.new_price < 999999
   AND EXISTS (SELECT 1 FROM sales_product p WHERE p.sku = s.sku);

UPDATE price_import_staging s
   SET valid_flag = 'N',
       reject_reason = CASE
         WHEN s.new_price <= 0 OR s.new_price >= 999999 THEN 'PRICE_OUT_OF_RANGE'
         ELSE 'SKU_NOT_FOUND' END
 WHERE s.valid_flag IS NULL;

-- 2. Apply valid rows set-based
MERGE INTO sales_product t
USING price_import_staging s
   ON (t.sku = s.sku)
 WHEN MATCHED THEN UPDATE SET t.unit_price = s.new_price
 WHERE s.valid_flag = 'Y';
COMMIT;

-- 3. Report rejects
SELECT reject_reason, COUNT(*) rows_rejected
  FROM price_import_staging
 WHERE valid_flag = 'N'
 GROUP BY reject_reason;
```

**Three set-based statements handle any volume.** The row-by-row equivalent is
where a 5-minute import becomes a 2-hour one.

## 9. Progress Reporting for Long Operations

```sql
-- Update progress so the user sees movement
APEX_APPLICATION.PROCESS(
  p_start_row => 1,
  p_end_row   => total_rows,
  p_processed => processed_count,
  p_total      => total_rows,
  p_error      => 0);
```

```sql
-- Chunk the work so progress advances and memory stays bounded
FOR chunk_start IN 1..CEIL(total/5000)*500 - 1 STEP 5000 LOOP
  MERGE ... ;   -- 5,000 rows per statement
  processed := processed + 5000;
  APEX_APPLICATION.PROCESS(..., p_processed => processed, ...);
  COMMIT;
END LOOP;
```

## 10. Cascading Filter Implementation

```sql
-- P1_CATEGORY LOV, dependent on P1_REGION
SELECT sc.category_id, sc.category_name
  FROM sales_category sc
 WHERE :P1_REGION IS NULL
    OR EXISTS (SELECT 1 FROM sales_order so
                WHERE so.category_id = sc.category_id
                  AND so.region_id = TO_NUMBER(:P1_REGION))
 ORDER BY 2;

-- Set "Cascading LOV Parent Item" = P1_REGION, and clear-dependent-items = Y
```

```
Without cascading: 12 regions × 40 categories = 480 combinations, many invalid
With cascading:    12 × ~8 = 96 combinations, all valid
Invalid combinations scan the full filtered range to prove emptiness.
```

## 11. Index Set for the Shared Query

```sql
CREATE INDEX ix_so_date_region ON sales_order (order_date, region_id);
CREATE INDEX ix_so_date_cat    ON sales_order (order_date, category_id);
CREATE INDEX ix_so_date_prod   ON sales_order (order_date, product_id);

-- Covering index for the collection population query
CREATE INDEX ix_so_cover ON sales_order
  (order_date, region_id, category_id, product_id, quantity, unit_price);

-- Reference data
CREATE INDEX ix_sp_active ON sales_product (sku, active_flag);
```

```sql
-- Confirm the shared query uses the index, not a full scan
EXPLAIN PLAN FOR
SELECT /*+ LEADING(so sr sc sp) USE_NL(sr sc sp) */
       so.order_id, so.order_date, so.region_id, so.quantity, so.unit_price
  FROM sales_order so
  JOIN sales_region sr ON sr.region_id = so.region_id
 WHERE so.order_date >= DATE '2026-01-01' AND so.order_date < DATE '2026-02-01';
```

## 12. Statistics — The Silent Killer of Index Performance

```sql
-- After a 5M-row bulk load, statistics are stale and the planner
-- may ignore a perfectly good index.
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname          => USER,
    tabname          => 'SALES_ORDER',
    method_opt       => 'FOR ALL COLUMNS SIZE AUTO',
    cascade          => TRUE,          -- indexes too
    degree           => 4,
    no_invalidate    => FALSE);
END;
/
```

```sql
-- Verify after gathering
SELECT table_name, num_rows, last_analyzed,
       ROUND(avg_row_len) avg_row_len
  FROM user_tables
 WHERE table_name = 'SALES_ORDER';
```

**`last_analyzed` before the load, `num_rows` far from actual = the planner is
working from bad information.** Indexes that were used yesterday are ignored
today.

## 13. p95 Measurement from the Activity Log

```sql
-- The requirement is p95, so measure p95
SELECT page_id,
       COUNT(*)                        executions,
       ROUND(AVG(elapsed_time), 0)     avg_ms,
       ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP
               (ORDER BY elapsed_time), 0) p95_ms,
       ROUND(PERCENTILE_CONT(0.99) WITHIN GROUP
               (ORDER BY elapsed_time), 0) p99_ms,
       ROUND(MAX(elapsed_time), 0)     max_ms
  FROM apex_user_activity_log
 WHERE application_id = 100
   AND page_id = 10
   AND view_time > SYSDATE - 7
   AND elapsed_time IS NOT NULL
 GROUP BY page_id;
```

```
Averages hide the problem. p99 is where the timeouts live.
```

## 14. Bulk Cleanup — Avoid Fragmentation Growth

```sql
-- Batched delete, not one 10M-row DELETE
FOR i IN 1..100 LOOP
  DELETE FROM sales_order_archive
   WHERE order_date < ADD_MONTHS(TRUNC(SYSDATE), -36)
     AND ROWNUM <= 50000;
  COMMIT;
  DBMS_LOCK.SLEEP(0.2);      -- let other work through
END LOOP;
```

**One enormous DELETE holds locks for minutes and generates undo that can stall
the instance.** Batching with a small sleep keeps the database responsive.

## 15. Health Check

```sql
SELECT
  (SELECT COUNT(*) FROM apex_collection
    GROUP BY collection_name ORDER BY 2 DESC FETCH FIRST 1 ROWS ONLY) largest_collection,
  (SELECT COUNT(DISTINCT collection_name) FROM apex_collection) collections_open,
  (SELECT num_rows FROM user_tables WHERE table_name='SALES_ORDER') sales_order_rows,
  (SELECT last_analyzed FROM user_tables WHERE table_name='SALES_ORDER') last_analyzed,
  (SELECT ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY elapsed_time))
     FROM apex_user_activity_log
    WHERE application_id=100 AND view_time > SYSDATE - 1) p95_ms_24h
FROM dual;
```