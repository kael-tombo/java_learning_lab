# Amazon Interview Guide — Oracle APEX Academy

## Interview Process for APEX/Database Roles

### Rounds and Timeline

The Amazon interview process for database engineer and application developer roles typically spans 3-6 weeks.

- **Recruiter Phone (30 min)**: Screen focused on Amazon Leadership Principles and high-level APEX experience. The recruiter evaluates whether you have the right mix of technical and behavioral skills.

- **Online Assessment (90 min)**: SQL coding test on platforms like HackerRank plus a work style assessment. The SQL test covers joins, aggregations, window functions, and performance optimization.

- **Phone Interview (60 min)**: Technical round with a Bar Raiser covering SQL, PL/SQL, and APEX architecture. Leadership Principles are woven into technical questions.

- **Virtual Onsite (5 rounds)**: 4 technical rounds (SQL, data modeling, system design, APEX architecture) plus 1 Bar Raiser round. Each round is 60 minutes. Bar Raiser has veto power over the hiring decision.

- **Timeline**: 3 to 6 weeks depending on role level and team. SDE and DAE roles follow similar processes.

### APEX-Specific Expectations

Amazon looks for builders who can deliver results with bias for action. APEX experience is valued as evidence of ability to rapidly prototype and deliver production applications. Amazon's interview approach is heavily structured around their Leadership Principles (LPs). Every answer should tie back to one or more LPs.

Amazon expects you to think at scale — even if your APEX experience was for small teams, discuss how your design decisions would scale. They also value deep diving into technical details, so be prepared to explain the internals of your solutions.

### Key Areas Assessed

- **SQL Proficiency**: Complex queries, analytic functions, performance at Amazon scale (millions of orders, billions of events).

- **Data Modeling**: Star schemas, slowly changing dimensions, fact tables for e-commerce analytics.

- **APEX Architecture**: Understanding when APEX is the right tool versus a custom solution. Cost-benefit analysis of low-code platforms.

- **Leadership Principles**: Customer Obsession, Ownership, Deliver Results, Invent and Simplify, Dive Deep, Have Backbone.

- **System Design**: Scalable database designs for e-commerce workloads, inventory management, order processing.

---

## Top SQL/PLSQL Problems by Lab

### Lab 01: Getting Started with APEX

#### Problem: Products with Highest Sales in Each Category (LC SQL 2329)

- **Difficulty/Frequency**: Medium / High

- **SQL Problem Statement**: For each product category, find the product with the highest total sales amount. Return category name, product name, and total sales. If there are ties, return all tied products.

- **Interview Walkthrough**: Amazon loves this problem because it maps directly to their e-commerce business. Join products, sales, and categories. Aggregate sales by product within category using SUM. Use RANK() to find the top seller(s) per category. The RANK function handles ties naturally — if two products have the same total sales, both are returned.

- **SQL Solution**:

```sql
WITH product_sales AS (
    SELECT c.category_name,
           p.product_name,
           SUM(s.quantity * s.unit_price) AS total_sales
    FROM categories c
    JOIN products p
        ON c.category_id = p.category_id
    JOIN sales s
        ON p.product_id = s.product_id
    GROUP BY c.category_name, p.product_name
),
ranked_sales AS (
    SELECT category_name, product_name, total_sales,
           RANK() OVER (
               PARTITION BY category_name
               ORDER BY total_sales DESC
           ) AS sales_rank
    FROM product_sales
)
SELECT category_name, product_name, total_sales
FROM ranked_sales
WHERE sales_rank = 1
ORDER BY category_name;
```

- **Oracle-Specific Syntax**: RANK() handles ties by assigning the same rank to tied values. Oracle's WITH clause (Common Table Expression) is well-optimized. Oracle 12c+ supports multiple CTEs in a single WITH clause for readability.

- **What Amazon Evaluates**: Ability to aggregate data correctly, handle ties (Amazon needs accurate reporting), and write readable queries. This mirrors real Amazon problems like "find the best-selling ASIN in each product group."

- **Follow-ups**: 1) Return the top 3 products per category. 2) Exclude products with fewer than 10 total sales. 3) Add a time filter for the last 90 days using a bind variable.

#### Problem: Customers Who Bought All Products in a Category (LC SQL 1045)

- **Difficulty/Frequency**: Hard / Medium

- **SQL Problem Statement**: Find customers who have purchased at least one unit of every product in the 'Electronics' category. Return customer name and the number of electronics products purchased.

- **Interview Walkthrough**: This is a relational division problem — find customers for whom there is no product in the electronics category that they haven't bought. Use a double NOT EXISTS or GROUP BY with COUNT and HAVING. Amazon needs this type of analysis for recommendation systems.

- **SQL Solution**:

```sql
SELECT c.customer_name,
       COUNT(DISTINCT p.product_id) AS electronics_count
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
JOIN categories cat ON p.category_id = cat.category_id
WHERE cat.category_name = 'Electronics'
GROUP BY c.customer_id, c.customer_name
HAVING COUNT(DISTINCT p.product_id) = (
    SELECT COUNT(*)
    FROM products p2
    JOIN categories cat2
        ON p2.category_id = cat2.category_id
    WHERE cat2.category_name = 'Electronics'
);
```

- **Oracle-Specific Syntax**: Oracle supports MINUS operator (same as EXCEPT) for an elegant alternative:
SELECT customer_name FROM customers c WHERE NOT EXISTS (SELECT product_id FROM products p JOIN categories cat ON p.category_id = cat.category_id WHERE cat.category_name = 'Electronics' MINUS SELECT oi.product_id FROM orders o JOIN order_items oi ON o.order_id = oi.order_id WHERE o.customer_id = c.customer_id);

- **What Amazon Evaluates**: Relational division thinking — Amazon needs to find "customers who bought from all subcategories" for its recommendation engine. Understanding of set operations (MINUS/EXCEPT) shows depth.

- **Follow-ups**: 1) Find customers who bought from ALL categories. 2) Find customers who bought at least 3 products from every category. 3) Optimize for a product catalog of 10M+ items.

---

### Lab 04: Security in APEX

#### Problem: Detect Brute-Force Login Attempts (Amazon-specific)

- **Difficulty/Frequency**: Medium / High

- **SQL Problem Statement**: Given a login_attempts table with attempt_id, user_id, ip_address, attempt_time, and success_flag (Y/N), write a query to identify brute-force attacks — defined as 5+ failed attempts from the same IP address within any 15-minute window.

- **Interview Walkthrough**: This is a sliding window problem. Use Oracle's analytic functions with RANGE BETWEEN INTERVAL for temporal sliding windows. Amazon prioritizes security and this scenario mirrors their threat detection systems.

- **SQL Solution**:

```sql
WITH failed_attempts AS (
    SELECT ip_address, attempt_time,
           COUNT(*) OVER (
               PARTITION BY ip_address
               ORDER BY attempt_time
               RANGE BETWEEN INTERVAL '15' MINUTE PRECEDING
                         AND CURRENT ROW
           ) AS attempt_count_15min
    FROM login_attempts
    WHERE success_flag = 'N'
)
SELECT DISTINCT ip_address,
       MIN(attempt_time) OVER (
           PARTITION BY ip_address
       ) AS window_start,
       MAX(attempt_time) OVER (
           PARTITION BY ip_address
       ) AS window_end,
       MAX(attempt_count_15min) AS max_attempts
FROM failed_attempts
WHERE attempt_count_15min >= 5
ORDER BY max_attempts DESC, ip_address;
```

- **Oracle-Specific Syntax**: RANGE BETWEEN INTERVAL '15' MINUTE PRECEDING AND CURRENT ROW is Oracle-specific for temporal sliding windows. Oracle also supports ROWS and RANGE framing modes.

- **What Amazon Evaluates**: Security mindset and ability to handle time-series data with window functions. This maps directly to Amazon's security monitoring systems.

- **Follow-ups**: 1) Include account lockout logic (prevent subsequent attempts after lockout). 2) Detect distributed brute force (same username, many different IPs). 3) Create an APEX dynamic action that alerts the security team when this query returns results.

#### Problem: Mask Sensitive Customer Data (LC SQL 196 variant)

- **Difficulty/Frequency**: Easy / High

- **SQL Problem Statement**: Write a query to mask PII for customer support agents. Mask email addresses by showing first character and domain (j***@example.com). Mask credit card numbers by showing only last 4 digits.

- **Interview Walkthrough**: Use Oracle's string manipulation functions — SUBSTR, INSTR, RPAD/LPAD. Oracle provides powerful built-in functions for data masking at the query level.

- **SQL Solution**:

```sql
SELECT customer_id,
       SUBSTR(email, 1, 1)
           || '***'
           || SUBSTR(email, INSTR(email, '@'))
           AS masked_email,
       '****-****-****-'
           || SUBSTR(credit_card, -4)
           AS masked_cc,
       CASE
           WHEN INSTR(phone, '-') > 0
               THEN SUBSTR(phone, 1, INSTR(phone, '-'))
                    || '***-****'
           ELSE '***-***-'
                || SUBSTR(phone, -4)
       END AS masked_phone
FROM customers;
```

- **Oracle-Specific Syntax**: SUBSTR with negative position (-4) extracts from the end. INSTR finds character positions. Oracle also supports REGEXP_REPLACE for regex-based masking. Oracle 12c+ introduced DBMS_REDACT for transparent data redaction.

- **What Amazon Evaluates**: Practical data protection knowledge. Amazon's Customer Obsession LP requires protecting customer data. Knowing when to mask at the database level versus application level is key.

- **Follow-ups**: 1) Use Oracle's DBMS_REDACT to create a redaction policy. 2) Implement in APEX via an authorization scheme that conditionally applies the mask. 3) Extend to mask address fields (street, city, ZIP) while keeping state visible for analytics.

---

### Lab 05: Interactive Reports

#### Problem: Running Total with Monthly Reset (LC SQL 1308)

- **Difficulty/Frequency**: Medium / Medium

- **SQL Problem Statement**: Calculate a running total of daily sales amounts that resets at the start of each month. Show order_date, daily_total, and running_total.

- **Interview Walkthrough**: Use SUM() with OVER (PARTITION BY month ORDER BY day ROWS UNBOUNDED PRECEDING). The PARTITION BY creates the monthly reset. This is the kind of financial reporting Amazon does for daily sales tracking across product categories.

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

- **Oracle-Specific Syntax**: TRUNC(date) truncates to midnight. EXTRACT(YEAR/MONTH FROM date) is standard. Oracle's ROWS UNBOUNDED PRECEDING is standard SQL.

- **What Amazon Evaluates**: Understanding of running totals with reset — essential for financial reporting. Amazon expects clean handling of date boundaries.

- **Follow-ups**: 1) Add a rolling 7-day average alongside the running total. 2) Handle months with no sales. 3) Aggregate by week with the same monthly reset logic.

#### Problem: Year-over-Year Sales Comparison (Amazon-specific)

- **Difficulty/Frequency**: Medium / High

- **SQL Problem Statement**: Write a query showing monthly sales for the current year alongside the same month from the previous year. Include the YoY percentage change. Show NULL for months that haven't occurred yet in the current year.

- **Interview Walkthrough**: Use LAG with a 12-month offset, or self-join on month with year offset. Amazon needs YoY comparisons constantly for business reviews.

- **SQL Solution**:

```sql
WITH monthly_sales AS (
    SELECT EXTRACT(YEAR FROM order_date) AS yr,
           EXTRACT(MONTH FROM order_date) AS mo,
           SUM(order_amount) AS monthly_total
    FROM orders
    WHERE order_date >= ADD_MONTHS(TRUNC(SYSDATE, 'YYYY'), -24)
    GROUP BY EXTRACT(YEAR FROM order_date),
             EXTRACT(MONTH FROM order_date)
)
SELECT curr.yr AS year,
       curr.mo AS month,
       curr.monthly_total AS current_year_sales,
       prev.monthly_total AS prev_year_sales,
       CASE
           WHEN prev.monthly_total IS NULL THEN NULL
           WHEN prev.monthly_total = 0 THEN NULL
           ELSE ROUND(
               (curr.monthly_total - prev.monthly_total)
               * 100.0 / prev.monthly_total, 2
           )
       END AS yoy_growth_pct
FROM monthly_sales curr
LEFT JOIN monthly_sales prev
    ON curr.mo = prev.mo
   AND curr.yr = prev.yr + 1
WHERE curr.yr = EXTRACT(YEAR FROM SYSDATE)
ORDER BY curr.mo;
```

- **Oracle-Specific Syntax**: ADD_MONTHS for month arithmetic. TRUNC(SYSDATE, 'YYYY') truncates to January 1 of current year. EXTRACT for date part extraction. Oracle's date functions are extensive and well-optimized.

- **What Amazon Evaluates**: Business intelligence SQL skills. Amazon runs on metrics and YoY comparisons are fundamental to their business reviews.

- **Follow-ups**: 1) Add quarter-over-quarter comparison. 2) Create an APEX chart showing the YoY trend. 3) Add a trailing 12-month view instead of calendar year.

---

### Lab 08: Performance Tuning

#### Problem: Optimize an E-commerce Dashboard (Amazon-specific)

- **Difficulty/Frequency**: Hard / High

- **SQL Problem Statement**: A daily sales dashboard query takes 45+ minutes. The query joins 6 tables (orders, order_items, products, customers, inventory, shipments) and filters on the last 90 days. The orders table has 50M rows. Write an optimized version using materialized views, partitioning, and query restructuring.

- **Interview Walkthrough**: Amazon requires obsession over performance. The bottleneck is likely the orders table without proper date indexing. Use a materialized view for pre-aggregation. Push filters into subqueries. Use parallel execution hints.

- **SQL Solution**:

```sql
CREATE MATERIALIZED VIEW LOG ON orders
WITH ROWID, PRIMARY KEY
    (order_id, order_date, customer_id, total_amount)
INCLUDING NEW VALUES;

CREATE MATERIALIZED VIEW mv_daily_sales_summary
REFRESH FAST ON COMMIT
ENABLE QUERY REWRITE
AS
SELECT TRUNC(o.order_date) AS order_day,
       p.category_id,
       COUNT(DISTINCT o.order_id) AS order_count,
       COUNT(oi.product_id) AS units_sold,
       SUM(oi.quantity * oi.unit_price) AS revenue,
       COUNT(DISTINCT o.customer_id) AS unique_customers
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.order_date >= TRUNC(SYSDATE) - 90
GROUP BY TRUNC(o.order_date), p.category_id;

SELECT /*+ PARALLEL(4) */
       mv.order_day,
       c.category_name,
       mv.order_count,
       mv.units_sold,
       mv.revenue,
       mv.unique_customers,
       ROUND(mv.revenue / NULLIF(mv.units_sold, 0), 2)
           AS avg_unit_price
FROM mv_daily_sales_summary mv
JOIN categories c ON mv.category_id = c.category_id
WHERE mv.order_day >= TRUNC(SYSDATE) - 90
ORDER BY mv.order_day DESC, c.category_name;
```

- **Oracle-Specific Syntax**: Materialized view logs, REFRESH FAST ON COMMIT, and QUERY REWRITE are Oracle-specific. PARALLEL hint enables parallel execution. NULLIF prevents division by zero.

- **What Amazon Evaluates**: Understanding of real-world performance optimization at scale. Amazon wants to see you think about the full lifecycle: schema design, indexing strategy, materialization, query optimization, and monitoring.

- **Follow-ups**: 1) Design the MV refresh strategy for near-real-time data (every 5 minutes). 2) Add partitioning to the orders table by date range (monthly). 3) Set up an APEX report against this MV with drill-down to daily detail.

---

## APEX-Specific Deep Dive Questions

1. **How would you design an APEX application that supports Amazon's multi-tenant marketplace model?** Discuss workspace isolation, data partitioning by seller (row-level vs schema-level), and how to ensure one seller's data is never visible to another. Connect this to Customer Obsession.

2. **Describe how to build an inventory management dashboard in APEX showing real-time stock levels across multiple warehouses.** Discuss data refresh strategies, AJAX polling vs WebSocket, and how to handle stale data gracefully.

3. **How do you ensure APEX applications meet Amazon's bar for operational excellence?** Discuss error handling, logging, monitoring, alarming, and integration with monitoring tools.

4. **Explain how to build a seller analytics portal with customizable dashboards, scheduled report delivery, and data export.** Discuss dynamic report generation architecture and handling 100+ concurrent seller requests.

---

## System Design Questions

1. **Design a pricing and promotions engine** for an e-commerce platform where rules change frequently. Discuss storing dynamic pricing rules in Oracle, how APEX provides the admin interface, and how to ensure price calculations meet real-time SLAs (< 100ms). Cover caching strategies and invalidation.

2. **Design a recommendation system database schema** that tracks customer behavior (views, purchases, cart additions). Discuss modeling user-item interactions, precomputing recommendations, and handling the cold-start problem for new users.

3. **Design a global order management system** tracking orders across multiple countries with different currencies, tax rules, and shipping providers. Discuss schema design, currency conversion, tax calculation integration, and APEX interfaces for operations teams.

---

## Behavioral Questions

1. **Tell me about a time you delivered a complex APEX project under a tight deadline.**

   - **S**ituation: Client needed a compliance reporting APEX application in 4 weeks (normally 12-week project).

   - **T**ask: Deliver a production-ready application with zero defects.

   - **A**ction: Prioritized features using MoSCoW analysis, built core data model first, used Agile sprints with daily demos, automated testing, and negotiated scope trade-offs transparently with the client.

   - **R**esult: Delivered in 4 weeks with all must-have features. Client satisfaction was high and they extended the contract.

   - **L**eadership Principle: Deliver Results, Bias for Action.

2. **Describe a time you had a disagreement with a stakeholder about technical direction.**

   - **S**ituation: Stakeholder insisted on building a custom report engine; I recommended using APEX Interactive Reports.

   - **T**ask: Convince the stakeholder while maintaining the relationship.

   - **A**ction: Built a side-by-side POC showing IR capabilities vs custom build. Showed IRs would save 6 weeks. Addressed customization concerns with documented extension points.

   - **R**esult: Stakeholder agreed to IRs. Saved 6 weeks used for additional features.

   - **L**eadership Principle: Customer Obsession, Have Backbone; Disagree and Commit.

3. **Tell me about a time you identified a critical bug in production.**

   - **S**ituation: APEX financial application showed incorrect calculations due to a rounding error in PL/SQL.

   - **T**ask: Fix immediately and prevent recurrence.

   - **A**ction: Identified root cause (BINARY_DOUBLE vs NUMBER for currency). Applied hotfix. Created unit test suite for all financial calculations. Implemented code review checklist for data types.

   - **R**esult: Zero discrepancies post-fix. Test suite caught 3 similar issues.

   - **L**eadership Principle: Insist on the Highest Standards, Dive Deep.

4. **Describe a time you invented a simple solution to a complex problem.**

   - **S**ituation: Complex multi-step approval workflow causing user confusion and delays.

   - **T**ask: Simplify without losing compliance.

   - **A**ction: Mapped the full workflow, identified 3 parallelizable steps. Used APEX built-in approval capabilities instead of custom PL/SQL state machine.

   - **R**esult: Approval time reduced 60%. User errors dropped 80%.

   - **L**eadership Principle: Invent and Simplify.

5. **Tell me about a time you mentored someone on your team.**

   - **S**ituation: New hire struggled with Oracle SQL and APEX concepts.

   - **T**ask: Bring them to productivity without sacrificing own deliverables.

   - **A**ction: Created structured onboarding plan with weekly goals. Paired on complex tickets then gradually transitioned ownership.

   - **R**esult: Team member became independent in 8 weeks. Later became APEX SME.

   - **L**eadership Principle: Hire and Develop the Best.

---

## Study Plan

### Priority Labs by Interview Impact

| Priority | Lab | Why It Matters for Amazon Interviews |
|----------|-----|--------------------------------------|
| P0 | Lab 01: Getting Started | Foundation for all SQL problems Amazon asks |
| P0 | Lab 08: Performance | Scale optimization is critical at Amazon |
| P1 | Lab 05: Interactive Reports | Data reporting maps to Amazon analytics needs |
| P1 | Lab 04: Security | Customer trust is Amazon's #1 priority |
| P2 | Lab 06: RESTful Services | API design for microservices architecture |
| P2 | Lab 03: Advanced Components | Shows breadth of APEX knowledge |
| P3 | Lab 02: Page Designer | Familiarity expected, not tested directly |
| P3 | Lab 07: Migration | Lower priority unless your background fits |

---

## Tips

### Company-Specific APEX Interview Strategies

- **Leadership Principles Are Everything**: Amazon interviews are built around LPs. For every answer, mentally map it to 2-3 LPs and use the LP names in your responses. Customer Obsession, Ownership, Deliver Results, and Dive Deep are most relevant for APEX roles.

- **Use STAR+B Format**: Situation, Task, Action, Result, and tie back to a Leadership Principle. Amazon interviewers literally check boxes during your answers.

- **Prepare for the Bar Raiser**: The Bar Raiser has veto power. They evaluate cultural fit and LP alignment. Show you raise standards, not just meet them.

- **Show Ownership**: Use "I" not "we." Talk about decisions you owned and their outcomes. Discuss going beyond defined scope.

- **Bias for Action**: Show examples where you prioritized shipping over perfecting. In APEX, this means rapid prototyping and iterative development.

- **Think at Scale**: Even if your APEX experience was small, discuss how your design decisions would scale to Amazon's size.

- **E-commerce Domain Knowledge**: Study Amazon's core business. Practice designing data models for orders, inventory, payments, fulfillment.

- **Prepare for SQL Online Assessment**: Practice timed SQL problems covering joins, aggregations, window functions. Time management is critical.

- **Customer Obsession Stories**: Have 2+ stories showing deep user need understanding. For APEX, user research before building, usability testing, accessibility improvements.

- **Be Ready for "Why Amazon?"**: Have an authentic answer connecting APEX to Amazon's mission of being Earth's most customer-centric company.

### Lab 03: Advanced Components

#### Problem: Dynamic Pivot of Sales by Product Category (Amazon-specific)

- **Difficulty/Frequency**: Hard / High

- **SQL Problem Statement**: Write a query that dynamically pivots monthly sales data. Columns should be product categories, rows should be months. The number of categories is unknown at query writing time.

- **Interview Walkthrough**: Use Oracle's PIVOT operator for static pivot, or a dynamic SQL approach using XML or REF CURSOR for dynamic pivot. Amazon needs this for their product catalog analytics.

- **SQL Solution**:

`sql
-- Static pivot using Oracle PIVOT
SELECT * FROM (
    SELECT TO_CHAR(s.sale_date, 'MON-YYYY') AS sale_month,
           c.category_name,
           SUM(s.amount) AS total_sales
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    JOIN categories c ON p.category_id = c.category_id
    WHERE s.sale_date >= ADD_MONTHS(SYSDATE, -12)
    GROUP BY TO_CHAR(s.sale_date, 'MON-YYYY'),
             c.category_name
)
PIVOT (
    SUM(total_sales)
    FOR category_name IN (
        'Electronics' AS electronics,
        'Clothing' AS clothing,
        'Books' AS books,
        'Home' AS home_goods
    )
)
ORDER BY MIN(TO_DATE(sale_month, 'MON-YYYY'));

-- Dynamic pivot using XML
SELECT * FROM (
    SELECT TO_CHAR(s.sale_date, 'MON-YYYY') AS sale_month,
           c.category_name,
           SUM(s.amount) AS total_sales
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    JOIN categories c ON p.category_id = c.category_id
    GROUP BY TO_CHAR(s.sale_date, 'MON-YYYY'),
             c.category_name
)
PIVOT XML (
    SUM(total_sales)
    FOR category_name IN (SELECT category_name FROM categories)
)
ORDER BY 1;
`

- **Oracle-Specific Syntax**: PIVOT operator (Oracle 11g+) transforms rows to columns. PIVOT XML generates dynamic pivot when column values are unknown. ADD_MONTHS for date arithmetic.

- **What Amazon Evaluates**: Advanced data transformation skills. Amazon's business intelligence relies on pivoting product data across multiple dimensions.

- **Follow-ups**: 1) Write a dynamic SQL procedure that generates pivot query. 2) Add grand total column per row. 3) Create an APEX IR with pivot functionality.

#### Problem: Find Products Frequently Bought Together (Market Basket Analysis)

- **Difficulty/Frequency**: Hard / High

- **SQL Problem Statement**: Given an orders table, find pairs of products that are frequently purchased together in the same order (at least 5% of orders that contain one product also contain the other). Return product pair and support percentage.

- **Interview Walkthrough**: Self-join order_items table to find co-occurring products. Use COUNT with ratio calculation. Amazon's core recommendation engine relies on this type of analysis.

- **SQL Solution**:

`sql
WITH product_pairs AS (
    SELECT oi1.product_id AS product_a,
           oi2.product_id AS product_b,
           COUNT(DISTINCT oi1.order_id) AS pair_count
    FROM order_items oi1
    JOIN order_items oi2
        ON oi1.order_id = oi2.order_id
       AND oi1.product_id < oi2.product_id
    GROUP BY oi1.product_id, oi2.product_id
),
product_totals AS (
    SELECT product_id,
           COUNT(DISTINCT order_id) AS order_count
    FROM order_items
    GROUP BY product_id
)
SELECT pp.product_a,
       pp.product_b,
       pp.pair_count,
       ROUND(pp.pair_count * 100.0 / pt.order_count, 2)
           AS support_pct
FROM product_pairs pp
JOIN product_totals pt ON pp.product_a = pt.product_id
WHERE pp.pair_count * 100.0 / pt.order_count >= 5.0
ORDER BY support_pct DESC;
`

- **Oracle-Specific Syntax**: Self-join with inequality condition (product_a < product_b) to avoid duplicate pairs. DISTINCT in COUNT for accurate co-occurrence.

- **What Amazon Evaluates**: Understanding of market basket analysis and association rule mining. Amazon's recommendation engine generates significant revenue from cross-selling.

- **Follow-ups**: 1) Calculate confidence and lift metrics. 2) Find triple-product combinations. 3) Create an APEX dashboard showing product affinity networks.

### Lab 06: RESTful Services

#### Problem: Inventory Check REST Endpoint (Amazon-specific)

- **Difficulty/Frequency**: Medium / Medium

- **SQL Problem Statement**: Create an ORDS REST handler that accepts a list of product IDs and returns real-time inventory availability for each product across all warehouses.

- **Interview Walkthrough**: Amazon needs real-time inventory checks. Use JSON_TABLE to parse input array.

- **SQL Solution**:

`sql
SELECT JSON_OBJECT(
    KEY 'request_id' VALUE :p_request_id,
    KEY 'products' VALUE (
        SELECT JSON_ARRAYAGG(
            JSON_OBJECT(
                KEY 'product_id' VALUE p.product_id,
                KEY 'product_name' VALUE p.product_name,
                KEY 'total_inventory' VALUE
                    NVL(SUM(i.quantity_on_hand), 0),
                KEY 'warehouses' VALUE (
                    SELECT JSON_ARRAYAGG(
                        JSON_OBJECT(
                            KEY 'warehouse' VALUE w.code,
                            KEY 'quantity' VALUE i.quantity_on_hand
                        )
                    )
                    FROM inventory i
                    JOIN warehouses w
                        ON i.warehouse_id = w.warehouse_id
                    WHERE i.product_id = p.product_id
                )
            )
        )
        FROM products p
        LEFT JOIN inventory i
            ON p.product_id = i.product_id
        WHERE p.product_id IN (
            SELECT COLUMN_VALUE
            FROM JSON_TABLE(:p_product_ids, '$[*]'
                COLUMNS (product_id NUMBER PATH '$')
            )
        )
        GROUP BY p.product_id, p.product_name
    )
) AS inventory_response
FROM DUAL;
`

- **Oracle-Specific Syntax**: JSON_TABLE parses JSON arrays into rows. COLUMN_VALUE for collection elements. NVL for NULL quantities.

- **What Amazon Evaluates**: Real-time data access patterns and JSON parsing. Amazon's systems require low-latency inventory checks.

- **Follow-ups**: 1) Add low-stock alerts. 2) Implement caching for hot products. 3) Add estimated restock date for out-of-stock items.
