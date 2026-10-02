# Quiz: Interactive Reports

---

## Question 1: WHERE Clause Bind Variables
**When using page items in an IR Region's WHERE clause, which syntax is correct for security and performance?**

A) `WHERE sale_date >= '&P1_DATE_RANGE.'`
B) `WHERE sale_date >= :P1_DATE_RANGE`
C) `WHERE sale_date >= ' || :P1_DATE_RANGE || '`
D) `WHERE sale_date >= v('P1_DATE_RANGE')`

**Answer: B**

**Explanation**: Bind variables (`:P1_ITEM`) allow SQL plan reuse, prevent SQL injection, and are properly typed. Substitution strings (`&P1_ITEM.`) cause hard parses and injection risk. `v()` function works but adds function call overhead.

---

## Question 2: Pagination for Large Tables
**An IR on a 1 million row table hangs the browser. What is the most critical setting to fix this?**

A) Increase Maximum Row Count to 10000
B) Change Pagination Type to **Server-side**
C) Disable Search Bar
D) Use Client-Side pagination with lazy loading

**Answer: B**

**Explanation**: Client-side pagination fetches ALL rows to the browser (memory crash). Server-side pagination only fetches the visible page (e.g., 15 rows) via `OFFSET/FETCH`. This is the single most important setting for large datasets.

---

## Question 3: Row Selection Array
**When Row Selection is enabled on an IR, selected row IDs are available in which APEX array?**

A) `APEX_APPLICATION.G_F01`
B) `APEX_APPLICATION.G_F02`
C) `APEX_APPLICATION.G_CHECKBOXES`
D) `WWV_FLOW_IR.SELECTED_ROWS`

**Answer: A**

**Explanation**: APEX maps checkbox inputs with `name="f01"` to `G_F01` array. Each checked row adds an entry. Process with `FOR i IN 1..APEX_APPLICATION.G_F01.COUNT`.

---

## Question 4: CSV Export of Selected Rows
**Which package/function generates CSV from a query with bind variables in APEX 23.1+?**

A) `APEX_UTIL.DOWNLOAD_CSV`
B) `APEX_DATA_EXPORT.EXPORT(p_format => 'CSV', ...)`
C) `WWV_FLOW_CSV.GENERATE`
D) `APEX_IR.EXPORT_TO_CSV`

**Answer: B**

**Explanation**: `APEX_DATA_EXPORT.EXPORT` is the modern (23.1+) API supporting CSV, JSON, XLSX, HTML, PDF with bind variable support via `p_binds`.

---

## Question 5: APEX_MAIL Commit Requirement
**After calling `APEX_MAIL.SEND`, what must you do for the email to actually queue?**

A) Nothing, it's automatic
B) Call `APEX_MAIL.PUSH_QUEUE`
C) Issue `COMMIT`
D) Call `DBMS_SCHEDULER.RUN_JOB('APEX_MAIL_PUSH')`

**Answer: C**

**Explanation**: `APEX_MAIL.SEND` inserts into `WWV_FLOW_MAIL_QUEUE`. The transaction must be committed for the background job (`APEX_MAIL_PUSH`) to see and send the mail.

---

## Question 6: Master-Detail IR Link Column
**To pass the clicked master ORDER_ID to a detail page (Page 2) via URL, the Link Column Target should be:**

A) `f?p=&APP_ID.:2:&SESSION.::::P2_ORDER_ID:#ORDER_ID#`
B) `f?p=&APP_ID.:2:&SESSION.:::P2_ORDER_ID:#ORDER_ID#`
C) `javascript:apex.navigation.dialog('2', {P2_ORDER_ID: '#ORDER_ID#'});`
D) `#ORDER_ID#` (handled by Dynamic Action)

**Answer: A**

**Explanation**: Standard APEX URL syntax: `f?p=APP:PAGE:SESSION:REQUEST:DEBUG:CLEAR_CACHE:ITEM_NAMES:ITEM_VALUES`. The `::::` clears cache for items not listed. Option B has wrong number of colons. Option C is for modal dialogs (different syntax). Option D doesn't navigate.

---

## Question 6: Materialized View Refresh
**For a materialized view that must reflect base table changes immediately after commit, which refresh mode is correct?**

A) `REFRESH COMPLETE ON DEMAND`
B) `REFRESH FAST ON COMMIT`
C) `REFRESH FORCE ON SCHEDULE`
D) `REFRESH NEVER`

**Answer: B**

**Explanation**: `FAST ON COMMIT` uses the MV log to apply only changed rows at commit time, providing real-time data. `COMPLETE` rebuilds entire MV. `ON DEMAND` requires manual refresh. `SCHEDULED` has latency.

---

## Question 7: Search Column Performance
**An IR searches across 50 columns and is slow. Best fix?**

A) Increase Maximum Row Count
B) Limit **Search Column(s)** to 3-5 key columns
C) Switch to Client-Side pagination
D) Add `/*+ PARALLEL */` hint

**Answer: B**

**Explanation**: "Search on All Columns" generates `WHERE col1 LIKE :s OR col2 LIKE :s OR ...` — expensive OR-expansion. Limiting to indexed key columns (e.g., `PRODUCT_NAME,CUSTOMER_NAME`) dramatically improves performance.

---

## Question 8: IR JavaScript Refresh
**To programmatically refresh an IR with Static ID `SALES_IR` from JavaScript:**

A) `apex.region('SALES_IR').refresh();`
B) `apex.region('SALES_IR').widget().interactiveReport('refresh');`
C) `$('#SALES_IR').trigger('refresh');`
D) `apex.ir.refresh('SALES_IR');`

**Answer: B**

**Explanation**: The IR widget exposes `interactiveReport('refresh')` method. `apex.region().refresh()` is for generic regions. jQuery trigger doesn't work. No `apex.ir` namespace exists.

---

## Question 9: Index Usage Verification
**How to verify an IR query uses an index on the filtered column?**

A) Check Region → Attributes → Explain Plan
B) Run `EXPLAIN PLAN FOR <IR query>` and check for `INDEX RANGE SCAN`
C) Enable Debug and look for "Index used"
D) Check `USER_INDEXES` for `STATUS = 'VALID'`

**Answer: B**

**Explanation**: `EXPLAIN PLAN` shows the actual execution plan. Look for `INDEX RANGE SCAN` or `INDEX UNIQUE SCAN` on your index. `TABLE ACCESS FULL` means index not used.

---

## Question 10: Subscription Email Not Sending
**A user creates an IR subscription but never receives email. First troubleshooting step?**

A) Check `APEX_MAIL_QUEUE` for pending/failed mails
B) Recreate the subscription
C) Change email format from CSV to HTML
D) Increase Maximum Row Count

**Answer: A**

**Explanation**: `SELECT * FROM apex_mail_queue WHERE created_on > SYSDATE - 1` shows queued/failed/sent status. Common issues: SMTP not configured, mail job not running, attachment too large.

---

## Answer Key
1. B | 2. B | 3. A | 4. B | 5. C | 6. A | 7. B | 8. B | 9. B | 10. A