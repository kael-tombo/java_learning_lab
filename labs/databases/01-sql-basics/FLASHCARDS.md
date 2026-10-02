# Flashcards: SQL Basics (Lab 01)

> **Instructions:** Cover the answer side, recall from memory, then reveal. Shuffle periodically.

---

## Core Concepts

| # | Question | Answer |
|---|----------|--------|
| 1 | What is the basic SELECT syntax? | `SELECT col1, col2 FROM table WHERE condition ORDER BY col;` |
| 2 | How does Oracle DATE arithmetic work? | `SYSDATE + 1` = tomorrow, `SYSDATE - 90` = 90 days ago. |
| 3 | What does `TRUNC(date)` do? | Removes time component, sets to midnight (00:00:00). |
| 4 | What is three-valued logic in SQL? | TRUE, FALSE, UNKNOWN (NULL). WHERE keeps only TRUE. |
| 5 | How to check for NULL? | `col IS NULL` or `col IS NOT NULL` — never `col = NULL`. |

---

## Problem 1: Employees Hired in Last N Days

| # | Question | Answer |
|---|----------|--------|
| 6 | Query for last 90 days hires | `SELECT employee_id, first_name, last_name, hire_date, department_id FROM employees WHERE hire_date >= SYSDATE - 90 ORDER BY hire_date DESC;` |
| 7 | Why use `>=` not `>`? | Includes hires exactly 90 days ago (boundary inclusive). |
| 8 | How to handle time component in hire_date? | `TRUNC(hire_date) >= TRUNC(SYSDATE) - 90` for date-only comparison. |
| 9 | Index for this query | `CREATE INDEX emp_hire_date_idx ON employees(hire_date DESC);` — avoids sort. |
| 10 | Partitioning for large table | `PARTITION BY RANGE (hire_date)` with recent partition for fast pruning. |

---

## Problem 2: Big Countries

| # | Question | Answer |
|---|----------|--------|
| 11 | Query for big countries | `SELECT name, population, area FROM world WHERE area >= 3000000 OR population >= 25000000 ORDER BY name;` |
| 12 | Why OR not AND? | Country is "big" if EITHER condition met. AND would require both. |
| 13 | Edge case: exactly 3M area | Included (`>=`). Same for exactly 25M population. |
| 14 | NULL area with large population | `area >= 3M` is UNKNOWN, but `OR population >= 25M` is TRUE → row included. |
| 15 | Index strategy | Composite: `CREATE INDEX world_area_pop_idx ON world(area, population);` |

---

## Problem 3: Customer Referee (NULL Semantics)

| # | Question | Answer |
|---|----------|--------|
| 16 | Why `referee_id != 2` fails for NULL | `NULL != 2` → UNKNOWN → row excluded by WHERE. |
| 17 | Correct: explicit NULL check | `WHERE referee_id != 2 OR referee_id IS NULL` |
| 18 | Correct: NVL | `WHERE NVL(referee_id, -1) != 2` — converts NULL to -1. |
| 19 | Correct: COALESCE | `WHERE COALESCE(referee_id, -1) != 2` — standard SQL, short-circuits. |
| 20 | Correct: DECODE | `WHERE DECODE(referee_id, 2, 1, 0) = 0` — Oracle-specific. |
| 21 | Bitmap index for low cardinality | `CREATE BITMAP INDEX cust_referee_bmx ON customer(referee_id);` — includes NULLs. |

---

## Execution Plans & Optimization

| # | Question | Answer |
|---|----------|--------|
| 22 | What is a Full Table Scan? | Reads all blocks of table. OK for small tables, bad for large. |
| 23 | What is Index Range Scan? | Traverses B-tree index for range, then table access by ROWID. |
| 24 | What is Index Fast Full Scan? | Reads entire index (like full scan but smaller). No order. |
| 25 | What is Partition Pruning? | Only scans relevant partitions based on partition key in WHERE. |
| 26 | How to read execution plan | `EXPLAIN PLAN FOR ...; SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);` |
| 27 | Key plan operations | TABLE ACCESS FULL, INDEX RANGE SCAN, SORT ORDER BY, HASH JOIN. |

---

## Oracle-Specific Functions

| # | Question | Answer |
|---|----------|--------|
| 28 | SYSDATE vs SYSTIMESTAMP | SYSDATE = DATE (sec precision); SYSTIMESTAMP = TIMESTAMP WITH TIME ZONE. |
| 29 | NVL(expr1, expr2) | Returns expr1 if not null, else expr2. Oracle proprietary. |
| 30 | COALESCE(expr1, expr2, ...) | Returns first non-null. Standard SQL. Short-circuits. |
| 31 | DECODE(expr, search, result [, search, result]... [, default]) | If-then-else for equality. Oracle only. |
| 32 | CASE WHEN ... THEN ... END | Standard SQL conditional. More flexible than DECODE. |

---

## Company-Specific Notes

| # | Question | Answer |
|---|----------|--------|
| 33 | Oracle interview focus | DATE arithmetic, execution plans, TRUNC, NVL/DECODE, partitioning. |
| 34 | Amazon interview focus | Scalability, partition pruning, DynamoDB alternatives. |
| 35 | Google interview focus | Spanner syntax: `TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)`. |
| 36 | Microsoft interview focus | T-SQL: `GETDATE()`, `DATEADD(day, -90, GETDATE())`. |

---

## Common Pitfalls

| Pitfall | Consequence | Fix |
|---------|-------------|-----|
| `WHERE col = NULL` | Always UNKNOWN, no rows returned | Use `col IS NULL` |
| `WHERE col != value` with NULLs | NULL rows excluded | Add `OR col IS NULL` |
| No index on filtered column | Full table scan on large table | Create appropriate index |
| `SYSDATE` in partition key | Partition pruning fails | Use literal dates or virtual columns |
| Forgetting ORDER BY | Non-deterministic results | Always specify ORDER BY |

---

## Quick Reference: Key Syntax

| Task | Oracle Syntax |
|------|---------------|
| Current date/time | `SYSDATE` |
| Current timestamp | `SYSTIMESTAMP` |
| Date N days ago | `SYSDATE - N` |
| Add months | `ADD_MONTHS(date, n)` |
| Truncate time | `TRUNC(date)` |
| Null coalesce (2 args) | `NVL(expr, default)` |
| Null coalesce (N args) | `COALESCE(expr1, expr2, ...)` |
| If-then-else (equality) | `DECODE(expr, val1, res1, val2, res2, default)` |
| If-then-else (general) | `CASE WHEN cond THEN res ELSE default END` |
| Create B-tree index | `CREATE INDEX idx ON table(col);` |
| Create bitmap index | `CREATE BITMAP INDEX idx ON table(col);` |
| Create descending index | `CREATE INDEX idx ON table(col DESC);` |
| Range partition | `PARTITION BY RANGE (col) (PARTITION p1 VALUES LESS THAN (val), ...)` |

---

## Practice Problems

1. **LeetCode 595** — Big Countries (this lab)
2. **LeetCode 584** — Find Customer Referee (this lab)
3. **LeetCode 596** — Classes More Than 5 Students (GROUP BY + HAVING)
4. **LeetCode 175** — Combine Two Tables (LEFT JOIN)
5. **LeetCode 181** — Employees Earning More Than Managers (Self JOIN)