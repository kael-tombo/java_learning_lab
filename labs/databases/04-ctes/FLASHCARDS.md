# Flashcards: SQL CTEs & Window Functions (Lab 04)

> **Instructions:** Cover the answer side, recall from memory, then reveal. Shuffle periodically.

---

## CTE Fundamentals

| # | Question | Answer |
|---|----------|--------|
| 1 | What is a CTE? | Common Table Expression: `WITH name AS (query) SELECT ... FROM name;` |
| 2 | Benefits of CTE | Readability, modularity, can reference multiple times, enables recursion. |
| 3 | Multiple CTEs | `WITH cte1 AS (...), cte2 AS (SELECT * FROM cte1 ...) SELECT ... FROM cte2;` |
| 4 | CTE vs Inline View | CTE defined before main query, can be reused. Inline view in FROM clause. |
| 5 | Materialization | Oracle may materialize CTE (temp table) or inline it. `/*+ MATERIALIZE */` forces. |

---

## Problem 1: Continuous Ranges (Gaps-and-Islands)

| # | Question | Answer |
|---|----------|--------|
| 6 | Core trick | `id - ROW_NUMBER() OVER (ORDER BY id)` = constant for consecutive group. |
| 7 | Why it works | Consecutive: 1-1=0, 2-2=0, 3-3=0. Gap: 7-4=3, 8-5=3. Different constants = different groups. |
| 8 | Query structure | CTE1: add ROW_NUMBER. CTE2: compute grp = id - rn. Main: GROUP BY grp, MIN/MAX. |
| 9 | Compact version | `WITH cte AS (SELECT log_id, log_id - ROW_NUMBER() OVER (ORDER BY log_id) grp FROM logs) SELECT MIN(log_id), MAX(log_id) FROM cte GROUP BY grp ORDER BY 1;` |
| 10 | Index for this | `CREATE INDEX logs_id_idx ON logs(log_id);` → INDEX FULL SCAN instead of TABLE FULL SCAN. |
| 11 | Edge cases | Single row → (id,id). All consecutive → one group. All gaps → each row own group. |
| 12 | Alternative: LAG | `SUM(CASE WHEN id - LAG(id) OVER (ORDER BY id) = 1 THEN 0 ELSE 1 END) OVER (ORDER BY id)` as group number. |

---

## Problem 2: Consecutive Available Seats

| # | Question | Answer |
|---|----------|--------|
| 13 | LAG/LEAD approach | `SELECT seat_id FROM (SELECT seat_id, free, LAG(free) OVER (ORDER BY seat_id) prev, LEAD(free) OVER (ORDER BY seat_id) nxt FROM cinema) WHERE free=1 AND (prev=1 OR nxt=1);` |
| 14 | Self-join approach | `SELECT DISTINCT c1.seat_id FROM cinema c1 JOIN cinema c2 ON ABS(c1.seat_id - c2.seat_id)=1 WHERE c1.free=1 AND c2.free=1;` |
| 15 | EXISTS approach | `SELECT seat_id FROM cinema c1 WHERE free=1 AND EXISTS (SELECT 1 FROM cinema c2 WHERE c2.free=1 AND ABS(c2.seat_id - c1.seat_id)=1);` |
| 16 | Why LAG/LEAD best | Single scan, no join, no DISTINCT needed, handles edges (NULL prev/nxt). |
| 17 | Index for this | `CREATE INDEX cinema_free_seat_idx ON cinema(free, seat_id);` |
| 18 | Edge: first seat | LAG=NULL → only included if LEAD=1. |
| 19 | Edge: last seat | LEAD=NULL → only included if LAG=1. |

---

## Problem 3: Quiet Students

| # | Question | Answer |
|---|----------|--------|
| 20 | Definition | Student who never got min OR max score in ANY exam they took. |
| 21 | Window function approach | `MIN(score) OVER (PARTITION BY exam_id) min_s, MAX(score) OVER (PARTITION BY exam_id) max_s` |
| 22 | Flag not-quiet | `WHERE score = min_s OR score = max_s` → these are NOT quiet. |
| 23 | HAVING trick | `GROUP BY student_id HAVING SUM(CASE WHEN score IN (min_s, max_s) THEN 1 ELSE 0 END) = 0` |
| 24 | Must have taken exam | Add `AND EXISTS (SELECT 1 FROM exam WHERE student_id = s.student_id)` |
| 25 | Edge: single exam | If student takes 1 exam and scores middle → quiet. If min/max → not quiet. |
| 26 | Edge: all same score | All scores = min = max → all students NOT quiet. |

---

## Advanced Window Functions

| # | Question | Answer |
|---|----------|--------|
| 27 | ROW_NUMBER | Unique 1..N per partition. Breaks ties arbitrarily. |
| 28 | RANK | Same rank for ties, skips next rank (1,2,2,4). |
| 29 | DENSE_RANK | Same rank for ties, no skip (1,2,2,3). |
| 30 | NTILE(n) | Divides partition into n buckets. |
| 31 | LAG(col, n, default) | Value from n rows before. Default if out of bounds. |
| 32 | LEAD(col, n, default) | Value from n rows after. |
| 33 | FIRST_VALUE / LAST_VALUE | First/last in window frame. Need `IGNORE NULLS` for null handling. |
| 34 | NTILE(4) | Quartiles. Useful for bucketing. |

---

## Window Frames

| # | Question | Answer |
|---|----------|--------|
| 35 | ROWS vs RANGE | ROWS = physical rows. RANGE = logical values (peers included). |
| 36 | Default frame | `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` |
| 37 | Running total | `SUM(sal) OVER (PARTITION BY dept ORDER BY hiredate ROWS UNBOUNDED PRECEDING)` |
| 38 | Moving average | `AVG(sal) OVER (ORDER BY date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)` |
| 39 | Exclude current row | `ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING` |

---

## Advanced Analytics

| # | Question | Answer |
|---|----------|--------|
| 40 | PERCENTILE_CONT(0.5) | Continuous median (interpolated). |
| 41 | PERCENTILE_DISC(0.5) | Discrete median (actual value from set). |
| 42 | PERCENT_RANK | Relative rank: (rank-1)/(total-1). 0 to 1. |
| 43 | CUME_DIST | Cumulative distribution: rank/total. |
| 44 | STDDEV / VARIANCE | Standard deviation, variance over window. |
| 45 | CORR / COVAR_POP | Correlation, covariance over window. |
| 46 | RATIO_TO_REPORT | Value / SUM(value) over partition. |

---

## MATCH_RECOGNIZE (Pattern Matching)

| # | Question | Answer |
|---|----------|--------|
| 46 | Syntax | `SELECT * FROM table MATCH_RECOGNIZE (PARTITION BY ... ORDER BY ... MEASURES ... PATTERN (A B+ C) DEFINE B AS B.val > PREV(B.val), C AS C.val < PREV(C.val))` |
| 47 | Use cases | Stock patterns (V-shape, W-shape), sessionization, anomaly detection. |
| 48 | PATTERN | Regex-like: A (start), B+ (one or more up), C (down). |
| 49 | DEFINE | Conditions for each pattern variable. |
| 50 | MEASURES | Output columns: `MATCH_NUMBER()`, `CLASSIFIER()`, `RUNNING`/`FINAL` semantics. |

---

## Oracle-Specific

| # | Question | Answer |
|---|----------|--------|
| 51 | Recursive queries | Use `CONNECT BY PRIOR child = parent START WITH parent IS NULL` |
| 52 | SYS_CONNECT_BY_PATH | Build path string in hierarchy. |
| 53 | CONNECT_BY_ISLEAF | 1 if leaf node. |
| 54 | LEVEL pseudocolumn | Depth in hierarchy (1 = root). |
| 55 | NOCYCLE | Prevent infinite loops in cyclic data. |

---

## Company-Specific Notes

| # | Question | Answer |
|---|----------|--------|
| 56 | Google interview | Gaps-and-islands, MATCH_RECOGNIZE, window frames. |
| 57 | Oracle interview | CONNECT BY, advanced analytics, execution plan WINDOW SORT. |
| 58 | Amazon interview | Redshift: window functions supported, but no MATCH_RECOGNIZE. |
| 59 | Microsoft interview | T-SQL: same window functions, recursive CTE with `WITH RECURSIVE`. |

---

## Common Pitfalls

| Pitfall | Consequence | Fix |
|---------|-------------|-----|
| Default RANGE frame | Includes peers (ties) unexpectedly | Use ROWS for precise row counts |
| LAG/LEAD without ORDER BY | Error | Always specify ORDER BY |
| FIRST_VALUE without frame | Returns first of whole partition | Add `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` |
| Recursive CTE in Oracle | Not supported | Use CONNECT BY |
| MATCH_RECOGNIZE greediness | May not match expected pattern | Use reluctant quantifiers `*?`, `+?` |

---

## Quick Reference: Key Syntax

| Pattern | Oracle Syntax |
|---------|---------------|
| CTE | `WITH cte AS (SELECT ...) SELECT * FROM cte;` |
| ROW_NUMBER | `ROW_NUMBER() OVER (PARTITION BY grp ORDER BY val)` |
| RANK | `RANK() OVER (PARTITION BY grp ORDER BY val)` |
| DENSE_RANK | `DENSE_RANK() OVER (PARTITION BY grp ORDER BY val)` |
| LAG | `LAG(col, 1, default) OVER (PARTITION BY grp ORDER BY val)` |
| LEAD | `LEAD(col, 1, default) OVER (PARTITION BY grp ORDER BY val)` |
| Running sum | `SUM(col) OVER (PARTITION BY grp ORDER BY val ROWS UNBOUNDED PRECEDING)` |
| Median (cont) | `PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY col) OVER (PARTITION BY grp)` |
| Median (disc) | `PERCENTILE_DISC(0.5) WITHIN GROUP (ORDER BY col) OVER (PARTITION BY grp)` |
| Gaps-islands | `val - ROW_NUMBER() OVER (ORDER BY val)` as group key |
| CONNECT BY | `SELECT * FROM t CONNECT BY PRIOR child = parent START WITH parent IS NULL` |
| MATCH_RECOGNIZE | `SELECT * FROM t MATCH_RECOGNIZE (PARTITION BY p ORDER BY o MEASURES ... PATTERN (...) DEFINE ...)` |

---

## Practice Problems

1. **LeetCode 1285** — Find Start and End of Continuous Ranges (this lab)
2. **LeetCode 603** — Consecutive Available Seats (this lab)
3. **LeetCode 1412** — Find the Quiet Students (this lab)
4. **LeetCode 574** — Winning Candidate (window functions)
5. **LeetCode 1148** — Article Views I (CTE)
6. **LeetCode 185** — Department Top Three Salaries (DENSE_RANK)