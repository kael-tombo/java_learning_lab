# Worked SQL Query Examples: Relational Databases (Lab 01)

**Style:** SQL_SOLUTIONS — Step-by-step worked examples with execution plans and optimizations  
**Target:** Oracle 19c+ syntax (adaptable to PostgreSQL, MySQL, SQL Server)

---

## Example 1: Employee Tenure Analysis

### Business Question
"Find employees who have been with the company for more than 15 years as of today, grouped by department, showing average tenure per department."

### Step 1: Understand the Data
```sql
-- Tables
-- EMPLOYEES: employee_id, first_name, last_name, hire_date, department_id, salary
-- DEPARTMENTS: department_id, department_name
```

### Step 2: Write the Query
```sql
WITH tenure_calc AS (
  SELECT 
    e.employee_id,
    e.first_name || ' ' || e.last_name AS full_name,
    e.hire_date,
    d.department_name,
    -- Tenure in years (precise)
    FLOOR(MONTHS_BETWEEN(SYSDATE, e.hire_date) / 12) AS tenure_years,
    -- Tenure in months (for precise filtering)
    MONTHS_BETWEEN(SYSDATE, e.hire_date) AS tenure_months
  FROM employees e
  JOIN departments d ON e.department_id = d.department_id
)
SELECT 
  department_name,
  COUNT(*) AS employee_count,
  ROUND(AVG(tenure_years), 1) AS avg_tenure_years,
  MIN(tenure_years) AS min_tenure,
  MAX(tenure_years) AS max_tenure
FROM tenure_calc
WHERE tenure_months >= 180  -- 15 years * 12 months
GROUP BY department_name
ORDER BY avg_tenure_years DESC;
```

### Step 3: Execution Plan Analysis
```sql
EXPLAIN PLAN FOR
WITH tenure_calc AS (...) 
SELECT ... FROM tenure_calc WHERE tenure_months >= 180 GROUP BY department_name;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

**Expected Plan:**
```
| Id | Operation                    | Name          | Rows | Cost |
|----|------------------------------|---------------|------|------|
|  0 | SELECT STATEMENT             |               |    5 |    8 |
|  1 |  SORT GROUP BY               |               |    5 |    8 |
|  2 |   VIEW                       |               |  107 |    7 |
|  3 |    HASH JOIN                 |               |  107 |    7 |
|  4 |     TABLE ACCESS FULL        | DEPARTMENTS   |   27 |    3 |
|  5 |     TABLE ACCESS FULL        | EMPLOYEES     |  107 |    4 |
```
- **HASH JOIN** between EMPLOYEES and DEPARTMENTS
- **SORT GROUP BY** for aggregation
- No index on `hire_date` → full scan on EMPLOYEES

### Step 4: Optimization
```sql
-- Index for tenure filter
CREATE INDEX emp_hire_date_idx ON employees(hire_date);

-- Better: Composite index for join + filter
CREATE INDEX emp_dept_hire_idx ON employees(department_id, hire_date);

-- Partition by hire_date for large tables
ALTER TABLE employees 
PARTITION BY RANGE (hire_date) (
  PARTITION p_before_2000 VALUES LESS THAN (DATE '2000-01-01'),
  PARTITION p_2000_2010 VALUES LESS THAN (DATE '2010-01-01'),
  PARTITION p_2010_2020 VALUES LESS THAN (DATE '2020-01-01'),
  PARTITION p_future VALUES LESS THAN (MAXVALUE)
);
```

### Step 5: Test Edge Cases
```sql
-- Edge case: Future hire_date (data quality issue)
WHERE tenure_months >= 180 AND hire_date <= SYSDATE

-- Edge case: NULL hire_date
WHERE hire_date IS NOT NULL AND tenure_months >= 180

-- Verify with known data
SELECT * FROM tenure_calc WHERE employee_id IN (100, 101, 200);
-- King (17-JUN-03) → ~21 years
-- Kochhar (21-SEP-05) → ~19 years
-- Whalen (17-SEP-03) → ~21 years
```

---

## Example 2: Salary Band Distribution

### Business Question
"Show salary distribution by department using bands: <30K, 30K-50K, 50K-80K, 80K-120K, 120K+. Include percentage of department total."

### Step 1: Define Bands
```sql
WITH salary_bands AS (
  SELECT 
    e.employee_id,
    d.department_name,
    e.salary,
    CASE 
      WHEN e.salary < 30000 THEN '<30K'
      WHEN e.salary < 50000 THEN '30K-50K'
      WHEN e.salary < 80000 THEN '50K-80K'
      WHEN e.salary < 120000 THEN '80K-120K'
      ELSE '120K+'
    END AS salary_band
  FROM employees e
  JOIN departments d ON e.department_id = d.department_id
)
```

### Step 2: Aggregate with Window Function for Percentage
```sql
SELECT 
  department_name,
  salary_band,
  COUNT(*) AS employee_count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY department_name), 1) AS pct_of_dept
FROM salary_bands
GROUP BY department_name, salary_band
ORDER BY department_name, 
  CASE salary_band 
    WHEN '<30K' THEN 1 
    WHEN '30K-50K' THEN 2 
    WHEN '50K-80K' THEN 3 
    WHEN '80K-120K' THEN 4 
    ELSE 5 
  END;
```

### Step 3: Alternative - Pivot for Reporting
```sql
SELECT * FROM (
  SELECT department_name, salary_band
  FROM salary_bands
)
PIVOT (
  COUNT(*) FOR salary_band IN (
    '<30K' AS "UNDER_30K",
    '30K-50K' AS "30K_50K",
    '50K-80K' AS "50K_80K",
    '80K-120K' AS "80K_120K",
    '120K+' AS "OVER_120K"
  )
)
ORDER BY department_name;
```

---

## Example 3: Manager Hierarchy with Levels

### Business Question
"Display the management hierarchy starting from the CEO, showing each employee's level, their manager, and span of control (direct reports count)."

### Step 1: Recursive Hierarchy (CONNECT BY)
```sql
SELECT 
  LEVEL AS mgmt_level,
  LPAD(' ', 2*(LEVEL-1)) || e.first_name || ' ' || e.last_name AS employee_name,
  e.employee_id,
  e.manager_id,
  (SELECT COUNT(*) FROM employees WHERE manager_id = e.employee_id) AS direct_reports
FROM employees e
CONNECT BY PRIOR e.employee_id = e.manager_id
START WITH e.manager_id IS NULL
ORDER SIBLINGS BY e.last_name;
```

### Step 2: Same with Recursive CTE (Portable)
```sql
WITH RECURSIVE hierarchy AS (
  -- Anchor: CEO(s)
  SELECT 
    employee_id, 
    first_name, 
    last_name, 
    manager_id, 
    1 AS mgmt_level,
    CAST(first_name || ' ' || last_name AS VARCHAR2(4000)) AS path
  FROM employees
  WHERE manager_id IS NULL
  
  UNION ALL
  
  -- Recursive: direct reports
  SELECT 
    e.employee_id, 
    e.first_name, 
    e.last_name, 
    e.manager_id, 
    h.mgmt_level + 1,
    h.path || ' > ' || e.first_name || ' ' || e.last_name
  FROM employees e
  JOIN hierarchy h ON e.manager_id = h.employee_id
)
SELECT 
  mgmt_level,
  LPAD(' ', 2*(mgmt_level-1)) || first_name || ' ' || last_name AS employee_name,
  employee_id,
  manager_id,
  (SELECT COUNT(*) FROM employees WHERE manager_id = h.employee_id) AS direct_reports
FROM hierarchy h
ORDER BY path;
```

### Step 3: Span of Control Analysis
```sql
WITH mgr_stats AS (
  SELECT 
    m.employee_id AS mgr_id,
    m.first_name || ' ' || m.last_name AS mgr_name,
    COUNT(e.employee_id) AS direct_reports,
    COUNT(e.employee_id) OVER () AS total_managers,
    AVG(COUNT(e.employee_id)) OVER () AS avg_reports
  FROM employees m
  LEFT JOIN employees e ON m.employee_id = e.manager_id
  GROUP BY m.employee_id, m.first_name, m.last_name
)
SELECT 
  mgr_name,
  direct_reports,
  CASE 
    WHEN direct_reports = 0 THEN 'Individual Contributor'
    WHEN direct_reports <= 3 THEN 'Small Team'
    WHEN direct_reports <= 7 THEN 'Medium Team'
    WHEN direct_reports <= 15 THEN 'Large Team'
    ELSE 'Very Large Team'
  END AS team_size_category,
  ROUND(direct_reports / avg_reports * 100, 1) AS pct_of_avg
FROM mgr_stats
ORDER BY direct_reports DESC;
```

---

## Example 4: Department Budget vs Actual

### Business Question
"Compare each department's total salary cost against a budget (1.5x the average department salary). Flag over-budget departments."

### Step 1: Compute Department Salary Totals
```sql
WITH dept_salaries AS (
  SELECT 
    d.department_id,
    d.department_name,
    SUM(e.salary) AS total_salary,
    COUNT(e.employee_id) AS headcount,
    AVG(e.salary) AS avg_salary
  FROM departments d
  LEFT JOIN employees e ON d.department_id = e.department_id
  GROUP BY d.department_id, d.department_name
),
budget_calc AS (
  SELECT 
    department_name,
    total_salary,
    headcount,
    avg_salary,
    -- Budget = 1.5 * average department salary * headcount
    (SELECT 1.5 * AVG(avg_salary) FROM dept_salaries) * headcount AS budget
  FROM dept_salaries
)
SELECT 
  department_name,
  headcount,
  TO_CHAR(total_salary, 'FM$999,999,990') AS actual_cost,
  TO_CHAR(budget, 'FM$999,999,990') AS budget,
  TO_CHAR(budget - total_salary, 'FM$999,999,990') AS variance,
  CASE 
    WHEN total_salary > budget THEN 'OVER BUDGET'
    WHEN total_salary > budget * 0.9 THEN 'NEAR LIMIT'
    ELSE 'WITHIN BUDGET'
  END AS status,
  ROUND((total_salary / budget) * 100, 1) AS pct_of_budget
FROM budget_calc
ORDER BY pct_of_budget DESC;
```

---

## Example 5: Hiring Trends Over Time

### Business Question
"Show hiring trends by quarter for the last 5 years, with running total and year-over-year growth."

### Step 1: Generate Time Series (Oracle)
```sql
WITH quarters AS (
  SELECT 
    TRUNC(ADD_MONTHS(SYSDATE, -60), 'Q') + (LEVEL-1)*INTERVAL '3' MONTH AS quarter_start,
    TRUNC(ADD_MONTHS(SYSDATE, -60), 'Q') + LEVEL*INTERVAL '3' MONTH - INTERVAL '1' DAY AS quarter_end
  FROM dual
  CONNECT BY LEVEL <= 20  -- 5 years * 4 quarters
),
hiring AS (
  SELECT 
    TRUNC(hire_date, 'Q') AS hire_quarter,
    COUNT(*) AS hires
  FROM employees
  WHERE hire_date >= TRUNC(ADD_MONTHS(SYSDATE, -60), 'Q')
  GROUP BY TRUNC(hire_date, 'Q')
)
SELECT 
  TO_CHAR(q.quarter_start, 'YYYY-"Q"Q') AS quarter,
  COALESCE(h.hires, 0) AS hires,
  SUM(COALESCE(h.hires, 0)) OVER (ORDER BY q.quarter_start ROWS UNBOUNDED PRECEDING) AS running_total,
  CASE 
    WHEN LAG(COALESCE(h.hires, 0)) OVER (ORDER BY q.quarter_start) = 0 THEN NULL
    ELSE ROUND(
      (COALESCE(h.hires, 0) - LAG(COALESCE(h.hires, 0)) OVER (ORDER BY q.quarter_start))
      * 100.0 / LAG(COALESCE(h.hires, 0)) OVER (ORDER BY q.quarter_start), 1
    )
  END AS qoq_growth_pct
FROM quarters q
LEFT JOIN hiring h ON q.quarter_start = h.hire_quarter
ORDER BY q.quarter_start;
```

---

## Example 6: Top Performers by Department

### Business Question
"Find the top 3 performers in each department based on a composite score: 60% salary percentile + 40% tenure percentile."

### Step 1: Calculate Percentiles
```sql
WITH percentiles AS (
  SELECT 
    e.employee_id,
    e.first_name || ' ' || e.last_name AS name,
    d.department_name,
    e.salary,
    e.hire_date,
    -- Salary percentile within department
    PERCENT_RANK() OVER (PARTITION BY e.department_id ORDER BY e.salary) AS sal_pctile,
    -- Tenure percentile within department
    PERCENT_RANK() OVER (PARTITION BY e.department_id ORDER BY e.hire_date) AS tenure_pctile
  FROM employees e
  JOIN departments d ON e.department_id = d.department_id
),
scored AS (
  SELECT 
    *,
    -- Composite: 60% salary percentile (higher = better) + 40% tenure percentile (older = better)
    -- Tenure: older hire_date = lower percentile, so use (1 - tenure_pctile)
    (0.6 * sal_pctile + 0.4 * (1 - tenure_pctile)) * 100 AS composite_score
  FROM percentiles
)
SELECT 
  department_name,
  name,
  salary,
  ROUND(sal_pctile * 100, 1) AS salary_percentile,
  ROUND((1 - tenure_pctile) * 100, 1) AS tenure_percentile,
  ROUND(composite_score, 1) AS composite_score
FROM (
  SELECT 
    *,
    ROW_NUMBER() OVER (PARTITION BY department_name ORDER BY composite_score DESC) AS rn
  FROM scored
)
WHERE rn <= 3
ORDER BY department_name, composite_score DESC;
```

---

## Example 7: Data Quality Checks

### Business Question
"Identify data quality issues: employees with future hire dates, negative salaries, missing departments, duplicate emails."

### Step 1: Comprehensive Quality Query
```sql
WITH issues AS (
  SELECT 'FUTURE_HIRE' AS issue_type, 
         employee_id, 
         first_name || ' ' || last_name AS name,
         'hire_date > SYSDATE' AS description,
         TO_CHAR(hire_date, 'YYYY-MM-DD') AS value
  FROM employees WHERE hire_date > SYSDATE
  
  UNION ALL
  SELECT 'NEGATIVE_SALARY', employee_id, first_name || ' ' || last_name,
         'salary < 0', TO_CHAR(salary)
  FROM employees WHERE salary < 0
  
  UNION ALL
  SELECT 'MISSING_DEPT', employee_id, first_name || ' ' || last_name,
         'department_id IS NULL', 'NULL'
  FROM employees WHERE department_id IS NULL
  
  UNION ALL
  SELECT 'DUPLICATE_EMAIL', employee_id, first_name || ' ' || last_name,
         'email appears ' || cnt || ' times', email
  FROM (
    SELECT email, COUNT(*) cnt FROM employees 
    WHERE email IS NOT NULL GROUP BY email HAVING COUNT(*) > 1
  ) d
  JOIN employees e ON e.email = d.email
  
  UNION ALL
  SELECT 'ORPHAN_DEPT', d.department_id, d.department_name,
         'no employees', '0'
  FROM departments d
  LEFT JOIN employees e ON d.department_id = e.department_id
  WHERE e.employee_id IS NULL
)
SELECT * FROM issues ORDER BY issue_type, employee_id;
```

---

## Example 8: Salary Compression Analysis

### Business Question
"Detect salary compression: cases where a manager earns less than or close to their direct reports."

### Step 1: Manager vs Report Comparison
```sql
WITH mgr_comparison AS (
  SELECT 
    m.employee_id AS mgr_id,
    m.first_name || ' ' || m.last_name AS mgr_name,
    m.salary AS mgr_salary,
    e.employee_id AS emp_id,
    e.first_name || ' ' || e.last_name AS emp_name,
    e.salary AS emp_salary,
    e.salary - m.salary AS difference,
    ROUND((e.salary - m.salary) / m.salary * 100, 1) AS pct_diff
  FROM employees m
  JOIN employees e ON m.employee_id = e.manager_id
)
SELECT 
  mgr_name,
  mgr_salary,
  emp_name,
  emp_salary,
  difference,
  pct_diff,
  CASE 
    WHEN difference > 0 THEN 'Report earns MORE'
    WHEN difference > -5000 THEN 'COMPRESSION RISK'
    ELSE 'Normal'
  END AS status
FROM mgr_comparison
WHERE difference > -10000  -- Within $10K or report earns more
ORDER BY difference DESC;
```

### Step 2: Department-Level Summary
```sql
WITH mgr_comparison AS (...)
SELECT 
  d.department_name,
  COUNT(*) AS compression_cases,
  ROUND(AVG(pct_diff), 1) AS avg_pct_diff,
  MAX(pct_diff) AS max_pct_diff
FROM mgr_comparison mc
JOIN employees m ON mc.mgr_id = m.employee_id
JOIN departments d ON m.department_id = d.department_id
WHERE mc.difference > -5000
GROUP BY d.department_name
HAVING COUNT(*) > 0
ORDER BY compression_cases DESC;
```

---

## Example 9: Cross-Dialect Quick Reference

| Feature | Oracle | PostgreSQL | MySQL | SQL Server |
|---------|--------|------------|-------|------------|
| Current date | `SYSDATE` | `CURRENT_DATE` | `CURDATE()` | `GETDATE()` |
| Date - N days | `SYSDATE - 30` | `CURRENT_DATE - INTERVAL '30 days'` | `DATE_SUB(CURDATE(), INTERVAL 30 DAY)` | `DATEADD(day, -30, GETDATE())` |
| Months between | `MONTHS_BETWEEN(d1, d2)` | `EXTRACT(epoch FROM (d1-d2))/2592000` | `TIMESTAMPDIFF(MONTH, d2, d1)` | `DATEDIFF(month, d2, d1)` |
| String concat | `a \|\| b` | `a \|\| b` | `CONCAT(a, b)` | `a + b` |
| Null coalesce | `NVL(a, b)` / `COALESCE` | `COALESCE(a, b)` | `IFNULL(a, b)` / `COALESCE` | `ISNULL(a, b)` / `COALESCE` |
| Top N | `FETCH FIRST N ROWS` | `LIMIT N` / `FETCH FIRST N ROWS` | `LIMIT N` | `TOP N` / `OFFSET 0 ROWS FETCH NEXT N ROWS` |
| Median | `PERCENTILE_CONT(0.5)` | `PERCENTILE_CONT(0.5)` | Not built-in | `PERCENTILE_CONT(0.5)` |
| Recursive query | `CONNECT BY` | `WITH RECURSIVE` | `WITH RECURSIVE` (8.0+) | `WITH RECURSIVE` |

---

## Performance Checklist

| ✅ | Optimization |
|----|--------------|
|  | Index on filtered columns (`hire_date`, `salary`, `department_id`) |
|  | Composite indexes for join + filter (`department_id, hire_date`) |
|  | Partition large tables by date (`hire_date`, `order_date`) |
|  | Use `/*+ MATERIALIZE */` for reused CTEs |
|  | Prefer `NOT EXISTS` over `NOT IN` (NULL-safe) |
|  | Use window functions instead of self-joins |
|  | Avoid functions on indexed columns in WHERE (`TRUNC(hire_date)`) |
|  | Gather statistics: `DBMS_STATS.GATHER_TABLE_STATS` |
|  | Use bind variables, not literals |
|  | Monitor `V$SQL_PLAN` for plan changes |

---

## Further Practice

1. **LeetCode 185** — Department Top Three Salaries
2. **LeetCode 181** — Employees Earning More Than Managers  
3. **LeetCode 177** — Nth Highest Salary
4. **LeetCode 176** — Second Highest Salary
5. **LeetCode 196** — Delete Duplicate Emails
6. **LeetCode 1285** — Find Start and End of Continuous Ranges
7. **LeetCode 603** — Consecutive Available Seats
8. **LeetCode 1412** — Find the Quiet Students