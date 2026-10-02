# Flashcards: Interactive Reports

## Core Concepts

---
**Q**: What is an Interactive Report (IR)?
**A**: Declarative APEX report component allowing end-users to filter, sort, group, chart, download, and subscribe — no developer code needed.

---
**Q**: Three ways to filter an IR?
**A**: 1) User column filters (header), 2) Developer WHERE clause with binds, 3) Global search bar.

---
**Q**: Bind variable vs substitution string in WHERE clause?
**A**: `:P1_ITEM` = bind (plan reuse, secure). `&P1_ITEM.` = substitution (hard parse, injection risk).

---
**Q**: Server-side vs Client-side pagination?
**A**: Server = fetches only visible page (OFFSET/FETCH). Client = fetches ALL rows to browser. **Always Server for >10K rows.**

---
**Q**: What does "Maximum Row Count" do?
**A**: Limits total rows processed (default 500). Prevents "Export All" from melting DB. Set to business requirement.

---

## Master-Detail IR

---
**Q**: Link Column Target syntax for master → detail page?
**A**: `f?p=&APP_ID.:DETAIL_PAGE:&SESSION.::::P_DETAIL_ITEM:#MASTER_PK#`

---
**Q**: Modal Dialog master-detail — how to set title dynamically?
**A**: Dialog Attributes → Title: `Order #&P2_ORDER_ID.` (substitution string)

---
**Q**: Single-page AJAX master-detail — which lab?
**A**: Lab 02 (Workshop Builder) — uses Dynamic Actions, not page navigation.

---

## Row Selection & Export

---
**Q**: How to enable multi-row selection?
**A**: IR Attributes → Enable Row Selection = Yes. Adds checkbox column.

---
**Q**: Where are selected row IDs in PL/SQL?
**A**: `APEX_APPLICATION.G_F01` (VARCHAR2 array). Cast to NUMBER for queries.

---
**Q**: Modern CSV export function (APEX 23.1+)?
**A**: `APEX_DATA_EXPORT.EXPORT(p_format => 'CSV', p_query => ..., p_binds => ...)`

---
**Q**: APEX_DATA_EXPORT supported formats?
**A**: CSV, JSON, XLSX, HTML, PDF.

---
**Q**: Email CSV attachment — critical step after APEX_MAIL.SEND?
**A**: `COMMIT;` — inserts into mail queue, background job needs committed data.

---

## Performance

---
**Q**: Three indexes to create for IR on sales(sale_date, product_name, customer_name)?
**A**: `CREATE INDEX idx_sales_date ON sales(sale_date); CREATE INDEX idx_sales_prod ON sales(product_name); CREATE INDEX idx_sales_cust ON sales(customer_name);`

---
**Q**: How to verify index usage?
**A**: `EXPLAIN PLAN FOR <query>; SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);` → Look for `INDEX RANGE SCAN`.

---
**Q**: "Search on All Columns" performance problem?
**A**: Generates `col1 LIKE :s OR col2 LIKE :s OR ...` — expensive OR-expansion. Fix: Limit Search Column(s) to 3-5 indexed columns.

---
**Q**: Materialized View for daily sales — fast refresh prerequisites?
**A**: 1) MV LOG on base table `WITH ROWID, SEQUENCE (cols) INCLUDING NEW VALUES` 2) MV `REFRESH FAST ON COMMIT`

---
**Q**: MV refresh modes comparison?
**A**: ON COMMIT = real-time. ON DEMAND = manual. SCHEDULED = periodic (latency).

---

## JavaScript API

---
**Q**: Get IR widget by Static ID?
**A**: `apex.region('MY_IR').widget()`

---
**Q**: Programmatically refresh IR?
**A**: `apex.region('MY_IR').widget().interactiveReport('refresh');`

---
**Q**: Set filter via JavaScript?
**A**: `ir.interactiveReport('setFilter', 'COLUMN_NAME', 'VALUE');`

---
**Q**: Clear all filters via JavaScript?
**A**: `ir.interactiveReport('clearFilters');`

---
**Q**: Get selected row IDs via JavaScript?
**A**: `ir.interactiveReport('getSelectedRows');` — returns array of PK values.

---

## Saved Reports & Subscriptions

---
**Q**: Private vs Public saved report?
**A**: Private = only creator sees. Public = all users see (developer creates).

---
**Q**: Subscription schedule options?
**A**: Daily, Weekly, Monthly, Custom (cron-like).

---
**Q**: Subscription email not arriving — where to check?
**A**: `SELECT * FROM apex_mail_queue WHERE created_on > SYSDATE - 1;` — check STATUS, ERROR_MESSAGE.

---
**Q**: Subscription format options?
**A**: CSV, HTML, PDF.

---

## Debugging

---
**Q**: Enable IR debug?
**A**: URL: `&p_debug=YES&p_debug_level=9`

---
**Q**: Key debug message for query building?
**A**: `IR: Final query: SELECT ... WHERE ...` — shows exact SQL executed.

---
**Q**: "Maximum row count exceeded" in debug?
**A**: Query returns more rows than Maximum Row Count setting. Increase or add filters.

---
**Q**: "Bind variable P1_ITEM not in session state"?
**A**: Page item not submitted. Ensure item is on page, not conditionally hidden, or add to Page Items to Submit.

---

## Quick Reference: IR Settings Cheat Sheet

| Setting | Location | Recommended Value |
|---------|----------|-------------------|
| Pagination Type | Region Attributes | **Server** |
| Rows Per Page | Region Attributes | 15-50 |
| Maximum Row Count | Region Attributes | **500** (or less) |
| Search Column(s) | Region Attributes | **3-5 key cols** (not All) |
| Enable Row Selection | Region Attributes | Yes (if multi-row actions) |
| Link Column Target | Column Attributes | `f?p=&APP_ID.:PAGE:&SESSION.::::P_ITEM:#PK#` |
| Static ID | Region Attributes | **Required for JS API** |

---

## Quick Reference: PL/SQL Patterns

| Task | Code |
|------|------|
| Process selected rows | `FOR i IN 1..APEX_APPLICATION.G_F01.COUNT LOOP l_ids(l_ids.LAST) := TO_NUMBER(G_F01(i)); END LOOP;` |
| Export selected to CSV | `APEX_DATA_EXPORT.EXPORT(p_format=>'CSV', p_query=>'SELECT * FROM t WHERE id IN (SELECT * FROM TABLE(:ids))', p_binds=>T_BINDS('ids'=>l_ids))` |
| Email CSV | `APEX_MAIL.SEND(p_to=>:P1_EMAIL, p_att_clob=>l_csv, p_att_mime=>'text/csv', p_att_names=>'file.csv'); COMMIT;` |
| Check MV refresh | `SELECT mview_name, last_refresh_type, last_refresh_date FROM user_mviews;` |
| Rebuild MV log | `DROP MATERIALIZED VIEW LOG ON t; CREATE MATERIALIZED VIEW LOG ON t WITH ROWID...` |

---

## Study Tips
1. **Build Exercise 1** without looking — muscle memory for WHERE clause syntax
2. **EXPLAIN PLAN** every IR query you write — verify indexes
3. **Test Export/Email** — verify `COMMIT` and mail queue
4. **Use JS API** in browser console — `apex.region('IR').widget().interactiveReport('getFilters')`
5. **Create MV** for any aggregated report — feel the speed difference