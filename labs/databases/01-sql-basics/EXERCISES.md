# Exercises: SQL Basics (Lab 01)

**Prerequisites:** Read `PROBLEM_WALKTHROUGH.md`  
**Difficulty:** Progressive (Easy → Medium)

---

## Exercise 1: Date Range Variations (Easy)

### Task
Write queries for different hiring date windows.

### Requirements
```sql
-- 1a. Employees hired in last 30 days
-- 1b. Employees hired in last 7 days (this week)
-- 1c. Employees hired in current month
-- 1d. Employees hired in previous month
-- 1e. Employees hired between two specific dates (e.g., '2023-01-01' and '2023-12-31')
```

### Test Cases
```sql
-- Verify with sample data:
-- employee_id 100: hire_date 17-JUN-03
-- employee_id 101: hire_date 21-SEP-05
-- employee_id 200: hire_date 17-SEP-03
```

---

## Exercise 2: NULL Handling Patterns (Easy)

### Task
Practice different NULL handling techniques.

### Requirements
```sql
-- 2a. Find employees with NULL commission_pct
-- 2b. Find employees with non-NULL commission_pct
-- 2c. Show commission_pct, but display 'No Commission' for NULLs
-- 2d. Calculate annual compensation: salary + (salary * commission_pct), treating NULL as 0
-- 2e. Find employees where manager_id is NULL (top-level executives)
```

### Test Cases
```sql
-- Expected: NVL, COALESCE, CASE all produce same result for 2c/2d
-- commission_pct NULL → 'No Commission' / 0
```

---

## Exercise 3: String & Date Functions (Easy)

### Task
Use Oracle string and date functions.

### Requirements
```sql
-- 3a. Show employee names in UPPER, LOWER, INITCAP
-- 3b. Extract first 3 letters of first_name (SUBSTR)
-- 3c. Concatenate first_name || ' ' || last_name as full_name
-- 3d. Find employees whose last_name starts with 'K' (LIKE)
-- 3e. Find employees hired on a Monday (TO_CHAR(hire_date, 'DY'))
-- 3f. Calculate months employed: MONTHS_BETWEEN(SYSDATE, hire_date)
-- 3g. Show hire_date formatted as 'Month DD, YYYY' (TO_CHAR)
```

---

## Exercise 4: Conditional Logic (Medium)

### Task
Use CASE expressions for business logic.

### Requirements
```sql
-- 4a. Categorize salary: 
--     < 5000 → 'Low', 5000-10000 → 'Medium', > 10000 → 'High'
-- 4b. Show department name based on department_id:
--     10 → 'Administration', 20 → 'Marketing', 90 → 'Executive', else 'Other'
-- 4c. Bonus calculation:
--     If hire_date before 2005-01-01 → 10% of salary
--     Else if commission_pct not null → 5% of salary
--     Else → 2% of salary
-- 4d. Flag: 'Senior' if hired before 2010, 'Junior' otherwise
```

---

## Exercise 5: Aggregation Basics (Medium)

### Task
Practice aggregate functions with GROUP BY.

### Requirements
```sql
-- 5a. Count employees per department
-- 5b. Average salary per department
-- 5c. Min/Max/Avg salary per job_id
-- 5d. Departments with more than 5 employees (HAVING)
-- 5e. Job titles with average salary > 8000
-- 5f. Total salary cost per department
```

---

## Exercise 6: Index & Optimization (Medium)

### Task
Analyze and create indexes for the queries above.

### Requirements
```sql
-- 6a. For query 1a (last 30 days), what index helps?
-- 6b. For query 3d (last_name LIKE 'K%'), what index helps?
-- 6c. For query 5a (count per department), what index helps?
-- 6d. Write CREATE INDEX statements for each
-- 6e. Explain why a composite index (department_id, hire_date) helps query 5a filtered by department
```

---

## Exercise 7: Partitioning Practice (Medium)

### Task
Design partitioning for a large employees table.

### Requirements
```sql
-- 7a. Create range-partitioned table by hire_date (yearly partitions)
-- 7b. Create list-partitioned table by department_id
-- 7c. Create hash-partitioned table by employee_id (for even distribution)
-- 7d. Show how partition pruning works for "last 90 days" query
-- 7e. Add a new partition for 2024 hires
```

---

## Exercise 8: Real-World Scenarios (Medium)

### Task
Solve practical business questions.

### Requirements
```sql
-- 8a. Find the most recently hired employee in each department
-- 8b. Find employees who earn more than the average salary in their department
-- 8c. Find departments where all employees have commission_pct NOT NULL
-- 8d. Rank employees by salary within each department (DENSE_RANK)
-- 8e. Find the 2nd highest salary in the company (distinct)
```

---

## Exercise 9: Cross-Dialect Comparison (Medium)

### Task
Translate Oracle queries to other dialects.

### Requirements
```sql
-- 9a. Oracle: SYSDATE - 90 → PostgreSQL: CURRENT_DATE - INTERVAL '90 days'
-- 9b. Oracle: NVL(col, 0) → PostgreSQL: COALESCE(col, 0) / MySQL: IFNULL(col, 0)
-- 9c. Oracle: TRUNC(date) → PostgreSQL: date_trunc('day', date)::date
-- 9d. Oracle: MONTHS_BETWEEN(d1, d2) → PostgreSQL: EXTRACT(epoch FROM (d1-d2))/2592000
-- 9e. Oracle: DECODE → PostgreSQL: CASE WHEN
```

---

## Exercise 10: Performance Tuning Challenge (Hard)

### Task
Optimize a slow query on a 10M-row employees table.

### Scenario
```sql
-- Slow query (full table scan, 10M rows):
SELECT e.employee_id, e.first_name, e.last_name, e.salary, d.department_name
FROM employees e
JOIN departments d ON e.department_id = d.department_id
WHERE e.hire_date >= SYSDATE - 365
  AND e.salary > 5000
  AND d.location_id = 1700
ORDER BY e.salary DESC;
```

### Requirements
```sql
-- 10a. Analyze execution plan (EXPLAIN PLAN)
-- 10b. Create optimal indexes (consider join, filter, order by)
-- 10c. Consider partitioning strategy
-- 10d. Rewrite query if needed (e.g., push predicates)
-- 10e. Estimate cost improvement
```

---

## Solutions

### Exercise 1
```sql
-- 1a: WHERE hire_date >= SYSDATE - 30
-- 1b: WHERE hire_date >= SYSDATE - 7
-- 1c: WHERE hire_date >= TRUNC(SYSDATE, 'MM')
-- 1d: WHERE hire_date >= ADD_MONTHS(TRUNC(SYSDATE, 'MM'), -1) 
--     AND hire_date < TRUNC(SYSDATE, 'MM')
-- 1e: WHERE hire_date BETWEEN DATE '2023-01-01' AND DATE '2023-12-31'
```

### Exercise 2
```sql
-- 2a: WHERE commission_pct IS NULL
-- 2b: WHERE commission_pct IS NOT NULL
-- 2c: NVL(TO_CHAR(commission_pct), 'No Commission')
-- 2d: salary + salary * NVL(commission_pct, 0)
-- 2e: WHERE manager_id IS NULL
```

### Exercise 3
```sql
-- 3a: UPPER(first_name), LOWER(last_name), INITCAP(first_name || ' ' || last_name)
-- 3b: SUBSTR(first_name, 1, 3)
-- 3c: first_name || ' ' || last_name
-- 3d: WHERE last_name LIKE 'K%'
-- 3e: WHERE TO_CHAR(hire_date, 'DY') = 'MON'
-- 3f: MONTHS_BETWEEN(SYSDATE, hire_date)
-- 3g: TO_CHAR(hire_date, 'Month DD, YYYY')
```

### Exercise 4
```sql
-- 4a: CASE WHEN salary < 5000 THEN 'Low' WHEN salary <= 10000 THEN 'Medium' ELSE 'High' END
-- 4b: CASE department_id WHEN 10 THEN 'Admin' WHEN 20 THEN 'Marketing' WHEN 90 THEN 'Executive' ELSE 'Other' END
-- 4c: CASE WHEN hire_date < DATE '2005-01-01' THEN salary * 0.10 
--          WHEN commission_pct IS NOT NULL THEN salary * 0.05 
--          ELSE salary * 0.02 END
-- 4d: CASE WHEN hire_date < DATE '2010-01-01' THEN 'Senior' ELSE 'Junior' END
```

### Exercise 5
```sql
-- 5a: SELECT department_id, COUNT(*) FROM employees GROUP BY department_id
-- 5b: SELECT department_id, AVG(salary) FROM employees GROUP BY department_id
-- 5c: SELECT job_id, MIN(salary), MAX(salary), AVG(salary) FROM employees GROUP BY job_id
-- 5d: SELECT department_id, COUNT(*) FROM employees GROUP BY department_id HAVING COUNT(*) > 5
-- 5e: SELECT job_id, AVG(salary) FROM employees GROUP BY job_id HAVING AVG(salary) > 8000
-- 5f: SELECT department_id, SUM(salary) FROM employees GROUP BY department_id
```

### Exercise 6
```sql
-- 6a: CREATE INDEX emp_hire_date_idx ON employees(hire_date DESC);
-- 6b: CREATE INDEX emp_last_name_idx ON employees(last_name); -- supports LIKE 'K%'
-- 6c: CREATE INDEX emp_dept_idx ON employees(department_id);
-- 6d: (see above)
-- 6e: Composite (department_id, hire_date) allows index range scan for specific dept + date range
```

### Exercise 7
```sql
-- 7a: PARTITION BY RANGE (hire_date) (
--       PARTITION p_2020 VALUES LESS THAN (DATE '2021-01-01'),
--       PARTITION p_2021 VALUES LESS THAN (DATE '2022-01-01'),
--       PARTITION p_2022 VALUES LESS THAN (DATE '2023-01-01'),
--       PARTITION p_2023 VALUES LESS THAN (DATE '2024-01-01'),
--       PARTITION p_future VALUES LESS THAN (MAXVALUE)
--     )
-- 7b: PARTITION BY LIST (department_id) (
--       PARTITION p_admin VALUES (10),
--       PARTITION p_mktg VALUES (20),
--       PARTITION p_exec VALUES (90),
--       PARTITION p_other VALUES (DEFAULT)
--     )
-- 7c: PARTITION BY HASH (employee_id) PARTITIONS 16
-- 7d: Query "hire_date >= SYSDATE - 90" only scans p_2023 and p_future
-- 7e: ALTER TABLE employees ADD PARTITION p_2024 VALUES LESS THAN (DATE '2025-01-01');
```

### Exercise 8
```sql
-- 8a: SELECT * FROM (
--       SELECT e.*, d.department_name,
--              ROW_NUMBER() OVER (PARTITION BY e.department_id ORDER BY e.hire_date DESC) rn
--       FROM employees e JOIN departments d ON e.department_id = d.department_id
--     ) WHERE rn = 1;

-- 8b: SELECT e.* FROM employees e
--     JOIN (SELECT department_id, AVG(salary) avg_sal FROM employees GROUP BY department_id) d
--       ON e.department_id = d.department_id
--     WHERE e.salary > d.avg_sal;

-- 8c: SELECT department_id FROM employees
--     GROUP BY department_id
--     HAVING COUNT(*) = COUNT(commission_pct);

-- 8d: SELECT e.*, DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) sal_rank
--     FROM employees e;

-- 8e: SELECT DISTINCT salary FROM employees ORDER BY salary DESC 
--     OFFSET 1 ROWS FETCH NEXT 1 ROWS ONLY;
```

### Exercise 9
```sql
-- 9a: CURRENT_DATE - INTERVAL '90 days'
-- 9b: COALESCE(col, 0) / IFNULL(col, 0)
-- 9c: date_trunc('day', date)::date
-- 9d: EXTRACT(epoch FROM (d1-d2))/2592000 (approx)
-- 9e: CASE WHEN expr = val1 THEN res1 WHEN expr = val2 THEN res2 ELSE default END
```

### Exercise 10
```sql
-- 10a: EXPLAIN PLAN FOR ... ; SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
-- 10b: CREATE INDEX emp_hire_sal_idx ON employees(hire_date, salary);
--      CREATE INDEX emp_dept_sal_idx ON employees(department_id, salary);
--      CREATE INDEX dept_loc_idx ON departments(location_id);
-- 10c: PARTITION BY RANGE (hire_date) -- prunes to last year
-- 10d: Use inline view to filter departments first:
--      SELECT ... FROM (SELECT * FROM employees WHERE hire_date >= ... AND salary > 5000) e
--      JOIN (SELECT * FROM departments WHERE location_id = 1700) d ...
-- 10e: Full scan cost ~10M → Index range scan cost ~1000 (10000x improvement)
```

---

## Grading Rubric

| Exercise | Points | Criteria |
|----------|--------|----------|
| 1 | 10 | All date windows correct |
| 2 | 15 | NULL handling patterns correct |
| 3 | 15 | String/date functions used properly |
| 4 | 20 | CASE expressions handle all branches |
| 5 | 20 | GROUP BY + HAVING correct |
| 6 | 20 | Indexes match query patterns |
| 7 | 20 | Partition syntax correct, pruning explained |
| 8 | 30 | Window functions, subqueries correct |
| 9 | 20 | Dialect translations accurate |
| 10 | 30 | Plan analysis, indexing, partitioning |

**Total: 200 points**

---

## Next Steps

1. Run queries against Oracle HR schema or equivalent
2. Practice: LeetCode SQL Easy/Medium problems
3. Study: `PROBLEM_WALKTHROUGH.md` execution plans
4. Read: Oracle SQL Tuning Guide