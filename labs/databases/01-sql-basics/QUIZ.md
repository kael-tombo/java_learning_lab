# Quiz: SQL Basics (Lab 01)

**Topic:** Fundamental SQL Queries — Filtering, Ordering, Basic Functions  
**Difficulty:** Easy  
**Time Limit:** 15 minutes

---

## Questions

### 1. Date Filtering
In Oracle, how do you find employees hired in the last 90 days?
- A) `WHERE hire_date >= SYSDATE - 90`
- B) `WHERE hire_date >= DATEADD(day, -90, GETDATE())`
- C) `WHERE hire_date >= CURRENT_DATE - INTERVAL '90 days'`
- D) `WHERE hire_date >= NOW() - 90`

### 2. NULL Handling
In the "Customer Referee" problem, why does `WHERE referee_id != 2` fail to include customers with NULL referee_id?
- A) NULL != 2 evaluates to FALSE
- B) NULL != 2 evaluates to UNKNOWN, and WHERE filters out UNKNOWN
- C) NULL values are automatically excluded from all comparisons
- D) Oracle treats NULL as 0 in numeric comparisons

### 3. Correct NULL Check
Which query correctly finds customers NOT referred by customer 2 (including NULL referees)?
- A) `WHERE referee_id != 2 OR referee_id IS NULL`
- B) `WHERE NVL(referee_id, -1) != 2`
- C) `WHERE COALESCE(referee_id, -1) != 2`
- D) All of the above

### 4. Big Countries
For the "Big Countries" problem (area ≥ 3M OR population ≥ 25M), which index would be most effective?
- A) `CREATE INDEX ON world(area)`
- B) `CREATE INDEX ON world(population)`
- C) `CREATE INDEX ON world(area, population)`
- D) Full table scan is optimal regardless

### 5. Oracle DATE vs TIMESTAMP
What is the difference between `SYSDATE` and `SYSTIMESTAMP` in Oracle?
- A) No difference
- B) SYSDATE has seconds precision; SYSTIMESTAMP has fractional seconds + timezone
- C) SYSDATE is UTC; SYSTIMESTAMP is session timezone
- D) SYSTIMESTAMP is deprecated

### 6. Execution Plan
What operation does Oracle typically choose for `WHERE hire_date >= SYSDATE - 90` without an index?
- A) INDEX RANGE SCAN
- B) FULL TABLE SCAN
- C) INDEX FAST FULL SCAN
- D) TABLE ACCESS BY ROWID

### 7. Index for Ordering
To optimize `ORDER BY hire_date DESC` with the date filter, which index is best?
- A) `CREATE INDEX ON employees(hire_date)`
- B) `CREATE INDEX ON employees(hire_date DESC)`
- C) `CREATE INDEX ON employees(hire_date, department_id)`
- D) `CREATE INDEX ON employees(department_id, hire_date)`

### 8. Partitioning Strategy
For a large employees table queried frequently by hire_date range, what partitioning strategy helps?
- A) Hash partitioning on employee_id
- B) List partitioning on department_id
- C) Range partitioning on hire_date
- D) No partitioning needed

### 9. NVL vs COALESCE
What is the key difference between `NVL` and `COALESCE` in Oracle?
- A) NVL takes 2 args; COALESCE takes N args
- B) COALESCE is standard SQL; NVL is Oracle-specific
- C) COALESCE short-circuits; NVL may evaluate both args
- D) All of the above

### 10. Edge Case: Future Dates
If hire_date can contain future dates, how do you exclude them from "last 90 days"?
- A) `WHERE hire_date BETWEEN SYSDATE - 90 AND SYSDATE`
- B) `WHERE hire_date >= SYSDATE - 90 AND hire_date <= SYSDATE`
- C) Both A and B work
- D) Neither works correctly

---

## Answers

| # | Answer | Explanation |
|---|--------|-------------|
| 1 | **A** | Oracle DATE arithmetic: `SYSDATE - 90` subtracts 90 days. |
| 2 | **B** | SQL three-valued logic: NULL comparison yields UNKNOWN, filtered by WHERE. |
| 3 | **D** | All three handle NULL correctly: explicit IS NULL, NVL, COALESCE. |
| 4 | **C** | Composite index on both filtered columns allows INDEX RANGE SCAN. |
| 5 | **B** | SYSTIMESTAMP includes fractional seconds and timezone info. |
| 6 | **B** | Without index, Oracle does full table scan + filter. |
| 7 | **B** | DESC index matches ORDER BY, avoiding SORT ORDER BY step. |
| 8 | **C** | Range partitioning on hire_date enables partition pruning. |
| 9 | **D** | All true: NVL(2 args), COALESCE(N args, standard, short-circuits). |
| 10 | **C** | Both `BETWEEN` and explicit `AND` work to cap at SYSDATE. |

---

## Scoring

| Score | Level |
|-------|-------|
| 9-10 | Expert — Oracle SQL fundamentals mastered |
| 7-8 | Proficient — Solid grasp of filtering, NULLs, indexes |
| 5-6 | Developing — Review NULL semantics and date functions |
| <5 | Beginner — Re-read PROBLEM_WALKTHROUGH.md |

---

## Further Study

- Read `PROBLEM_WALKTHROUGH.md` for detailed problem walkthroughs
- Practice: LeetCode SQL 595, 596, 584
- Study: Oracle DATE arithmetic, execution plans, partitioning