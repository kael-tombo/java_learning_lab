# Flashcards: SQL Joins (Lab 02)

> **Instructions:** Cover the answer side, recall from memory, then reveal. Shuffle periodically.

---

## JOIN Types

| # | Question | Answer |
|---|----------|--------|
| 1 | INNER JOIN | Returns only rows with matches in BOTH tables. |
| 2 | LEFT JOIN | Returns ALL rows from left, matches from right, NULLs for non-matches. |
| 3 | RIGHT JOIN | Returns ALL rows from right, matches from left, NULLs for non-matches. |
| 4 | FULL OUTER JOIN | Returns all rows from both tables, NULLs where no match. |
| 5 | CROSS JOIN | Cartesian product: every row from left × every row from right. |
| 6 | SEMI JOIN | Returns left rows that have at least one match (EXISTS). No right columns. |
| 7 | ANTI JOIN | Returns left rows with NO match (NOT EXISTS, LEFT JOIN/IS NULL). |

---

## Problem 1: Department Top Three Salaries

| # | Question | Answer |
|---|----------|--------|
| 8 | Window function for "top N per group" | `DENSE_RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC)` |
| 9 | Why DENSE_RANK not ROW_NUMBER? | Ties get same rank; next rank is consecutive (no gaps). |
| 10 | Query structure | Inline view with DENSE_RANK → filter rank <= 3 → JOIN department |
| 11 | LATERAL alternative (12c+) | `CROSS JOIN LATERAL (SELECT ... FROM emp WHERE dept_id = d.id ORDER BY salary DESC FETCH FIRST 3 ROWS WITH TIES)` |
| 12 | FETCH FIRST WITH TIES | Includes all rows tied with the Nth row. |
| 13 | Index for window function | `CREATE INDEX emp_dept_sal_idx ON employee(departmentId, salary DESC);` |
| 14 | Execution plan: WINDOW SORT | Sorts by partition key + order key for DENSE_RANK computation. |

---

## Problem 2: Customers Who Never Order

| # | Question | Answer |
|---|----------|--------|
| 15 | LEFT JOIN approach | `FROM customers c LEFT JOIN orders o ON c.id = o.customerId WHERE o.id IS NULL` |
| 16 | NOT EXISTS approach | `FROM customers c WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customerId = c.id)` |
| 17 | NOT IN approach (caution) | `FROM customers c WHERE c.id NOT IN (SELECT customerId FROM orders WHERE customerId IS NOT NULL)` |
| 18 | Why NOT IN is dangerous | If subquery returns any NULL, entire NOT IN evaluates to UNKNOWN → empty result. |
| 19 | Execution plan: HASH JOIN ANTI | Oracle transforms LEFT JOIN/IS NULL and NOT EXISTS to anti-join. Very efficient. |
| 20 | Index for NOT EXISTS | `CREATE INDEX orders_customer_idx ON orders(customerId);` → NESTED LOOPS ANTI. |

---

## Problem 3: Employees Earning More Than Managers

| # | Question | Answer |
|---|----------|--------|
| 21 | Self-join condition | `e1.managerId = e2.id` (employee's managerId = manager's id) |
| 22 | Filter condition | `e1.salary > e2.salary` |
| 23 | CEO handling | CEO has managerId = NULL → excluded by JOIN (NULL = NULL is UNKNOWN) |
| 24 | Execution plan: HASH JOIN | Reads employee table twice, hashes on id/managerId. |
| 25 | Index optimization | `CREATE INDEX emp_mgr_idx ON employee(managerId);` + `CREATE INDEX emp_id_sal_idx ON employee(id, salary);` → NESTED LOOPS. |

---

## Advanced JOIN Patterns

| # | Question | Answer |
|---|----------|--------|
| 26 | Multiple JOIN order | Optimizer reorders based on cardinality estimates. Use hints if needed. |
| 27 | JOIN vs WHERE filter | `JOIN ... ON a.id = b.id AND b.status = 'active'` vs `JOIN ... ON a.id = b.id WHERE b.status = 'active'` — same for INNER, different for OUTER. |
| 28 | Partition-wise JOIN | If both tables partitioned on join key, Oracle can join partition-to-partition. |
| 29 | Bloom filter | Oracle uses Bloom filters for hash joins to reduce probe side I/O. |
| 30 | Star transformation | For star schemas: fact table joined to multiple dimensions → bitmap indexes + star transformation. |

---

## Company-Specific Notes

| # | Question | Answer |
|---|----------|--------|
| 31 | Oracle interview focus | JOIN methods (HASH/NL/MERGE), execution plans, anti-join vs semi-join, LATERAL. |
| 32 | Amazon interview focus | Redshift: distribution keys, sort keys, broadcast vs distribute. |
| 33 | Google interview focus | Spanner: distributed JOINs, co-location, interleaved tables. |
| 34 | Microsoft interview focus | T-SQL: APPLY (similar to LATERAL), JOIN hints (HASH, MERGE, LOOP). |

---

## Common Pitfalls

| Pitfall | Consequence | Fix |
|---------|-------------|-----|
| Missing JOIN condition | Cartesian product (CROSS JOIN) | Always specify ON clause |
| JOIN on NULL columns | NULL = NULL is UNKNOWN, no match | Handle NULLs explicitly if needed |
| NOT IN with NULL subquery | Empty result set | Use NOT EXISTS or add IS NOT NULL |
| LEFT JOIN + WHERE on right | Converts to INNER JOIN | Move right-table filters to ON clause |
| Duplicate rows from JOIN | One-to-many inflates row count | Use DISTINCT, aggregate, or fix grain |

---

## Quick Reference: Key Syntax

| Pattern | Oracle Syntax |
|---------|---------------|
| Inner join | `FROM a JOIN b ON a.id = b.a_id` |
| Left join | `FROM a LEFT JOIN b ON a.id = b.a_id` |
| Self join | `FROM emp e1 JOIN emp e2 ON e1.mgr_id = e2.id` |
| Anti-join (LEFT/NULL) | `FROM a LEFT JOIN b ON ... WHERE b.id IS NULL` |
| Anti-join (NOT EXISTS) | `FROM a WHERE NOT EXISTS (SELECT 1 FROM b WHERE b.a_id = a.id)` |
| LATERAL (12c+) | `FROM a CROSS JOIN LATERAL (SELECT * FROM b WHERE b.a_id = a.id)` |
| Top N per group | `DENSE_RANK() OVER (PARTITION BY grp ORDER BY val DESC)` |
| FETCH WITH TIES | `ORDER BY val DESC FETCH FIRST 3 ROWS WITH TIES` |

---

## Practice Problems

1. **LeetCode 185** — Department Top Three Salaries (this lab)
2. **LeetCode 183** — Customers Who Never Order (this lab)
3. **LeetCode 181** — Employees Earning More Than Managers (this lab)
4. **LeetCode 175** — Combine Two Tables (LEFT JOIN)
5. **LeetCode 176** — Second Highest Salary (subquery)
6. **LeetCode 177** — Nth Highest Salary (window function)