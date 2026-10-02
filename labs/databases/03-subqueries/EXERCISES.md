# Exercises: SQL Subqueries (Lab 03)

**Prerequisites:** Read `PROBLEM_WALKTHROUGH.md`  
**Difficulty:** Progressive (Easy → Medium → Hard)

---

## Exercise 1: Nth Highest Salary Variations (Easy)

### Task
Implement Nth highest salary using different approaches.

### Requirements
```sql
-- 1a. DENSE_RANK approach (standard)
-- 1b. OFFSET/FETCH (Oracle 12c+)
-- 1c. Correlated subquery with COUNT(DISTINCT)
-- 1d. Create Oracle function get_nth_highest_salary(N)
-- 1e. Handle edge cases: N=0, N > distinct count, all salaries same
```

---

## Exercise 2: Deduplication Patterns (Easy)

### Task
Practice deleting duplicates using different methods.

### Requirements
```sql
-- Table: Person(id PK, email)
-- 2a. NOT IN approach (with NULL-safe subquery)
-- 2b. NOT EXISTS approach
-- 2c. ROW_NUMBER + ROWID approach (recommended)
-- 2d. Compare execution plans for each
-- 2e. Handle case where email can be NULL
```

---

## Exercise 3: Conditional Filtering (Easy)

### Task
Variations on "Not Boring Movies".

### Requirements
```sql
-- Table: Cinema(id PK, movie, description, rating)
-- 3a. Odd IDs, description not 'boring', order by rating DESC
-- 3b. Even IDs, description contains 'great' (case-insensitive)
-- 3c. IDs divisible by 3, rating > 8.0
-- 3d. Use BITAND instead of MOD for odd/even
-- 3e. Handle NULL descriptions (include or exclude)
```

---

## Exercise 4: Scalar Subqueries (Medium)

### Task
Use scalar subqueries in SELECT and WHERE.

### Requirements
```sql
-- Schema: Employee(id, name, salary, dept_id), Department(id, name)
-- 4a. List employees with their department's average salary (scalar subquery in SELECT)
-- 4b. Employees earning more than their department's average
-- 4c. Departments with above-company-average salary
-- 4c. For each employee, show: name, salary, dept_avg, company_avg, diff_from_dept_avg
```

---

## Exercise 5: Correlated Subqueries (Medium)

### Task
Practice correlated subqueries for row-by-row logic.

### Requirements
```sql
-- 5a. For each department, find highest-paid employee (correlated subquery)
-- 5b. Employees who earn more than ANY employee in department 10
-- 5c. Employees who earn more than ALL employees in department 10
-- 5d. Find "lonely" employees: no one else in their department has same salary
-- 5e. For each employee, count how many colleagues earn more
```

---

## Exercise 6: Inline Views & WITH Clause (Medium)

### Task
Use inline views and CTEs for complex logic.

### Requirements
```sql
-- 6a. Department salary stats: dept_name, min_sal, max_sal, avg_sal, emp_count
-- 6b. Find departments where avg_sal > company avg (use CTE)
-- 6c. Top 3 departments by average salary
-- 6d. Employee rank within department (using inline view with DENSE_RANK)
-- 6e. Median salary per department (use PERCENTILE_CONT or ROW_NUMBER trick)
```

---

## Exercise 7: DML with Subqueries (Medium)

### Task
INSERT, UPDATE, DELETE using subqueries.

### Requirements
```sql
-- 7a. INSERT: Archive high-salary employees to EMP_ARCHIVE table
-- 7b. UPDATE: Give 10% raise to employees below department average
-- 7c. DELETE: Remove employees in departments with < 3 people
-- 7d. MERGE: Upsert department stats into DEPT_STATS table
-- 7e. Multi-table INSERT: Split employees into HIGH_SAL and LOW_SAL tables
```

---

## Exercise 8: Advanced Analytics (Hard)

### Task
Complex subquery challenges.

### Requirements
```sql
-- 8a. Running total of salaries ordered by hire_date (per department)
-- 8b. Salary percentile for each employee (PERCENT_RANK)
-- 8c. Find salary outliers: > 2 standard deviations from department mean
-- 8d. Department salary distribution: histogram (salary ranges + counts)
-- 8e. Employees paid more than 90th percentile of their job title
```

---

## Exercise 9: Subquery Optimization (Hard)

### Task
Analyze and optimize subquery performance.

### Requirements
```sql
-- 9a. EXPLAIN PLAN for a correlated subquery query
-- 9b. Identify: FILTER operation (correlated subquery not unnested)
-- 9c. Rewrite correlated subquery as JOIN/inline view
-- 9d. Use /*+ UNNEST */ hint to force unnesting
-- 9e. Compare performance before/after
```

---

## Exercise 10: Cross-Dialect Subqueries (Hard)

### Task
Translate subquery patterns to other SQL dialects.

### Requirements
```sql
-- 10a. Oracle DENSE_RANK → PostgreSQL / MySQL / SQL Server (same)
-- 10b. Oracle OFFSET/FETCH → PostgreSQL (same) / MySQL (LIMIT/OFFSET) / SQL Server (OFFSET/FETCH)
-- 10c. Oracle ROWID → PostgreSQL (ctid) / MySQL (no direct equivalent) / SQL Server (%%physloc%%)
-- 10d. Oracle KEEP/DENSE_RANK → PostgreSQL (DISTINCT ON) / SQL Server (TOP 1 WITH TIES)
-- 10e. Oracle CONNECT BY (hierarchical) → PostgreSQL (WITH RECURSIVE) / SQL Server (WITH RECURSIVE)
```

---

## Solutions

### Exercise 1
```sql
-- 1a: SELECT DISTINCT salary FROM (
--       SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) rnk FROM employee
--     ) WHERE rnk = N;
-- 1b: SELECT DISTINCT salary FROM employee ORDER BY salary DESC 
--     OFFSET N-1 ROWS FETCH NEXT 1 ROWS ONLY;
-- 1c: SELECT DISTINCT salary FROM employee e1 
--     WHERE N = (SELECT COUNT(DISTINCT salary) FROM employee e2 WHERE e2.salary >= e1.salary);
-- 1d: CREATE OR REPLACE FUNCTION get_nth_highest_salary(n NUMBER) RETURN NUMBER IS
--       result NUMBER;
--     BEGIN
--       SELECT DISTINCT salary INTO result FROM (
--         SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) rnk FROM employee
--       ) WHERE rnk = n;
--       RETURN result;
--     EXCEPTION WHEN NO_DATA_FOUND THEN RETURN NULL; END;
-- 1e: N=0 → invalid; N>count → NULL; all same → only N=1 returns value.
```

### Exercise 2
```sql
-- 2a: DELETE FROM person WHERE id NOT IN (
--       SELECT MIN(id) FROM person WHERE email IS NOT NULL GROUP BY email
--     );
-- 2b: DELETE FROM person p1 WHERE NOT EXISTS (
--       SELECT 1 FROM person p2 
--       WHERE p2.email = p1.email 
--       GROUP BY p2.email 
--       HAVING MIN(p2.id) = p1.id
--     );
-- 2c: DELETE FROM person WHERE ROWID IN (
--       SELECT rid FROM (
--         SELECT ROWID rid, ROW_NUMBER() OVER (PARTITION BY email ORDER BY id) rn FROM person
--       ) WHERE rn > 1
--     );
-- 2d: ROW_NUMBER+ROWID usually fastest (single scan, no self-join).
-- 2e: ROW_NUMBER approach handles NULL emails naturally (all NULLs in one partition).
```

### Exercise 3
```sql
-- 3a: SELECT * FROM cinema WHERE MOD(id, 2) = 1 AND description != 'boring' ORDER BY rating DESC;
-- 3b: SELECT * FROM cinema WHERE MOD(id, 2) = 0 AND LOWER(description) LIKE '%great%';
-- 3c: SELECT * FROM cinema WHERE MOD(id, 3) = 0 AND rating > 8.0;
-- 3d: BITAND(id, 1) = 1 for odd; BITAND(id, 1) = 0 for even.
-- 3e: NVL(description, '') != 'boring' to include NULLs; description IS NOT NULL AND description != 'boring' to exclude.
```

### Exercise 4
```sql
-- 4a: SELECT e.name, e.salary, 
--       (SELECT AVG(salary) FROM employee WHERE dept_id = e.dept_id) dept_avg
--     FROM employee e;
-- 4b: SELECT * FROM employee e 
--     WHERE e.salary > (SELECT AVG(salary) FROM employee WHERE dept_id = e.dept_id);
-- 4c: SELECT d.name FROM department d
--     WHERE (SELECT AVG(salary) FROM employee WHERE dept_id = d.id) > 
--           (SELECT AVG(salary) FROM employee);
-- 4c (corrected): SELECT e.name, e.salary, 
--       (SELECT AVG(salary) FROM employee WHERE dept_id = e.dept_id) dept_avg,
--       (SELECT AVG(salary) FROM employee) company_avg,
--       e.salary - (SELECT AVG(salary) FROM employee WHERE dept_id = e.dept_id) diff
--     FROM employee e;
```

### Exercise 5
```sql
-- 5a: SELECT e.* FROM employee e
--     WHERE e.salary = (SELECT MAX(salary) FROM employee WHERE dept_id = e.dept_id);
-- 5b: SELECT * FROM employee WHERE salary > ANY (SELECT salary FROM employee WHERE dept_id = 10);
-- 5c: SELECT * FROM employee WHERE salary > ALL (SELECT salary FROM employee WHERE dept_id = 10);
-- 5d: SELECT * FROM employee e1
--     WHERE NOT EXISTS (SELECT 1 FROM employee e2 
--                       WHERE e2.dept_id = e1.dept_id 
--                         AND e2.id != e1.id 
--                         AND e2.salary = e1.salary);
-- 5e: SELECT e1.name, e1.salary,
--       (SELECT COUNT(*) FROM employee e2 
--        WHERE e2.dept_id = e1.dept_id AND e2.salary > e1.salary) higher_count
--     FROM employee e1;
```

### Exercise 6
```sql
-- 6a: WITH dept_stats AS (
--       SELECT d.name dept_name, MIN(e.salary) min_sal, MAX(e.salary) max_sal,
--              AVG(e.salary) avg_sal, COUNT(*) emp_count
--       FROM department d JOIN employee e ON d.id = e.dept_id
--       GROUP BY d.name
--     ) SELECT * FROM dept_stats;
-- 6b: WITH dept_stats AS (...), company_avg AS (SELECT AVG(salary) a FROM employee)
--     SELECT ds.dept_name FROM dept_stats ds, company_avg ca
--     WHERE ds.avg_sal > ca.a;
-- 6c: SELECT dept_name FROM dept_stats ORDER BY avg_sal DESC FETCH FIRST 3 ROWS ONLY;
-- 6d: SELECT * FROM (
--       SELECT e.*, d.name dept_name,
--              DENSE_RANK() OVER (PARTITION BY e.dept_id ORDER BY e.salary DESC) rnk
--       FROM employee e JOIN department d ON e.dept_id = d.id
--     ) WHERE rnk <= 3;
-- 6e: SELECT dept_id, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary) median_sal
--     FROM employee GROUP BY dept_id;
--     -- Or ROW_NUMBER: SELECT dept_id, AVG(salary) FROM (
--       SELECT dept_id, salary, 
--              ROW_NUMBER() OVER (PARTITION BY dept_id ORDER BY salary) rn,
--              COUNT(*) OVER (PARTITION BY dept_id) cnt
--       FROM employee
--     ) WHERE rn IN (cnt/2+1, (cnt+1)/2) GROUP BY dept_id;
```

### Exercise 7
```sql
-- 7a: INSERT INTO emp_archive SELECT * FROM employee WHERE salary > 100000;
-- 7b: UPDATE employee e SET salary = salary * 1.10
--     WHERE salary < (SELECT AVG(salary) FROM employee WHERE dept_id = e.dept_id);
-- 7c: DELETE FROM employee 
--     WHERE dept_id IN (SELECT dept_id FROM employee GROUP BY dept_id HAVING COUNT(*) < 3);
-- 7d: MERGE INTO dept_stats ds
--     USING (SELECT dept_id, AVG(salary) avg_sal, COUNT(*) cnt FROM employee GROUP BY dept_id) src
--     ON (ds.dept_id = src.dept_id)
--     WHEN MATCHED THEN UPDATE SET ds.avg_sal = src.avg_sal, ds.emp_count = src.cnt
--     WHEN NOT MATCHED THEN INSERT (dept_id, avg_sal, emp_count) VALUES (src.dept_id, src.avg_sal, src.cnt);
-- 7e: INSERT ALL
--       WHEN salary > 50000 THEN INTO high_sal VALUES (id, name, salary, dept_id)
--       ELSE INTO low_sal VALUES (id, name, salary, dept_id)
--     SELECT * FROM employee;
```

### Exercise 8
```sql
-- 8a: SELECT e.*, SUM(salary) OVER (PARTITION BY dept_id ORDER BY hire_date) running_total
--     FROM employee e;
-- 8b: SELECT e.*, PERCENT_RANK() OVER (PARTITION BY dept_id ORDER BY salary) sal_pctile
--     FROM employee e;
-- 8c: WITH dept_stats AS (
--       SELECT dept_id, AVG(salary) avg_sal, STDDEV(salary) std_sal FROM employee GROUP BY dept_id
--     )
--     SELECT e.* FROM employee e JOIN dept_stats d ON e.dept_id = d.dept_id
--     WHERE e.salary > d.avg_sal + 2*d.std_sal OR e.salary < d.avg_sal - 2*d.std_sal;
-- 8d: SELECT dept_id, 
--       CASE WHEN salary < 3000 THEN '<3K'
--            WHEN salary < 5000 THEN '3K-5K'
--            WHEN salary < 8000 THEN '5K-8K'
--            WHEN salary < 12000 THEN '8K-12K'
--            ELSE '12K+' END salary_band,
--       COUNT(*) cnt
--     FROM employee GROUP BY dept_id, salary_band ORDER BY dept_id, salary_band;
-- 8e: WITH job_pct AS (
--       SELECT job_id, PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY salary) p90
--       FROM employee GROUP BY job_id
--     )
--     SELECT e.* FROM employee e JOIN job_pct j ON e.job_id = j.job_id
--     WHERE e.salary > j.p90;
```

### Exercise 9
```sql
-- 9a: EXPLAIN PLAN FOR 
--     SELECT * FROM employee e 
--     WHERE salary > (SELECT AVG(salary) FROM employee WHERE dept_id = e.dept_id);
-- 9b: Plan shows FILTER operation with subquery executed per row.
-- 9c: Rewrite: SELECT e.* FROM employee e
--     JOIN (SELECT dept_id, AVG(salary) avg_sal FROM employee GROUP BY dept_id) d
--       ON e.dept_id = d.dept_id
--     WHERE e.salary > d.avg_sal;
-- 9d: Add /*+ UNNEST */ to correlated subquery.
-- 9e: Correlated: cost ~N x subquery_cost. Unnested: single hash join, much faster.
```

### Exercise 10
```sql
-- 10a: All support DENSE_RANK() OVER (PARTITION BY ... ORDER BY ...)
-- 10b: MySQL: LIMIT 1 OFFSET N-1; SQL Server: OFFSET N-1 ROWS FETCH NEXT 1 ROWS ONLY
-- 10c: PostgreSQL: ctid; MySQL: use primary key; SQL Server: %%physloc%% (undocumented)
-- 10d: PostgreSQL: DISTINCT ON (job_id) with ORDER BY salary DESC; SQL Server: TOP 1 WITH TIES
-- 10e: Oracle: CONNECT BY PRIOR id = mgr_id START WITH mgr_id IS NULL
--      PostgreSQL/SQL Server: WITH RECURSIVE cte AS (SELECT ... UNION ALL SELECT ...)
```

---

## Grading Rubric

| Exercise | Points | Criteria |
|----------|--------|----------|
| 1 | 15 | All 3 approaches + function + edge cases |
| 2 | 20 | Three delete methods, NULL handling |
| 3 | 15 | MOD/BITAND, string filtering, NULL logic |
| 4 | 20 | Scalar subqueries in SELECT/WHERE |
| 5 | 20 | ANY/ALL, NOT EXISTS, correlated counts |
| 6 | 20 | CTEs, inline views, percentiles |
| 7 | 20 | INSERT/UPDATE/DELETE/MERGE with subqueries |
| 8 | 30 | Window functions, analytics, stats |
| 9 | 20 | Plan analysis, unnesting, hints |
| 10 | 15 | Accurate dialect translations |

**Total: 200 points**

---

## Next Steps

1. Run against Oracle HR schema or equivalent
2. Practice: LeetCode SQL Medium/Hard subquery problems
3. Study: Oracle subquery unnesting transformations
4. Read: Oracle SQL Tuning Guide — Subquery optimization