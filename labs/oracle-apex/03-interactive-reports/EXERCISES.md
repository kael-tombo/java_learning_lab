# Exercises: Interactive Reports

## Exercise 1: Dynamic Date-Range Filter (Guided)
**Time**: 20 minutes  
**Difficulty**: Beginner

### Objective
Build an IR with a select list for date range (30/60/90 days) and a search box.

### Steps
1. **Create Page Items**:
   - `P1_DATE_RANGE` (Select List): Static values: 30, 60, 90. Default: 30
   - `P1_SEARCH` (Text Field): Placeholder "Search products..."
2. **Create IR Region** on `sales` table
3. **Region Attributes → Source → Where Clause**:
   ```sql
   sale_date >= CASE :P1_DATE_RANGE
       WHEN '30' THEN SYSDATE - 30
       WHEN '60' THEN SYSDATE - 60
       WHEN '90' THEN SYSDATE - 90
       ELSE SYSDATE - 30
   END
   AND (INSTR(UPPER(product_name), UPPER(:P1_SEARCH)) > 0 OR :P1_SEARCH IS NULL)
   ```
4. **Enable Search Bar** (default)
5. **Test**: Change date range, type in search, verify filters apply

### Verification
- [ ] Date range dropdown filters correctly
- [ ] Search box filters product names (case-insensitive)
- [ ] Combined filters work together

---

## Exercise 2: Master-Detail IR with Modal Dialog
**Time**: 25 minutes  
**Difficulty**: Beginner-Intermediate

### Objective
Click order in master IR → open detail IR in modal dialog.

### Steps
1. **Page 1 (Master)**:
   - IR on `orders` with columns: ORDER_ID (Link), CUSTOMER, ORDER_DATE, STATUS, TOTAL
   - Link Column: `ORDER_ID`, Target: Page 2, Set `P2_ORDER_ID = #ORDER_ID#`
   - Link Attributes: `data-dialog="true"` (or set in Link Column → Target → Dialog)
2. **Page 2 (Detail)**:
   - Page Mode: Modal Dialog
   - IR on `order_items` with `WHERE order_id = :P2_ORDER_ID`
   - Dialog Attributes: Width=800, Height=600, Title="Order Items for Order #&P2_ORDER_ID."
3. **Test**: Click order → modal opens with line items

### Verification
- [ ] Modal opens on click
- [ ] Detail shows correct line items
- [ ] Close modal → back to master

---

## Exercise 3: Multi-Row Selection & CSV Download
**Time**: 20 minutes  
**Difficulty**: Intermediate

### Objective
Select multiple orders → click button → download CSV.

### Steps
1. **Master IR**: Enable Row Selection (Attributes → Enable Row Selection = Yes)
2. **Button**: "Download Selected" in IR region header
3. **Dynamic Action**: Click button → Execute PL/SQL
   ```sql
   DECLARE
       l_csv CLOB;
       l_ids APEX_T_NUMBER;
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
       
       -- Return CSV via page item or download
       :P1_CSV_DATA := l_csv;
   END;
   ```
4. **Add Second True Action**: Execute JavaScript to trigger download
   ```javascript
   var csv = apex.item('P1_CSV_DATA').getValue();
   var blob = new Blob([csv], {type: 'text/csv'});
   var url = URL.createObjectURL(blob);
   var a = document.createElement('a');
   a.href = url;
   a.download = 'orders.csv';
   a.click();
   URL.revokeObjectURL(url);
   ```

### Verification
- [ ] Can select multiple rows via checkboxes
- [ ] Click button downloads CSV with selected orders
- [ ] CSV has correct headers and data

---

## Exercise 4: Email Selected Rows as CSV
**Time**: 20 minutes  
**Difficulty**: Intermediate

### Objective
Add "Email Report" button that sends CSV to user's email.

### Prerequisites
- APEX_MAIL configured (Instance Admin → Email)
- User has email in `apex_workspace_users` or page item `P1_EMAIL`

### Steps
1. **Page Item**: `P1_EMAIL` (Text Field, default: `&APP_USER.`)
2. **Button**: "Email Report" in IR region header
3. **Dynamic Action**: Click → Execute PL/SQL
   ```sql
   DECLARE
       l_csv CLOB;
       l_ids APEX_T_NUMBER;
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
           p_subj      => 'Your Orders Report - ' || TO_CHAR(SYSDATE, 'YYYY-MM-DD'),
           p_body      => 'Attached are the selected orders.',
           p_att_names => 'orders.csv',
           p_att_mime  => 'text/csv',
           p_att_clob  => l_csv
       );
       COMMIT;
       
       :P1_MAIL_STATUS := 'Email sent to ' || :P1_EMAIL;
   END;
   ```
4. **True Action 2**: Show success message (Set Value on `P1_MAIL_STATUS`)

### Verification
- [ ] Select rows, click Email Report
- [ ] Email received with CSV attachment
- [ ] CSV contains only selected orders

---

## Exercise 5: Performance Optimization for Large Table
**Time**: 25 minutes  
**Difficulty**: Intermediate

### Objective
Optimize IR on 500K+ row table.

### Steps
1. **Create Large Table**:
   ```sql
   CREATE TABLE big_sales AS
   SELECT level AS sale_id,
          'Product ' || MOD(level, 1000) AS product_name,
          SYSDATE - DBMS_RANDOM.VALUE(0, 365) AS sale_date,
          DBMS_RANDOM.VALUE(10, 5000) AS amount,
          'Customer ' || MOD(level, 5000) AS customer_name
   FROM dual CONNECT BY LEVEL <= 500000;
   CREATE INDEX idx_big_sales_date ON big_sales(sale_date);
   CREATE INDEX idx_big_sales_prod ON big_sales(product_name);
   ```
2. **IR on `big_sales`** with date range + search filters
3. **Configure Performance Settings**:
   - Pagination: Server-side, 15 rows
   - Maximum Row Count: 500
   - Search Column(s): `PRODUCT_NAME` only (not all)
4. **Test**: Filter by date, search product → verify < 1 sec response
5. **EXPLAIN PLAN** verification:
   ```sql
   EXPLAIN PLAN FOR
   SELECT sale_id, product_name, sale_date, amount
   FROM big_sales
   WHERE sale_date >= SYSDATE - 30
     AND product_name LIKE 'Product 5%';
   SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
   ```

### Verification
- [ ] IR loads in < 2 seconds
- [ ] Filter by date returns in < 500ms
- [ ] Search returns in < 500ms
- [ ] EXPLAIN PLAN shows INDEX RANGE SCAN

---

## Exercise 6: Materialized View for Aggregated IR
**Time**: 20 minutes  
**Difficulty**: Advanced

### Objective
Create daily sales summary MV and build IR on it.

### Steps
1. **Create MV Log**:
   ```sql
   CREATE MATERIALIZED VIEW LOG ON big_sales
   WITH ROWID, SEQUENCE (sale_date, amount)
   INCLUDING NEW VALUES;
   ```
2. **Create MV**:
   ```sql
   CREATE MATERIALIZED VIEW sales_daily_mv
   BUILD IMMEDIATE
   REFRESH FAST ON COMMIT
   AS SELECT TRUNC(sale_date) AS sale_day,
             COUNT(*) AS order_count,
             SUM(amount) AS total_sales,
             AVG(amount) AS avg_order
        FROM big_sales
        GROUP BY TRUNC(sale_date);
   CREATE INDEX idx_sales_daily_day ON sales_daily_mv(sale_day);
   ```
3. **IR on `sales_daily_mv`** with date range filter
4. **Compare Performance**: Query MV vs base table for monthly totals

### Verification
- [ ] MV query returns in < 100ms
- [ ] Base table aggregation takes > 5 seconds
- [ ] INSERT into `big_sales` → MV auto-updates (COMMIT)

---

## Exercise 7: Saved Reports and Subscriptions
**Time**: 15 minutes  
**Difficulty**: Beginner

### Objective
Save a custom report and create email subscription.

### Steps
1. **Run IR page**
2. **Actions → Report → Save Report**:
   - Name: "High Value Orders"
   - Filters: Amount > 1000, Status = 'CONFIRMED'
   - Columns: Hide NOTES, Show all others
   - Sort: Amount DESC
   - Public: Yes
3. **Actions → Subscription → Create**:
   - Name: "Daily High Value Orders"
   - Schedule: Daily, 8:00 AM
   - Format: CSV
   - Email: Your email
4. **Verify**: Check email next morning (or check `apex_mail_queue`)

### Verification
- [ ] Saved report appears in Report list
- [ ] Subscription created successfully
- [ ] Email received (or queued in `apex_mail_queue`)

---

## Exercise 8: IR JavaScript API - Programmatic Filter
**Time**: 15 minutes  
**Difficulty**: Advanced

### Objective
Add button to filter IR to "Last 7 Days" programmatically.

### Steps
1. **IR Static ID**: `SALES_IR`
2. **Button**: "Last 7 Days"
3. **Dynamic Action**: Click → Execute JavaScript
   ```javascript
   var ir = apex.region('SALES_IR').widget();
   
   // Clear existing filters
   ir.interactiveReport('clearFilters');
   
   // Set date filter (assuming SALE_DATE column)
   var sevenDaysAgo = new Date();
   sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
   var dateStr = sevenDaysAgo.toISOString().split('T')[0]; // YYYY-MM-DD
   
   ir.interactiveReport('setFilter', 'SALE_DATE', '>=' + dateStr);
   
   // Refresh
   ir.interactiveReport('refresh');
   ```

### Verification
- [ ] Click button → IR filters to last 7 days
- [ ] Filter shows in IR header
- [ ] Other filters cleared

---

## Exercise 9: Reset Button for All Filters
**Time**: 10 minutes  
**Difficulty**: Beginner

### Objective
Add "Clear All Filters" button.

### Steps
1. **Button**: "Reset Filters" in IR region header
2. **Dynamic Action**: Click → Execute JavaScript
   ```javascript
   apex.region('SALES_IR').widget().interactiveReport('clearFilters');
   apex.region('SALES_IR').widget().interactiveReport('refresh');
   
   // Also clear page items if used
   apex.item('P1_DATE_RANGE').setValue('30');
   apex.item('P1_SEARCH').setValue('');
   ```

### Verification
- [ ] Click resets all column filters
- [ ] Page items reset to defaults
- [ ] IR shows all data

---

## Exercise 10: Column-Level Security (VPD Simulation)
**Time**: 20 minutes  
**Difficulty**: Advanced

### Objective
Hide `COST` column from non-managers.

### Steps
1. **Create Authorization Scheme**: `IS_MANAGER`
   - Type: PL/SQL Function Body
   - Code: `RETURN :APP_USER IN ('MANAGER1','MANAGER2');`
2. **IR Column `COST`**: Authorization Scheme = `IS_MANAGER`
3. **Test**: Login as regular user → COST column hidden
4. **Test**: Login as manager → COST column visible

### Verification
- [ ] Non-managers don't see COST column
- [ ] Managers see COST column
- [ ] Export respects authorization (non-manager CSV lacks COST)

---

## Solutions Reference
- `WORKED_EXAMPLE.sql` — Complete SQL for all exercises
- `MINI_PROJECT/` — Sales dashboard with 5 saved reports
- `REAL_WORLD_PROJECT/` — Executive portal with role-based subscriptions