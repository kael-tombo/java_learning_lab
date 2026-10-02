# Theory: Interactive Reports in Oracle APEX

## What is an Interactive Report?

An **Interactive Report (IR)** is APEX's declarative reporting component that empowers end users to:
- Filter, sort, highlight, and group data
- Create and save private/public reports
- Download data (CSV, HTML, PDF, Excel)
- Subscribe to scheduled email delivery
- Build charts and pivot views on-the-fly

All without developer intervention.

## IR Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    APEX INTERACTIVE REPORT                   │
├─────────────────────────────────────────────────────────────┤
│  SQL Source (SELECT ...)                                     │
│       │                                                      │
│       ▼                                                      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │ Pagination  │    │  Filtering  │    │  Sorting    │      │
│  │ (Server-side)│    │ (WHERE +)   │    │ (ORDER BY)  │      │
│  └─────────────┘    └─────────────┘    └─────────────┘      │
│       │                                                      │
│       ▼                                                      │
│  Result Set → Render Engine → HTML/JSON                      │
│       │                                                      │
│       ├── Actions Menu → Download, Chart, Group By, Subscribe│
│       ├── Column Headers → Filter, Sort, Highlight           │
│       └── Search Bar → Text search across columns            │
└─────────────────────────────────────────────────────────────┘
```

## Filtering Mechanisms

### 1. Declarative Column Filters (User-Driven)
Each column header has a filter icon. APEX builds dynamic WHERE clauses:
```sql
-- User filters STATUS = 'SHIPPED'
-- APEX generates: WHERE status = 'SHIPPED'
```

### 2. Developer-Defined WHERE Clause (Static + Bind)
```sql
-- In Region Attributes → Source → Where Clause:
sale_date >= CASE :P1_DATE_RANGE
    WHEN '30' THEN SYSDATE - 30
    WHEN '60' THEN SYSDATE - 60
    WHEN '90' THEN SYSDATE - 90
    ELSE SYSDATE - 30
END
AND (INSTR(UPPER(product_name), UPPER(:P1_SEARCH)) > 0 OR :P1_SEARCH IS NULL)
```
**Key**: Use bind variables (`:P1_DATE_RANGE`) — not substitution strings (`&P1_DATE_RANGE.`) — for security and plan reuse.

### 3. Search Bar (Global Text Search)
- Searches all visible columns by default
- Can be restricted: Region → Attributes → Search Column(s) = `PRODUCT_NAME,CUSTOMER_NAME`

## Master-Detail with Interactive Reports

### Pattern A: Page Navigation (Classic)
```
Page 1 (Master IR) 
  └─ Link Column → f?p=&APP_ID.:2:&SESSION.:::P2_ORDER_ID:#ORDER_ID#
  
Page 2 (Detail IR)
  └─ Source: SELECT * FROM order_items WHERE order_id = :P2_ORDER_ID
```

### Pattern B: Modal Dialog (Modern)
```
Page 1 (Master IR)
  └─ Link Column → Target: Page 2 (Modal Dialog)
  
Page 2 (Detail IR/Form) — Opens in overlay, parent page visible
  └─ Dialog Attributes: Width=800, Height=600, Title=Order #&P2_ORDER_ID.
```

### Pattern C: Single-Page AJAX (See Lab 02)
- Master IR + Detail IG on same page
- Dynamic Action refreshes detail

**Choose Based On**:
| Need | Pattern |
|------|---------|
| Bookmarkable, shareable URLs | Page Navigation |
| Quick lookup without losing context | Modal Dialog |
| Dashboard with frequent switching | Single-Page AJAX |

## Row Selection and Multi-Row Actions

### Enable Row Selection
Region → Attributes → **Enable Row Selection = Yes**
- Adds checkbox column (configurable position)
- Selected row IDs available in `APEX_APPLICATION.G_F01` array

### Accessing Selected Rows in PL/SQL
```sql
DECLARE
    l_ids APEX_T_NUMBER;
BEGIN
    FOR i IN 1..APEX_APPLICATION.G_F01.COUNT LOOP
        l_ids.EXTEND;
        l_ids(l_ids.LAST) := APEX_APPLICATION.G_F01(i);
    END LOOP;
    -- l_ids now contains selected ORDER_IDs
END;
```

## Export and Email

### APEX_DATA_EXPORT (23.1+)
```sql
SELECT APEX_DATA_EXPORT.EXPORT(
    p_format   => 'CSV',
    p_query    => 'SELECT * FROM orders WHERE order_id IN (SELECT * FROM TABLE(:ids))',
    p_binds    => APEX_DATA_EXPORT.T_BINDS(1 => 'ids')
) INTO l_csv FROM DUAL;
```
Formats: `CSV`, `JSON`, `XLSX`, `HTML`, `PDF`

### APEX_MAIL for Email with Attachment
```sql
APEX_MAIL.SEND(
    p_to        => :P1_EMAIL,
    p_from      => 'noreply@company.com',
    p_subj      => 'Your Report',
    p_body      => 'Attached CSV of selected orders.',
    p_att_names => 'orders.csv',
    p_att_mime  => 'text/csv',
    p_att_clob  => l_csv
);
COMMIT; -- Required for mail queue
```

**Prerequisites**: Instance Admin → Manage Instance → Email → Configure SMTP

## Performance Optimization for Large Datasets

### 1. Server-Side Pagination (Critical)
Region → Attributes → **Pagination Type = Server**
- Default: 50 rows per page
- Only fetches visible rows + buffer
- **Never use Client-Side** for > 10K rows

### 2. Maximum Row Count
Region → Attributes → **Maximum Row Count = 500** (or lower)
- Limits total rows processed
- Prevents "Export All" from melting the database

### 3. Bind Variables in WHERE Clause
```sql
-- GOOD: Bind variables (plan reuse, security)
WHERE sale_date >= :P1_DATE
  AND product_name LIKE :P1_SEARCH || '%'

-- BAD: Concatenation (SQL injection, hard parse)
WHERE sale_date >= '||:P1_DATE||'
  AND product_name LIKE '%' || :P1_SEARCH || '%'
```

### 4. Indexes on Filtered Columns
```sql
CREATE INDEX idx_sales_date ON sales(sale_date);
CREATE INDEX idx_sales_product ON sales(product_name);
CREATE INDEX idx_sales_cust ON sales(customer_name);
```
Verify with `EXPLAIN PLAN` — should show `INDEX RANGE SCAN`.

### 5. Materialized Views for Aggregations
```sql
CREATE MATERIALIZED VIEW sales_daily_mv
BUILD IMMEDIATE
REFRESH FAST ON COMMIT
AS SELECT TRUNC(sale_date) AS day, 
          COUNT(*) AS cnt, 
          SUM(amount) AS total
     FROM sales 
     GROUP BY TRUNC(sale_date);
```
IR source becomes: `SELECT * FROM sales_daily_mv` — instant response.

### 6. Disable "Search on All Columns"
Region → Attributes → **Search Column(s) = Specific columns only**
- Reduces OR-expansion in execution plan
- `WHERE col1 LIKE :search OR col2 LIKE :search ...` is expensive

### 7. Optimize Base Query
```sql
-- AVOID
SELECT * FROM huge_table;

-- PREFER
SELECT sale_id, product_name, sale_date, amount  -- Only needed columns
FROM sales
WHERE sale_date >= :P1_DATE
  AND product_name LIKE :P1_SEARCH || '%';
```

## Saved Reports and Subscriptions

### User Saved Reports
- Users click **Actions → Report → Save Report**
- Private (default) or Public (developers)
- Stores: filters, sort, columns, highlights, breaks, chart config

### Subscriptions (Scheduled Email)
- Actions → Subscription → Create
- Schedule: Daily, Weekly, Monthly, Custom
- Format: CSV, HTML, PDF
- Requires: APEX_MAIL configured, `DBMS_SCHEDULER` jobs running

## IR JavaScript API (Advanced)

```javascript
// Get IR widget
var ir = apex.region('MY_IR').widget();

// Get current filters
var filters = ir.interactiveReport('getFilters');

// Programmatically set filter
ir.interactiveReport('setFilter', 'PRODUCT_NAME', 'Mouse');

// Refresh IR
ir.interactiveReport('refresh');

// Get selected rows (if row selection enabled)
var selected = ir.interactiveReport('getSelectedRows');
```

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Client-side pagination on 100K rows | Page hangs, browser freezes | Switch to Server-side |
| `SELECT *` in source | Slow, exports useless columns | List explicit columns |
| No indexes on filter columns | Full table scan on every filter | Add indexes |
| Concatenation in WHERE | SQL injection, no plan reuse | Use bind variables |
| Search on all columns | Slow text search | Limit to key columns |
| No max row count | Export All crashes DB | Set Maximum Row Count |

## Summary: IR Configuration Checklist

- [ ] Source: Explicit column list, bind variables in WHERE
- [ ] Pagination: Server-side, 15-50 rows
- [ ] Maximum Row Count: 500 (or business requirement)
- [ ] Search: Limited to 3-5 key columns
- [ ] Link Column: Proper target with page item passing
- [ ] Row Selection: Enabled if multi-row actions needed
- [ ] Indexes: On all filtered/joined columns
- [ ] Materialized View: For heavy aggregations
- [ ] Email: SMTP configured, test subscription works