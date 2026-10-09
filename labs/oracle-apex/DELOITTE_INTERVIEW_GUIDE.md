# Deloitte Interview Guide — Oracle APEX Academy

## Interview Process for APEX/Database Roles

### Rounds and Timeline

The Deloitte interview process for APEX and database consulting roles typically spans 2-4 weeks.

- **Recruiter Screen (30 min)**: Call covering background, consulting experience, APEX project exposure, and availability for client travel.

- **Technical Phone (60 min)**: Senior manager evaluates SQL skills, APEX architecture understanding, and project delivery experience.

- **Virtual Onsite (3-4 rounds)**: 1 case study (business scenario), 1 technical deep-dive, 1 behavioral/partner fit. Each round is 45-60 minutes.

- **Timeline**: 2 to 4 weeks. Faster than product companies due to consulting engagement needs.

### APEX-Specific Expectations

Deloitte hires APEX developers for client consulting engagements. They value practical experience delivering real-world APEX projects. Communication skills, client management, and the ability to translate business requirements into APEX solutions are critical.

Deloitte expects candidates to have end-to-end project experience — from requirements gathering through deployment and support. Industry domain knowledge (financial services, healthcare, government) is a significant differentiator.

### Key Areas Assessed

- **SQL/PL/SQL**: Practical query writing, data migration skills, performance tuning for client deliverables.

- **APEX Project Delivery**: Full lifecycle experience, Agile methodology, client demos, estimation skills.

- **Consulting Skills**: Requirements gathering, estimation, documentation, client communication, stakeholder management.

- **Domain Knowledge**: Industry experience (finance, healthcare, government) is a significant plus.

- **Team Leadership**: Mentoring, code reviews, technical direction, offshore team collaboration.

---

## Top SQL/PLSQL Problems by Lab

### Lab 01: Getting Started with APEX

#### Problem: Department Salary Statistics (LC SQL 174 variant)

- **Difficulty/Frequency**: Medium / High

- **SQL Problem Statement**: Compute department-level salary statistics: total, average, minimum, maximum salary, and employee count. Only include departments with at least 2 employees. Format salary columns with two decimal places.

- **Interview Walkthrough**: Use GROUP BY with aggregate functions and TO_CHAR for formatted output. Deloitte consultants need to deliver professional client-ready reports.

- **SQL Solution**:

```sql
SELECT d.dname AS department,
       COUNT(e.empno) AS emp_count,
       TO_CHAR(SUM(e.sal), '999,999.99') AS total_salary,
       TO_CHAR(AVG(e.sal), '999,999.99') AS avg_salary,
       TO_CHAR(MIN(e.sal), '999,999.99') AS min_salary,
       TO_CHAR(MAX(e.sal), '999,999.99') AS max_salary
FROM emp e
RIGHT JOIN dept d
    ON e.deptno = d.deptno
GROUP BY d.dname
HAVING COUNT(e.empno) >= 2
ORDER BY AVG(e.sal) DESC;
```

- **Oracle-Specific Syntax**: TO_CHAR with number format model for formatted output. RIGHT JOIN ensures zero-employee departments appear. Oracle's NVL handles NULL salaries.

- **What Deloitte Evaluates**: Client-ready formatted output. Consulting deliverables need to look professional.

- **Follow-ups**: 1) Handle zero-employee departments (display zeros). 2) Add percentage of total salary. 3) Create APEX IR with conditional formatting.

#### Problem: Find Employees by Role Across Departments (simple filter)

- **Difficulty/Frequency**: Easy / Medium

- **SQL Problem Statement**: Find all ANALYST and MANAGER roles. Show name, job, department, salary. Sort by department, then salary descending.

- **Interview Walkthrough**: Simple SELECT with IN filter and JOIN. Deloitte values clean, readable SQL.

- **SQL Solution**:

```sql
SELECT e.ename AS employee_name,
       e.job,
       d.dname AS department,
       e.sal AS salary
FROM emp e
JOIN dept d ON e.deptno = d.deptno
WHERE e.job IN ('ANALYST', 'MANAGER')
ORDER BY d.dname, e.sal DESC;
```

- **Oracle-Specific Syntax**: Standard SQL. Oracle's IN clause is well-optimized.

- **What Deloitte Evaluates**: Clean, readable SQL that clients can understand.

- **Follow-ups**: 1) Include count per department. 2) Exclude specific locations. 3) Create parameterized APEX report.

---

### Lab 04: Security in APEX

#### Problem: Data Quality Audit Query (LC SQL 584)

- **Difficulty/Frequency**: Medium / High

- **SQL Problem Statement**: Find customer records with missing or invalid data: NULL email, NULL phone, invalid ZIP (not 5 digits), age outside 0-120. Return customer ID, name, and concatenated list of issues.

- **Interview Walkthrough**: Use CASE for each validation and LISTAGG to concatenate issues. Deloitte does extensive data quality assessment for clients.

- **SQL Solution**:

```sql
SELECT customer_id,
       customer_name,
       LISTAGG(issue, '; ')
           WITHIN GROUP (ORDER BY issue) AS issues
FROM (
    SELECT customer_id, customer_name,
           'Missing email' AS issue
    FROM customers WHERE email IS NULL
    UNION ALL
    SELECT customer_id, customer_name,
           'Invalid ZIP'
    FROM customers
    WHERE LENGTH(TRIM(zip)) != 5
       OR NOT REGEXP_LIKE(zip, '^[0-9]{5}$')
    UNION ALL
    SELECT customer_id, customer_name,
           'Invalid age'
    FROM customers
    WHERE age IS NULL OR age < 0 OR age > 120
)
GROUP BY customer_id, customer_name
ORDER BY customer_id;
```

- **Oracle-Specific Syntax**: LISTAGG concatenates strings (Oracle 11g+). REGEXP_LIKE for pattern validation. UNION ALL combines validation queries.

- **What Deloitte Evaluates**: Data quality assessment methodology. Critical for migration and integration projects.

- **Follow-ups**: 1) Add severity rating per issue. 2) Create APEX data quality dashboard. 3) Write PL/SQL procedure for dynamic data quality reports.

#### Problem: Row-Level Security for Multi-Tenant Client (Deloitte-specific)

- **Difficulty/Frequency**: Hard / High

- **SQL Problem Statement**: Implement row-level security for a multi-tenant APEX app. Create VPD policy, context, and PL/SQL function.

- **Interview Walkthrough**: Use Oracle's DBMS_RLS with context-based security policy.

- **SQL Solution**:

```sql
CREATE OR REPLACE CONTEXT apex_client_ctx USING pkg_client_context;

CREATE OR REPLACE PACKAGE pkg_client_context AS
    PROCEDURE set_client_org(p_org_id NUMBER);
    FUNCTION get_client_org RETURN NUMBER;
END;
/

CREATE OR REPLACE PACKAGE BODY pkg_client_context AS
    PROCEDURE set_client_org(p_org_id NUMBER) IS
    BEGIN
        DBMS_SESSION.SET_CONTEXT(
            'apex_client_ctx', 'client_org_id', p_org_id);
    END;
    FUNCTION get_client_org RETURN NUMBER IS
    BEGIN
        RETURN SYS_CONTEXT(
            'apex_client_ctx', 'client_org_id');
    END;
END;
/

CREATE OR REPLACE FUNCTION f_client_access(
    p_schema VARCHAR2, p_table VARCHAR2
) RETURN VARCHAR2 AS
BEGIN
    RETURN 'client_org_id = SYS_CONTEXT(
        ''apex_client_ctx'', ''client_org_id'')';
END;
/

BEGIN
    DBMS_RLS.ADD_POLICY(
        object_schema => 'APEX_APP',
        object_name => 'CLIENT_DATA',
        policy_name => 'client_access_policy',
        function_schema => 'APEX_APP',
        policy_function => 'f_client_access',
        statement_types => 'SELECT,INSERT,UPDATE,DELETE',
        sec_relevant_cols => 'client_org_id');
END;
/
```

- **Oracle-Specific Syntax**: DBMS_RLS is Oracle's VPD package. SYS_CONTEXT retrieves context values.

- **What Deloitte Evaluates**: Multi-tenant security implementation for enterprise clients.

- **Follow-ups**: 1) Handle unset client_org_id (block access). 2) Add admin exception. 3) Create separate policies for different tables.

---

### Lab 05: Interactive Reports

#### Problem: Sales Performance Dashboard (Deloitte-specific)

- **Difficulty/Frequency**: Medium / High

- **SQL Problem Statement**: Build sales performance: YTD sales by region, month-over-month growth, budget variance, trailing 3-month average.

- **Interview Walkthrough**: Combine aggregations, window functions with LAG, calculated fields. Typical Deloitte client deliverable.

- **SQL Solution**:

```sql
WITH monthly_sales AS (
    SELECT r.region_name,
           TRUNC(s.sale_date, 'MM') AS sale_month,
           SUM(s.amount) AS actual_sales,
           b.budget_amount
    FROM sales s
    JOIN regions r ON s.region_id = r.region_id
    JOIN budgets b
        ON r.region_id = b.region_id
       AND TRUNC(s.sale_date, 'MM') = b.budget_month
    GROUP BY r.region_name, TRUNC(s.sale_date, 'MM'),
             b.budget_amount
)
SELECT region_name,
       TO_CHAR(sale_month, 'MON YYYY') AS month,
       actual_sales,
       SUM(actual_sales) OVER (
           PARTITION BY region_name,
                        EXTRACT(YEAR FROM sale_month)
           ORDER BY sale_month
       ) AS ytd_sales,
       ROUND(
           (actual_sales / NULLIF(
               LAG(actual_sales) OVER (
                   PARTITION BY region_name
                   ORDER BY sale_month
               ), 0) - 1) * 100, 2
       ) AS mom_growth_pct,
       ROUND(
           (actual_sales - budget_amount)
           / NULLIF(budget_amount, 0) * 100, 2
       ) AS budget_variance_pct,
       ROUND(
           AVG(actual_sales) OVER (
               PARTITION BY region_name
               ORDER BY sale_month
               ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
           ), 2
       ) AS trailing_3mo_avg
FROM monthly_sales
ORDER BY region_name, sale_month;
```

- **Oracle-Specific Syntax**: TO_CHAR with 'MON YYYY'. NULLIF for zero-division. LAG for previous period. ROWS BETWEEN 2 PRECEDING.

- **What Deloitte Evaluates**: Building client-ready analytics for executive dashboards.

- **Follow-ups**: 1) Add drill-down to sales reps. 2) Create APEX chart. 3) Conditional formatting for negative variances.

---

### Lab 06: RESTful Services

#### Problem: REST API for Client Timesheet Integration (Deloitte-specific)

- **Difficulty/Frequency**: Medium / High

- **SQL Problem Statement**: Create ORDS REST service returning employee timesheet data as JSON with pagination and filtering.

- **Interview Walkthrough**: Deloitte frequently integrates APEX with third-party systems via REST APIs.

- **SQL Solution**:

```sql
SELECT JSON_OBJECT(
    KEY 'status' VALUE 'success',
    KEY 'data' VALUE (
        SELECT JSON_ARRAYAGG(
            JSON_OBJECT(
                KEY 'employee' VALUE e.ename,
                KEY 'project' VALUE p.project_name,
                KEY 'hours' VALUE t.hours_worked,
                KEY 'billable' VALUE CASE t.is_billable
                    WHEN 'Y' THEN 'Billable'
                    ELSE 'Non-Billable'
                END
            )
            ORDER BY e.ename
        )
        FROM timesheets t
        JOIN employees e ON t.empno = e.empno
        JOIN projects p ON t.project_id = p.project_id
        WHERE t.work_date BETWEEN :start_date AND :end_date
          AND (:project IS NULL OR p.project_name = :project)
    ),
    KEY 'metadata' VALUE JSON_OBJECT(
        KEY 'total' VALUE (
            SELECT COUNT(*)
            FROM timesheets t
            JOIN projects p ON t.project_id = p.project_id
            WHERE t.work_date BETWEEN :start_date AND :end_date
              AND (:project IS NULL OR p.project_name = :project)
        )
    )
) AS result FROM DUAL;
```

- **Oracle-Specific Syntax**: Nested JSON_OBJECT and JSON_ARRAYAGG. Bind variables from ORDS. FROM DUAL for scalar queries.

- **What Deloitte Evaluates**: REST API design for system integration projects.

- **Follow-ups**: 1) Add error handling. 2) Implement OAuth 2.0. 3) Create APEX page consuming this REST service.

---

### Lab 08: Performance Tuning

#### Problem: Index Analysis for Client Database (Deloitte-specific)

- **Difficulty/Frequency**: Hard / Medium

- **SQL Problem Statement**: Analyze indexing strategy for client database. Identify missing, redundant, and unused indexes.

- **Interview Walkthrough**: Query DBA_INDEXES, DBA_IND_COLUMNS, DBA_TABLES, V$OBJECT_USAGE.

- **SQL Solution**:

```sql
WITH index_analysis AS (
    SELECT i.owner, i.table_name, i.index_name,
           i.index_type, i.uniqueness,
           ic.column_name, t.num_rows,
           NVL(u.used, 'NO') AS used
    FROM dba_indexes i
    JOIN dba_ind_columns ic
        ON i.index_name = ic.index_name
       AND i.owner = ic.index_owner
    JOIN dba_tables t
        ON i.table_name = t.table_name
       AND i.owner = t.owner
    LEFT JOIN v$object_usage u
        ON i.index_name = u.index_name
       AND i.owner = u.owner
    WHERE t.num_rows > 10000
      AND i.owner = 'APEX_APP'
)
SELECT table_name, index_name, index_type, num_rows,
       CASE
           WHEN used = 'NO' THEN 'UNUSED - Drop'
           WHEN num_rows > 100000
                AND index_type = 'NORMAL'
               THEN 'Consider bitmap'
           ELSE 'OK'
       END AS recommendation
FROM index_analysis
ORDER BY num_rows DESC, recommendation;
```

- **Oracle-Specific Syntax**: DBA_INDEXES, DBA_IND_COLUMNS, DBA_TABLES. V$OBJECT_USAGE tracks index usage.

- **What Deloitte Evaluates**: Database health assessment — directly billable consulting skill.

- **Follow-ups**: 1) Generate CREATE INDEX statements. 2) Create APEX dashboard. 3) Write PL/SQL for automated reports.

---

## APEX-Specific Deep Dive Questions

1. **How do you estimate an APEX project for a client?** Discuss requirements gathering, complexity assessment, component-based estimation, risk factors.

2. **Describe your approach to managing scope creep.** How to balance client requests with constraints? Change management processes.

3. **How would you architect an APEX solution for client handover?** Documentation, code organization, knowledge transfer, training.

4. **Your methodology for debugging APEX in production.** Systematic isolation, log analysis, reproducible cases, stakeholder communication.

---

## System Design Questions

1. **Compliance tracking system for financial services.** Data model, workflow, reporting, regulatory change handling.

2. **Data migration from legacy to APEX.** ETL strategy, data quality, transformation, validation, rollback.

3. **Helpdesk ticketing system in APEX.** SLA management, escalation, knowledge base, email-to-case, agent dashboard.

---

## Behavioral Questions

1. **Challenging client engagement.** Unrealistic timeline negotiated to phased delivery.

2. **Helping client adopt new technology.** Excel to APEX migration with POC.

3. **Delivered under tight deadline.** Compliance report in 2 weeks for audit.

4. **Identified opportunity beyond scope.** Manual approval process automated with APEX.

5. **Managed difficult team dynamic.** Onshore-offshore conflict resolved with standups and pairing.

---

## Study Plan

| Priority | Lab | Why |
|----------|-----|-----|
| P0 | Lab 01: Getting Started | Foundation for all client work |
| P0 | Lab 05: Interactive Reports | Client deliverables are report-heavy |
| P1 | Lab 04: Security | Enterprise clients require robust security |
| P1 | Lab 06: RESTful Services | System integration in consulting |
| P2 | Lab 08: Performance | Database health assessments |
| P2 | Lab 03: Advanced Components | Breadth for client demos |
| P3 | Lab 02: Page Designer | Practical tool familiarity |
| P3 | Lab 07: Migration | Relevant for migration projects |

---

## Tips

- **Client-Facing Mindset**: Every answer should demonstrate awareness of the client perspective.

- **Show Business Acumen**: Discuss ROI, TCO, business cases, measurable value delivered.

- **Communication is Key**: Speak clearly, structure answers, use analogies.

- **Be Ready for Case Studies**: Practice framing: understand problem, gather requirements, design solution, estimate effort.

- **Demonstrate Project Experience**: Specific stories about full lifecycle from requirements to support.

- **Industry Knowledge**: Highlight financial services, healthcare, government experience.

- **Certifications Help**: Oracle APEX certification, OCP, PMP valued at Deloitte.

- **Be Coachable**: Show openness to feedback and client adaptation.

- **Practice Elevator Pitch**: Crisp 2-minute summary of APEX experience and key projects.

### Lab 03: Advanced Components

#### Problem: Dynamic Approval Workflow Query (Deloitte-specific)

- **Difficulty/Frequency**: Hard / High

- **SQL Problem Statement**: Write a query that returns the current status of all pending approval requests in a multi-stage workflow. For each request, show the current approver, days pending, escalation level, and whether it's overdue based on SLA.

- **Interview Walkthrough**: Use CASE for SLA calculation, ROW_NUMBER to find current approver. Deloitte consultants frequently build workflow applications for clients.

- **SQL Solution**:

`sql
WITH current_approvals AS (
    SELECT ar.request_id,
           ar.request_type,
           ar.submitted_date,
           ar.amount,
           a.approver_id,
           a.approver_name,
           a.approval_level,
           a.assigned_date,
           ar.status,
           ROW_NUMBER() OVER (
               PARTITION BY ar.request_id
               ORDER BY a.approval_level
           ) AS current_stage
    FROM approval_requests ar
    JOIN approval_assignments a
        ON ar.request_id = a.request_id
    WHERE a.status = 'PENDING'
      AND ar.status = 'IN_PROGRESS'
)
SELECT request_id, request_type, amount,
       approver_name AS current_approver,
       ROUND(SYSDATE - assigned_date) AS days_pending,
       CASE approval_level
           WHEN 1 THEN 'Standard'
           WHEN 2 THEN 'Manager'
           WHEN 3 THEN 'Director'
           WHEN 4 THEN 'VP'
           ELSE 'Executive'
       END AS escalation_level,
       CASE
           WHEN SYSDATE - assigned_date >
                CASE approval_level
                    WHEN 1 THEN 3
                    WHEN 2 THEN 5
                    WHEN 3 THEN 7
                    ELSE 10
                END
               THEN 'OVERDUE'
           WHEN SYSDATE - assigned_date >
                CASE approval_level
                    WHEN 1 THEN 2
                    WHEN 2 THEN 3
                    WHEN 3 THEN 5
                    ELSE 7
                END
               THEN 'WARNING'
           ELSE 'ON_TRACK'
       END AS sla_status
FROM current_approvals
WHERE current_stage = 1
ORDER BY days_pending DESC, amount DESC;
`

- **Oracle-Specific Syntax**: ROW_NUMBER for finding current stage. SYSDATE - assigned_date for days calculation. ROUND for integer days.

- **What Deloitte Evaluates**: Workflow implementation skills. Deloitte builds many approval workflow applications for enterprise clients.

- **Follow-ups**: 1) Add auto-escalation logic. 2) Create APEX approval dashboard. 3) Implement email notification trigger.

#### Problem: Generate Invoice with Line Items (Deloitte-specific)

- **Difficulty/Frequency**: Medium / Medium

- **SQL Problem Statement**: Write a query that generates a complete invoice report showing invoice header info, line items with running subtotal, tax calculation, and grand total. Format as a professional document-ready output.

- **Interview Walkthrough**: Use analytic SUM for running subtotal, TO_CHAR for formatting. Deloitte consultants need to generate professional financial documents.

- **SQL Solution**:

`sql
WITH invoice_header AS (
    SELECT i.invoice_id,
           i.invoice_date,
           c.customer_name,
           c.billing_address,
           i.po_number
    FROM invoices i
    JOIN customers c ON i.customer_id = c.customer_id
    WHERE i.invoice_id = :p_invoice_id
),
line_items AS (
    SELECT li.line_number,
           li.description,
           li.quantity,
           li.unit_price,
           li.quantity * li.unit_price AS line_total,
           SUM(li.quantity * li.unit_price) OVER (
               ORDER BY li.line_number
               ROWS UNBOUNDED PRECEDING
           ) AS running_subtotal
    FROM invoice_lines li
    WHERE li.invoice_id = :p_invoice_id
),
invoice_summary AS (
    SELECT SUM(line_total) AS subtotal,
           SUM(line_total) * 0.08 AS tax_amount,
           SUM(line_total) * 1.08 AS grand_total
    FROM line_items
)
SELECT ih.invoice_id,
       TO_CHAR(ih.invoice_date, 'Month DD, YYYY') AS date,
       ih.customer_name,
       ih.billing_address,
       ih.po_number,
       li.line_number,
       li.description,
       li.quantity,
       TO_CHAR(li.unit_price, ',999.99') AS unit_price,
       TO_CHAR(li.line_total, ',999.99') AS line_total,
       TO_CHAR(li.running_subtotal, ',999.99')
           AS running_subtotal,
       TO_CHAR(isum.subtotal, ',999.99') AS subtotal,
       TO_CHAR(isum.tax_amount, ',999.99') AS tax,
       TO_CHAR(isum.grand_total, ',999.99') AS grand_total
FROM invoice_header ih
CROSS JOIN line_items li
CROSS JOIN invoice_summary isum
ORDER BY li.line_number;
`

- **Oracle-Specific Syntax**: CROSS JOIN for combining header, items, and summary. TO_CHAR with currency format model. ROWS UNBOUNDED PRECEDING for running total.

- **What Deloitte Evaluates**: Financial document generation. Deloitte consultants frequently build invoicing and billing systems.

- **Follow-ups**: 1) Add discount calculation. 2) Create APEX printable invoice page. 3) Add multi-currency support.

### Lab 02: Page Designer

#### Problem: Calculate SLA Adherence Percentage (Deloitte-specific)

- **Difficulty/Frequency**: Medium / Medium

- **SQL Problem Statement**: Calculate the percentage of service tickets resolved within SLA by priority level and month. Show target vs actual for each priority.

- **Interview Walkthrough**: Use CASE with date comparison, GROUP BY, and ratio calculation.

- **SQL Solution**:

`sql
WITH ticket_performance AS (
    SELECT ticket_id,
           priority,
           TRUNC(created_date, 'MM') AS month,
           resolved_date,
           created_date,
           target_hours,
           CASE
               WHEN resolved_date IS NULL THEN 'OPEN'
               WHEN (resolved_date - created_date) * 24
                    <= target_hours
                   THEN 'WITHIN_SLA'
               ELSE 'BREACHED'
           END AS sla_status
    FROM service_tickets
    WHERE created_date >= ADD_MONTHS(SYSDATE, -6)
)
SELECT TO_CHAR(month, 'MON YYYY') AS period,
       priority,
       COUNT(*) AS total_tickets,
       SUM(CASE
           WHEN sla_status = 'WITHIN_SLA' THEN 1 ELSE 0
       END) AS met_sla,
       ROUND(
           SUM(CASE
               WHEN sla_status = 'WITHIN_SLA' THEN 1 ELSE 0
           END) * 100.0 / COUNT(*), 1
       ) AS sla_pct,
       CASE
           WHEN ROUND(
               SUM(CASE
                   WHEN sla_status = 'WITHIN_SLA'
                   THEN 1 ELSE 0
               END) * 100.0 / COUNT(*), 1
           ) >= 95 THEN 'EXCEEDS TARGET'
           WHEN ROUND(
               SUM(CASE
                   WHEN sla_status = 'WITHIN_SLA'
                   THEN 1 ELSE 0
               END) * 100.0 / COUNT(*), 1
           ) >= 90 THEN 'MEETS TARGET'
           ELSE 'BELOW TARGET'
       END AS target_status
FROM ticket_performance
GROUP BY month, priority
ORDER BY month DESC, priority;
`

- **Oracle-Specific Syntax**: ADD_MONTHS for date range. TRUNC(date, 'MM') for month grouping. Date arithmetic (resolved_date - created_date) * 24 gives hours.

- **What Deloitte Evaluates**: Service desk analytics. Deloitte consultants build ITSM solutions for clients.

- **Follow-ups**: 1) Add agent-level breakdown. 2) Create trend chart in APEX. 3) Implement automated escalation for breached tickets.
