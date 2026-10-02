-- =====================================================================
-- WORKED EXAMPLE: Interactive Reports - Complete SQL/PLSQL
-- Lab 03: Interactive Reports
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. SAMPLE SCHEMA FOR EXERCISES
-- ---------------------------------------------------------------------

-- Sales table (base table for IR exercises)
CREATE TABLE sales (
    sale_id         NUMBER PRIMARY KEY,
    product_name    VARCHAR2(200) NOT NULL,
    sale_date       DATE NOT NULL,
    amount          NUMBER(12,2) NOT NULL,
    customer_name   VARCHAR2(200),
    region          VARCHAR2(50),
    sales_rep       VARCHAR2(100),
    status          VARCHAR2(20) DEFAULT 'COMPLETED'
);

CREATE INDEX idx_sales_date ON sales(sale_date);
CREATE INDEX idx_sales_product ON sales(product_name);
CREATE INDEX idx_sales_customer ON sales(customer_name);
CREATE INDEX idx_sales_rep ON sales(sales_rep);

CREATE SEQUENCE sales_seq START WITH 1000;

-- Generate 500K sample rows
BEGIN
    FOR i IN 1..500000 LOOP
        INSERT INTO sales VALUES (
            sales_seq.NEXTVAL,
            'Product ' || MOD(i, 1000),
            SYSDATE - DBMS_RANDOM.VALUE(0, 365),
            ROUND(DBMS_RANDOM.VALUE(10, 5000), 2),
            'Customer ' || MOD(i, 5000),
            CASE MOD(i, 4) WHEN 0 THEN 'NORTH' WHEN 1 THEN 'SOUTH' WHEN 2 THEN 'EAST' ELSE 'WEST' END,
            'Rep ' || MOD(i, 50),
            CASE MOD(i, 10) WHEN 0 THEN 'PENDING' WHEN 1 THEN 'CANCELLED' ELSE 'COMPLETED' END
        );
    END LOOP;
    COMMIT;
END;
/

-- Orders/Order Items for Master-Detail exercises
CREATE TABLE orders (
    order_id      NUMBER PRIMARY KEY,
    customer_name VARCHAR2(200),
    order_date    DATE,
    status        VARCHAR2(20),
    total_amount  NUMBER(12,2)
);

CREATE TABLE order_items (
    item_id       NUMBER PRIMARY KEY,
    order_id      NUMBER REFERENCES orders(order_id) ON DELETE CASCADE,
    product_name  VARCHAR2(200),
    quantity      NUMBER,
    unit_price    NUMBER(10,2),
    line_total    NUMBER(12,2) GENERATED ALWAYS AS (quantity * unit_price) VIRTUAL
);

CREATE SEQUENCE order_seq START WITH 1000;
CREATE SEQUENCE item_seq START WITH 10000;

INSERT INTO orders VALUES (1001, 'Acme Corp', SYSDATE-5, 'SHIPPED', 299.99);
INSERT INTO orders VALUES (1002, 'Globex Inc', SYSDATE-3, 'PENDING', 549.50);
INSERT INTO order_items VALUES (10001, 1001, 'Widget A', 2, 49.99);
INSERT INTO order_items VALUES (10002, 1001, 'Widget B', 1, 199.99);
INSERT INTO order_items VALUES (10003, 1002, 'Gadget X', 1, 549.50);
COMMIT;

-- ---------------------------------------------------------------------
-- 2. EXERCISE 1: DYNAMIC DATE-RANGE + SEARCH FILTER
-- ---------------------------------------------------------------------

-- Page Items: P1_DATE_RANGE (Select List: 30,60,90), P1_SEARCH (Text)
-- IR Region Source:
SELECT sale_id, product_name, sale_date, amount, customer_name, region, sales_rep, status
FROM sales
WHERE sale_date >= CASE :P1_DATE_RANGE
    WHEN '30' THEN SYSDATE - 30
    WHEN '60' THEN SYSDATE - 60
    WHEN '90' THEN SYSDATE - 90
    ELSE SYSDATE - 30
END
AND (INSTR(UPPER(product_name), UPPER(:P1_SEARCH)) > 0 OR :P1_SEARCH IS NULL)
ORDER BY sale_date DESC;

-- Alternative using bind variables directly in query (recommended):
SELECT sale_id, product_name, sale_date, amount, customer_name, region, sales_rep, status
FROM sales
WHERE sale_date >= 
    CASE :P1_DATE_RANGE
        WHEN '30' THEN SYSDATE - 30
        WHEN '60' THEN SYSDATE - 60
        WHEN '90' THEN SYSDATE - 90
        ELSE SYSDATE - 30
    END
AND (:P1_SEARCH IS NULL OR UPPER(product_name) LIKE '%' || UPPER(:P1_SEARCH) || '%')
ORDER BY sale_date DESC;

-- ---------------------------------------------------------------------
-- 3. EXERCISE 2: MASTER-DETAIL IR (PAGE NAVIGATION)
-- ---------------------------------------------------------------------

-- PAGE 1 (Master) - IR on orders
-- Link Column: ORDER_ID
-- Target: Page 2, Set P2_ORDER_ID = #ORDER_ID#
-- URL: f?p=&APP_ID.:2:&SESSION.::::P2_ORDER_ID:#ORDER_ID#

SELECT order_id, customer_name, order_date, status, total_amount
FROM orders
ORDER BY order_date DESC;

-- PAGE 2 (Detail) - IR on order_items
-- Page Mode: Modal Dialog
-- Source:
SELECT item_id, product_name, quantity, unit_price, line_total
FROM order_items
WHERE order_id = :P2_ORDER_ID
ORDER BY item_id;

-- ---------------------------------------------------------------------
-- 4. EXERCISE 3: MULTI-ROW SELECTION + CSV DOWNLOAD
-- ---------------------------------------------------------------------

-- IR: Enable Row Selection = Yes
-- Button: "Download Selected" → Dynamic Action → Execute PL/SQL

DECLARE
    l_csv CLOB;
    l_ids APEX_T_NUMBER := APEX_T_NUMBER();
BEGIN
    -- Collect selected ORDER_IDs from G_F01 array
    FOR i IN 1..APEX_APPLICATION.G_F01.COUNT LOOP
        l_ids.EXTEND;
        l_ids(l_ids.LAST) := TO_NUMBER(APEX_APPLICATION.G_F01(i));
    END LOOP;

    -- Generate CSV using APEX_DATA_EXPORT
    l_csv := APEX_DATA_EXPORT.EXPORT(
        p_format => 'CSV',
        p_query  => 'SELECT * FROM orders WHERE order_id IN (SELECT * FROM TABLE(:ids))',
        p_binds  => APEX_DATA_EXPORT.T_BINDS('ids' => l_ids)
    );

    -- Store in page item for JavaScript download
    :P1_CSV_DATA := l_csv;
END;

-- JavaScript True Action (Execute JavaScript):
/*
var csv = apex.item('P1_CSV_DATA').getValue();
var blob = new Blob([csv], {type: 'text/csv;charset=utf-8;'});
var url = URL.createObjectURL(blob);
var a = document.createElement('a');
a.href = url;
a.download = 'selected_orders_' + new Date().toISOString().slice(0,10) + '.csv';
document.body.appendChild(a);
a.click();
document.body.removeChild(a);
URL.revokeObjectURL(url);
*/

-- ---------------------------------------------------------------------
-- 5. EXERCISE 4: EMAIL SELECTED ROWS AS CSV
-- ---------------------------------------------------------------------

-- Page Item: P1_EMAIL (Text, default: &APP_USER.)
-- Button: "Email Report" → Dynamic Action → Execute PL/SQL

DECLARE
    l_csv CLOB;
    l_ids APEX_T_NUMBER := APEX_T_NUMBER();
BEGIN
    FOR i IN 1..APEX_APPLICATION.G_F01.COUNT LOOP
        l_ids.EXTEND;
        l_ids(l_ids.LAST) := TO_NUMBER(APEX_APPLICATION.G_F01(i));
    END LOOP;

    l_csv := APEX_DATA_EXPORT.EXPORT(
        p_format => 'CSV',
        p_query  => 'SELECT * FROM orders WHERE order_id IN (SELECT * FROM TABLE(:ids))',
        p_binds  => APEX_DATA_EXPORT.T_BINDS('ids' => l_ids)
    );

    APEX_MAIL.SEND(
        p_to        => :P1_EMAIL,
        p_from      => 'noreply@company.com',
        p_subj      => 'Orders Report - ' || TO_CHAR(SYSDATE, 'YYYY-MM-DD HH24:MI'),
        p_body      => 'Please find attached the selected orders report.',
        p_att_names => 'orders_report.csv',
        p_att_mime  => 'text/csv',
        p_att_clob  => l_csv
    );
    COMMIT; -- Critical: commits to mail queue

    :P1_MAIL_STATUS := 'Email queued to ' || :P1_EMAIL || ' at ' || TO_CHAR(SYSDATE, 'HH24:MI:SS');
END;

-- Verify mail queue:
SELECT mail_id, to_address, subject, status, created_on, error_message
FROM apex_mail_queue
WHERE created_on > SYSDATE - 1/24
ORDER BY created_on DESC;

-- ---------------------------------------------------------------------
-- 6. EXERCISE 5: PERFORMANCE OPTIMIZATION
-- ---------------------------------------------------------------------

-- IR Settings for 500K row table:
-- Pagination Type: Server
-- Rows Per Page: 15
-- Maximum Row Count: 500
-- Search Column(s): PRODUCT_NAME (not ALL)

-- Verify execution plan:
EXPLAIN PLAN FOR
SELECT sale_id, product_name, sale_date, amount, customer_name
FROM sales
WHERE sale_date >= SYSDATE - 30
  AND UPPER(product_name) LIKE '%MOUSE%';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);

-- Expected good plan:
-- | Id | Operation                    | Name            | Rows |
-- |  0 | SELECT STATEMENT             |                 |   50 |
-- |  1 |  VIEW                        |                 |   50 |
-- |  2 |   WINDOW SORT PUSHED RANK    |                 |   50 |
-- |  3 |    TABLE ACCESS BY INDEX ROWID| SALES          | 1000 |
-- |  4 |     INDEX RANGE SCAN         | IDX_SALES_DATE  | 1000 |

-- ---------------------------------------------------------------------
-- 7. EXERCISE 6: MATERIALIZED VIEW FOR AGGREGATION
-- ---------------------------------------------------------------------

-- Step 1: Create MV Log (prerequisite for FAST REFRESH)
CREATE MATERIALIZED VIEW LOG ON sales
WITH ROWID, SEQUENCE (sale_date, amount)
INCLUDING NEW VALUES;

-- Step 2: Create Materialized View
CREATE MATERIALIZED VIEW sales_daily_mv
BUILD IMMEDIATE
REFRESH FAST ON COMMIT
AS 
SELECT TRUNC(sale_date) AS sale_day,
       COUNT(*) AS order_count,
       SUM(amount) AS total_sales,
       AVG(amount) AS avg_order,
       MIN(amount) AS min_order,
       MAX(amount) AS max_order
FROM sales
GROUP BY TRUNC(sale_date);

CREATE INDEX idx_sales_daily_day ON sales_daily_mv(sale_day);

-- Step 3: IR on MV (instant response for daily aggregates)
SELECT sale_day, order_count, total_sales, avg_order
FROM sales_daily_mv
WHERE sale_day >= :P1_START_DATE
  AND sale_day <= :P1_END_DATE
ORDER BY sale_day DESC;

-- Verify MV refresh:
INSERT INTO sales VALUES (sales_seq.NEXTVAL, 'Test Product', SYSDATE, 999.99, 'Test Customer', 'NORTH', 'Rep 1', 'COMPLETED');
COMMIT;

SELECT * FROM sales_daily_mv WHERE sale_day = TRUNC(SYSDATE);

-- ---------------------------------------------------------------------
-- 8. EXERCISE 7: SAVED REPORTS & SUBSCRIPTIONS
-- ---------------------------------------------------------------------

-- Saved Report (via UI Actions → Report → Save Report):
-- Name: "High Value Orders"
-- Filters: AMOUNT > 1000, STATUS = 'COMPLETED'
-- Sort: AMOUNT DESC
-- Columns: Hide REGION, SALES_REP
-- Public: Yes

-- Subscription (via UI Actions → Subscription → Create):
-- Name: "Daily High Value Summary"
-- Report: "High Value Orders"
-- Schedule: Daily, 08:00
-- Format: CSV
-- Email: &APP_USER.

-- Query subscriptions:
SELECT subscription_id, name, schedule, format, email_to, last_sent, next_run
FROM apex_application_subscriptions
WHERE application_id = :APP_ID;

-- ---------------------------------------------------------------------
-- 9. EXERCISE 8: IR JAVASCRIPT API - PROGRAMMATIC FILTER
-- ---------------------------------------------------------------------

-- IR Static ID: SALES_IR
-- Button: "Last 7 Days" → Dynamic Action → Execute JavaScript

/*
var ir = apex.region('SALES_IR').widget();

// Clear existing filters
ir.interactiveReport('clearFilters');

// Calculate 7 days ago
var sevenDaysAgo = new Date();
sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
var dateStr = sevenDaysAgo.toISOString().split('T')[0]; // YYYY-MM-DD

// Set filter on SALE_DATE column (operator >=)
ir.interactiveReport('setFilter', 'SALE_DATE', '>=' + dateStr);

// Refresh to apply
ir.interactiveReport('refresh');
*/

-- Alternative: Set multiple filters
/*
ir.interactiveReport('setFilter', 'STATUS', 'COMPLETED');
ir.interactiveReport('setFilter', 'AMOUNT', '>1000');
ir.interactiveReport('refresh');
*/

-- ---------------------------------------------------------------------
-- 10. EXERCISE 9: RESET ALL FILTERS BUTTON
-- ---------------------------------------------------------------------

-- Button: "Reset Filters" → Dynamic Action → Execute JavaScript

/*
var ir = apex.region('SALES_IR').widget();
ir.interactiveReport('clearFilters');
ir.interactiveReport('refresh');

// Also reset page items if used for filtering
apex.item('P1_DATE_RANGE').setValue('30');
apex.item('P1_SEARCH').setValue('');
*/

-- ---------------------------------------------------------------------
-- 11. EXERCISE 10: COLUMN-LEVEL SECURITY (VPD SIMULATION)
-- ---------------------------------------------------------------------

-- Authorization Scheme: IS_MANAGER
-- Type: PL/SQL Function Body
-- Code:
/*
RETURN :APP_USER IN ('MANAGER1','MANAGER2','ADMIN');
*/

-- Apply to IR Column: COST (or AMOUNT in our schema)
-- Column Attributes → Authorization Scheme → IS_MANAGER

-- Test: Login as regular user → column hidden
-- Test: Login as MANAGER1 → column visible
-- Export respects authorization automatically

-- ---------------------------------------------------------------------
-- 12. ADVANCED: CUSTOM IR PLUGIN SKELETON
-- ---------------------------------------------------------------------

/*
CREATE OR REPLACE PACKAGE BODY my_ir_plugin AS

FUNCTION render(p_region IN apex_plugin.t_region, ...)
RETURN apex_plugin.t_region_render_result IS
    l_query VARCHAR2(32767);
BEGIN
    -- Custom logic: dynamic columns, complex joins, etc.
    l_query := 'SELECT ... FROM ... WHERE ...';
    
    -- Execute and render as HTML table or JSON for JS grid
    -- HTP.P('<table>...');
    
    RETURN NULL;
END;

FUNCTION ajax(p_region IN apex_plugin.t_region, ...)
RETURN apex_plugin.t_region_ajax_result IS
BEGIN
    -- Handle filter/sort/paginate via apex.server.process
    -- Return JSON
END;

END my_ir_plugin;
*/

-- ---------------------------------------------------------------------
-- 13. VERIFICATION & CLEANUP
-- ---------------------------------------------------------------------

-- Check IR performance:
SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(FORMAT => 'ALLSTATS LAST'));

-- Check mail queue:
SELECT * FROM apex_mail_queue WHERE status != 'SENT';

-- Check MV status:
SELECT mview_name, refresh_mode, refresh_method, last_refresh_date, staleness
FROM user_mviews;

-- Cleanup (if needed):
-- DROP MATERIALIZED VIEW sales_daily_mv;
-- DROP MATERIALIZED VIEW LOG ON sales;
-- DROP TABLE sales PURGE;

-- =====================================================================
-- END OF WORKED EXAMPLE
-- =====================================================================