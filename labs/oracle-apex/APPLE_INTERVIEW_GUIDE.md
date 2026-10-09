# Apple Interview Guide — Oracle APEX Academy

## Interview Process for APEX/Database Roles

### Rounds and Timeline

The Apple interview process for database engineer roles typically spans 4-8 weeks.

- **Recruiter Screen (30 min)**: Call covering background, APEX experience, and Apple product awareness. Apple values candidates who understand their product ecosystem.

- **Technical Phone (60 min)**: Database engineer evaluates SQL, data structures, and basic algorithms. Expect live coding in a shared document.

- **Virtual Onsite (5-6 rounds)**: 3 technical rounds (SQL, PL/SQL, data privacy), 1 systems design, 1 behavioral, 1 hiring manager. Each round is 60 minutes.

- **Timeline**: 4 to 8 weeks. Apple is thorough and deliberate, especially for roles involving customer data.

### APEX-Specific Expectations

Apple looks for engineers who build elegant, intuitive, and highly reliable systems. APEX experience demonstrates ability to rapidly create data-driven applications. Apple values craftsmanship — attention to detail, clean architecture, and polished user experiences.

Privacy and security are paramount at Apple. Expect deep questions about how you handle sensitive data in APEX applications, encryption at rest and in transit, access control, and audit trails.

### Key Areas Assessed

- **SQL Proficiency**: Complex joins, hierarchical queries (CONNECT BY), analytic functions, date/time handling.

- **Data Privacy**: HIPAA compliance, data encryption (DBMS_CRYPTO, TDE), fine-grained access control, immutable audit trails.

- **PL/SQL**: Error handling, bulk operations, packages, autonomous transactions, security-focused PL/SQL.

- **APEX UX**: Theme customization, responsive design, accessibility (VoiceOver, WCAG 2.1).

- **System Design**: High-reliability systems, data integrity, failover strategies, global deployments.

---

## Top SQL/PLSQL Problems by Lab

### Lab 01: Getting Started with APEX

#### Problem: Employees Hired in Last N Days (LC SQL 1158)

- **Difficulty/Frequency**: Easy / Medium

- **SQL Problem Statement**: Find employees hired in the last 90 days. Return name, hire date (formatted YYYY-MM-DD), and department. Order by hire date descending.

- **Interview Walkthrough**: Use SYSDATE for current date. Subtract 90 days. Use TO_CHAR for formatting. Apple focuses on date handling precision.

- **SQL Solution**:

```sql
SELECT e.ename,
       TO_CHAR(e.hiredate, 'YYYY-MM-DD') AS hire_date,
       d.dname AS department
FROM emp e
JOIN dept d
    ON e.deptno = d.deptno
WHERE e.hiredate >= SYSDATE - 90
ORDER BY e.hiredate DESC;
```

- **Oracle-Specific Syntax**: SYSDATE returns current date and time. TO_CHAR with format model controls output. Oracle also supports CURRENT_DATE (session timezone) and SYSTIMESTAMP (fractional seconds).

- **What Apple Evaluates**: Date handling precision and attention to output format. Apple values exactness.

- **Follow-ups**: 1) Filter by hire month. 2) Calculate days since hire. 3) Add hire anniversary status column.

#### Problem: Organizational Hierarchy Tree (LC SQL 608)

- **Difficulty/Frequency**: Medium / High

- **SQL Problem Statement**: Display the full organizational hierarchy showing each employee, their level, the root manager, and whether they are a leaf node.

- **Interview Walkthrough**: Use Oracle's CONNECT BY PRIOR hierarchical query. Apple asks this to test understanding of organizational structures.

- **SQL Solution**:

```sql
SELECT LEVEL AS hier_level,
       LPAD(' ', 2 * (LEVEL - 1)) || ename AS indented_name,
       CONNECT_BY_ROOT ename AS root_manager,
       CONNECT_BY_ISLEAF AS is_leaf
FROM emp
START WITH mgr IS NULL
CONNECT BY PRIOR empno = mgr
ORDER SIBLINGS BY ename;
```

- **Oracle-Specific Syntax**: CONNECT BY PRIOR is Oracle-specific. LEVEL, CONNECT_BY_ROOT, CONNECT_BY_ISLEAF are Oracle pseudo-columns. ORDER SIBLINGS BY preserves hierarchy.

- **What Apple Evaluates**: Hierarchical data understanding for org charts and BOMs.

- **Follow-ups**: 1) Write using recursive CTE. 2) Find all subordinates of a manager. 3) Detect cycles.

---

### Lab 04: Security in APEX

#### Problem: Sensitive Data Access Audit (Apple-specific)

- **Difficulty/Frequency**: Medium / High

- **SQL Problem Statement**: Generate an audit report showing who accessed sensitive customer data (PII, PHI, PCI) in an APEX application. Flag unauthorized access.

- **Interview Walkthrough**: Apple prioritizes privacy above all. Join APEX activity logs with access control tables.

- **SQL Solution**:

```sql
SELECT aa.VIEW_DATE,
       aa.USERNAME,
       aa.APP_PAGE,
       aa.IP_ADDRESS,
       CASE
           WHEN acr.owner_id = u.user_id
                OR u.role = 'ADMIN'
               THEN 'AUTHORIZED'
           WHEN u.role = 'SUPPORT'
                AND acr.owner_id IN (
                    SELECT managed_id
                    FROM support_assignments
                    WHERE support_user_id = u.user_id
                )
               THEN 'AUTHORIZED'
           ELSE 'UNAUTHORIZED'
       END AS access_status,
       CASE
           WHEN acr.data_classification IN ('PII','PHI','PCI')
               THEN 'CRITICAL'
           ELSE 'STANDARD'
       END AS sensitivity
FROM apex_activity_log aa
JOIN user_roles u ON aa.USERNAME = u.username
JOIN access_control_records acr
    ON aa.USERNAME = acr.accessor
WHERE acr.data_classification IN ('PII', 'PHI', 'PCI')
  AND aa.VIEW_DATE >= SYSDATE - 30
ORDER BY aa.VIEW_DATE DESC;
```

- **Oracle-Specific Syntax**: APEX_ACTIVITY_LOG records all page views. Oracle's APEX provides comprehensive audit logging.

- **What Apple Evaluates**: Privacy-first mindset. Knowledge of data classification and unauthorized access detection.

- **Follow-ups**: 1) Create APEX IR for unauthorized access only. 2) Implement FGA for SELECT operations. 3) Use DBMS_CRYPTO for data integrity verification.

#### Problem: Encrypt Sensitive Data at Rest (Apple-specific)

- **Difficulty/Frequency**: Hard / Medium

- **SQL Problem Statement**: Write a PL/SQL package that encrypts sensitive columns using DBMS_CRYPTO with AES-256. Include key management and decryption for authorized users.

- **Interview Walkthrough**: Use DBMS_CRYPTO with AES-256 CBC. Manage keys in a secure location.

- **SQL Solution**:

```sql
CREATE OR REPLACE PACKAGE pkg_data_protection AS
    FUNCTION encrypt_sensitive(
        p_plaintext VARCHAR2
    ) RETURN RAW;
    FUNCTION decrypt_sensitive(
        p_ciphertext RAW
    ) RETURN VARCHAR2;
END;
/

CREATE OR REPLACE PACKAGE BODY pkg_data_protection AS
    encryption_key RAW(32) :=
        UTL_RAW.CAST_TO_RAW('A1B2C3D4E5F6A7B8C9D0E1F2A3B4C5D6');
    encryption_type PLS_INTEGER :=
        DBMS_CRYPTO.ENCRYPT_AES256
        + DBMS_CRYPTO.CHAIN_CBC
        + DBMS_CRYPTO.PAD_PKCS5;

    FUNCTION encrypt_sensitive(
        p_plaintext VARCHAR2
    ) RETURN RAW IS
    BEGIN
        RETURN DBMS_CRYPTO.ENCRYPT(
            UTL_I18N.STRING_TO_RAW(p_plaintext, 'AL32UTF8'),
            encryption_type,
            encryption_key
        );
    END encrypt_sensitive;

    FUNCTION decrypt_sensitive(
        p_ciphertext RAW
    ) RETURN VARCHAR2 IS
    BEGIN
        RETURN UTL_I18N.RAW_TO_CHAR(
            DBMS_CRYPTO.DECRYPT(
                p_ciphertext, encryption_type, encryption_key
            ),
            'AL32UTF8'
        );
    END decrypt_sensitive;
END;
/
```

- **Oracle-Specific Syntax**: DBMS_CRYPTO is Oracle's encryption package. UTL_I18N handles character set conversion. Encryption type is a bitmask combining algorithm, chain, and padding.

- **What Apple Evaluates**: Deep understanding of data protection. Apple expects proactive data protection.

- **Follow-ups**: 1) Implement TDE instead of column-level. 2) Create view that decrypts for authorized users. 3) Discuss key rotation strategy.

---

### Lab 05: Interactive Reports

#### Problem: Moving Average and Running Total (LC SQL 1097)

- **Difficulty/Frequency**: Medium / High

- **SQL Problem Statement**: Show daily sales, a 7-day moving average, and a running total for 2023.

- **Interview Walkthrough**: Combine SUM OVER for running totals and AVG OVER with ROWS BETWEEN 6 PRECEDING.

- **SQL Solution**:

```sql
WITH daily_sales AS (
    SELECT TRUNC(order_date) AS sale_date,
           SUM(amount) AS daily_amount
    FROM orders
    WHERE EXTRACT(YEAR FROM order_date) = 2023
    GROUP BY TRUNC(order_date)
)
SELECT sale_date,
       daily_amount,
       ROUND(
           AVG(daily_amount) OVER (
               ORDER BY sale_date
               ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
           ), 2
       ) AS moving_avg_7day,
       SUM(daily_amount) OVER (
           ORDER BY sale_date
           ROWS UNBOUNDED PRECEDING
       ) AS running_total
FROM daily_sales
ORDER BY sale_date;
```

- **Oracle-Specific Syntax**: ROWS BETWEEN framing. EXTRACT(YEAR FROM date). TRUNC removes time.

- **What Apple Evaluates**: Time-series analysis for product performance tracking.

- **Follow-ups**: 1) Add 30-day moving average. 2) Identify deviation days. 3) Build APEX chart.

#### Problem: Consecutive Month Streaks (Apple-specific)

- **Difficulty/Frequency**: Hard / Medium

- **SQL Problem Statement**: Find users with transactions in at least 3 consecutive months in 2023.

- **Interview Walkthrough**: Gap-and-islands pattern with ROW_NUMBER.

- **SQL Solution**:

```sql
WITH monthly_activity AS (
    SELECT DISTINCT user_id,
           TRUNC(transaction_date, 'MM') AS activity_month
    FROM transactions
    WHERE EXTRACT(YEAR FROM transaction_date) = 2023
),
numbered AS (
    SELECT user_id, activity_month,
           EXTRACT(MONTH FROM activity_month) AS month_num,
           ROW_NUMBER() OVER (
               PARTITION BY user_id
               ORDER BY activity_month
           ) AS rn
    FROM monthly_activity
),
islands AS (
    SELECT user_id, activity_month,
           month_num - rn AS grp
    FROM numbered
)
SELECT user_id,
       MIN(activity_month) AS streak_start,
       MAX(activity_month) AS streak_end,
       COUNT(*) AS streak_months
FROM islands
GROUP BY user_id, grp
HAVING COUNT(*) >= 3
ORDER BY user_id, streak_start;
```

- **Oracle-Specific Syntax**: TRUNC(date, 'MM') truncates to month start. Oracle date truncation with format masks.

- **What Apple Evaluates**: User engagement pattern recognition for Apple services.

- **Follow-ups**: 1) Handle year boundaries. 2) Find longest streak ever. 3) Create retention cohorts in APEX.

---

### Lab 08: Performance Tuning

#### Problem: Optimize Inventory Query (Apple-specific)

- **Difficulty/Frequency**: Hard / High

- **SQL Problem Statement**: Inventory query joining 5 tables runs for 3+ hours on 500M-row inventory table. Write the optimized query using partitioning, MVs, and hints.

- **Interview Walkthrough**: Apple's supply chain needs fast inventory queries. Use partition pruning and materialized views.

- **SQL Solution**:

```sql
CREATE MATERIALIZED VIEW mv_daily_inventory
REFRESH COMPLETE ON DEMAND
AS
SELECT i.warehouse_id,
       i.product_id,
       TRUNC(i.snapshot_date) AS inventory_date,
       SUM(i.quantity_on_hand) AS total_qty,
       SUM(i.quantity_reserved) AS total_reserved
FROM inventory i
WHERE i.snapshot_date >= TRUNC(SYSDATE) - 90
GROUP BY i.warehouse_id, i.product_id,
         TRUNC(i.snapshot_date);

SELECT /*+ PARALLEL(8) */
       w.warehouse_name,
       p.product_name,
       mv.inventory_date,
       mv.total_qty,
       mv.total_reserved,
       ROUND(
           (mv.total_qty - mv.total_reserved)
           * 100.0 / NULLIF(mv.total_qty, 0), 2
       ) AS pct_available
FROM mv_daily_inventory mv
JOIN warehouses w ON mv.warehouse_id = w.warehouse_id
JOIN products p ON mv.product_id = p.product_id
WHERE mv.warehouse_id IN ('WH001','WH002','WH003')
  AND mv.inventory_date >= TRUNC(SYSDATE) - 30
ORDER BY mv.inventory_date DESC, w.warehouse_name;
```

- **Oracle-Specific Syntax**: PARALLEL hint. REFRESH COMPLETE ON DEMAND. NULLIF prevents division by zero.

- **What Apple Evaluates**: Supply chain optimization at global scale.

- **Follow-ups**: 1) Add DBMS_SCHEDULER refresh. 2) Implement query rewrite. 3) Add partition exchange load.

---

## APEX-Specific Deep Dive Questions

1. **How to ensure APEX meets Apple's accessibility standards?** Discuss WCAG 2.1, ARIA, keyboard navigation, VoiceOver, color contrast.

2. **Implement end-to-end encryption for an APEX healthcare app.** Cover TDE, DBMS_CRYPTO, TLS, key management.

3. **Design an APEX app with complete audit trails for compliance.** Discuss FGA, APEX activity logs, immutable tables.

4. **Build an iOS-like APEX prototype.** Discuss Universal Theme, CSS animations, responsive iPad design, gestures.

---

## System Design Questions

1. **Global product launch tracking across 50+ countries.** Discuss timezone, localization, multi-language, workflow, dashboards.

2. **Supplier quality management database.** Model suppliers, parts, metrics, inspections, defect alerts.

3. **Retail store operations system for Apple Stores.** Employee scheduling, inventory, Genius Bar, sales reporting.

---

## Behavioral Questions

1. **Time you showed exceptional attention to detail.** Financial report rounding bug traced through 6 PL/SQL layers. Fix with explicit CAST.

2. **Time you went above and beyond for quality.** Redesigned 45 APEX pages to Apple design standards. CSAT improved from 3.2 to 4.8.

3. **Time you protected user privacy.** Eliminated PII from dev logs using DBMS_CRYPTO masking. Passed privacy audit.

4. **Time you simplified a complex system.** Reduced 15-state approval workflow to 6 states. Error rate dropped 90%.

5. **Time you collaborated cross-functionally.** APEX + hardware test equipment integration. Dashboard cut analysis from 3 days to 30 min.

---

## Study Plan

| Priority | Lab | Why |
|----------|-----|-----|
| P0 | Lab 04: Security | Privacy is Apple's #1 priority |
| P0 | Lab 08: Performance | Apple scale demands performance |
| P1 | Lab 01: Getting Started | Hierarchical and date query foundation |
| P1 | Lab 05: Interactive Reports | Product data analysis |
| P2 | Lab 03: Advanced Components | Shows APEX depth |
| P2 | Lab 06: RESTful Services | System integration |
| P3 | Lab 02: Page Designer | On-the-job learning |
| P3 | Lab 07: Migration | Lower priority |

---

## Tips

- **Privacy First**: Every answer should consider privacy. Apple's brand depends on user trust.

- **Craftsmanship Mentality**: Discuss code quality, UI detail, and commitment to excellence.

- **Master Hierarchical Queries**: CONNECT BY and recursive CTEs are frequently tested.

- **Zero Tolerance for Bugs**: Discuss testing practices — PL/SQL unit tests, integration testing.

- **Accessibility**: Know WCAG 2.1, VoiceOver, keyboard navigation.

- **Simplicity**: When discussing complex apps, emphasize how you simplified for users.

- **Security Depth**: Know TDE, DBMS_CRYPTO, FGA, VPD, APEX security features.

- **Design Sensibility**: Discuss UX in APEX — theme customization, responsive design, polish.

### Lab 03: Advanced Components

#### Problem: Find Product Categories with All Products Sold (Apple-specific)

- **Difficulty/Frequency**: Hard / Medium

- **SQL Problem Statement**: Find product categories where every product in that category has been sold at least once. Return category name and number of products. This is a relational division problem.

- **Interview Walkthrough**: Use double NOT EXISTS or COUNT comparison. Apple uses this for inventory and product lifecycle analysis.

- **SQL Solution**:

`sql
SELECT c.category_name,
       COUNT(DISTINCT p.product_id) AS product_count
FROM categories c
JOIN products p ON c.category_id = p.category_id
WHERE NOT EXISTS (
    SELECT 1
    FROM products p2
    WHERE p2.category_id = c.category_id
      AND NOT EXISTS (
          SELECT 1
          FROM order_items oi
          WHERE oi.product_id = p2.product_id
      )
)
GROUP BY c.category_name
ORDER BY c.category_name;

-- Alternative using COUNT comparison
SELECT c.category_name,
       COUNT(DISTINCT p.product_id) AS total_products,
       COUNT(DISTINCT CASE
           WHEN oi.order_id IS NOT NULL
           THEN p.product_id
       END) AS sold_products
FROM categories c
JOIN products p ON c.category_id = p.category_id
LEFT JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY c.category_name
HAVING COUNT(DISTINCT p.product_id) = COUNT(DISTINCT CASE
    WHEN oi.order_id IS NOT NULL THEN p.product_id
END);
`

- **Oracle-Specific Syntax**: Double NOT EXISTS for relational division. Oracle optimizes this pattern well. CASE inside COUNT for conditional aggregation.

- **What Apple Evaluates**: Relational division thinking. Apple needs to analyze product adoption and coverage across their ecosystem.

- **Follow-ups**: 1) Find categories where at least 80% of products have been sold. 2) Add time filter (last quarter). 3) Create APEX report for product category health.

#### Problem: Sessionization - Convert Event Log to User Sessions (Apple-specific)

- **Difficulty/Frequency**: Hard / High

- **SQL Problem Statement**: Given a user activity log (user_id, event_time, event_type), convert events into sessions where a session is a series of events from the same user with no gap longer than 30 minutes between consecutive events.

- **Interview Walkthrough**: Classic sessionization problem. Use LAG to find gaps, SUM with CASE to create session IDs, then aggregate.

- **SQL Solution**:

`sql
WITH event_gaps AS (
    SELECT user_id, event_time, event_type,
           CASE
               WHEN event_time - LAG(event_time) OVER (
                   PARTITION BY user_id
                   ORDER BY event_time
               ) > INTERVAL '30' MINUTE
                   OR LAG(event_time) OVER (
                       PARTITION BY user_id
                       ORDER BY event_time
                   ) IS NULL
               THEN 1 ELSE 0
           END AS is_new_session
    FROM user_activity
),
sessions AS (
    SELECT user_id, event_time, event_type,
           SUM(is_new_session) OVER (
               PARTITION BY user_id
               ORDER BY event_time
               ROWS UNBOUNDED PRECEDING
           ) AS session_id
    FROM event_gaps
)
SELECT user_id,
       session_id,
       MIN(event_time) AS session_start,
       MAX(event_time) AS session_end,
       COUNT(*) AS event_count,
       MAX(event_time) - MIN(event_time) AS session_duration
FROM sessions
GROUP BY user_id, session_id
ORDER BY user_id, session_start;
`

- **Oracle-Specific Syntax**: INTERVAL '30' MINUTE for time difference comparison. Oracle's interval arithmetic. ROWS UNBOUNDED PRECEDING for cumulative SUM.

- **What Apple Evaluates**: User behavior analytics. Apple uses sessionization for understanding how users interact with their products and services.

- **Follow-ups**: 1) Find average session duration per user. 2) Identify users with unusually long sessions. 3) Create APEX dashboard showing session analytics.

### Lab 06: RESTful Services

#### Problem: Secure REST API with Data Classification (Apple-specific)

- **Difficulty/Frequency**: Medium / Medium

- **SQL Problem Statement**: Create an ORDS REST handler that returns customer data but redacts sensitive fields based on the caller's authorization level. Use Oracle's data redaction or conditional JSON generation.

- **Interview Walkthrough**: Use CASE expressions in JSON_OBJECT to conditionally include or mask fields.

- **SQL Solution**:

`sql
SELECT JSON_OBJECT(
    KEY 'customer_id' VALUE c.customer_id,
    KEY 'name' VALUE c.name,
    KEY 'email' VALUE CASE
        WHEN :p_user_role = 'ADMIN'
            THEN c.email
        ELSE SUBSTR(c.email, 1, 1) || '***'
             || SUBSTR(c.email, INSTR(c.email, '@'))
    END,
    KEY 'phone' VALUE CASE
        WHEN :p_user_role IN ('ADMIN', 'SUPPORT')
            THEN c.phone
        ELSE '***-***-' || SUBSTR(c.phone, -4)
    END,
    KEY 'credit_card' VALUE CASE
        WHEN :p_user_role = 'ADMIN'
            THEN '****-****-****-'
                 || SUBSTR(c.credit_card, -4)
        ELSE NULL ABSENT ON NULL
    END,
    KEY 'access_level' VALUE :p_user_role,
    KEY 'data_classification' VALUE
        'CONFIDENTIAL - Apple Internal'
) AS customer_response
FROM customers c
WHERE c.customer_id = :p_customer_id;
`

- **Oracle-Specific Syntax**: ABSENT ON NULL omits keys with NULL values. CASE for conditional field inclusion. SUBSTR and INSTR for string masking.

- **What Apple Evaluates**: Privacy-by-design API implementation. Apple expects all data access APIs to consider data classification and user authorization.

- **Follow-ups**: 1) Implement row-level filtering based on data classification. 2) Add audit logging for all API access. 3) Create an APEX admin page to manage access roles.
