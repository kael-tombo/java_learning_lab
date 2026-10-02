# Exercises: SQL CTEs & Window Functions (Lab 04)

**Prerequisites:** Read `PROBLEM_WALKTHROUGH.md`  
**Difficulty:** Progressive (Medium → Hard)

---

## Exercise 1: Gaps-and-Islands Variations (Medium)

### Task
Practice the gaps-and-islands pattern with different scenarios.

### Requirements
```sql
-- Table: Logs(log_id PK with gaps)
-- 1a. Find start/end of consecutive ranges (from walkthrough)
-- 1b. Find ranges of consecutive dates (table: Events(event_date DATE))
-- 1c. Find gaps: missing IDs in sequence 1..MAX (return missing IDs)
-- 1d. Group by "session": events within 30 min of each other = same session
-- 1e. Find longest consecutive streak (max range length)
```

### Test Data
```sql
-- 1a: 1,2,3,7,8,10 → (1,3), (7,8), (10,10)
-- 1b: '2023-01-01', '2023-01-02', '2023-01-05' → ('2023-01-01','2023-01-02'), ('2023-01-05','2023-01-05')
-- 1c: 1,2,4,5,8 → missing: 3,6,7
-- 1d: timestamps: 10:00, 10:15, 10:45, 11:20 → sessions: (10:00,10:15), (10:45), (11:20)
```

---

## Exercise 2: LAG/LEAD Mastery (Medium)

### Task
Use LAG and LEAD for row-to-row comparisons.

### Requirements
```sql
-- Table: Readings(sensor_id, reading_time, value)
-- 2a. Flag rows where value > previous value (per sensor)
-- 2b. Calculate rate of change: (value - LAG(value)) / (reading_time - LAG(reading_time))
-- 2c. Detect anomalies: value > 2 * STDDEV from moving average (window 5)
-- 2d. Find "peaks": value > LAG(value) AND value > LEAD(value)
-- 2e. Fill gaps: interpolate missing timestamps with linear interpolation
```

---

## Exercise 3: Consecutive Seats Variations (Medium)

### Task
Variations on "Consecutive Available Seats".

### Requirements
```sql
-- Table: Seats(seat_id PK, free NUMBER(1))
-- 3a. Seats with at least 2 consecutive free seats (free + next free)
-- 3b. Seats with at least 3 consecutive free seats
-- 3c. Find all blocks of N+ consecutive free seats (return start_seat, end_seat, length)
-- 3d. Seats where both adjacent seats are occupied (isolated free seats)
-- 3e. Theater sections: section_id, seat_id. Consecutive within section only.
```

---

## Exercise 4: Running Totals & Moving Averages (Medium)

### Task
Practice window frames for cumulative and moving calculations.

### Requirements
```sql
-- Table: Sales(sale_date, amount, region)
-- 4a. Running total of amount per region ordered by date
-- 4b. 7-day moving average per region
-- 4c. Year-to-date total per region (reset each year)
-- 4d. Running total but only for last 30 days (sliding window)
-- 4e. Cumulative percentage: running_total / total * 100
```

---

## Exercise 5: Ranking & Percentiles (Medium)

### Task
Advanced ranking and percentile calculations.

### Requirements
```sql
-- Table: Scores(student_id, subject, score)
-- 5a. Rank students per subject (DENSE_RANK)
-- 5b. Percentile rank per subject (PERCENT_RANK)
-- 5c. Top 10% students per subject (CUME_DIST > 0.9)
-- 5d. Median score per subject (PERCENTILE_CONT 0.5)
-- 5e. Quartile buckets per subject (NTILE(4))
-- 5f. Students in top quartile for ALL subjects
```

---

## Exercise 6: Quiet Students Variations (Hard)

### Task
Variations on "Quiet Students" problem.

### Requirements
```sql
-- Tables: Student(student_id, name), Exam(exam_id, student_id, score)
-- 6a. Students who were NEVER in top 2 OR bottom 2 in any exam
-- 6b. Students who were top 1 at least once but never bottom 1
-- 6c. "Consistent" students: score always within 1 stddev of exam mean
-- 6d. "Volatile" students: score outside 2 stddev in at least 2 exams
-- 6e. Rank students by "quietness": fewest min/max occurrences
```

---

## Exercise 7: MATCH_RECOGNIZE (Hard)

### Task
Row pattern matching for complex sequences.

### Requirements
```sql
-- Table: StockPrice(symbol, price_date, close_price)
-- 7a. Find "V-shape" patterns: down then up (at least 2 days each)
-- 7b. Find "W-shape": down-up-down-up
-- 7c. Find "head and shoulders": up-down-up-down-up (middle peak highest)
-- 7d. Sessionize user events: events within 30 min = same session
-- 7e. Detect "gap up": today's open > yesterday's close + 5%
```

---

## Exercise 8: Recursive Hierarchies (Hard)

### Task
Use CONNECT BY for hierarchical queries (Oracle).

### Requirements
```sql
-- Table: Employee(id, name, manager_id)
-- 8a. Full org chart from CEO down (indented names)
-- 8b. Path from employee to CEO (SYS_CONNECT_BY_PATH)
-- 8c. All subordinates of a given manager (recursive)
-- 8d. Management levels: count employees per level
-- 8e. Find circular references (manager chain loops)
-- 8f. Convert to recursive CTE (for PostgreSQL/SQL Server compatibility)
```

---

## Exercise 9: Complex Analytics (Hard)

### Task
Multi-step analytical queries.

### Requirements
```sql
-- Tables: Orders(order_id, customer_id, order_date, total), Customers(id, name, segment)
-- 9a. Customer cohort analysis: retention by signup month
-- 9b. RFM analysis: Recency, Frequency, Monetary scores per customer
-- 9c. Market basket: product pairs bought together (support, confidence)
-- 9d. Churn prediction: customers with no orders in 90 days who were active before
-- 9e. Lifetime value: NPV of future cash flows (simplified)
```

---

## Exercise 10: Performance & Optimization (Hard)

### Task
Analyze and optimize window function queries.

### Requirements
```sql
-- 10a. EXPLAIN PLAN for Exercise 1a (gaps-and-islands)
-- 10b. Identify WINDOW SORT cost
-- 10c. Create index to avoid sort (if possible)
-- 10d. Compare ROWS vs RANGE frame performance
-- 10e. Use /*+ NO_MERGE */ to prevent CTE inlining
-- 10f. Rewrite MATCH_RECOGNIZE as window functions (if possible)
```

---

## Solutions

### Exercise 1
```sql
-- 1a: WITH cte AS (
--       SELECT log_id, log_id - ROW_NUMBER() OVER (ORDER BY log_id) grp FROM logs
--     ) SELECT MIN(log_id) start_id, MAX(log_id) end_id FROM cte GROUP BY grp ORDER BY start_id;
-- 1b: WITH cte AS (
--       SELECT event_date, 
--              event_date - ROW_NUMBER() OVER (ORDER BY event_date) grp FROM events
--     ) SELECT MIN(event_date) start_dt, MAX(event_date) end_dt FROM cte GROUP BY grp ORDER BY start_dt;
-- 1c: WITH all_nums AS (
--       SELECT LEVEL n FROM dual CONNECT BY LEVEL <= (SELECT MAX(log_id) FROM logs)
--     ) SELECT n FROM all_nums WHERE n NOT IN (SELECT log_id FROM logs);
-- 1d: WITH ordered AS (
--       SELECT *, 
--              SUM(CASE WHEN reading_time - LAG(reading_time) OVER (PARTITION BY sensor_id ORDER BY reading_time) 
--                        > INTERVAL '30' MINUTE THEN 1 ELSE 0 END) 
--              OVER (PARTITION BY sensor_id ORDER BY reading_time) session_id
--       FROM readings
--     ) SELECT * FROM ordered;
-- 1e: WITH cte AS (...) SELECT grp, MAX(log_id)-MIN(log_id)+1 len FROM cte GROUP BY grp ORDER BY len DESC FETCH FIRST 1 ROW ONLY;
```

### Exercise 2
```sql
-- 2a: SELECT *, CASE WHEN value > LAG(value) OVER (PARTITION BY sensor_id ORDER BY reading_time) THEN 1 ELSE 0 END increased FROM readings;
-- 2b: SELECT *, (value - LAG(value) OVER (PARTITION BY sensor_id ORDER BY reading_time)) / 
--       (reading_time - LAG(reading_time) OVER (PARTITION BY sensor_id ORDER BY reading_time)) rate FROM readings;
-- 2c: SELECT * FROM (
--       SELECT *, 
--              AVG(value) OVER (PARTITION BY sensor_id ORDER BY reading_time ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) ma,
--              STDDEV(value) OVER (PARTITION BY sensor_id ORDER BY reading_time ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) sd
--       FROM readings
--     ) WHERE value > ma + 2*sd OR value < ma - 2*sd;
-- 2d: SELECT * FROM (
--       SELECT *, 
--              LAG(value) OVER (PARTITION BY sensor_id ORDER BY reading_time) prev,
--              LEAD(value) OVER (PARTITION BY sensor_id ORDER BY reading_time) nxt
--       FROM readings
--     ) WHERE value > prev AND value > nxt;
-- 2e: Complex — use MATCH_RECOGNIZE or generate series + interpolate.
```

### Exercise 3
```sql
-- 3a: SELECT seat_id FROM (SELECT seat_id, free, LEAD(free) OVER (ORDER BY seat_id) nxt FROM seats) WHERE free=1 AND nxt=1;
-- 3b: SELECT seat_id FROM (SELECT seat_id, free, LEAD(free) OVER (ORDER BY seat_id) n1, LEAD(free,2) OVER (ORDER BY seat_id) n2 FROM seats) WHERE free=1 AND n1=1 AND n2=1;
-- 3c: WITH marked AS (
--       SELECT seat_id, free,
--              SUM(CASE WHEN free=0 THEN 1 ELSE 0 END) OVER (ORDER BY seat_id) grp
--       FROM seats
--     ) SELECT MIN(seat_id) start_seat, MAX(seat_id) end_seat, COUNT(*) length
--       FROM marked WHERE free=1 GROUP BY grp HAVING COUNT(*) >= 3;
-- 3d: SELECT seat_id FROM (SELECT seat_id, free, LAG(free) OVER (ORDER BY seat_id) prev, LEAD(free) OVER (ORDER BY seat_id) nxt FROM seats) WHERE free=1 AND NVL(prev,1)=0 AND NVL(nxt,1)=0;
-- 3e: Add PARTITION BY section_id to all window functions.
```

### Exercise 4
```sql
-- 4a: SELECT region, sale_date, amount, SUM(amount) OVER (PARTITION BY region ORDER BY sale_date ROWS UNBOUNDED PRECEDING) running_total FROM sales;
-- 4b: SELECT region, sale_date, amount, AVG(amount) OVER (PARTITION BY region ORDER BY sale_date RANGE BETWEEN INTERVAL '6' DAY PRECEDING AND CURRENT ROW) ma7 FROM sales;
-- 4c: SELECT region, sale_date, amount, SUM(amount) OVER (PARTITION BY region, EXTRACT(YEAR FROM sale_date) ORDER BY sale_date ROWS UNBOUNDED PRECEDING) ytd FROM sales;
-- 4d: SELECT region, sale_date, amount, SUM(amount) OVER (PARTITION BY region ORDER BY sale_date RANGE BETWEEN INTERVAL '29' DAY PRECEDING AND CURRENT ROW) sliding_30 FROM sales;
-- 4e: SELECT region, sale_date, amount, SUM(amount) OVER (PARTITION BY region ORDER BY sale_date ROWS UNBOUNDED PRECEDING) / SUM(amount) OVER (PARTITION BY region) * 100 pct FROM sales;
```

### Exercise 5
```sql
-- 5a: SELECT *, DENSE_RANK() OVER (PARTITION BY subject ORDER BY score DESC) rnk FROM scores;
-- 5b: SELECT *, PERCENT_RANK() OVER (PARTITION BY subject ORDER BY score) pct_rnk FROM scores;
-- 5c: SELECT * FROM (SELECT *, CUME_DIST() OVER (PARTITION BY subject ORDER BY score) cume FROM scores) WHERE cume > 0.9;
-- 5d: SELECT subject, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY score) median FROM scores GROUP BY subject;
-- 5e: SELECT *, NTILE(4) OVER (PARTITION BY subject ORDER BY score) quartile FROM scores;
-- 5f: SELECT student_id FROM scores GROUP BY student_id HAVING MIN(CASE WHEN NTILE(4) OVER (PARTITION BY subject ORDER BY score) = 4 THEN 1 ELSE 0 END) = 1;
```

### Exercise 6
```sql
-- 6a: WITH stats AS (
--       SELECT student_id, score, 
--              MIN(score) OVER (PARTITION BY exam_id) min_s,
--              MAX(score) OVER (PARTITION BY exam_id) max_s,
--              -- For top 2 / bottom 2
--              DENSE_RANK() OVER (PARTITION BY exam_id ORDER BY score) rnk_asc,
--              DENSE_RANK() OVER (PARTITION BY exam_id ORDER BY score DESC) rnk_desc
--       FROM exam
--     ) SELECT s.student_id, s.name FROM student s
--       WHERE NOT EXISTS (SELECT 1 FROM stats WHERE student_id = s.student_id AND (rnk_asc <= 2 OR rnk_desc <= 2));
-- 6b: WITH stats AS (
--       SELECT student_id, 
--              MAX(CASE WHEN DENSE_RANK() OVER (PARTITION BY exam_id ORDER BY score DESC) = 1 THEN 1 ELSE 0 END) was_top,
--              MAX(CASE WHEN DENSE_RANK() OVER (PARTITION BY exam_id ORDER BY score) = 1 THEN 1 ELSE 0 END) was_bottom
--       FROM exam GROUP BY student_id
--     ) SELECT student_id FROM stats WHERE was_top = 1 AND was_bottom = 0;
-- 6c: WITH exam_stats AS (SELECT exam_id, AVG(score) avg_s, STDDEV(score) std_s FROM exam GROUP BY exam_id),
--      student_stats AS (
--       SELECT e.student_id, 
--              SUM(CASE WHEN e.score BETWEEN es.avg_s - es.std_s AND es.avg_s + es.std_s THEN 1 ELSE 0 END) within_1sd,
--              COUNT(*) total
--       FROM exam e JOIN exam_stats es ON e.exam_id = es.exam_id
--       GROUP BY e.student_id
--     ) SELECT student_id FROM student_stats WHERE within_1sd = total;
-- 6d: Similar, count outside 2sd >= 2.
-- 6e: WITH stats AS (
--       SELECT student_id, SUM(CASE WHEN score IN (min_s, max_s) THEN 1 ELSE 0 END) extremes
--       FROM (SELECT student_id, score, 
--                    MIN(score) OVER (PARTITION BY exam_id) min_s,
--                    MAX(score) OVER (PARTITION BY exam_id) max_s
--            FROM exam)
--       GROUP BY student_id
--     ) SELECT student_id FROM stats ORDER BY extremes FETCH FIRST 10 ROWS ONLY;
```

### Exercise 7
```sql
-- 7a: SELECT * FROM StockPrice MATCH_RECOGNIZE (
--       PARTITION BY symbol ORDER BY price_date
--       MEASURES MATCH_NUMBER() match_num, CLASSIFIER() cls, COUNT(*) cnt
--       PATTERN (DOWN+ UP+)
--       DEFINE DOWN AS DOWN.close_price < PREV(DOWN.close_price),
--              UP AS UP.close_price > PREV(UP.close_price)
--     );
-- 7b: PATTERN (DOWN+ UP+ DOWN+ UP+)
-- 7c: PATTERN (UP1+ DOWN1+ UP2+ DOWN2+ UP3) DEFINE UP2 AS UP2.close_price > UP1.close_price AND UP2.close_price > UP3.close_price
-- 7d: MATCH_RECOGNIZE (PARTITION BY user_id ORDER BY event_time PATTERN (START EVENT+) DEFINE EVENT AS EVENT.event_time - PREV(EVENT.event_time) <= INTERVAL '30' MINUTE)
-- 7e: PATTERN (GAP_UP) DEFINE GAP_UP AS GAP_UP.open_price > PREV(GAP_UP.close_price) * 1.05
```

### Exercise 8
```sql
-- 8a: SELECT LPAD(' ', 2*(LEVEL-1)) || name org_chart FROM employee CONNECT BY PRIOR id = manager_id START WITH manager_id IS NULL;
-- 8b: SELECT SYS_CONNECT_BY_PATH(name, ' -> ') path FROM employee CONNECT BY PRIOR id = manager_id START WITH manager_id IS NULL;
-- 8c: SELECT * FROM employee CONNECT BY PRIOR manager_id = id START WITH id = :manager_id;
-- 8d: SELECT LEVEL lvl, COUNT(*) cnt FROM employee CONNECT BY PRIOR id = manager_id START WITH manager_id IS NULL GROUP BY LEVEL;
-- 8e: SELECT * FROM employee WHERE CONNECT_BY_ISCYCLE = 1 CONNECT BY NOCYCLE PRIOR id = manager_id START WITH manager_id IS NULL;
-- 8f: WITH RECURSIVE cte AS (SELECT id, name, manager_id, 1 lvl FROM employee WHERE manager_id IS NULL UNION ALL SELECT e.id, e.name, e.manager_id, c.lvl+1 FROM employee e JOIN cte c ON e.manager_id = c.id) SELECT * FROM cte;
```

### Exercise 9
```sql
-- 9a: WITH cohorts AS (SELECT customer_id, TRUNC(MIN(order_date), 'MM') cohort FROM orders GROUP BY customer_id),
--      activity AS (SELECT c.cohort, TRUNC(o.order_date, 'MM') month, COUNT(DISTINCT o.customer_id) active
--                   FROM orders o JOIN cohorts c ON o.customer_id = c.customer_id GROUP BY c.cohort, TRUNC(o.order_date, 'MM'))
--     SELECT cohort, month, active FROM activity ORDER BY cohort, month;
-- 9b: WITH rfm AS (
--       SELECT c.id, c.name,
--              SYSDATE - MAX(o.order_date) recency,
--              COUNT(o.order_id) frequency,
--              SUM(o.total) monetary
--       FROM customers c LEFT JOIN orders o ON c.id = o.customer_id GROUP BY c.id, c.name
--     ) SELECT *, NTILE(5) OVER (ORDER BY recency) r_score, NTILE(5) OVER (ORDER BY frequency DESC) f_score, NTILE(5) OVER (ORDER BY monetary DESC) m_score FROM rfm;
-- 9c: SELECT oi1.product_id p1, oi2.product_id p2, COUNT(DISTINCT oi1.order_id) support
--     FROM orderitems oi1 JOIN orderitems oi2 ON oi1.order_id = oi2.order_id AND oi1.product_id < oi2.product_id
--     GROUP BY oi1.product_id, oi2.product_id HAVING COUNT(DISTINCT oi1.order_id) > 10;
-- 9d: SELECT c.id, c.name FROM customers c WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id AND o.order_date >= SYSDATE - 90) AND EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id AND o.order_date < SYSDATE - 90);
-- 9e: Simplified: SELECT c.id, SUM(o.total) * 0.9 AS ltv FROM customers c JOIN orders o ON c.id = o.customer_id GROUP BY c.id;
```

### Exercise 10
```sql
-- 10a: EXPLAIN PLAN FOR [1a query]; SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
-- 10b: Plan shows WINDOW SORT (step 3) — cost proportional to N log N.
-- 10c: CREATE INDEX logs_id_idx ON logs(log_id); — enables INDEX FULL SCAN instead of TABLE FULL SCAN + SORT.
-- 10d: ROWS frame: fixed row count, faster. RANGE: includes peers, slower but correct for ties.
-- 10e: WITH /*+ MATERIALIZE */ cte AS (...) — forces temp table creation.
-- 10f: MATCH_RECOGNIZE often faster for complex patterns; window functions for simple LAG/LEAD.
```

---

## Grading Rubric

| Exercise | Points | Criteria |
|----------|--------|----------|
| 1 | 25 | All gaps-and-islands variations correct |
| 2 | 25 | LAG/LEAD calculations, anomaly detection |
| 3 | 20 | Consecutive seats variations |
| 4 | 20 | Running totals, moving averages, frames |
| 5 | 20 | Ranking, percentiles, quartiles |
| 6 | 30 | Quiet students variations |
| 7 | 40 | MATCH_RECOGNIZE patterns |
| 8 | 30 | CONNECT BY, recursive CTE |
| 9 | 40 | Cohort, RFM, market basket, churn |
| 10 | 20 | Plan analysis, optimization |

**Total: 270 points**

---

## Next Steps

1. Run against Oracle sample schemas
2. Practice: LeetCode SQL Hard problems
3. Study: Oracle MATCH_RECOGNIZE documentation
4. Read: "SQL for Smarties" by Joe Celko (advanced analytics)
5. Explore: Time-series analysis in Oracle