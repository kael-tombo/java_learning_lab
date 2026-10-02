# Quiz: SQL CTEs & Window Functions (Lab 04)

**Topic:** CTEs, Gaps-and-Islands, LAG/LEAD, Advanced Analytics  
**Difficulty:** Medium-Hard  
**Time Limit:** 15 minutes

---

## Questions

### 1. Gaps-and-Islands
In "Find Start and End of Continuous Ranges", what is the key insight for grouping consecutive IDs?
- A) `LAG(id) OVER (ORDER BY id)` gives previous ID
- B) `id - ROW_NUMBER() OVER (ORDER BY id)` is constant for consecutive sequences
- C) `LEAD(id) OVER (ORDER BY id) - id = 1` finds consecutive pairs
- D) `SUM(CASE WHEN ...) OVER (...)` accumulates group numbers

### 2. LAG/LEAD
For "Consecutive Available Seats", why use LAG/LEAD instead of self-join?
- A) LAG/LEAD is always faster
- B) LAG/LEAD avoids self-join duplication and is more readable
- C) Self-join doesn't work for adjacent rows
- D) LAG/LEAD uses less memory

### 3. Window Frame
What is the default window frame for `SUM(salary) OVER (PARTITION BY dept ORDER BY hire_date)`?
- A) `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`
- B) `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`
- C) `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`
- D) `RANGE BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING`

### 4. HAVING with Window Function
In "Quiet Students", how does `HAVING SUM(CASE WHEN score IN (min_s, max_s) THEN 1 ELSE 0 END) = 0` work?
- A) Counts exams where student got min or max score
- B) Filters students who never got min or max in any exam
- C) Both A and B
- D) Neither

### 5. ROW_NUMBER vs RANK vs DENSE_RANK
For finding top student per exam, which ranking function handles ties correctly for "all ties included"?
- A) ROW_NUMBER
- B) RANK
- C) DENSE_RANK
- D) All handle ties the same

### 6. CTE Recursion
Can Oracle CTEs be recursive?
- A) Yes, with `WITH RECURSIVE`
- B) Yes, with `CONNECT BY` in CTE
- C) No, Oracle doesn't support recursive CTEs (use CONNECT BY)
- D) Only in Oracle 21c+

### 7. Execution Plan: WINDOW SORT
What does `WINDOW SORT` in an execution plan indicate?
- A) Sorting for ORDER BY clause
- B) Computing analytic function (LAG, ROW_NUMBER, SUM OVER, etc.)
- C) Sorting for GROUP BY
- D) Sorting for DISTINCT

### 8. PERCENTILE_CONT
What does `PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary)` compute?
- A) Average salary
- B) Median salary (interpolated)
- C) 50th percentile (discrete)
- D) Standard deviation

### 9. MATCH_RECOGNIZE
What is `MATCH_RECOGNIZE` used for?
- A) Pattern matching in row sequences
- B) Fuzzy string matching
- C) Join condition matching
- D) Index matching

### 10. Performance: Window Function vs Self-Join
For "Consecutive Available Seats", window function vs self-join:
- A) Window function always faster
- B) Self-join with index can be faster for small tables
- C) They have identical plans
- D) Self-join is always faster

---

## Answers

| # | Answer | Explanation |
|---|--------|-------------|
| 1 | **B** | `id - ROW_NUMBER()` produces same value for consecutive IDs (the "difference" trick). |
| 2 | **B** | LAG/LEAD: single pass, no duplication, cleaner. Self-join duplicates rows for each match. |
| 3 | **B** | Default is `RANGE UNBOUNDED PRECEDING` (not ROWS). Includes peers (ties in ORDER BY). |
| 4 | **C** | A counts per exam, B filters students — together they find students with zero min/max occurrences. |
| 5 | **B** | RANK gives same rank to ties, skips next rank. For "top N including ties" use RANK. |
| 6 | **C** | Oracle uses `CONNECT BY` for recursion. Recursive CTEs (`WITH RECURSIVE`) not supported (as of 19c). |
| 7 | **B** | WINDOW SORT computes analytic/window functions. |
| 8 | **B** | PERCENTILE_CONT interpolates; PERCENTILE_DISC returns discrete value. |
| 9 | **A** | MATCH_RECOGNIZE = row pattern matching (like regex for rows). |
| 10 | **B** | For small tables, indexed self-join can beat window sort overhead. |

---

## Scoring

| Score | Level |
|-------|-------|
| 9-10 | Expert — Advanced analytics master |
| 7-8 | Proficient — Strong CTE/window function skills |
| 5-6 | Developing — Review gaps-and-islands, window frames |
| <5 | Beginner — Re-read PROBLEM_WALKTHROUGH.md |

---

## Further Study

- Read `PROBLEM_WALKTHROUGH.md` for Continuous Ranges, Consecutive Seats, Quiet Students
- Practice: LeetCode SQL 1285, 603, 1412
- Study: Oracle window functions, MATCH_RECOGNIZE, CONNECT BY