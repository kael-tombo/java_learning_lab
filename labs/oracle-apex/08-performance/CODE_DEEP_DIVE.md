# Lab 08: APEX Performance — Code Deep Dive

## 1. Attribution — APEX Debug

```
Enable:  Administration → Shared Components → Debug → Set Debugging On
Then:    one page load, and read the "Execution Log" section.

Example output:
  APEX  PAGE PROCESSING                     8,214 ms
  SQL Queries                              7,102 ms
    Region: Orders                          3,214 ms   ← 27% of total
    Region: Customers                      1,802 ms
    Region: Chart Revenue by Category       1,020 ms
    Region: Chart Revenue by Channel          840 ms
    Region: Chart Revenue by Region           260 ms
    Regions 5-8                               ~0 ms
  PL/SQL Processing                          912 ms
  Processes (10 Dynamic Actions)            200 ms
  RENDERING                                3,008 ms
  SESSION STATE                              604 ms
  TOTAL                                    12,026 ms
```

## 2. The Dominant Region — Query Rewrite

### Before: non-sargable, 3.2 seconds

```sql
SELECT o.order_id, o.order_date, c.customer_name, o.net_amount
  FROM orders o
  JOIN customer c ON c.customer_id = o.customer_id
 WHERE TRUNC(o.order_date) = TO_DATE(:P1_ORDER_DATE,'YYYY-MM-DD')
 ORDER BY o.net_amount DESC;
```

```sql
EXPLAIN PLAN FOR ...;   -- confirms: TABLE ACCESS FULL (scan of 5,000,000)
```

### After: sargable, 190 ms

```sql
SELECT o.order_id, o.order_date, c.customer_name, o.net_amount
  FROM orders o
  JOIN customer c ON c.customer_id = o.customer_id
 WHERE o.order_date >= TO_DATE(:P1_ORDER_DATE,'YYYY-MM-DD')
   AND o.order_date <  TO_DATE(:P1_ORDER_DATE,'YYYY-MM-DD') + 1
 ORDER BY o.net_amount DESC;
```

```sql
CREATE INDEX ix_orders_date ON orders (order_date, net_amount);
-- Now: INDEX RANGE SCAN + NESTED LOOPS
```

```
5,000,000 rows examined → 208,000 rows examined
3,214 ms → 190 ms
```

## 3. Bind Variables — Replacing String-Built SQL

### Anti-pattern in a page process

```sql
-- Inside a PL/SQL page process: literal built from the page item
l_sql := 'SELECT * FROM orders WHERE status = ''' || :P1_STATUS || '''';
FOR r IN EXECUTE IMMEDIATE l_sql LOOP ... END LOOP;
```

```sql
-- Proof of the problem: how many statements does this create?
SELECT COUNT(DISTINCT sql_text) distinct_statements,
       SUM(executions) total_executions,
       SUM(hard_parse_elapsed_time)/1e6 hard_parse_sec
  FROM v$sql
 WHERE sql_text LIKE 'SELECT * FROM orders WHERE status%';
```

### Fix: static SQL with a bind

```sql
SELECT o.order_id, o.order_date, o.net_amount
  FROM orders o
 WHERE o.status = :P1_STATUS
 ORDER BY o.order_date DESC;
```

```sql
-- Verify: one statement, many executions
SELECT COUNT(DISTINCT sql_text) distinct_statements,
       SUM(executions) total_executions
  FROM v$sql
 WHERE sql_text LIKE 'SELECT%FROM orders%status = :*';
```

```
Before: distinct statements = number of distinct status values (say 8)
        hard parses: ~1 per new value per session
After:  distinct statements = 1
        hard parses: 1 ever
```

## 4. Library Cache Latch Contention — The Database-Wide Effect

```sql
-- Symptom: CPU is not high, but sessions are slow, and the app is not obviously heavy
SELECT event, total_waits, time_waited_micro/1e6 wait_sec,
       ROUND(average_wait*1000, 3) avg_wait_ms
  FROM v$system_event
 WHERE event LIKE 'latch:%'
 ORDER BY total_waits DESC FETCH FIRST 10 ROWS ONLY;
```

```sql
-- The specific contention: library cache latches
SELECT name, gets, sleeps, ROUND(sleeps/GREATEST(gets,1)*100, 4) sleep_pct
  FROM v$latch
 WHERE name LIKE 'library cache%'
 ORDER BY sleeps DESC FETCH FIRST 10 ROWS ONLY;
```

| Metric | Healthy | Contended |
|--------|---------|-----------|
| `sleep_pct` on library cache latches | < 1% | > 5% |
| `total_waits` growth | Flat | Rising steadily |

**A contended `library cache` latch impairs every session on the instance**,
including applications with no relationship to APEX. This is why APEX hard-parse
problems get reported as "the database got slow".

## 5. Region Cache — Correct Application

```
Region: Orders (Interactive Report)
  Region Cache:
    Type:          CACHE
    Time to Live:  60 seconds
    Dependency:    orders, customer
    Session:       Shared        ← shared across all users, not per-session
```

```sql
-- Explicit invalidation when order data changes materially
APEX_REGION_CACHE.clear_cache(
  p_application_id => 100,
  p_region_id      => 12,
  p_dependency     => 'orders');
```

### Page Cache — and When It Is Wrong

```
Page: Dashboard  ← CONTAINS PER-USER FILTERS

  Page Cache:  *** DO NOT ENABLE ON THIS PAGE ***
  Reason:      one user's rendered HTML could be served to another

Correct alternative: cache each SLOW region individually.
```

```sql
-- Confirm before enabling page cache
SELECT page_id, COUNT(DISTINCT session_id) distinct_sessions,
       COUNT(*) views, ROUND(AVG(elapsed_time)) avg_ms
  FROM apex_user_activity_log
 WHERE application_id = 100 AND page_id = 5
   AND view_time > SYSDATE - 7
 GROUP BY page_id;
```

```
distinct_sessions = 240 over 3,500 views
→ Page is per-user. Page cache would be a data disclosure bug.
```

## 6. Session State Audit and Reduction

```sql
-- Inventory: every session state key in use
SELECT sess_key, COUNT(DISTINCT session_id) sessions,
       MAX(sess_last_update_date) last_used
  FROM apex_user_session_storage
 GROUP BY sess_key
 ORDER BY last_used DESC NULLS LAST;
```

```sql
-- Size: which keys are actually large?
SELECT sess_key, ROUND(SUM(LENGTH(sess_value))/1024, 1) total_kb
  FROM apex_user_session_storage
 GROUP BY sess_key
 HAVING SUM(LENGTH(sess_value)) > 1024
 ORDER BY 2 DESC;
```

### Reduce: move lookups to a cached region instead

```sql
-- BEFORE: a 40 KB lookup blob in session state, re-serialised every request
-- AFTER: a cached LOV region, invalidated on change

APEX_REGION_CACHE.clear_cache(
  p_application_id => 100, p_region_id => NULL, p_dependency => 'category');
```

**Decision rule for each item:**
```
1. Does it need to survive across pages?  No → remove
2. Could the database re-derive it cheaply? Yes → remove, query instead
3. Does it change more than once per session? Yes → cache it, not session state
```

## 7. PL/SQL Bulk Access Pattern

### Anti-pattern

```plsql
-- Page process, 500 iterations, one query each
FOR r IN (SELECT item_id, new_qty FROM stock_update_staging) LOOP
  UPDATE stock
     SET quantity_on_hand = r.new_qty
   WHERE item_id = r.item_id AND (:P1_WH IS NULL OR warehouse_id = :P1_WH);
  l_done := l_done + 1;
  IF MOD(l_done, 50) = 0 THEN COMMIT; END IF;
END LOOP;
```

### Fix: BULK COLLECT then set-based DML

```plsql
TYPE t_ids  IS TABLE OF NUMBER;
TYPE t_qtys IS TABLE OF NUMBER;
l_ids  t_ids;
l_qtys t_qtys;

SELECT item_id, new_qty BULK COLLECT INTO l_ids, l_qtys
  FROM stock_update_staging;

FORALL i IN 1 .. l_ids.COUNT
  UPDATE stock
     SET quantity_on_hand = l_qtys(i)
   WHERE item_id = l_ids(i)
     AND (:P1_WH IS NULL OR warehouse_id = :P1_WH);
COMMIT;
```

```sql
-- Or a single MERGE, which is usually faster still
MERGE INTO stock t
USING (SELECT item_id, new_qty, warehouse_id FROM stock_update_staging) s
   ON (t.item_id = s.item_id
       AND t.warehouse_id = NVL(s.warehouse_id, t.warehouse_id))
 WHEN MATCHED THEN UPDATE SET t.quantity_on_hand = s.new_qty;
COMMIT;
```

| Approach | 500 rows |
|----------|----------|
| Row-by-row in a cursor | ~900 ms |
| FORALL | ~30 ms |
| MERGE | ~15 ms |

## 8. PL/SQL Performance — Specific APEX Patterns

### Loop over a collection instead of re-querying

```plsql
-- BAD: queries the collection's source table per iteration
FOR i IN 1 .. 200 LOOP
  SELECT description INTO l_desc FROM item WHERE item_code = l_codes(i);
  l_total := l_total + l_desc;
END LOOP;

-- GOOD: BULK COLLECT the lookup once
SELECT item_code, description BULK COLLECT INTO l_codes2, l_descs
  FROM item WHERE item_code IN (SELECT column_value FROM TABLE(l_codes));

FOR i IN 1 .. l_codes.COUNT
  l_total := l_total + l_descs(i);
END LOOP;
```

### Index the lookup instead of scanning

```sql
-- A PL/SQL associative array used as an in-memory map, instead of
-- a correlated query per row. This turns O(n log n) SQL into O(n) PL/SQL.
TYPE t_map IS TABLE OF NUMBER INDEX BY VARCHAR2(40);
l_map t_map;

FOR r IN (SELECT item_code, unit_price FROM item) LOOP
  l_map(r.item_code) := r.unit_price;
END LOOP;

FOR r IN (SELECT item_code, qty FROM order_line) LOOP
  l_total := l_total + l_map(r.item_code) * r.qty;   -- no SQL per row
END LOOP;
```

## 9. Rendering — Dynamic Action Optimisation

```sql
-- Reduce condition complexity: this is evaluated on EVERY page load
-- BEFORE: nested CASE with function calls
WHEN CASE WHEN :P1_A IS NULL THEN 0 ELSE TO_NUMBER(:P1_A) END
             + CASE WHEN :P1_B IS NULL THEN 0 ELSE TO_NUMBER(:P1_B) END > 100

-- AFTER: simple comparison against a precomputed item
WHEN :P1_THRESHOLD_EXCEEDED = 'Y'
```

```sql
-- Compute once in a computation, use the simple flag in every DA condition
-- Computation: "Threshold exceeded", Before Header
CASE WHEN NVL(TO_NUMBER(:P1_A),0) + NVL(TO_NUMBER(:P1_B),0) > 100
     THEN 'Y' ELSE 'N' END
```

### Consolidate actions

```
10 dynamic actions on the same element  →  1 action with a compound condition
  Each action: event binding + condition evaluation per page load
  1 action:    one binding, one evaluation
```

## 10. Theme Asset Optimisation

```
Administration → Site Appearance → Advanced → Theme
```

```
Universal Theme:
  CSS minification:   OFF  →  ON
  JavaScript minification: OFF → ON
```

```sql
-- Confirm the reduction in delivered bytes
-- Before: ~1.8 MB uncompressed CSS + JS
-- After minification: ~0.8 MB
-- With gzip at the web server: ~0.25 MB

-- Verify gzip is active
SELECT * FROM v$dnf ORDER BY 1 FETCH FIRST 5 ROWS ONLY;
-- Or check response headers for Content-Encoding: gzip
```

| Assets | Uncompressed | Minified | Minified + gzip |
|--------|--------------|----------|-----------------|
| CSS + JS | 1.8 MB | 0.8 MB | ~0.25 MB |
| Time on 5 Mbps | 2.9 s | 1.3 s | **0.4 s** |

```
Saving: 2.5 s of pre-render transfer time.
No server-side change can produce this saving.
```

## 11. Application Performance Analyzer (APA)

```
Shared Components → Performance Analyzer (with the APEX Performance Analyzer
extension installed)

Gives, across the whole application:
  - Top SQL statements by elapsed time, executions, and rows
  - Top PL/SQL units
  - Slowest pages at p50/p95/p99
  - Which region each slow page's time belongs to
```

```sql
-- Equivalent for SQL: find the statements worth investigating
SELECT sql_id,
       ROUND(elapsed_time/1e6, 1)  elapsed_sec,
       executions,
       ROUND(elapsed_time/GREATEST(executions,1)/1e3, 2) avg_ms,
       buffer_gets,
       rows_processed,
       SUBSTR(sql_text,1,90) sql_text
  FROM v$sql
 WHERE sql_id IN (/* statement ids from APEX Debug / the activity log */)
 ORDER BY elapsed_time DESC;
```

## 12. Activity Log Percentiles

```sql
SELECT page_id,
       COUNT(*) requests,
       ROUND(AVG(elapsed_time), 0) avg_ms,
       ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY elapsed_time), 0) p50_ms,
       ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY elapsed_time), 0) p95_ms,
       ROUND(PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY elapsed_time), 0) p99_ms,
       ROUND(MAX(elapsed_time), 0) max_ms
  FROM apex_user_activity_log
 WHERE application_id = 100
   AND view_time > SYSDATE - 7
   AND elapsed_time IS NOT NULL
 GROUP BY page_id
 ORDER BY p95_ms DESC;
```

```
The requirement is p95. Report p95, and always inspect p99.
```

## 13. Database-Level Tuning the App Cannot Compromise For

```sql
-- System waits: if these dominate, it is not the application
SELECT event, wait_class, total_waits,
       ROUND(time_waited_micro/1e6, 0) wait_sec,
       ROUND(average_wait*1000, 2) avg_ms
  FROM v$system_event
 WHERE wait_class NOT IN ('Idle')
 ORDER BY time_waited_micro DESC
 FETCH FIRST 15 ROWS ONLY;
```

| Top wait | Meaning | Whose problem |
|----------|---------|---------------|
| `db file sequential read` | Storage latency | **Infrastructure** |
| `latch: library cache` | Hard parse contention | **Application (fix binds)** |
| `log file sync` | Commit latency | Infrastructure |
| `db file scattered read` | Poorly ordered index access | Application (index design) |

**`db file sequential read` dominating means the SQL is waiting on I/O.** Rewriting
the query to be more selective genuinely helps here — so this is one case where
application work and database wait interact.

## 14. Statistics Refresh

```sql
-- Stale statistics cause the planner to abandon a usable index
SELECT table_name, num_rows, last_analyzed,
       ROUND(last_analyzed) AS analyzed_days_ago
  FROM user_tables
 WHERE table_name IN ('ORDERS','ORDER_LINE','CUSTOMER','ITEM')
 ORDER BY last_analyzed NULLS FIRST;
```

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname   => USER,
    tabname   => 'ORDERS',
    method_opt=> 'FOR ALL COLUMNS SIZE AUTO',
    cascade   => TRUE,
    degree    => 4);
END;
/
```

**Re-check the plan after refreshing.** An index ignored yesterday is often
resumed today, with no code change.

## 15. Complete Before/After

```sql
SELECT page_id, COUNT(*) requests,
       ROUND(AVG(elapsed_time)) avg_ms,
       ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY elapsed_time)) p95_ms
  FROM apex_user_activity_log
 WHERE application_id = 100 AND page_id = 5
   AND view_time > SYSDATE - 7
 GROUP BY page_id;
```

| Component | Before | After | Fix |
|-----------|--------|-------|-----|
| Region: Orders | 3,214 ms | 190 ms | Sargable predicate + index |
| Region: Customers | 1,802 ms | 180 ms | Bind variable, covering index |
| 3 charts | 2,120 ms | 340 ms | Region cache, 60 s TTL |
| 5 other regions | ~20 ms | ~20 ms | — |
| PL/SQL processing | 912 ms | 120 ms | FORALL instead of row loop |
| Rendering | 3,008 ms | 1,410 ms | 10 DAs consolidated to 3 |
| Session state | 604 ms | 90 ms | Lookup blob removed |
| Theme assets (pre-render) | 2,900 ms | 400 ms | Minify + gzip |
| **Total** | **~14,600 ms** | **~2,750 ms** | |

**Server-measured p95: 14.6 s → 2.75 s.** The user-visible improvement is larger
because theme assets are transfer time the server timings do not include.