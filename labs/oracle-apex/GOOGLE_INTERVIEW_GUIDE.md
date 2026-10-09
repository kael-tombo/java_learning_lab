# Google Interview Guide — Oracle APEX Academy

## Interview Process for APEX/Database Roles

### Rounds and Timeline

The Google interview process for database engineer and data analyst roles typically spans 4-8 weeks.

- **Recruiter Screen (30 min)**: Introductory call covering background, APEX experience level, and database familiarity. The recruiter assesses whether your profile aligns with available roles in Google's database engineering or data platform teams.

- **Phone Technical Screen (45 min)**: Google Hangouts session with a software engineer covering SQL, data structures, and basic algorithms. You'll write SQL queries in a shared Google Doc. No syntax highlighting or auto-complete.

- **Virtual Onsite (4-5 rounds)**: Coding round (algorithms/data structures), SQL/data analysis round (complex queries, data modeling), systems design round (scalable data architectures), and googleyness/behavioral round. Each round is 45-60 minutes.

- **Timeline**: 4 to 8 weeks. Google's process is methodical and thorough. There may be waiting periods between rounds for feedback and calibration.

### APEX-Specific Expectations

Google does not directly interview for "APEX developer" roles. Instead, they interview for database engineers, data analysts, and application developers who happen to use low-code tools. Your APEX experience must be framed as proof of your ability to build scalable, data-driven applications.

Google values clean, maintainable code, algorithmic thinking, and data processing at scale. When discussing APEX projects, emphasize the SQL and PL/SQL complexity, the data modeling decisions, and how you handled performance at scale. Minimize discussion of drag-and-drop page building.

### Key Areas Assessed

- **SQL Mastery**: Complex joins, window functions, recursive CTEs, performance at Google scale. Google's SQL questions are notoriously thorough.

- **Data Structures**: Trees, graphs, hash maps applied to data problems. Expect to use algorithms in the context of data processing and analysis.

- **System Design**: Scalable database architectures, distributed systems, data pipelines, and how to handle petabytes of data.

- **Problem Solving**: Analytical approach to ambiguous data problems. Google interviewers often present underspecified problems and expect you to ask clarifying questions.

- **Googleyness**: Leadership, humility, collaboration, intellectual curiosity, and comfort with ambiguity.

---

## Top SQL/PLSQL Problems by Lab

### Lab 01: Getting Started with APEX

#### Problem: Find Employees Who Earn More Than Their Managers (LC SQL 181)

- **Difficulty/Frequency**: Easy / Very High

- **SQL Problem Statement**: Write a SQL query to find employees who earn more than their direct managers. Return the employee's name and salary, along with their manager's name and salary.

- **Interview Walkthrough**: This classic self-join problem tests your ability to work with hierarchical data in a single table. Join the EMP table to itself where one instance represents employees (e) and the other represents managers (m). The join condition is e.mgr = m.empno. Compare salaries in the WHERE clause. Google loves this problem because it mirrors real-world data integrity checks — detecting salary anomalies in organizational data.

- **SQL Solution**:

```sql
SELECT e.ename AS employee_name,
       e.sal AS employee_salary,
       m.ename AS manager_name,
       m.sal AS manager_salary
FROM emp e
JOIN emp m
    ON e.mgr = m.empno
WHERE e.sal > m.sal
ORDER BY e.sal DESC;
```

- **Oracle-Specific Syntax**: Self-joins work identically in Oracle and standard SQL. Oracle's implicit join syntax (comma-separated FROM with WHERE condition) is also valid but ANSI JOIN syntax is preferred at Google for readability and clarity.

- **What Google Evaluates**: Clarity of logic, correct handling of the self-join, understanding of NULL (employees without managers, who are excluded by the INNER JOIN), and ability to write readable code. Google interviewers will probe edge cases: what if an employee has no manager (CEO)? What if there are multiple management layers?

- **Follow-ups**: 1) Modify to include the CEO (who has no manager) using a LEFT JOIN. 2) Find the largest salary discrepancy between employee and manager. 3) Find all indirect subordinates who earn more than any manager 3+ levels above.

#### Problem: Department Top Three Salaries (LC SQL 185)

- **Difficulty/Frequency**: Hard / High

- **SQL Problem Statement**: Write a SQL query to find employees who earn the top three unique salaries in each department. A department may have fewer than three employees with unique salaries. Return department name, employee name, and salary.

- **Interview Walkthrough**: Use DENSE_RANK() partitioned by department and ordered by salary descending. Filter for rank <= 3. This demonstrates analytic function proficiency, which Google values highly for data analysis roles. Google interviewers will ask about the difference between RANK, DENSE_RANK, and ROW_NUMBER.

- **SQL Solution**:

```sql
SELECT d.dname AS department,
       e.ename AS employee,
       e.sal AS salary
FROM (
    SELECT ename, sal, deptno,
           DENSE_RANK() OVER (
               PARTITION BY deptno
               ORDER BY sal DESC
           ) AS sal_rank
    FROM emp
) e
JOIN dept d
    ON e.deptno = d.deptno
WHERE e.sal_rank <= 3
ORDER BY d.dname, e.sal DESC;
```

- **Oracle-Specific Syntax**: DENSE_RANK() with OVER (PARTITION BY ... ORDER BY ...) is ANSI standard. Oracle has supported analytic functions since Oracle 8i, making them mature and well-optimized. Oracle also supports RANK() (which includes gaps for ties) and ROW_NUMBER() (which assigns unique numbers even with ties).

- **What Google Evaluates**: Understanding of window functions — a must-have for Google data roles. Google expects candidates to explain WHY they chose DENSE_RANK over RANK or ROW_NUMBER. Can you articulate the business implications of ties, gaps, and unique assignments?

- **Follow-ups**: 1) What if you need EXACTLY 3 rows per department (no ties)? Use ROW_NUMBER. 2) Add a department filter dynamically using a bind variable. 3) Rewrite using a correlated subquery for comparison.

---

### Lab 04: Security in APEX

#### Problem: Find Duplicate Emails (LC SQL 182)

- **Difficulty/Frequency**: Easy / Very High

- **SQL Problem Statement**: Write a SQL query to find all duplicate email addresses in a Person table. A person's email is considered a duplicate if it appears more than once. Return the duplicate emails.

- **Interview Walkthrough**: Use GROUP BY with HAVING COUNT(*) > 1. Google considers this a warm-up question but expects thorough discussion about edge cases: data cleaning, case sensitivity, NULL handling, and whitespace trimming.

- **SQL Solution**:

```sql
SELECT LOWER(email) AS duplicate_email,
       COUNT(*) AS occurrence_count
FROM person
WHERE email IS NOT NULL
GROUP BY LOWER(email)
HAVING COUNT(*) > 1
ORDER BY occurrence_count DESC;
```

- **Oracle-Specific Syntax**: LOWER() is standard SQL. Oracle's NVL or COALESCE can handle NULLs. In Oracle, string comparison is case-sensitive by default unless NLS_COMP is set to LINGUISTIC. Oracle's TRIM function can remove leading/trailing whitespace.

- **What Google Evaluates**: Fundamental SQL skills and edge-case thinking. Google expects you to consider NULLs, case sensitivity, and whitespace without being prompted. They also probe on how to handle millions of emails efficiently and what index strategy supports the query.

- **Follow-ups**: 1) Find exact duplicates (case-sensitive). 2) Find near-duplicates (typos, same domain different prefix). 3) Write a query that marks duplicates for deletion, keeping only the earliest entry per email.

#### Problem: Calculate Total Distinct Login Time (LC SQL 5784)

- **Difficulty/Frequency**: Medium / High

- **SQL Problem Statement**: Given a table user_sessions(user_id, login_ts, logout_ts) with possible overlapping sessions, calculate the total distinct time (in minutes) each user was logged in during a day. Sessions may overlap or have gaps.

- **Interview Walkthrough**: This is a classic interval merging problem that Google loves. Use the gap-and-islands approach (Tabibitosan method) with LAG and SUM analytic functions. The key insight is to merge overlapping intervals by finding where a new island begins (when login_ts > previous max logout_ts) and then aggregating within each island.

- **SQL Solution**:

```sql
WITH session_islands AS (
    SELECT user_id, login_ts, logout_ts,
           SUM(CASE
               WHEN prev_max_logout IS NULL
                 OR login_ts >= prev_max_logout
               THEN 1 ELSE 0
           END) OVER (
               PARTITION BY user_id
               ORDER BY login_ts
           ) AS island_id
    FROM (
        SELECT user_id, login_ts, logout_ts,
               MAX(logout_ts) OVER (
                   PARTITION BY user_id
                   ORDER BY login_ts
                   ROWS BETWEEN UNBOUNDED PRECEDING
                            AND 1 PRECEDING
               ) AS prev_max_logout
        FROM user_sessions
    )
)
SELECT user_id,
       SUM(
           (MAX(logout_ts) - MIN(login_ts)) * 24 * 60
       ) AS total_minutes
FROM session_islands
GROUP BY user_id, island_id;
```

- **Oracle-Specific Syntax**: The timestamp subtraction (date1 - date2) returns days in Oracle. Multiply by 24 * 60 to get minutes. Oracle's ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING creates a running maximum of previous logout times.

- **What Google Evaluates**: Ability to solve complex interval merging using window functions. Understanding of gaps-and-islands patterns. Google interviewers appreciate candidates who can think in terms of set operations and analytic functions rather than procedural loops.

- **Follow-ups**: 1) Solve using a recursive CTE instead of window functions. 2) Handle sessions that span midnight. 3) Find peak concurrency (maximum simultaneous users at any point).

---

### Lab 05: Interactive Reports

#### Problem: Rank Employee Salaries with Tie-Breaking (LC SQL 178)

- **Difficulty/Frequency**: Medium / High

- **SQL Problem Statement**: Write a query to rank employees within each department by salary descending. If two employees have the same salary, rank them by hire_date ascending (earlier hire first). Show employee name, salary, hire_date, department, and rank.

- **Interview Walkthrough**: This tests window functions with ORDER BY using multiple columns. The ordering logic within the OVER clause determines the ranking behavior. Google expects candidates to choose the correct ranking function based on the tie-breaking requirement.

- **SQL Solution**:

```sql
SELECT d.dname AS department,
       e.ename AS employee,
       e.sal AS salary,
       e.hiredate,
       RANK() OVER (
           PARTITION BY e.deptno
           ORDER BY e.sal DESC, e.hiredate ASC
       ) AS emp_rank
FROM emp e
JOIN dept d
    ON e.deptno = d.deptno
ORDER BY d.dname, emp_rank;
```

- **Oracle-Specific Syntax**: RANK() includes gaps for ties. The ORDER BY within OVER supports multiple columns. Oracle also supports NULLS FIRST/LAST in the OVER clause to control NULL positioning in the ranking.

- **What Google Evaluates**: Precision in ranking logic — understanding the subtle differences between RANK, DENSE_RANK, and ROW_NUMBER. Google expects you to explain the trade-offs and choose based on business requirements.

- **Follow-ups**: 1) Show the difference between RANK and DENSE_RANK with example data. 2) Add a running total of salaries within each department. 3) Include a moving average of salary over 3 employees ordered by hire_date.

#### Problem: Report Cumulative Sum with Reset Condition (LC SQL 1308)

- **Difficulty/Frequency**: Medium / High

- **SQL Problem Statement**: Calculate a running total of daily sales amounts where the running total resets at the start of each month. Show order_date, daily_total, and running_total columns.

- **Interview Walkthrough**: Use SUM() with OVER (PARTITION BY year, month ORDER BY day ROWS UNBOUNDED PRECEDING). The PARTITION BY creates the monthly reset boundary.

- **SQL Solution**:

```sql
WITH daily_sales AS (
    SELECT TRUNC(order_date) AS order_day,
           SUM(order_amount) AS daily_total
    FROM orders
    GROUP BY TRUNC(order_date)
)
SELECT order_day,
       daily_total,
       SUM(daily_total) OVER (
           PARTITION BY EXTRACT(YEAR FROM order_day),
                        EXTRACT(MONTH FROM order_day)
           ORDER BY order_day
           ROWS UNBOUNDED PRECEDING
       ) AS running_total
FROM daily_sales
ORDER BY order_day;
```

- **Oracle-Specific Syntax**: TRUNC(date) removes the time component. EXTRACT(YEAR/MONTH FROM date) extracts date parts. Oracle also supports TO_CHAR(date, 'YYYYMM') as an alternative partitioning key.

- **What Google Evaluates**: Understanding of running totals with reset conditions. This is essential for financial reporting and time-series analysis.

- **Follow-ups**: 1) Add a rolling 7-day average alongside the running total. 2) Handle months with zero sales. 3) Aggregate by week instead of day with the same monthly reset.

---

### Lab 08: Performance Tuning

#### Problem: Human Traffic of Stadium (LC SQL 601)

- **Difficulty/Frequency**: Hard / High

- **SQL Problem Statement**: Write a SQL query to find rows where at least 3 consecutive rows have a people value greater than or equal to 100. Table stadium has columns id, visit_date, and people. Return the id, visit_date, and people for all consecutive groups of 3+, ordered by visit_date.

- **Interview Walkthrough**: This is the quintessential gaps-and-islands problem. Use ROW_NUMBER() to establish ordering, then subtract row number from id to create island groups. Filter groups with COUNT >= 3. Google asks this to test advanced SQL pattern recognition.

- **SQL Solution**:

```sql
WITH numbered AS (
    SELECT id, visit_date, people,
           id - ROW_NUMBER() OVER (ORDER BY id) AS grp
    FROM stadium
    WHERE people >= 100
),
grouped AS (
    SELECT id, visit_date, people, grp,
           COUNT(*) OVER (PARTITION BY grp) AS grp_size
    FROM numbered
)
SELECT id, visit_date, people
FROM grouped
WHERE grp_size >= 3
ORDER BY visit_date;
```

- **Oracle-Specific Syntax**: ROW_NUMBER() is ANSI standard but Oracle was an early adopter. Oracle's CONNECT BY can also solve this but window functions are more performant and readable.

- **What Google Evaluates**: Pattern recognition for islands, proper understanding of ROW_NUMBER mechanics, and ability to debug off-by-one errors. Google interviewers will modify the condition (>= 100 vs > 100) and ask how the query changes.

- **Follow-ups**: 1) Find consecutive visit_dates (handle gaps in ID sequence). 2) Find 3+ consecutive rows where people is in the top 10% of all values. 3) Optimize for a table with 100M+ rows using materialized views and indexes.

#### Problem: Find Median Salary per Department (Google-specific)

- **Difficulty/Frequency**: Hard / High

- **SQL Problem Statement**: Find the median salary for each department. If a department has an even number of employees, take the average of the two middle salaries.

- **Interview Walkthrough**: Google asks median problems frequently. Use PERCENTILE_CONT (Oracle's inverse percentile function) for a clean solution. Alternatively, use ROW_NUMBER with COUNT to find middle values.

- **SQL Solution**:

```sql
SELECT d.dname AS department,
       ROUND(
           PERCENTILE_CONT(0.5) WITHIN GROUP (
               ORDER BY e.sal
           ), 2
       ) AS median_salary
FROM dept d
LEFT JOIN emp e
    ON d.deptno = e.deptno
GROUP BY d.dname
ORDER BY median_salary DESC;

-- Alternative approach using ROW_NUMBER
SELECT department, ROUND(AVG(sal), 2) AS median_salary
FROM (
    SELECT d.dname AS department, e.sal,
           ROW_NUMBER() OVER (
               PARTITION BY d.deptno ORDER BY e.sal
           ) AS rn_asc,
           ROW_NUMBER() OVER (
               PARTITION BY d.deptno ORDER BY e.sal DESC
           ) AS rn_desc
    FROM dept d
    LEFT JOIN emp e ON d.deptno = e.deptno
)
WHERE rn_asc = rn_desc
   OR rn_asc + 1 = rn_desc
   OR rn_asc = rn_desc + 1
GROUP BY department;
```

- **Oracle-Specific Syntax**: PERCENTILE_CONT is an Oracle inverse distribution function (also available in SQL Server). It computes the median by interpolating between values. The WITHIN GROUP clause defines the sort order for the calculation.

- **What Google Evaluates**: Understanding of statistical functions in SQL and ability to implement complex calculations without external tools. Google values engineers who can push analytical computation into the database.

- **Follow-ups**: 1) Calculate percentiles (25th, 75th, 90th) in addition to median. 2) Use PERCENTILE_DISC vs PERCENTILE_CONT — explain the difference. 3) Create an APEX dashboard showing salary distribution statistics by department.

---

## APEX-Specific Deep Dive Questions

1. **How would you structure an APEX app to handle large-scale data processing (millions of rows)?** Google wants to see understanding of pagination, lazy loading, materialized views, partitioning, and when to push processing to the database versus the application layer. Discuss the trade-offs between server-side and client-side processing.

2. **Explain how APEX interactive reports compare to Google's internal reporting tools**. Discuss filtering, aggregation, column selection, and export capabilities. How would you customize an interactive report to meet Google's data exploration requirements?

3. **How do you implement row-level security in APEX at scale?** Discuss VPD policies, APEX authorization schemes, context-based security, and how to maintain performance with row-level access control on tables with hundreds of millions of rows.

4. **Describe how you would use APEX to build a data dashboard that refreshes in near-real-time**. Cover AJAX callbacks, dynamic actions, PL/SQL scheduled jobs, and materialized view refreshes. How would you handle 100+ concurrent users all requesting fresh data?

---

## System Design Questions

1. **Design a database schema for a Google Analytics dashboard built in APEX**. Cover event tracking (page views, clicks, conversions), session management, user dimensions (location, device, browser), and aggregation tables (hourly, daily, monthly). Discuss how to model clickstream data for efficient querying in APEX interactive reports. How would you handle 1 billion events per day? What partitioning strategy would you use?

2. **Design a distributed APEX application across multiple geographic regions with data replication**. Discuss Oracle GoldenGate for real-time replication, active-active vs active-passive configurations, conflict resolution strategies for concurrent updates, and how APEX session state behaves in multi-region deployments. How do you ensure cache consistency across regions?

3. **Design a logging and monitoring system for APEX applications serving 10,000+ users**. Discuss what to log (page views, errors, performance metrics), how to aggregate logs (database tables vs external systems), alerting thresholds for common issues, and how to visualize system health in an APEX dashboard. Discuss integration with Google Cloud Operations (Stackdriver) if applicable.

---

## Behavioral Questions

1. **Tell me about a time you solved a complex data problem with limited information.**

   - **S**ituation: A core APEX interactive report was returning inconsistent results across different environments. The error was intermittent and no error messages were being logged.

   - **T**ask: Identify the root cause and implement a permanent fix without clear error indicators.

   - **A**ction: Systematically compared SQL execution plans across environments using DBMS_XPLAN. Discovered a session-level NLS setting (NLS_DATE_FORMAT) causing date parsing differences between environments. The inconsistent results were due to implicit date conversions. Created a standardized initialization procedure (APEX_INIT_USER_DATA) that sets consistent session parameters for all users.

   - **R**esult: Reports became consistent across all environments. The fix prevented 20+ potential future inconsistencies. Documented the issue in the team knowledge base.

   - **S**kills: Analytical troubleshooting, SQL internals, systematic debugging, documentation.

2. **Describe a time you influenced a team decision through data analysis.**

   - **S**ituation: The team was debating whether to migrate from Oracle Forms to APEX. Half the team wanted to stay with Forms, citing stability concerns.

   - **T**ask: Provide data-driven evidence to support or reject the migration decision.

   - **A**ction: Built a proof-of-concept APEX application replicating the most complex Forms functionality. Measured development time, runtime performance, and gathered user feedback through structured testing sessions. Presented a cost-benefit analysis with concrete metrics: development time reduced by 60%, maintenance costs projected to decrease by 45%, and user satisfaction improved.

   - **R**esult: Management approved a phased migration based on the data. The first phase completed 3 months ahead of schedule. The methodology became the template for future technology decisions.

   - **S**kills: Data-driven decision making, POC development, stakeholder communication.

3. **Tell me about a time you failed and what you learned.**

   - **S**ituation: Deployed an APEX application without sufficient load testing. Under 200 concurrent users, the application became unresponsive and timed out.

   - **T**ask: Rescue the production deployment and prevent recurrence.

   - **A**ction: Immediately scaled database resources (increased SGA/PGA) and optimized the 3 most expensive queries (adding indexes, rewriting joins). Built a comprehensive load testing framework using JMeter specifically configured for APEX applications. Established performance benchmarks and gate criteria for future deployments.

   - **R**esult: The optimized application handled 2000+ concurrent users successfully. The load testing framework became the team standard for all APEX deployments.

   - **S**kills: Accountability, rapid problem solving, performance optimization, process improvement.

4. **Describe a time you had to make a decision with incomplete data.**

   - **S**ituation: Needed to choose between two APEX architectures (multi-page wizard vs single-page modal dialogs) for a complex workflow application. Requirements were unclear and stakeholders had conflicting preferences.

   - **T**ask: Make an architectural decision that would not block the team.

   - **A**ction: Built throwaway prototypes of both approaches (2 days each). Tested with 5 stakeholders and observed their interactions. Chose modals based on user preference data, but designed the page structure to be modular so conversion to multi-page would be straightforward.

   - **R**esult: Users strongly preferred modals. The modular design allowed easy migration when requirements changed 6 months later (the workflow needed to support mobile devices, which multi-page handled better).

   - **S**kills: Prototyping, user research, decision-making under uncertainty, architecture flexibility.

5. **Tell me about a time you collaborated across teams to deliver a project.**

   - **S**ituation: An APEX application required data from 3 different source systems owned by separate teams (CRM, ERP, and HR systems).

   - **T**ask: Coordinate the integration without direct authority over the other teams.

   - **A**ction: Established a cross-team working group with representatives from each system team. Created shared API contracts with clear SLAs. Set up automated data validation between source and target to catch issues early. Maintained a shared project timeline with clear dependencies.

   - **R**esult: Integration completed on schedule with zero data discrepancies. The cross-team collaboration model was adopted for other cross-functional projects.

   - **S**kills: Cross-functional leadership, stakeholder management, integration design, collaboration.

---

## Study Plan

### Priority Labs by Interview Impact

| Priority | Lab | Why It Matters for Google Interviews |
|----------|-----|--------------------------------------|
| P0 | Lab 08: Performance | Google's scale demands performance expertise |
| P0 | Lab 05: Interactive Reports | Data exploration is core to Google engineering |
| P1 | Lab 01: Getting Started | SQL fundamentals tested heavily in coding screens |
| P1 | Lab 04: Security | Google's security bar is extremely high |
| P2 | Lab 06: RESTful Services | REST APIs are central to Google's infrastructure |
| P2 | Lab 03: Advanced Components | Shows depth of APEX knowledge |
| P3 | Lab 02: Page Designer | Lower priority for Google-style interviews |
| P3 | Lab 07: Migration | Least relevant unless your background matches |

---

## Tips

### Company-Specific APEX Interview Strategies

- **Frame APEX as a Data Tool**: Google does not hire for "APEX developers." Frame your APEX experience as database application development and data platform engineering. Emphasize SQL, PL/SQL, and data modeling — not page designer skills.

- **Scale is Everything**: Every answer should demonstrate awareness of scale. Google operates at planetary scale. When you describe an APEX solution, explain how it would handle 100x more data, 100x more users, and 100x more transactions.

- **Be Ready for Coding in SQL**: Google's SQL interviews are conducted in a simple text editor. Practice writing complex SQL without auto-complete. Know window functions, recursive CTEs, self-joins, and pivot/unpivot operations cold.

- **Data Structures and Algorithms**: Even for database-focused roles, Google expects basic DSA knowledge. Understand Big O notation, hash tables, binary trees, and basic graph algorithms. Be prepared to apply these in the context of data processing.

- **Googleyness**: Demonstrate humility ("I don't know but here's how I'd find out"), collaboration (credit others explicitly), and intellectual curiosity (discuss what you read or explore beyond work).

- **Know the Cloud Story**: Google Cloud's database offerings (Cloud SQL, Spanner, BigQuery) may overlap with Oracle. Be ready to discuss how you'd build APEX-like applications on Google Cloud infrastructure.

- **Use Metrics**: Google loves data. In behavioral answers, use specific metrics: "reduced query time by 85%," "handled 50K queries per second," "saved 200 engineering hours per month."

- **Question the Question**: Google interviewers expect clarifying questions before diving into a solution. "What scale are we designing for? What are the consistency requirements? Is this read-heavy or write-heavy?"

- **Prepare for Ambiguity**: Google problems are often underspecified on purpose. Practice solving problems where you must define the scope and assumptions before writing code.

- **Show Leadership Without Authority**: Google values influence over hierarchy. In behavioral stories, highlight moments where you led by expertise and persuasion rather than title.

### Lab 03: Advanced Components

#### Problem: Tree Structure Query with Recursive CTE (LC SQL 608 variant)

- **Difficulty/Frequency**: Medium / High

- **SQL Problem Statement**: Display organizational hierarchy showing each employee, their level, and their root manager using a recursive CTE. Show the path from root to each employee.

- **Interview Walkthrough**: Use Oracle's recursive CTE (WITH RECURSIVE) to traverse the hierarchy. Google values understanding of both CONNECT BY and recursive CTE approaches. The recursive CTE is ANSI standard and portable across databases.

- **SQL Solution**:

`sql
WITH RECURSIVE org_hierarchy AS (
    SELECT empno, ename, mgr, 0 AS level,
           CAST(ename AS VARCHAR2(500)) AS path
    FROM emp
    WHERE mgr IS NULL
    UNION ALL
    SELECT e.empno, e.ename, e.mgr,
           oh.level + 1,
           oh.path || ' -> ' || e.ename
    FROM emp e
    JOIN org_hierarchy oh ON e.mgr = oh.empno
)
SELECT LEVEL AS hier_level,
       LPAD(' ', 2 * level) || ename AS indented_name,
       path
FROM org_hierarchy
ORDER BY path;
`

- **Oracle-Specific Syntax**: Oracle supports both CONNECT BY and recursive CTE syntax. The RECURSIVE keyword is optional in Oracle's WITH clause for recursive CTEs. CAST ensures the path string has sufficient length.

- **What Google Evaluates**: Understanding of both hierarchical query approaches. Google values ANSI-standard recursive CTEs for portability.

- **Follow-ups**: 1) Find all employees at level 3 or below. 2) Calculate the depth of each branch. 3) Find the longest reporting chain.

#### Problem: Generate Date Series for Missing Data (Google-specific)

- **Difficulty/Frequency**: Medium / High

- **SQL Problem Statement**: Generate a continuous date series for the year 2023 with daily sales data. For dates with no sales, show zero. Return date, day_of_week, sales_amount, and whether it's a weekend.

- **Interview Walkthrough**: Use Oracle's CONNECT BY to generate a date series, then LEFT JOIN to actual sales data. This is a common data preparation pattern for time-series analysis.

- **SQL Solution**:

`sql
WITH date_series AS (
    SELECT DATE '2023-01-01' + LEVEL - 1 AS calendar_date
    FROM dual
    CONNECT BY LEVEL <=
        DATE '2023-12-31' - DATE '2023-01-01' + 1
)
SELECT ds.calendar_date,
       TO_CHAR(ds.calendar_date, 'DAY') AS day_of_week,
       CASE
           WHEN TO_CHAR(ds.calendar_date, 'D')
                IN ('1', '7') THEN 'Weekend'
           ELSE 'Weekday'
       END AS day_type,
       NVL(SUM(s.amount), 0) AS daily_sales
FROM date_series ds
LEFT JOIN sales s
    ON TRUNC(s.sale_date) = ds.calendar_date
   AND EXTRACT(YEAR FROM s.sale_date) = 2023
GROUP BY ds.calendar_date
ORDER BY ds.calendar_date;
`

- **Oracle-Specific Syntax**: CONNECT BY LEVEL for row generation. DATE literal (DATE '2023-01-01'). TO_CHAR with 'DAY' for day name, 'D' for day number. NVL to replace NULL with zero.

- **What Google Evaluates**: Ability to generate and work with complete date series — essential for accurate time-series analysis. Handling missing data properly.

- **Follow-ups**: 1) Generate hourly series instead of daily. 2) Add a 7-day trailing average column. 3) Find the longest streak of zero-sales days.

### Lab 06: RESTful Services

#### Problem: API to Return Employee Hierarchical Data as JSON (Google-specific)

- **Difficulty/Frequency**: Hard / Medium

- **SQL Problem Statement**: Create an ORDS REST endpoint that returns employee organizational data as a nested JSON tree structure showing the full reporting hierarchy.

- **Interview Walkthrough**: Use Oracle's recursive SQL with JSON_OBJECT to build nested JSON. Google values clean API responses.

- **SQL Solution**:

`sql
WITH RECURSIVE org_tree AS (
    SELECT empno, ename, job, mgr,
           CAST('[]' AS VARCHAR2(4000)) AS children
    FROM emp WHERE mgr IS NULL
    UNION ALL
    SELECT e.empno, e.ename, e.job, e.mgr,
           CAST('[]' AS VARCHAR2(4000)) AS children
    FROM emp e
    JOIN org_tree ot ON e.mgr = ot.empno
)
SEARCH DEPTH FIRST BY ename SET ordering
SELECT JSON_OBJECT(
    KEY 'employee_id' VALUE empno,
    KEY 'name' VALUE ename,
    KEY 'job' VALUE job
) AS employee_json
FROM org_tree
ORDER BY ordering;
`

- **Oracle-Specific Syntax**: SEARCH DEPTH FIRST is Oracle's recursive CTE extension for ordering. JSON_OBJECT for JSON generation. The DEPTH FIRST ordering ensures parent-child nesting structure.

- **What Google Evaluates**: Hierarchical data serialization to JSON. Understanding of depth-first vs breadth-first traversal.

- **Follow-ups**: 1) Add a depth parameter to limit tree depth. 2) Include subordinate count. 3) Implement the same using CONNECT BY with SYS_CONNECT_BY_PATH.
