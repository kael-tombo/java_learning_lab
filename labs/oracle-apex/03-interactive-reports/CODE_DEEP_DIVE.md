# Code Deep Dive: Interactive Reports Internals

## IR Query Execution Flow

```
User Action (Filter/Sort/Page)
        │
        ▼
┌─────────────────────────────────────┐
│ APEX IR Engine (WWV_FLOW_IR)        │
│ 1. Parse saved report settings      │
│ 2. Merge with user runtime filters  │
│ 3. Build dynamic WHERE/ORDER BY     │
│ 4. Apply pagination (OFFSET/FETCH)  │
│ 5. Execute query                    │
│ 6. Render HTML/JSON                 │
└─────────────────────────────────────┘
        │
        ▼
   Browser Render
```

### Dynamic WHERE Clause Construction

When user applies filters:
```sql
-- Base query
SELECT * FROM sales

-- User filters: STATUS = 'SHIPPED', AMOUNT > 1000
-- APEX generates:
SELECT * FROM sales
WHERE status = 'SHIPPED'
  AND amount > 1000
  AND ROWNUM <= 50  -- pagination
```

### Bind Variable Handling

```sql
-- Developer WHERE clause (Region Attributes):
WHERE sale_date >= :P1_DATE_RANGE
  AND product_name LIKE :P1_SEARCH || '%'

-- APEX binds at execution time:
-- :P1_DATE_RANGE = '30' → SYSDATE - 30
-- :P1_SEARCH = 'mouse' → 'mouse%'
```

**Critical**: Page items in WHERE clause must be **Session State Protected = No** (or properly validated) to allow binding.

## APEX_DATA_EXPORT Internals

### Package Specification (Simplified)
```sql
PACKAGE APEX_DATA_EXPORT AS
    TYPE t_binds IS TABLE OF VARCHAR2(4000) INDEX BY VARCHAR2(100);
    
    FUNCTION export(
        p_format     IN VARCHAR2,  -- CSV, JSON, XLSX, HTML, PDF
        p_query      IN VARCHAR2,
        p_binds      IN t_binds DEFAULT NULL,
        p_max_rows   IN NUMBER DEFAULT NULL
    ) RETURN CLOB;
END;
```

### Export Flow
```sql
DECLARE
    l_csv CLOB;
BEGIN
    l_csv := APEX_DATA_EXPORT.EXPORT(
        p_format => 'CSV',
        p_query  => 'SELECT * FROM orders WHERE order_id IN (SELECT * FROM TABLE(:ids))',
        p_binds  => APEX_DATA_EXPORT.T_BINDS('ids' => l_ids)
    );
    -- l_csv contains CSV with headers
END;
```

### Supported Formats
| Format | MIME Type | Use Case |
|--------|-----------|----------|
| CSV | text/csv | Excel import, data exchange |
| JSON | application/json | API consumption |
| XLSX | application/vnd.openxmlformats-officedocument.spreadsheetml.sheet | Formatted Excel |
| HTML | text/html | Web display |
| PDF | application/pdf | Print-ready |

### Customizing Export
```sql
-- For XLSX with formatting:
SELECT APEX_DATA_EXPORT.EXPORT(
    p_format => 'XLSX',
    p_query  => 'SELECT order_id, customer, total FROM orders',
    -- Options via p_options (JSON):
    p_options => '{"freezeHeader":true,"autoFilter":true}'
) FROM DUAL;
```

## APEX_MAIL Internals

### Mail Queue Architecture
```
APEX_MAIL.SEND()
        │
        ▼
┌─────────────────────┐
│ APEX_MAIL_QUEUE     │  (Table: APEX_023200.WWV_FLOW_MAIL_QUEUE)
│ - Stores mail rows  │
│ - Attachments in    │
│   WWV_FLOW_MAIL_ATT │
└─────────┬───────────┘
          │
          ▼
   DBMS_SCHEDULER Job
   (APEX_MAIL_PUSH)
   Runs every 5 min
          │
          ▼
    SMTP Server
```

### Sending with Attachments
```sql
DECLARE
    l_csv CLOB;
BEGIN
    -- Generate CSV
    l_csv := APEX_DATA_EXPORT.EXPORT(p_format => 'CSV', p_query => ...);
    
    -- Send email
    APEX_MAIL.SEND(
        p_to        => 'user@company.com',
        p_from      => 'noreply@company.com',
        p_subj      => 'Orders Report',
        p_body      => 'See attached.',
        p_att_names => 'orders.csv',
        p_att_mime  => 'text/csv',
        p_att_clob  => l_csv
    );
    COMMIT; -- Critical: commits to mail queue
END;
```

### Checking Mail Status
```sql
SELECT mail_id, to_address, subject, status, created_on, last_updated
FROM apex_mail_queue
WHERE created_on > SYSDATE - 1
ORDER BY created_on DESC;

-- View errors
SELECT mail_id, error_message
FROM apex_mail_log
WHERE mail_id = :p_mail_id;
```

## IR JavaScript API Deep Dive

### Region Widget Initialization
```javascript
// Static ID: MY_IR
var ir = apex.region('MY_IR').widget();
```

### Key Methods

| Method | Description |
|--------|-------------|
| `ir.interactiveReport('refresh')` | Reload report with current filters |
| `ir.interactiveReport('getFilters')` | Returns array of active filters |
| `ir.interactiveReport('setFilter', col, val)` | Programmatically filter |
| `ir.interactiveReport('clearFilters')` | Remove all user filters |
| `ir.interactiveReport('getSelectedRows')` | Returns selected row IDs (if enabled) |
| `ir.interactiveReport('export', 'CSV')` | Trigger download |

### Filter Object Structure
```javascript
{
    column: 'PRODUCT_NAME',
    operator: 'LIKE',
    value: 'mouse%',
    isCaseSensitive: false
}
```

### Event Handlers
```javascript
// After refresh
apex.region('MY_IR').widget().on('interactivereportrefresh', function() {
    console.log('IR refreshed');
});

// Before refresh (can cancel)
apex.region('MY_IR').widget().on('interactivereportbeforerefresh', function(e, data) {
    if (someCondition) e.preventDefault();
});
```

## APEX_APPLICATION.G_F01 Array (Row Selection)

### How It Works
1. IR with Row Selection enabled renders checkboxes with `name="f01"`
2. User checks rows → form submits `f01=1001&f01=1002&f01=1003`
3. APEX populates `APEX_APPLICATION.G_F01(1)=1001`, `G_F01(2)=1002`, etc.

### Processing Selected Rows
```sql
DECLARE
    l_selected_ids APEX_T_NUMBER := APEX_T_NUMBER();
BEGIN
    -- G_F01 is VARCHAR2 array, cast to NUMBER
    FOR i IN 1..APEX_APPLICATION.G_F01.COUNT LOOP
        l_selected_ids.EXTEND;
        l_selected_ids(l_selected_ids.LAST) := TO_NUMBER(APEX_APPLICATION.G_F01(i));
    END LOOP;
    
    -- Use in query
    FOR rec IN (
        SELECT * FROM orders 
        WHERE order_id IN (SELECT * FROM TABLE(l_selected_ids))
    ) LOOP
        -- Process each
    END LOOP;
END;
```

### With APEX_DATA_EXPORT (Cleaner)
```sql
DECLARE
    l_csv CLOB;
BEGIN
    l_csv := APEX_DATA_EXPORT.EXPORT(
        p_format => 'CSV',
        p_query  => 'SELECT * FROM orders WHERE order_id IN (SELECT * FROM TABLE(:ids))',
        p_binds  => APEX_DATA_EXPORT.T_BINDS('ids' => 
            CAST(MULTISET(
                SELECT TO_NUMBER(column_value) 
                FROM TABLE(APEX_APPLICATION.G_F01)
            ) AS APEX_T_NUMBER))
    );
END;
```

## Performance: Execution Plan Analysis

### Check IR Query Plan
```sql
-- In SQL Workshop or SQL Developer:
EXPLAIN PLAN FOR
SELECT sale_id, product_name, sale_date, amount
FROM sales
WHERE sale_date >= :P1_DATE
  AND product_name LIKE :P1_SEARCH || '%';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Good Plan Indicators
```
| Id | Operation                    | Name          | Rows |
|----|------------------------------|---------------|------|
|  0 | SELECT STATEMENT             |               |   50 |
|  1 |  VIEW                        |               |   50 |
|  2 |   WINDOW SORT PUSHED RANK    |               |   50 |
|  3 |    TABLE ACCESS BY INDEX ROWID| SALES        | 1000 |
|  4 |     INDEX RANGE SCAN         | IDX_SALES_DATE| 1000 |
```

### Bad Plan Indicators
```
| Id | Operation          | Name  | Rows  |
|----|--------------------|-------|-------|
|  0 | SELECT STATEMENT   |       | 50000 |
|  1 |  TABLE ACCESS FULL | SALES | 50000 |  ← FULL SCAN!
```

## Materialized View Fast Refresh

### Prerequisites
```sql
-- Materialized view log on base table
CREATE MATERIALIZED VIEW LOG ON sales
WITH ROWID, SEQUENCE (sale_date, product_name, amount)
INCLUDING NEW VALUES;

-- MV with fast refresh
CREATE MATERIALIZED VIEW sales_daily_mv
BUILD IMMEDIATE
REFRESH FAST ON COMMIT
AS SELECT TRUNC(sale_date) AS day, COUNT(*) AS cnt, SUM(amount) AS total
   FROM sales GROUP BY TRUNC(sale_date);
```

### Refresh Modes
| Mode | When | Use Case |
|------|------|----------|
| ON COMMIT | After each DML | Real-time dashboards |
| ON DEMAND | Manual `DBMS_MVIEW.REFRESH` | Batch windows |
| SCHEDULED | `START WITH ... NEXT ...` | Nightly aggregates |

## Debugging IR Issues

### Enable IR Debug
URL: `&p_debug=YES&p_debug_level=9`

### Key Debug Messages
```
IR: Building query for region 12345
IR: Base query: SELECT * FROM sales
IR: Applied filters: STATUS='SHIPPED', AMOUNT>1000
IR: Final query: SELECT * FROM sales WHERE status='SHIPPED' AND amount>1000 ...
IR: Pagination: OFFSET 0 ROWS FETCH NEXT 50 ROWS ONLY
IR: Query executed in 45ms, 42 rows returned
```

### Common Issues in Debug
| Message | Meaning |
|---------|---------|
| `IR: Maximum row count exceeded` | Query returns > Max Row Count |
| `IR: Bind variable P1_DATE not in session state` | Page item not submitted |
| `IR: Column PRODUCT_NAME not found in query` | Typo in Search Column(s) |

## Advanced: Custom IR Plugin

For needs beyond declarative IR:
1. **Shared Components → Plug-ins → Create**
2. **Type**: Region
3. **Render Function**: Returns HTML via `HTP.P`
4. **AJAX Callback**: Handles filter/sort/paginate via `apex.server.process`

```sql
FUNCTION render_my_ir(p_region IN apex_plugin.t_region, ...)
RETURN apex_plugin.t_region_render_result IS
BEGIN
    -- Custom query with complex logic
    -- Return HTML table or JSON for JS rendering
END;
```

## Summary: Key Code Patterns

| Task | Code Pattern |
|------|--------------|
| Dynamic WHERE with binds | `WHERE col = :P1_ITEM` |
| Multi-row selection | `APEX_APPLICATION.G_F01` array |
| CSV export selected rows | `APEX_DATA_EXPORT.EXPORT(p_format=>'CSV', p_query=>...)` |
| Email CSV | `APEX_MAIL.SEND(p_att_clob=>l_csv, p_att_mime=>'text/csv')` |
| Server pagination | Region Attr: Pagination Type = Server |
| Index for filter | `CREATE INDEX idx_col ON table(col)` |
| MV for aggregation | `CREATE MATERIALIZED VIEW ... REFRESH FAST ON COMMIT` |
| IR JS refresh | `apex.region('ID').widget().interactiveReport('refresh')` |
| IR JS set filter | `apex.region('ID').widget().interactiveReport('setFilter','COL','VAL')` |