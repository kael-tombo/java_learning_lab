# Quiz: SQL Joins (Lab 02)

**Topic:** JOIN Types, Self-Joins, Anti-Joins, LATERAL  
**Difficulty:** Medium  
**Time Limit:** 15 minutes

---

## Questions

### 1. JOIN Types
Which JOIN returns all rows from the left table and matching rows from the right, with NULLs for non-matches?
- A) INNER JOIN
- B) LEFT JOIN
- C) RIGHT JOIN
- D) FULL OUTER JOIN

### 2. Self-Join
In "Employees Earning More Than Managers", what JOIN condition connects employee to manager?
- A) `e1.id = e2.managerId`
- B) `e1.managerId = e2.id`
- C) `e1.managerId = e2.managerId`
- D) `e1.id = e2.id`

### 3. Anti-Join
Which pattern finds customers who NEVER placed an order?
- A) `LEFT JOIN orders ON ... WHERE orders.id IS NULL`
- B) `NOT EXISTS (SELECT 1 FROM orders WHERE customerId = c.id)`
- C) `c.id NOT IN (SELECT customerId FROM orders WHERE customerId IS NOT NULL)`
- D) All of the above

### 4. NOT IN vs NOT EXISTS
Why is `NOT IN` dangerous with subqueries that might return NULL?
- A) It's slower
- B) `x NOT IN (1, 2, NULL)` evaluates to UNKNOWN for all x
- C) It doesn't use indexes
- D) It's not standard SQL

### 5. DENSE_RANK vs ROW_NUMBER
For "Department Top 3 Salaries", why use DENSE_RANK instead of ROW_NUMBER?
- A) DENSE_RANK is faster
- B) DENSE_RANK handles ties correctly (same salary = same rank)
- C) ROW_NUMBER doesn't support PARTITION BY
- D) DENSE_RANK uses less memory

### 6. LATERAL Join
What does `CROSS JOIN LATERAL` enable?
- A) Join without ON condition
- B) Subquery referencing columns from preceding tables
- C) Faster hash joins
- D) Automatic partition pruning

### 7. FETCH FIRST WITH TIES
What does `FETCH FIRST 3 ROWS WITH TIES` do?
- A) Returns exactly 3 rows
- B) Returns top 3 rows plus any additional rows with same sort key as row 3
- C) Returns 3 random rows
- D) Returns first 3 rows of each partition

### 8. Execution Plan: HASH JOIN ANTI
What does `HASH JOIN ANTI` in an execution plan indicate?
- A) Regular inner hash join
- B) Anti-join: rows from left with no match in right
- C) Semi-join: rows from left with at least one match
- D) Full outer join using hash

### 9. Index for Self-Join
For the self-join `e1.managerId = e2.id`, which indexes help?
- A) `INDEX ON employee(managerId)` only
- B) `INDEX ON employee(id, salary)` only
- C) Both `INDEX ON employee(managerId)` AND `INDEX ON employee(id, salary)`
- D) No index needed

### 10. Correlated Subquery vs JOIN
When is a correlated subquery preferred over JOIN?
- A) Always
- B) When subquery returns single value (scalar) per row
- C) When joining large tables
- D) Never

---

## Answers

| # | Answer | Explanation |
|---|--------|-------------|
| 1 | **B** | LEFT JOIN keeps all left rows, NULLs for non-matching right. |
| 2 | **B** | Employee's managerId points to manager's id. |
| 3 | **D** | All three are valid anti-join patterns. LEFT JOIN/IS NULL and NOT EXISTS are safest. |
| 4 | **B** | If subquery returns any NULL, `NOT IN` yields UNKNOWN for every row → empty result. |
| 5 | **B** | DENSE_RANK gives same rank to ties; ROW_NUMBER arbitrarily breaks ties. |
| 6 | **B** | LATERAL allows subquery to reference columns from left side of join. |
| 7 | **B** | WITH TIES includes all rows tied with the last row in the limit. |
| 8 | **B** | HASH JOIN ANTI = anti-join (find non-matching rows). |
| 9 | **C** | Index on managerId for probe, index on (id, salary) for fast manager lookup. |
| 10 | **B** | Scalar subqueries (EXISTS, SELECT single value) can be more readable and sometimes faster. |

---

## Scoring

| Score | Level |
|-------|-------|
| 9-10 | Expert — JOIN master |
| 7-8 | Proficient — Solid join patterns |
| 5-6 | Developing — Review anti-joins and LATERAL |
| <5 | Beginner — Re-read PROBLEM_WALKTHROUGH.md |

---

## Further Study

- Read `PROBLEM_WALKTHROUGH.md` for Department Top 3, Customers Never Order, Self-Join
- Practice: LeetCode SQL 185, 183, 181
- Study: Oracle JOIN methods (HASH, NESTED LOOPS, MERGE)