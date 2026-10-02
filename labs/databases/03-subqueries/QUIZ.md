# Quiz: SQL Subqueries (Lab 03)

**Topic:** Subquery Types, Correlated Subqueries, DML with Subqueries  
**Difficulty:** Medium  
**Time Limit:** 15 minutes

---

## Questions

### 1. Subquery Types
Which subquery type references columns from the outer query?
- A) Scalar subquery
- B) Correlated subquery
- C) Inline view
- D) Uncorrelated subquery

### 2. Nth Highest Salary
For "Nth Highest Salary" in Oracle, which approach is most idiomatic?
- A) `ROWNUM` with inline view
- B) `DENSE_RANK()` analytic function
- C) `OFFSET ... FETCH` (12c+)
- D) All of the above work

### 3. DELETE with Subquery
In "Delete Duplicate Emails", why does `DELETE WHERE id NOT IN (SELECT MIN(id) ...)` risk failure?
- A) It's too slow
- B) If subquery returns any NULL, NOT IN matches nothing
- C) It locks the whole table
- D) It doesn't work in Oracle

### 4. ROW_NUMBER for Deduplication
The ROW_NUMBER approach for deleting duplicates uses `ROWID` in the subquery. Why?
- A) ROWID is faster than primary key
- B) Need unique row identifier for DELETE
- C) PRIMARY KEY not available
- D) It's required by Oracle syntax

### 5. Scalar Subquery
What is a scalar subquery?
- A) Subquery in FROM clause
- B) Subquery returning exactly one row and one column
- C) Subquery with aggregate function
- D) Subquery in WHERE clause

### 6. NOT IN vs NOT EXISTS (Revisited)
For the duplicate email delete, which is safer?
- A) `NOT IN (SELECT MIN(id) ...)`
- B) `NOT EXISTS (SELECT 1 ... HAVING MIN(id) = p1.id)`
- C) `ROWID IN (SELECT rid FROM ... WHERE rn > 1)`
- D) All equally safe

### 7. MOD Function
In "Not Boring Movies", `MOD(id, 2) = 1` checks for what?
- A) Even IDs
- B) Odd IDs
- C) Prime IDs
- D) IDs divisible by 2

### 8. BITAND Alternative
`BITAND(id, 1) = 1` is equivalent to what?
- A) `MOD(id, 2) = 1`
- B) `id % 2 = 1`
- C) `id & 1 = 1` (bitwise AND)
- D) All of the above

### 9. Execution Plan: WINDOW SORT
What operation computes `DENSE_RANK() OVER (ORDER BY salary DESC)`?
- A) SORT AGGREGATE
- B) WINDOW SORT
- C) HASH GROUP BY
- D) SORT ORDER BY

### 10. KEEP/DENSE_RANK LAST
What does `MAX(salary) KEEP(DENSE_RANK LAST ORDER BY salary)` return?
- A) Minimum salary
- B) Maximum salary (same as MAX)
- C) Second highest salary
- D) Median salary

---

## Answers

| # | Answer | Explanation |
|---|--------|-------------|
| 1 | **B** | Correlated subquery references outer query columns; executed once per outer row. |
| 2 | **D** | All work: DENSE_RANK (pre-12c), OFFSET/FETCH (12c+), ROWNUM (legacy). DENSE_RANK is most idiomatic. |
| 3 | **B** | `NOT IN` with NULL in subquery → UNKNOWN for all rows → no rows deleted. |
| 4 | **B** | ROWID uniquely identifies each row; required for precise DELETE targeting. |
| 5 | **B** | Scalar subquery = single row, single column. Can appear in SELECT, WHERE, etc. |
| 6 | **C** | ROWID approach avoids NULL issues entirely. NOT EXISTS is also safe. NOT IN is risky. |
| 7 | **B** | MOD(n, 2) = 1 means remainder 1 when divided by 2 → odd numbers. |
| 8 | **D** | All equivalent: MOD, % operator, bitwise AND with 1 checks LSB. |
| 9 | **B** | WINDOW SORT computes analytic functions like DENSE_RANK, ROW_NUMBER. |
| 10 | **B** | `KEEP(DENSE_RANK LAST ORDER BY salary)` picks the max salary — same as MAX(salary). |

---

## Scoring

| Score | Level |
|-------|-------|
| 9-10 | Expert — Subquery specialist |
| 7-8 | Proficient — Solid correlated/uncorrelated understanding |
| 5-6 | Developing — Review NULL semantics in NOT IN |
| <5 | Beginner — Re-read PROBLEM_WALKTHROUGH.md |

---

## Further Study

- Read `PROBLEM_WALKTHROUGH.md` for Nth Highest, Delete Duplicates, Not Boring Movies
- Practice: LeetCode SQL 177, 196, 620
- Study: Oracle analytic functions, ROWID, subquery optimization