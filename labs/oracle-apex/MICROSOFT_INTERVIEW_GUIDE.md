# Microsoft Interview Guide — Oracle APEX Academy

## Interview Process for APEX/Database Roles

### Rounds and Timeline

The Microsoft interview process for database engineer and application developer roles typically spans 3-5 weeks.

- **Recruiter Screen (30 min)**: Call covering background, APEX experience, and Azure awareness. The recruiter assesses fit for database engineering or low-code platform roles.

- **Technical Screen (45 min)**: Teams call with a senior engineer covering SQL coding, data modeling, and cross-platform experience (Oracle vs SQL Server).

- **Virtual Onsite (4 rounds)**: 2 technical rounds (SQL, PL/SQL, data modeling), 1 system design, 1 behavioral/Azure culture fit. Each round is 45-60 minutes.

- **Timeline**: 3 to 5 weeks from initial screen to offer.

### APEX-Specific Expectations

Microsoft evaluates candidates for database engineer and application developer roles. APEX experience demonstrates rapid application development skills. Microsoft cares deeply about developer experience, tooling, and cloud integration (Azure).

They value candidates who can work across Oracle and Microsoft technologies. Understanding the differences between PL/SQL and T-SQL is highly valued. Microsoft also emphasizes Growth Mindset — a belief that abilities can be developed through dedication and hard work.

### Key Areas Assessed

- **SQL Proficiency**: T-SQL vs PL/SQL differences, performance tuning, complex queries, cross-platform SQL skills.

- **Data Modeling**: Entity-relationship design, normalization vs denormalization trade-offs, star schemas.

- **Cloud Integration**: Azure SQL Database, hybrid cloud architectures, migration from Oracle to Azure.

- **Cross-Platform Skills**: Experience working with both Oracle and SQL Server databases.

- **Growth Mindset**: Learning agility, embracing challenges, receptiveness to feedback.

---

## Top SQL/PLSQL Problems by Lab

### Lab 01: Getting Started with APEX

#### Problem: Combine Two Tables - Employee with Address (LC SQL 175)

- **Difficulty/Frequency**: Easy / Very High

- **SQL Problem Statement**: Write a SQL query to report employee name, city, and state. If an employee does not have an address record, still include them with NULL for city and state.

- **Interview Walkthrough**: This is a straightforward LEFT JOIN. Microsoft uses this as a warm-up but watches for Oracle-specific syntax differences. They want to see that you understand LEFT JOIN versus INNER JOIN and can handle NULLs.

- **SQL Solution**:

```sql
SELECT e.ename AS employee_name,
       e.job,
       a.city,
       a.state
FROM emp e
LEFT JOIN emp_address a
    ON e.empno = a.empno
ORDER BY e.ename;
```

- **Oracle-Specific Syntax**: Oracle supports both ANSI LEFT JOIN and the Oracle-specific (+) operator: FROM emp e, emp_address a WHERE e.empno = a.empno(+). Microsoft interviewers may ask about the (+) syntax and how it differs from ANSI JOIN syntax. NVL(a.city, 'Unknown') replaces NULLs.

- **What Microsoft Evaluates**: Fundamentals of outer joins and NULL handling. Microsoft places high value on portability between Oracle and SQL Server.

- **Follow-ups**: 1) Write using Oracle's (+) operator. 2) How would you write this in T-SQL? 3) Add a filter for 'WA' state employees.

#### Problem: Rising Temperature (LC SQL 197)

- **Difficulty/Frequency**: Medium / High

- **SQL Problem Statement**: Find all dates where the temperature was higher than the previous date's temperature. Return id and recordDate.

- **Interview Walkthrough**: Use LAG() window function for a clean solution. Alternatively, use a self-join on date = previous date using Oracle's date arithmetic.

- **SQL Solution**:

```sql
WITH temp_comparison AS (
    SELECT id, recordDate, temperature,
           LAG(temperature) OVER (ORDER BY recordDate) AS prev_temp,
           LAG(recordDate) OVER (ORDER BY recordDate) AS prev_date
    FROM weather
)
SELECT id, recordDate
FROM temp_comparison
WHERE temperature > prev_temp
  AND recordDate = prev_date + 1;
```

- **Oracle-Specific Syntax**: Oracle date arithmetic: date + 1 adds one day. TRUNC() removes time. LAG() is ANSI standard. Oracle's INTERVAL syntax: recordDate = prev_date + INTERVAL '1' DAY.

- **What Microsoft Evaluates**: Awareness of date handling differences. In Oracle, date + 1 = next day. In SQL Server, DATEADD(day, 1, date).

- **Follow-ups**: 1) Handle missing dates (gaps). 2) Find days exceeding both previous AND next day. 3) Use FIRST_VALUE for 3-day comparison.

---

### Lab 04: Security in APEX

#### Problem: Delete Duplicate Rows Keeping One (LC SQL 196)

- **Difficulty/Frequency**: Easy / Very High

- **SQL Problem Statement**: Delete duplicate rows from a Person table where duplicates have the same email. Keep only the record with the smallest ID.

- **Interview Walkthrough**: Use ROW_NUMBER for deduplication. Microsoft tests understanding of Oracle's DELETE with subquery syntax and transaction control.

- **SQL Solution**:

```sql
DELETE FROM person
WHERE id IN (
    SELECT id
    FROM (
        SELECT id, email,
               ROW_NUMBER() OVER (
                   PARTITION BY email ORDER BY id
               ) AS rn
        FROM person
    )
    WHERE rn > 1
);

-- Oracle alternative using ROWID
DELETE FROM person p1
WHERE EXISTS (
    SELECT 1 FROM person p2
    WHERE p2.email = p1.email
      AND p2.id < p1.id
);
```

- **Oracle-Specific Syntax**: ROWID is a pseudo-column unique to Oracle — the physical row address. ROWNUM is Oracle-specific but deprecated for most purposes. Oracle's COMMIT is implicit for DDL but explicit for DML.

- **What Microsoft Evaluates**: Data integrity and deduplication strategy. Microsoft interviewers will ask about transaction control — wrapping DELETE in a transaction and verifying before COMMIT.

- **Follow-ups**: 1) Add a unique constraint to prevent future duplicates. 2) Handle case-insensitive duplicates. 3) Use Oracle's MERGE instead of DELETE.

#### Problem: Customers Who Never Order (LC SQL 183)

- **Difficulty/Frequency**: Easy / Very High

- **SQL Problem Statement**: Find all customers who have never placed an order.

- **Interview Walkthrough**: Use LEFT JOIN with IS NULL filter or NOT EXISTS. Microsoft tests both approaches and probes on performance differences.

- **SQL Solution**:

```sql
-- NOT EXISTS (often more efficient)
SELECT c.id, c.name
FROM customers c
WHERE NOT EXISTS (
    SELECT 1 FROM orders o
    WHERE o.customer_id = c.id
);

-- LEFT JOIN approach
SELECT c.id, c.name
FROM customers c
LEFT JOIN orders o
    ON c.id = o.customer_id
WHERE o.customer_id IS NULL;
```

- **Oracle-Specific Syntax**: Oracle's NOT EXISTS is well-optimized. The MINUS operator provides another approach. Oracle's ANTI-JOIN transformation optimizes NOT EXISTS.

- **What Microsoft Evaluates**: Query optimization knowledge. Understanding when NOT EXISTS outperforms LEFT JOIN.

- **Follow-ups**: 1) Explain when NOT EXISTS beats LEFT JOIN. 2) Use Oracle's (+) outer join syntax. 3) Find customers with exactly one order.

---

### Lab 05: Interactive Reports

#### Problem: Exchange Seats - Swap Adjacent Rows (LC SQL 626)

- **Difficulty/Frequency**: Medium / High

- **SQL Problem Statement**: Swap the student name of every two consecutive seats. If the number of students is odd, the last seat remains unchanged.

- **Interview Walkthrough**: Use CASE with LEAD, or a self-join with arithmetic. Tests creative SQL thinking. Microsoft values seeing multiple solution approaches.

- **SQL Solution**:

```sql
SELECT CASE
           WHEN MOD(id, 2) = 1
                AND LEAD(id) OVER (ORDER BY id) IS NOT NULL
               THEN id + 1
           WHEN MOD(id, 2) = 0
               THEN id - 1
           ELSE id
       END AS new_id,
       student
FROM seat
ORDER BY new_id;
```

- **Oracle-Specific Syntax**: MOD() is standard. LEAD() and LAG() are supported in both Oracle and SQL Server. Oracle's DECODE could replace CASE but CASE is more portable.

- **What Microsoft Evaluates**: Analytical thinking and creative SQL. Microsoft values engineers who solve problems from multiple angles.

- **Follow-ups**: 1) Swap in groups of 3 instead of 2. 2) Implement this logic in an APEX interactive report using a CASE expression.

#### Problem: Game Play Analysis - Retention Rate (LC SQL 550)

- **Difficulty/Frequency**: Medium / High

- **SQL Problem Statement**: Find first-day retention rate — fraction of players who logged in the day after their first login.

- **Interview Walkthrough**: Use MIN to find first login per player, then JOIN to find next-day logins. Microsoft values this for understanding user engagement metrics.

- **SQL Solution**:

```sql
WITH first_login AS (
    SELECT player_id,
           MIN(event_date) AS first_date
    FROM activity
    GROUP BY player_id
),
consecutive_logins AS (
    SELECT DISTINCT a.player_id
    FROM activity a
    JOIN first_login f
        ON a.player_id = f.player_id
    WHERE a.event_date = f.first_date + 1
)
SELECT ROUND(
    COUNT(DISTINCT c.player_id)
    / COUNT(DISTINCT f.player_id), 2
) AS day1_retention
FROM first_login f
LEFT JOIN consecutive_logins c
    ON f.player_id = c.player_id;
```

- **Oracle-Specific Syntax**: Oracle's date arithmetic (date + 1) differs from SQL Server's DATEADD. Oracle also supports RATIO_TO_REPORT analytic function.

- **What Microsoft Evaluates**: Cohort analysis understanding. Microsoft uses similar metrics in Xbox and Office 365 products.

- **Follow-ups**: 1) Calculate 7-day and 30-day retention. 2) Find the longest login streak per player. 3) Create an APEX report visualizing retention cohorts.

---

### Lab 08: Performance Tuning

#### Problem: Database Connection Pool Analysis (Microsoft-specific)

- **Difficulty/Frequency**: Hard / Medium

- **SQL Problem Statement**: Analyze Oracle database connection usage. Identify sessions idle for 30+ minutes and users with excessive concurrent connections.

- **Interview Walkthrough**: Use V$SESSION with GROUP BY and CASE to classify session health.

- **SQL Solution**:

```sql
WITH session_analysis AS (
    SELECT username,
           COUNT(*) AS session_count,
           SUM(CASE
               WHEN last_call_et > 1800 THEN 1 ELSE 0
           END) AS idle_sessions,
           ROUND(AVG(last_call_et), 0) AS avg_idle_seconds
    FROM v$session
    WHERE username IS NOT NULL
      AND status = 'ACTIVE'
    GROUP BY username
)
SELECT username,
       session_count,
       idle_sessions,
       ROUND(idle_sessions * 100.0
             / NULLIF(session_count, 0), 1) AS pct_idle,
       CASE
           WHEN idle_sessions >= 10 THEN 'CRITICAL'
           WHEN idle_sessions >= 5 THEN 'WARNING'
           WHEN idle_sessions >= 1 THEN 'MONITOR'
           ELSE 'HEALTHY'
       END AS health
FROM session_analysis
ORDER BY idle_sessions DESC, session_count DESC;
```

- **Oracle-Specific Syntax**: V$SESSION is an Oracle dynamic performance view. LAST_CALL_ET gives idle time in seconds. NULLIF prevents division by zero.

- **What Microsoft Evaluates**: Proactive database management and Oracle monitoring skills.

- **Follow-ups**: 1) Write a PL/SQL block to kill idle sessions. 2) Create an APEX dashboard showing real-time session health. 3) Compare with SQL Server's sys.dm_exec_sessions.

#### Problem: Find Full Table Scan Queries (Microsoft-specific)

- **Difficulty/Frequency**: Hard / High

- **SQL Problem Statement**: Identify top 10 queries performing full table scans on large tables (>100K blocks). Include SQL text, table name, and cost.

- **Interview Walkthrough**: Query V$SQL_PLAN and V$SQLAREA joined with DBA_TABLES.

- **SQL Solution**:

```sql
SELECT * FROM (
    SELECT s.sql_id,
           SUBSTR(s.sql_text, 1, 100) AS sql_text_short,
           p.object_name AS table_name,
           t.num_rows,
           t.blocks,
           p.cost,
           p.cardinality
    FROM v$sql_plan p
    JOIN v$sqlarea s ON p.sql_id = s.sql_id
    JOIN dba_tables t ON p.object_name = t.table_name
    WHERE p.operation = 'TABLE ACCESS'
      AND p.options = 'FULL'
      AND t.blocks > 100000
    ORDER BY t.blocks DESC
)
WHERE ROWNUM <= 10;
```

- **Oracle-Specific Syntax**: ROWNUM for limiting (pre-12c). V$SQL_PLAN and V$SQLAREA are Oracle performance views.

- **What Microsoft Evaluates**: SQL tuning expertise using Oracle diagnostic views.

- **Follow-ups**: 1) Suggest indexes to eliminate full scans. 2) Use DBMS_XPLAN to format plans. 3) Create an APEX tuning dashboard.

---

## APEX-Specific Deep Dive Questions

1. **How would you integrate Oracle APEX with Azure Active Directory for authentication?** Discuss OpenID Connect, OAuth 2.0 flows, APEX authentication schemes, JWT token validation, and Azure AD group mapping to APEX roles.

2. **Compare Oracle APEX with Microsoft Power Apps.** What are strengths and weaknesses of each? When would you recommend APEX over Power Apps? Discuss licensing, deployment, data sources, and scalability.

3. **How would you architect a hybrid Oracle/Microsoft solution** where APEX on Oracle needs data from Azure SQL Database? Discuss database links, REST APIs, ODBC, and data synchronization.

4. **How to build an APEX app following Fluent Design principles?** Discuss Universal Theme customization, CSS overrides, template modifications, and component customization to match Microsoft's design language.

---

## System Design Questions

1. **Design a corporate expense reporting system in APEX integrated with Power BI.** Discuss data modeling, star schema for Power BI, and approval workflows.

2. **Design a cross-platform data migration from Oracle to Azure SQL Database** while maintaining an APEX frontend. Discuss migration tools, schema mapping, data type conversions, and handling Oracle-specific features.

3. **Design a real-time manufacturing dashboard using APEX with Azure IoT Hub.** Discuss IoT data ingestion, Stream Analytics, time-series storage, and AJAX-based real-time updates in APEX.

---

## Behavioral Questions

1. **Tell me about a time you learned a new technology to solve a problem.** (Growth Mindset)

   - **S**ituation: Client needed APEX integration with Azure AD which I had never done.
   - **T**ask: Implement seamless SSO within 3 weeks.
   - **A**ction: Studied OAuth 2.0 and OpenID Connect. Built custom APEX authentication scheme using ORDS REST API. Tested with multiple providers.
   - **R**esult: SSO in 2.5 weeks. Reused for 3 other clients.

2. **Describe a time you received critical feedback and improved.** (Growth Mindset)

   - **S**ituation: Code review feedback that PL/SQL lacked proper error handling.
   - **T**ask: Improve code quality.
   - **A**ction: Created standardized error handling template using PRAGMA EXCEPTION_INIT and DBMS_UTILITY.FORMAT_ERROR_STACK.
   - **R**esult: Post-implementation defects dropped 90%.

3. **Tell me about a time you collaborated across diverse teams.** (Collaboration)

   - **S**ituation: APEX project needed coordination between Oracle DBA, .NET devs, and Azure DevOps engineers.
   - **T**ask: Deliver integrated solution with zero production issues.
   - **A**ction: Established cross-team communication, documented API contracts, created shared test environments.
   - **R**esult: Project on time. Teams established ongoing collaboration.

4. **Describe a time you made an impact on customer experience.** (Customer Obsession)

   - **S**ituation: APEX app had confusing navigation causing high support call volume.
   - **T**ask: Redesign UX to reduce support calls.
   - **A**ction: Analyzed support tickets, redesigned navigation, added breadcrumbs, implemented contextual help.
   - **R**esult: Support calls reduced 65%. CSAT improved 40%.

5. **Tell me about a time you took on a task outside your job description.** (Ownership)

   - **S**ituation: DBA team was overloaded; APEX performance issues unresolved.
   - **T**ask: Diagnose and fix database performance.
   - **A**ction: Learned AWR reports, ASH analytics, SQL Tuning Advisor. Identified missing indexes.
   - **R**esult: Query performance improved 10x. Created new cross-functional role.

---

## Study Plan

### Priority Labs by Interview Impact

| Priority | Lab | Why |
|----------|-----|-----|
| P0 | Lab 01: Getting Started | Cross-platform SQL differences are core |
| P0 | Lab 08: Performance | Performance tuning universally valued |
| P1 | Lab 05: Interactive Reports | Data analysis skills transfer across platforms |
| P1 | Lab 04: Security | Security expectations high at Microsoft |
| P2 | Lab 06: RESTful Services | API design for Azure integration |
| P2 | Lab 03: Advanced Components | Shows APEX depth for Power Apps comparison |
| P3 | Lab 02: Page Designer | Familiarity expected, not tested |
| P3 | Lab 07: Migration | Relevant for migration consulting |

---

## Tips

### Company-Specific APEX Interview Strategies

- **Emphasize Cross-Platform Skills**: Microsoft values engineers who work across Oracle and Microsoft ecosystems. Highlight experience with both PL/SQL and T-SQL.

- **Compare APEX and Power Apps**: Know strengths of each. APEX for complex data-centric apps; Power Apps for rapid forms and Microsoft 365 integration.

- **Growth Mindset Language**: Use phrases like "I haven't learned that yet" instead of "I don't know that." Share learning stories.

- **Azure Integration Knowledge**: Learn Azure SQL, Azure AD, Azure DevOps, Power Platform basics.

- **Developer Tooling Focus**: Discuss how you use SQL Developer, VS Code, Git, and CI/CD for APEX.

- **Understand Microsoft-Oracle Partnership**: Show awareness of the Oracle on Azure partnership and cross-platform opportunities.

- **Be Ready for Open-Ended Design**: Microsoft design questions are vague. Practice asking clarifying questions.

- **Show End-to-End Thinking**: Discuss how APEX pages connect to database, PL/SQL processes, REST APIs, and UI rendering.

- **Practice STAR Format**: Microsoft uses structured behavioral interviewing. Clear Situation, Task, Action, Result.

- **One Microsoft Mindset**: Highlight cross-team collaboration and shared credit in your stories.

### Lab 03: Advanced Components

#### Problem: Consecutive Numbers - Find Sequences (LC SQL 180)

- **Difficulty/Frequency**: Medium / High

- **SQL Problem Statement**: Write a SQL query to find all numbers that appear at least three times consecutively in the Logs table. Return the distinct numbers.

- **Interview Walkthrough**: Use LAG and LEAD to compare each row with its neighbors. Microsoft values understanding of both self-join and window function approaches.

- **SQL Solution**:

`sql
-- Window functions approach
SELECT DISTINCT num AS consecutive_num
FROM (
    SELECT num,
           LAG(num, 1) OVER (ORDER BY id) AS prev1,
           LAG(num, 2) OVER (ORDER BY id) AS prev2
    FROM logs
)
WHERE num = prev1 AND num = prev2;

-- Self-join approach
SELECT DISTINCT l1.num AS consecutive_num
FROM logs l1
JOIN logs l2 ON l1.id = l2.id - 1
JOIN logs l3 ON l1.id = l3.id - 2
WHERE l1.num = l2.num AND l1.num = l3.num;
`

- **Oracle-Specific Syntax**: LAG with offset parameter (default 1). Oracle's window functions are highly optimized. The self-join approach works but is less efficient for large tables.

- **What Microsoft Evaluates**: Understanding of consecutive pattern detection using both window functions and self-joins. Microsoft values multiple solution approaches.

- **Follow-ups**: 1) Find numbers appearing N times consecutively using a parameter. 2) Detect value changes in time-series data. 3) Implement in APEX as a validation rule.

#### Problem: Calculate Median Using PERCENTILE_CONT (Microsoft-specific)

- **Difficulty/Frequency**: Medium / Medium

- **SQL Problem Statement**: Calculate the median salary for the entire company and for each department. Compare how Oracle's PERCENTILE_CONT works versus SQL Server's equivalent.

- **Interview Walkthrough**: Use PERCENTILE_CONT(0.5) WITHIN GROUP. Microsoft interviewers will ask about the difference between PERCENTILE_CONT (continuous/interpolation) and PERCENTILE_DISC (discrete).

- **SQL Solution**:

`sql
-- Company-wide median
SELECT ROUND(
    PERCENTILE_CONT(0.5) WITHIN GROUP (
        ORDER BY sal
    ), 2
) AS company_median_salary
FROM emp;

-- Median by department
SELECT d.dname AS department,
       ROUND(
           PERCENTILE_CONT(0.5) WITHIN GROUP (
               ORDER BY e.sal
           ), 2
       ) AS median_salary,
       ROUND(AVG(e.sal), 2) AS avg_salary
FROM emp e
JOIN dept d ON e.deptno = d.deptno
GROUP BY d.dname
ORDER BY median_salary DESC;

-- Percentile distribution
SELECT d.dname AS department,
       ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (
           ORDER BY e.sal), 2) AS p25_salary,
       ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (
           ORDER BY e.sal), 2) AS median_salary,
       ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (
           ORDER BY e.sal), 2) AS p75_salary,
       ROUND(PERCENTILE_CONT(0.90) WITHIN GROUP (
           ORDER BY e.sal), 2) AS p90_salary
FROM emp e
JOIN dept d ON e.deptno = d.deptno
GROUP BY d.dname;
`

- **Oracle-Specific Syntax**: PERCENTILE_CONT is ANSI SQL but Oracle and SQL Server implement it identically. PERCENTILE_DISC returns an actual value from the dataset; PERCENTILE_CONT interpolates between values.

- **What Microsoft Evaluates**: Understanding of statistical functions and their cross-platform behavior. Microsoft values engineers who understand the math behind the functions.

- **Follow-ups**: 1) Explain when to use PERCENTILE_CONT vs PERCENTILE_DISC. 2) Calculate weighted median. 3) Create an APEX report showing salary distribution charts.

### Lab 06: RESTful Services

#### Problem: REST API for Multi-Platform Integration (Microsoft-specific)

- **Difficulty/Frequency**: Medium / Medium

- **SQL Problem Statement**: Create an ORDS REST handler that returns employee data in a format compatible with both Microsoft Power BI and Excel. Include metadata about data types for Power Query.

- **Interview Walkthrough**: Microsoft values integration between Oracle and Microsoft tools. Use JSON_OBJECT with data type annotations.

- **SQL Solution**:

`sql
SELECT JSON_OBJECT(
    KEY 'schema' VALUE JSON_ARRAYAGG(
        JSON_OBJECT(
            KEY 'column' VALUE 'empno',
            KEY 'type' VALUE 'NUMBER'
        ),
        JSON_OBJECT(
            KEY 'column' VALUE 'ename',
            KEY 'type' VALUE 'VARCHAR2'
        ),
        JSON_OBJECT(
            KEY 'column' VALUE 'sal',
            KEY 'type' VALUE 'NUMBER'
        ),
        JSON_OBJECT(
            KEY 'column' VALUE 'hiredate',
            KEY 'type' VALUE 'DATE'
        )
    ),
    KEY 'data' VALUE (
        SELECT JSON_ARRAYAGG(
            JSON_OBJECT(
                KEY 'empno' VALUE e.empno,
                KEY 'ename' VALUE e.ename,
                KEY 'sal' VALUE e.sal,
                KEY 'hiredate' VALUE TO_CHAR(
                    e.hiredate, 'YYYY-MM-DD"T"HH24:MI:SS')
            )
        )
        FROM emp e
    ),
    KEY 'generated_at' VALUE TO_CHAR(
        SYSTIMESTAMP, 'YYYY-MM-DD"T"HH24:MI:SS.FF3"Z"')
) AS power_bi_response
FROM DUAL;
`

- **Oracle-Specific Syntax**: JSON_ARRAYAGG with multiple arguments. TO_CHAR with ISO 8601 timestamp format. SYSTIMESTAMP for high-precision timestamp.

- **What Microsoft Evaluates**: Cross-platform API design. Microsoft values APIs that integrate seamlessly with their tools (Power BI, Excel, Power Automate).

- **Follow-ups**: 1) Add OData-compatible pagination. 2) Support  and  parameters. 3) Implement OAuth 2.0 authentication for Azure AD.
