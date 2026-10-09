# Accenture Interview Guide — Oracle APEX Academy

## Interview Process for APEX/Database Roles

### Rounds and Timeline

The Accenture interview process for APEX and database consulting roles typically spans 2-4 weeks.

- **Recruiter Screen (30 min)**: Call covering background, APEX experience, availability for client travel, and willingness to work in a global delivery model.

- **Technical Phone (60 min)**: Technology Architect evaluates SQL, PL/SQL, APEX architecture, and project delivery methodology.

- **Virtual Onsite (3-4 rounds)**: 1 technical deep-dive (SQL, APEX, data modeling), 1 system design, 1 behavioral/HR. Each round is 45-60 minutes.

- **Timeline**: 2 to 4 weeks. Accenture moves quickly to staff client engagements.

### APEX-Specific Expectations

Accenture is the world's largest consulting firm with a massive Oracle practice. They hire APEX developers for client delivery projects ranging from small departmental apps to enterprise-scale systems. Accenture values practical, production-ready skills.

Accenture wants developers who can hit the ground running on client engagements. Communication, documentation, and methodology adherence are highly valued. Experience working in global delivery models (onshore-offshore teams) is a significant plus.

### Key Areas Assessed

- **SQL/PL/SQL**: Production-ready query writing, stored procedures, bulk operations, error handling.

- **APEX Development**: Page design, component configuration, dynamic actions, integrations, plug-ins.

- **Methodology**: Agile/Scrum, DevOps, CI/CD for APEX, version control, automated testing.

- **Client Delivery**: Estimation, documentation, testing, deployment, production support, knowledge transfer.

- **Technology Breadth**: Integration with other systems, data migration, cloud deployment (OCI, Azure, AWS).

---

## Top SQL/PLSQL Problems by Lab

### Lab 01: Getting Started with APEX

#### Problem: Salary Comparison with Department Average (LC SQL 615)

- **Difficulty/Frequency**: Medium / High

- **SQL Problem Statement**: Show each employee's salary alongside their department average salary and the difference. Show employees earning below average first.

- **Interview Walkthrough**: Use AVG as window function with OVER (PARTITION BY deptno). Compute the difference. Accenture values clean, maintainable SQL.

- **SQL Solution**:

```sql
SELECT d.dname AS department,
       e.ename AS employee,
       e.sal AS salary,
       ROUND(
           AVG(e.sal) OVER (PARTITION BY e.deptno), 2
       ) AS dept_avg_salary,
       ROUND(
           e.sal - AVG(e.sal) OVER (PARTITION BY e.deptno), 2
       ) AS salary_difference
FROM emp e
JOIN dept d ON e.deptno = d.deptno
ORDER BY salary_difference ASC, d.dname, e.ename;
```

- **Oracle-Specific Syntax**: AVG as window function with OVER (PARTITION BY). Oracle supports multiple window functions in one query. ROUND with precision.

- **What Accenture Evaluates**: Practical window function usage for comparative analytics — common client requirement.

- **Follow-ups**: 1) Add count of employees above/below average. 2) Show percentage difference. 3) Create APEX report with conditional formatting.

#### Problem: Managers with At Least 5 Direct Reports (LC SQL 570)

- **Difficulty/Frequency**: Medium / Medium

- **SQL Problem Statement**: Find managers with at least 5 direct reports. Return manager name and report count.

- **Interview Walkthrough**: Group by mgr, count employees, join for manager name.

- **SQL Solution**:

```sql
SELECT m.ename AS manager_name,
       COUNT(e.empno) AS report_count
FROM emp e
JOIN emp m ON e.mgr = m.empno
GROUP BY m.ename
HAVING COUNT(e.empno) >= 5
ORDER BY report_count DESC;
```

- **Oracle-Specific Syntax**: Standard SQL self-join. Oracle requires all non-aggregated columns in GROUP BY.

- **What Accenture Evaluates**: Practical reporting skills for management reports.

- **Follow-ups**: 1) Include managers with zero reports. 2) Calculate average report salary. 3) Create hierarchy report.

---

### Lab 04: Security in APEX

#### Problem: Employee Login Pattern Analysis (Accenture-specific)

- **Difficulty/Frequency**: Medium / Medium

- **SQL Problem Statement**: Analyze login patterns. Show total logins, last login, distinct IPs, and flag compromised accounts.

- **Interview Walkthrough**: Use analytic functions with PARTITION BY. Flag based on IP diversity.

- **SQL Solution**:

```sql
WITH user_summary AS (
    SELECT username,
           COUNT(*) AS total_logins,
           COUNT(DISTINCT ip_address) AS distinct_ips,
           MAX(login_time) AS last_login,
           MAX(CASE
               WHEN login_time >= SYSDATE - 1
               THEN 1 ELSE 0
           END) AS logged_in_today
    FROM login_audit
    WHERE login_time >= SYSDATE - 90
    GROUP BY username
)
SELECT username, total_logins, distinct_ips, last_login,
       CASE
           WHEN distinct_ips >= 5 AND total_logins >= 20
               THEN 'HIGH - Possible sharing'
           WHEN distinct_ips >= 3 AND logged_in_today = 1
               THEN 'MEDIUM - Unusual diversity'
           ELSE 'NORMAL'
       END AS risk_flag
FROM user_summary
WHERE risk_flag != 'NORMAL'
ORDER BY last_login DESC;
```

- **Oracle-Specific Syntax**: CASE inside aggregate. MAX with CASE for conditional aggregation.

- **What Accenture Evaluates**: Security analytics. Accenture has a massive security practice.

- **Follow-ups**: 1) Create APEX security dashboard. 2) Automated alerting. 3) Add geolocation lookup.

#### Problem: Audit Trail for Sensitive Table Changes (Accenture-specific)

- **Difficulty/Frequency**: Medium / High

- **SQL Problem Statement**: Create trigger-based audit trail for salary changes. Capture old/new values, user, time, IP.

- **Interview Walkthrough**: Create audit table, sequence, and trigger using :OLD/:NEW pseudorecords.

- **SQL Solution**:

```sql
CREATE TABLE emp_audit (
    audit_id NUMBER PRIMARY KEY,
    empno NUMBER,
    ename VARCHAR2(100),
    sal NUMBER,
    action_type VARCHAR2(10),
    changed_by VARCHAR2(100),
    changed_on TIMESTAMP,
    ip_address VARCHAR2(50)
);

CREATE SEQUENCE emp_audit_seq;

CREATE OR REPLACE TRIGGER trg_emp_audit
AFTER INSERT OR UPDATE OR DELETE ON emp
FOR EACH ROW
DECLARE
    v_action VARCHAR2(10);
BEGIN
    v_action := CASE
        WHEN INSERTING THEN 'INSERT'
        WHEN UPDATING THEN 'UPDATE'
        WHEN DELETING THEN 'DELETE'
    END;

    INSERT INTO emp_audit (
        audit_id, empno, ename, sal,
        action_type, changed_by, changed_on, ip_address
    ) VALUES (
        emp_audit_seq.NEXTVAL,
        :NEW.empno, :NEW.ename, :NEW.sal,
        v_action,
        NVL(v('APP_USER'), USER),
        SYSTIMESTAMP,
        SYS_CONTEXT('USERENV', 'IP_ADDRESS')
    );
END;
/
```

- **Oracle-Specific Syntax**: SYS_CONTEXT('USERENV', 'IP_ADDRESS') retrieves client IP. V('APP_USER') gets APEX user. :NEW/:OLD pseudorecords. SEQUENCE.NEXTVAL.

- **What Accenture Evaluates**: System auditing for compliance (SOX, HIPAA, GDPR).

- **Follow-ups**: 1) Create APEX history report. 2) Implement retention policy. 3) Use Flashback Data Archive.

---

### Lab 05: Interactive Reports

#### Problem: HR Analytics Dashboard (Accenture-specific)

- **Difficulty/Frequency**: Medium / High

- **SQL Problem Statement**: Build comprehensive HR analytics: employee count, average tenure, salary range, turnover rate.

- **Interview Walkthrough**: Multiple CTEs for different analyses, unified into single report.

- **SQL Solution**:

```sql
WITH dept_stats AS (
    SELECT d.deptno, d.dname,
           COUNT(e.empno) AS emp_count,
           ROUND(AVG(MONTHS_BETWEEN(
               SYSDATE, e.hiredate) / 12), 1
           ) AS avg_tenure_years,
           MIN(e.sal) AS min_salary,
           MAX(e.sal) AS max_salary,
           ROUND(AVG(e.sal), 2) AS avg_salary
    FROM dept d
    LEFT JOIN emp e ON d.deptno = e.deptno
    GROUP BY d.deptno, d.dname
),
turnover AS (
    SELECT d.deptno,
           COUNT(CASE
               WHEN e.hiredate < SYSDATE - 365
               THEN 1
           END) AS left_count,
           COUNT(CASE
               WHEN e.hiredate >= SYSDATE - 365
               THEN 1
           END) AS new_hires
    FROM dept d
    LEFT JOIN emp e ON d.deptno = e.deptno
    GROUP BY d.deptno
)
SELECT ds.dname AS department,
       ds.emp_count,
       ds.avg_tenure_years || ' yrs' AS avg_tenure,
       ds.avg_salary,
       t.left_count AS turnover_12mo,
       ROUND(t.left_count * 100.0
             / NULLIF(ds.emp_count, 0), 1
       ) AS turnover_rate_pct,
       t.new_hires
FROM dept_stats ds
JOIN turnover t ON ds.deptno = t.deptno
ORDER BY ds.emp_count DESC;
```

- **Oracle-Specific Syntax**: MONTHS_BETWEEN for date difference. LEFT JOIN for zero-emp departments. NULLIF prevents division by zero.

- **What Accenture Evaluates**: Comprehensive analytics for client dashboards.

- **Follow-ups**: 1) Add drill-down links. 2) Create charts. 3) Year-over-year comparison.

---

### Lab 07: Migration

#### Problem: Data Migration Validation (Accenture-specific)

- **Difficulty/Frequency**: Hard / High

- **SQL Problem Statement**: Write validation query comparing source and target tables after ETL. Identify only-in-source, only-in-target, and mismatched rows.

- **Interview Walkthrough**: Use FULL OUTER JOIN. Accenture does massive data migration projects.

- **SQL Solution**:

```sql
WITH comparison AS (
    SELECT NVL(s.customer_id, t.customer_id) AS id,
           CASE
               WHEN s.customer_id IS NULL
                   THEN 'ONLY_IN_TARGET'
               WHEN t.customer_id IS NULL
                   THEN 'ONLY_IN_SOURCE'
               WHEN s.name != t.name
                 OR s.email != t.email
                 OR NVL(s.status,'X') != NVL(t.status,'X')
                   THEN 'MISMATCH'
               ELSE 'MATCH'
           END AS status,
           s.name AS src_name, t.name AS tgt_name,
           s.email AS src_email, t.email AS tgt_email
    FROM source_customers s
    FULL OUTER JOIN target_customers t
        ON s.customer_id = t.customer_id
)
SELECT status, COUNT(*) AS count
FROM comparison
GROUP BY status
ORDER BY status;
```

- **Oracle-Specific Syntax**: FULL OUTER JOIN for complete comparison. NVL handles NULL comparisons.

- **What Accenture Evaluates**: Data migration validation — core consulting skill.

- **Follow-ups**: 1) Column-level mismatch detail. 2) APEX reconciliation dashboard. 3) Timing metrics.

#### Problem: Schema Migration with Data Type Conversion (Accenture-specific)

- **Difficulty/Frequency**: Hard / High

- **SQL Problem Statement**: Write PL/SQL procedure migrating data from legacy to normalized schema. Handle type conversions, cleansing, and error logging.

- **Interview Walkthrough**: Use BULK COLLECT, FORALL, SAVEPOINT, error logging.

- **SQL Solution**:

```sql
CREATE TABLE migration_errors (
    error_id NUMBER GENERATED BY DEFAULT AS IDENTITY,
    table_name VARCHAR2(100),
    source_key VARCHAR2(200),
    error_message VARCHAR2(4000),
    error_timestamp TIMESTAMP DEFAULT SYSTIMESTAMP
);

CREATE OR REPLACE PROCEDURE prc_migrate_customers AS
    TYPE cust_rec IS RECORD (
        old_id NUMBER,
        old_name VARCHAR2(200),
        old_dob VARCHAR2(20)
    );
    TYPE cust_tab IS TABLE OF cust_rec;
    l_custs cust_tab;
BEGIN
    SELECT c.cust_id, TRIM(c.cust_name), c.date_of_birth
    BULK COLLECT INTO l_custs
    FROM legacy_customers c
    WHERE NOT EXISTS (
        SELECT 1 FROM new_customers n
        WHERE n.legacy_id = c.cust_id
    );

    FORALL i IN 1..l_custs.COUNT
        SAVEPOINT before_insert;
        BEGIN
            INSERT INTO new_customers (
                customer_name,
                date_of_birth,
                legacy_id,
                migrated_date
            ) VALUES (
                l_custs(i).old_name,
                CASE
                    WHEN REGEXP_LIKE(l_custs(i).old_dob,
                         '^[0-9]{4}-[0-9]{2}-[0-9]{2}$')
                    THEN TO_DATE(l_custs(i).old_dob,
                         'YYYY-MM-DD')
                    ELSE NULL
                END,
                l_custs(i).old_id,
                SYSDATE
            );
        EXCEPTION
            WHEN OTHERS THEN
                INSERT INTO migration_errors (
                    table_name, source_key, error_message
                ) VALUES (
                    'CUSTOMERS',
                    l_custs(i).old_id,
                    SQLERRM
                );
                ROLLBACK TO SAVEPOINT before_insert;
        END;
    END LOOP;
    COMMIT;
END prc_migrate_customers;
/
```

- **Oracle-Specific Syntax**: BULK COLLECT INTO, FORALL, SAVEPOINT, REGEXP_LIKE validation. SQLERRM for error messages.

- **What Accenture Evaluates**: Real-world data migration experience with error handling.

- **Follow-ups**: 1) Add parallel processing. 2) Migration status dashboard. 3) Resumable migration.

---

### Lab 08: Performance Tuning

#### Problem: Top Resource-Consuming SQL Monitoring (Accenture-specific)

- **Difficulty/Frequency**: Hard / Medium

- **SQL Problem Statement**: Identify top 20 resource-consuming SQL queries from the last 24 hours.

- **Interview Walkthrough**: Query V$SQLAREA with filtering and ordering.

- **SQL Solution**:

```sql
SELECT sql_id,
       executions,
       ROUND(cpu_time / 1000000, 2) AS cpu_seconds,
       ROUND(elapsed_time / 1000000, 2) AS elapsed_seconds,
       ROUND(elapsed_time / NULLIF(executions, 0)
             / 1000000, 4) AS avg_elapsed_seconds,
       buffer_gets,
       disk_reads,
       rows_processed,
       SUBSTR(sql_text, 1, 200) AS sql_text_short,
       CASE
           WHEN disk_reads > 1000000 THEN 'CRITICAL'
           WHEN elapsed_time > 10000000000 THEN 'WARNING'
           WHEN buffer_gets/NULLIF(executions,0) > 10000
               THEN 'MONITOR'
           ELSE 'OK'
       END AS recommendation
FROM v$sqlarea
WHERE executions > 0
  AND command_type IN (2, 3, 6, 7)
  AND parsing_schema_name NOT IN ('SYS', 'SYSTEM')
  AND last_active_time >= SYSDATE - 1
ORDER BY elapsed_time DESC
FETCH FIRST 20 ROWS ONLY;
```

- **Oracle-Syntax**: V$SQLAREA for SQL statistics. CPU/ELAPSED_TIME in microseconds. FETCH FIRST (12c+).

- **What Accenture Evaluates**: Database performance monitoring and tuning skills.

- **Follow-ups**: 1) Create APEX tuning dashboard. 2) Generate SQL Tuning Advisor recommendations. 3) Add historical trending with DBA_HIST_SQLSTAT.

---

## APEX-Specific Deep Dive Questions

1. **How to ensure knowledge transfer to client's team?** Documentation, training, pair programming, code walkthroughs.

2. **Managing technical debt in APEX projects.** Refactoring strategies, communicating trade-offs to clients.

3. **Handling changing requirements mid-sprint.** Agile adaptation, change request process, impact analysis.

4. **Setting up DevOps pipeline for APEX.** Git, SQLcl, Liquibase, UTPLSQL, ORDS deployment, environment management.

---

## System Design Questions

1. **Consulting firm time tracking system.** Data model, workflow, utilization reports, profitability, payroll integration.

2. **Vendor management system.** Supplier onboarding, contracts, purchase orders, invoicing, scorecards.

3. **Learning management system in APEX.** Course catalog, enrollment, progress, assessments, certifications, HR integration.

---

## Behavioral Questions

1. **Helped team member succeed.** Mentored junior on complex integration. Delivered in 3 weeks.

2. **Adapted to significant change.** Client switched from Oracle to Azure SQL mid-project. Adapted with 95% code reuse.

3. **Identified process improvement.** Automated manual 4-hour deployment to 15-min CI/CD pipeline.

4. **Managed competing priorities.** Two clients needed simultaneous critical changes. Both delivered on time.

5. **Delivered innovative solution.** Mobile APEX app at 10% of native development cost.

---

## Study Plan

| Priority | Lab | Why |
|----------|-----|-----|
| P0 | Lab 01: Getting Started | Foundation for all client delivery |
| P0 | Lab 07: Migration | Core consulting competency |
| P1 | Lab 05: Interactive Reports | Client dashboards are common |
| P1 | Lab 04: Security | Compliance requirements ubiquitous |
| P2 | Lab 08: Performance | Reviews for clients |
| P2 | Lab 06: RESTful Services | Enterprise integration |
| P3 | Lab 03: Advanced Components | Breadth for complex requirements |
| P3 | Lab 02: Page Designer | Practical tool familiarity |

---

## Tips

- **Delivery Focus**: Emphasize project delivery — on-time, on-budget, high quality. Use metrics.

- **Methodology Matters**: Show Agile/Scrum experience. Know sprint, retrospective, velocity terminology.

- **Global Team Experience**: Highlight offshore/onshore collaboration, time zones, cross-cultural communication.

- **Certifications**: Oracle APEX certification, OCP, TOGAF, PMP add credibility.

- **Show Client Readiness**: Demonstrate consulting skills: active listening, business acumen, presentation.

- **Industry Knowledge**: Research Accenture's clients in your industry area (financial services, health, public service).

- **Estimation Questions**: Have a framework ready: identify components, assess complexity, apply velocity, add contingency.

- **Asset Reuse**: Discuss reusable frameworks, templates, components. Shows consulting maturity.

- **Offshore Collaboration**: Be ready to discuss leading distributed teams effectively.

- **Client Success Stories**: 2-3 STAR stories with consulting elements: business problem, solution, measurable value.
