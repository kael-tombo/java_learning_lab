# Problem Walkthrough: Interactive Reports

## Problem 1: Interactive Report with Custom Filter — Oracle
### APEX Interview Scenario
"An Oracle customer needs an Interactive Report that shows sales data with a complex filter: last 30, 60, or 90 days, and a search box for product name."

### The Problem
Build an Interactive Report on `sales` table with dynamic date-range filter and product search.

### Solution Walkthrough
1. **Create Interactive Report Region** — Source: `SELECT * FROM sales`
2. **Add Page Items** — P1_DATE_RANGE (Select List: '30 Days','60 Days','90 Days'), P1_SEARCH (Text Field)
3. **Modify Report WHERE Clause** — In region attributes, set `WHERE`:
   ```sql
   sale_date >= CASE :P1_DATE_RANGE
       WHEN '30' THEN SYSDATE - 30
       WHEN '60' THEN SYSDATE - 60
       WHEN '90' THEN SYSDATE - 90
       ELSE SYSDATE - 30
   END
   AND (INSTR(UPPER(product_name), UPPER(:P1_SEARCH)) > 0 OR :P1_SEARCH IS NULL)
   ```
4. **Enable Search Bar** — APEX built-in search works on all columns
5. **Add Reset Button** — Dynamic Action to clear filters and items
6. **Enable Actions Menu** — Download, chart, group by

### Code
```sql
-- Alternative: use bind variables in report SQL
SELECT sale_id, product_name, sale_date, amount, customer_name
FROM sales
WHERE sale_date >= NVL(:P1_DATE_RANGE, SYSDATE - 30)
  AND (:P1_SEARCH IS NULL OR product_name LIKE '%' || :P1_SEARCH || '%')
ORDER BY sale_date DESC;
```

### Company Evaluation
- **Oracle**: IR architecture, column filtering, saved reports, subscriptions
- **Deloitte**: Client training on IR features, ad-hoc reporting demos
- **Accenture**: Standardized report templates, consistent filter UX

---

## Problem 2: Master-Detail IR with Linking — Deloitte
### APEX Interview Scenario
"Deloitte's client wants a master-detail view: click a row in the order IR to see line items in a detail IR."

### Problem
Build a master-detail Interactive Report: Orders (master) → Order Items (detail). Navigate without page reload.

### Solution Walkthrough
1. **Create Master IR** — Orders with link column
2. **Set Link Column** — Column link: `f?p=&APP_ID.:2:&SESSION.:::P2_ORDER_ID:#ORDER_ID#`
3. **Create Detail Page (Page 2)** — Interactive Report on `order_items`
4. **Set Detail Report Source** — `SELECT * FROM order_items WHERE order_id = :P2_ORDER_ID`
5. **Add Back Button** — Navigation back to master page
6. **Modal Dialog Option** — Use "Modal Dialog" page type for detail without leaving master
7. **Configure Dialog Attributes** — Width, height, title template

### Code
```sql
-- Master IR query
SELECT order_id, customer_name, order_date, status, total_amount
FROM orders
ORDER BY order_date DESC;

-- Detail IR query
SELECT line_item_id, product_name, quantity, unit_price, (quantity * unit_price) AS line_total
FROM order_items
WHERE order_id = :P2_ORDER_ID;
```

### Company Evaluation
- **Deloitte**: Clean UX patterns, intuitive navigation, client presentation
- **Accenture**: Modal dialog patterns for scalable app design
- **Oracle**: Link column configuration, page item passing via URL

---

## Problem 3: Interactive Report Download & Email — Accenture
### APEX Interview Scenario
"Accenture needs to add a 'Download & Email' button to an Interactive Report. Users select rows, click button, and receive a CSV attachment."

### Problem
Add multi-row selection to an IR, then email selected data as CSV.

### Solution Walkthrough
1. **Enable Row Selection** — IR attribute "Enable Row Selection" = `Yes`, set "Selection Column" position
2. **Add Button** — "Download & Email" button in region header
3. **Dynamic Action on Button Click** — Execute PL/SQL
4. **PL/SQL Code**:
   - Parse `APEX_APPLICATION.G_F01` array for selected row IDs
   - Build CSV using `APEX_DATA_EXPORT.EXPORT`
   - Send email with `APEX_MAIL.SEND` attaching the CSV
5. **Set Up Mail** — Configure `APEX_MAIL` with SMTP server

### Code
```sql
DECLARE
    l_csv CLOB;
    l_ids APEX_T_NUMBER;
BEGIN
    -- Collect selected IDs from IR row selection
    FOR i IN 1..APEX_APPLICATION.G_F01.COUNT LOOP
        l_ids.EXTEND;
        l_ids(l_ids.LAST) := APEX_APPLICATION.G_F01(i);
    END LOOP;

    -- Generate CSV
    SELECT APEX_DATA_EXPORT.EXPORT(
        p_format   => 'CSV',
        p_query    => 'SELECT * FROM orders WHERE order_id IN (SELECT * FROM TABLE(:ids))',
        -- <!-- UNVERIFIED T_BINDS FORM: PROBLEM_WALKTHROUGH/THEORY show T_BINDS(1 => 'ids') while SQL/CODE_DEEP_DIVE show T_BINDS('ids' => l_ids). The two forms disagree and must be reconciled against the APEX docs. -->
        p_binds    => APEX_DATA_EXPORT.T_BINDS(1 => 'ids')
    ) INTO l_csv FROM DUAL;

    -- Send email
    APEX_MAIL.SEND(
        p_to        => :P1_EMAIL,
        p_from      => 'noreply@company.com',
        p_subj      => 'Your Report',
        p_body      => 'Attached CSV of selected orders.',
        p_att_names => 'orders.csv',
        p_att_mime  => 'text/csv',
        p_att_clob  => l_csv
    );
    COMMIT;
END;
/
```

### Company Evaluation
- **Accenture**: Business process automation, email integration, bulk operations
- **Deloitte**: Client-friendly feature, user training for selection workflows
- **Oracle**: APEX_DATA_EXPORT API, APEX_MAIL configuration

---

## Problem 4: Performance-Optimized IR — Oracle
### APEX Interview Scenario
"Oracle's client has an IR query returning 500K+ rows. The page hangs. Optimize."

### Problem
Interactive Report on a large table is slow to load and hangs on filtering.

### Solution Walkthrough
1. **Add Pagination** — Set "Maximum Row Count" (default 500)
2. **Enable "Server-side Pagination"** — Reduces data transfer
3. **Add Indexes** — Create indexes on filtered columns
   ```sql
   CREATE INDEX idx_sales_date ON sales(sale_date);
   CREATE INDEX idx_sales_product ON sales(product_name);
   ```
4. **Use Materialized View** — Pre-aggregate data for fast IR:
   ```sql
   CREATE MATERIALIZED VIEW sales_daily_mv
   AS SELECT TRUNC(sale_date) AS day, COUNT(*) AS cnt, SUM(amount) AS total
      FROM sales GROUP BY TRUNC(sale_date);
   ```
5. **Set IR "Where Clause"** — Use bind variables to leverage indexes
6. **Disable "Search on All Columns"** — Limit search to specific columns
7. **Optimize Query** — Use `EXISTS` instead of `IN`, avoid `SELECT *`

### Code
```sql
-- Check IR query performance
EXPLAIN PLAN FOR
SELECT sale_id, product_name, amount
FROM sales
WHERE sale_date >= :P1_DATE
  AND product_name LIKE :P1_SEARCH || '%';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Company Evaluation
- **Oracle**: Deep APEX IR internals, pagination models, SQL tuning
- **Accenture**: Production monitoring, query plan analysis
- **Deloitte**: Explaining performance to non-technical stakeholders
