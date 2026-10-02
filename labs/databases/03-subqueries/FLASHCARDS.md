# Flashcards: SQL Subqueries (Lab 03)

> **Instructions:** Cover the answer side, recall from memory, then reveal. Shuffle periodically.

---

## Subquery Types

| # | Question | Answer |
|---|----------|--------|
| 1 | Scalar subquery | Returns exactly 1 row, 1 column. Can be used in SELECT, WHERE, HAVING. |
| 2 | Correlated subquery | References column from outer query. Executed once per outer row. |
| 3 | Uncorrelated subquery | Independent of outer query. Executed once, result reused. |
| 4 | Inline view | Subquery in FROM clause. Treated as temporary table. |
| 5 | EXISTS subquery | Returns TRUE if subquery returns ≥1 row. Stops at first match. |
| 6 | IN subquery | Checks if value in subquery result set. NULL handling tricky. |

---

## Problem 1: Nth Highest Salary

| # | Question | Answer |
|---|----------|--------|
| 7 | DENSE_RANK approach | `SELECT DISTINCT salary FROM (SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) rnk FROM employee) WHERE rnk = N;` |
| 8 | OFFSET/FETCH (12c+) | `SELECT DISTINCT salary FROM employee ORDER BY salary DESC OFFSET N-1 ROWS FETCH NEXT 1 ROWS ONLY;` |
| 9 | Correlated subquery | `SELECT DISTINCT salary FROM employee e1 WHERE N = (SELECT COUNT(DISTINCT salary) FROM employee e2 WHERE e2.salary >= e1.salary);` |
| 10 | Oracle function template | `CREATE FUNCTION get_nth_highest_salary(n NUMBER) RETURN NUMBER IS result NUMBER; BEGIN SELECT ... INTO result ...; RETURN result; EXCEPTION WHEN NO_DATA_FOUND THEN RETURN NULL; END;` |
| 11 | NO_DATA_FOUND handling | When N > distinct salary count, SELECT INTO raises NO_DATA_FOUND → return NULL. |
| 12 | Optimize: avoid DISTINCT | `SELECT MIN(salary) FROM (SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) rnk FROM employee) WHERE rnk = N;` |
| 13 | Index for this query | `CREATE INDEX emp_salary_idx ON employee(salary DESC);` |

---

## Problem 2: Delete Duplicate Emails

| # | Question | Answer |
|---|----------|--------|
| 14 | Goal | Delete duplicates, keep row with MIN(id) per email. |
| 15 | NOT IN approach | `DELETE FROM person WHERE id NOT IN (SELECT MIN(id) FROM person GROUP BY email);` |
| 16 | NOT IN NULL danger | If subquery returns NULL (e.g., email IS NULL group), NOT IN matches nothing → no delete. |
| 17 | NOT EXISTS approach | `DELETE FROM person p1 WHERE NOT EXISTS (SELECT 1 FROM person p2 WHERE p2.email = p1.email GROUP BY p2.email HAVING MIN(p2.id) = p1.id);` |
| 18 | ROW_NUMBER + ROWID (best) | `DELETE FROM person WHERE ROWID IN (SELECT rid FROM (SELECT ROWID rid, ROW_NUMBER() OVER (PARTITION BY email ORDER BY id) rn FROM person) WHERE rn > 1);` |
| 19 | Why ROWID? | Uniquely identifies physical row. Works even with NULL emails. |
| 20 | Index for dedup | `CREATE INDEX person_email_idx ON person(email);` |

---

## Problem 3: Not Boring Movies

| # | Question | Answer |
|---|----------|--------|
| 21 | Query | `SELECT id, movie, description, rating FROM cinema WHERE MOD(id, 2) = 1 AND description != 'boring' ORDER BY rating DESC;` |
| 22 | MOD(id, 2) = 1 | Odd-numbered IDs (remainder 1 when divided by 2). |
| 23 | BITAND(id, 1) = 1 | Bitwise AND with 1 — checks least significant bit. Same as MOD for odd/even. |
| 24 | description != 'boring' | Excludes 'boring'. Note: NULL description → UNKNOWN → excluded. |
| 25 | Handle NULL description | `NVL(description, 'unknown') != 'boring'` to include NULLs. |
| 26 | Function-based index | `CREATE INDEX cinema_odd_idx ON cinema(BITAND(id, 1));` |
| 27 | Virtual column | `ALTER TABLE cinema ADD (is_odd AS (MOD(id, 2))); CREATE INDEX cinema_is_odd_idx ON cinema(is_odd);` |

---

## Advanced Subquery Patterns

| # | Question | Answer |
|---|----------|--------|
| 28 | Subquery in SELECT | Scalar subquery per row: `SELECT name, (SELECT COUNT(*) FROM orders WHERE customerId = c.id) order_count FROM customers c;` |
| 29 | Subquery in FROM | Inline view: `SELECT * FROM (SELECT dept_id, AVG(salary) avg_sal FROM employee GROUP BY dept_id) d WHERE avg_sal > 5000;` |
| 30 | Subquery in WHERE | `WHERE salary > (SELECT AVG(salary) FROM employee)` — uncorrelated, runs once. |
| 31 | Correlated in WHERE | `WHERE salary > (SELECT AVG(salary) FROM employee WHERE dept_id = e.dept_id)` — runs per row. |
| 32 | EXISTS vs IN | EXISTS: stops at first match, handles NULLs correctly. IN: materializes subquery, NULL breaks NOT IN. |
| 33 | ANY / ALL operators | `salary > ANY (SELECT salary FROM employee WHERE dept_id = 10)` — > at least one. `salary > ALL` — > all. |
| 34 | MERGE with subquery | `MERGE INTO target t USING (SELECT * FROM source) s ON (t.id = s.id) WHEN MATCHED THEN UPDATE SET ...` |

---

## Optimization & Execution Plans

| # | Question | Answer |
|---|----------|--------|
| 35 | Subquery unnesting | Oracle transforms subqueries to joins when possible (EXISTS → semi-join, IN → semi-join). |
| 36 | Filter subquery early | Push predicates into subquery: `WHERE x IN (SELECT y FROM t WHERE z = 1)` better than `WHERE x IN (SELECT y FROM t) AND z = 1`. |
| 37 | Materialize hint | `/*+ MATERIALIZE */` forces inline view to be materialized (useful for repeated access). |
| 38 | No unnest hint | `/*+ NO_UNNEST */` prevents subquery-to-join transformation. |
| 39 | Scalar subquery caching | Oracle caches scalar subquery results per execution — helps if same value repeated. |

---

## Company-Specific Notes

| # | Question | Answer |
|---|----------|--------|
| 40 | Oracle interview | DENSE_RANK, ROW_NUMBER, ROWID, NO_DATA_FOUND, KEEP/DENSE_RANK. |
| 41 | Amazon interview | Redshift: same window functions, LIMIT/OFFSET instead of FETCH. |
| 42 | Google interview | Spanner: ARRAY_AGG(DISTINCT salary ORDER BY salary DESC)[OFFSET(N-1)]. |
| 43 | Microsoft interview | T-SQL: TOP N, OFFSET/FETCH, ROW_NUMBER() same. |

---

## Common Pitfalls

| Pitfall | Consequence | Fix |
|---------|-------------|-----|
| NOT IN with NULL subquery | Deletes nothing | Use NOT EXISTS or ROWID approach |
| Correlated subquery in SELECT | N+1 execution | Consider JOIN or inline view |
| Missing DISTINCT in Nth salary | Wrong rank with duplicates | Use DENSE_RANK or DISTINCT |
| Scalar subquery returns >1 row | ORA-01427 | Ensure subquery returns single row |
| DELETE without WHERE | Deletes all rows | Always double-check WHERE clause |

---

## Quick Reference: Key Syntax

| Pattern | Oracle Syntax |
|---------|---------------|
| Scalar subquery | `(SELECT MAX(salary) FROM employee)` |
| Correlated subquery | `WHERE salary > (SELECT AVG(salary) FROM employee WHERE dept_id = e.dept_id)` |
| EXISTS | `WHERE EXISTS (SELECT 1 FROM orders WHERE customerId = c.id)` |
| NOT EXISTS | `WHERE NOT EXISTS (SELECT 1 FROM orders WHERE customerId = c.id)` |
| IN | `WHERE id IN (SELECT customerId FROM orders)` |
| NOT IN (safe) | `WHERE id NOT IN (SELECT customerId FROM orders WHERE customerId IS NOT NULL)` |
| DENSE_RANK | `DENSE_RANK() OVER (ORDER BY salary DESC)` |
| ROW_NUMBER | `ROW_NUMBER() OVER (PARTITION BY email ORDER BY id)` |
| OFFSET/FETCH (12c+) | `OFFSET 1 ROWS FETCH NEXT 1 ROWS ONLY` |
| ROWID delete | `DELETE FROM t WHERE ROWID IN (SELECT rid FROM ...)` |
| KEEP DENSE_RANK | `MAX(sal) KEEP(DENSE_RANK LAST ORDER BY sal)` |
| Function-based index | `CREATE INDEX idx ON t(MOD(id, 2));` |

---

## Practice Problems

1. **LeetCode 177** — Nth Highest Salary (this lab)
2. **LeetCode 196** — Delete Duplicate Emails (this lab)
3. **LeetCode 620** — Not Boring Movies (this lab)
4. **LeetCode 176** — Second Highest Salary
5. **LeetCode 180** — Consecutive Numbers (gaps-and-islands)