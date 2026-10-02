# Quiz: Master-Detail Pages with Dynamic Actions

**Instructions**: Answer all 10 questions. Each question is worth 10 points. Passing score: 70/100.

---

## Question 1: Master-Detail State Management
**What is the primary mechanism for sharing the selected master record key with the detail region in a single-page AJAX master-detail pattern?**

A) A hidden page item (e.g., `P1_SELECTED_ORDER`) referenced in the detail region's WHERE clause
B) A global JavaScript variable set by the click handler
C) A browser cookie storing the last clicked ID
D) The APEX session state is automatically synchronized without page items

**Answer: A**

**Explanation**: The detail region's SQL query uses a bind variable (`WHERE order_id = :P1_SELECTED_ORDER`). When the page item value changes via a Dynamic Action "Set Value" action, refreshing the detail region re-executes the query with the new value. This is the declarative, zero-JavaScript core of the pattern.

---

## Question 2: Dynamic Action Sequence
**In a Dynamic Action triggered by clicking a master Interactive Report link column, what is the correct order of True Actions to synchronize the detail?**

A) Refresh Detail → Set Value → Refresh Summary
B) Set Value → Refresh Detail → Refresh Summary
C) Refresh Summary → Set Value → Refresh Detail
D) Execute PL/SQL → Set Value → Refresh Detail

**Answer: B**

**Explanation**: The page item must be set *before* the dependent regions refresh. The detail region's query binds to `:P1_SELECTED_ORDER`, so if you refresh before setting the value, it queries with the old (or null) value. Order: 1) Set Value, 2) Refresh Detail, 3) Refresh Summary/other dependents.

---

## Question 3: Interactive Grid vs Interactive Report
**Why use an Interactive Grid (IG) instead of an Interactive Report (IR) for the detail region in an editable master-detail?**

A) IG supports inline editing, add row, and declarative save processing; IR does not
B) IG loads faster than IR for large datasets
C) IR cannot be refreshed via Dynamic Action
D) IG automatically creates master-detail relationships

**Answer: A**

**Explanation**: Interactive Grid provides full inline editing (edit, add, delete rows), a toolbar with Save/Reset, and a declarative "Interactive Grid - Save Data" process. Interactive Report is read-only. For master-detail where users edit children, IG is the correct choice.

---

## Question 4: Virtual Columns
**What is the advantage of defining `line_total` as a `GENERATED ALWAYS AS (quantity * unit_price) VIRTUAL` column in the database?**

A) It reduces storage by not persisting the calculated value
B) It ensures the calculation is consistent between database and APEX, is indexable, and requires no PL/SQL
C) It makes the column editable in Interactive Grid
D) It automatically creates a trigger to update the parent order total

**Answer: B**

**Explanation**: Virtual columns are computed on read, stored in the data dictionary (not table data), can be indexed, and the database guarantees the calculation. APEX sees it as a regular column. No triggers or PL/SQL needed. It is read-only in IG (correct for calculated fields).

---

## Question 5: Link Column Target for Persistence
**To make master selection persist across browser refresh and be bookmarkable, the Master IR link column target should be:**

A) `f?p=&APP_ID.:1:&SESSION.:::P1_SELECTED_ORDER:#ORDER_ID#`
B) `javascript:apex.item('P1_SELECTED_ORDER').setValue('#ORDER_ID#');`
C) `#ORDER_ID#` (with Dynamic Action handling the rest)
D) `f?p=&APP_ID.:2:&SESSION.::::P2_ORDER_ID:#ORDER_ID#`

**Answer: A**

**Explanation**: Option A uses the standard APEX URL syntax to set page item `P1_SELECTED_ORDER` on the same page (Page 1). This updates the URL, making it bookmarkable and surviving browser refresh. Option B is JavaScript-only (no URL change). Option C doesn't set the item. Option D navigates to a different page.

---

## Question 6: Dynamic Action "Fire on Page Load"
**For a Dynamic Action that refreshes the detail region when `P1_SELECTED_ORDER` changes, when should "Fire on Page Load" be set to Yes?**

A) Always, for all True Actions
B) Never, it causes double execution
C) On the Refresh actions, but only if the page item might have a value on initial load (e.g., from URL)
D) Only on the Set Value action

**Answer: C**

**Explanation**: If the user bookmarks `...:::P1_SELECTED_ORDER:1001`, the page loads with that value already set. The Refresh actions need `Fire on Page Load = Yes` to initialize the detail region. The Set Value action (triggered by click) should have `Fire on Page Load = No`.

---

## Question 7: IG Save Process Configuration
**When configuring the "Interactive Grid - Save Data" process for the detail region, which setting is critical for correct DML generation?**

A) "Editable Region" must point to the IG region name
B) "Primary Key" must be set to the detail table's PK (e.g., `ITEM_ID`)
C) "Lock Row" must be enabled
D) "Return Primary Key" must be checked

**Answer: B**

**Explanation**: The IG Save process needs to know the primary key column to generate correct UPDATE/DELETE statements. Without it, APEX cannot uniquely identify rows. The Editable Region is auto-detected from the process's "Affected Region" attribute.

---

## Question 8: Recalculating Parent Totals
**After saving changes in the detail IG, what is the correct pattern to update the master's `total_amount`?**

A) Trigger on detail table: `AFTER INSERT OR UPDATE ON order_items ... UPDATE orders SET total_amount = ...`
B) Page Process (PL/SQL) after IG Save: `UPDATE orders SET total_amount = (SELECT SUM(line_total) FROM order_items WHERE order_id = :P1_SELECTED_ORDER) WHERE order_id = :P1_SELECTED_ORDER;`
C) Dynamic Action on IG Save: Execute JavaScript to sum client-side and call AJAX
D) Database view with `SUM() OVER ()` — no update needed

**Answer: B**

**Explanation**: A page process after the IG Save runs in the same transaction, sees the committed child changes, and updates the parent. Triggers (A) work but couple logic to DML and complicate bulk operations. Client-side (C) is insecure. Views (D) don't persist the total for reporting.

---

## Question 9: Preventing Invalid Status Transitions
**Where should business logic preventing invalid order status transitions (e.g., SHIPPED → PENDING) be implemented?**

A) Only in JavaScript on the status dropdown
B) Only in a database CHECK constraint
C) In the PL/SQL of the "Update Status" button Dynamic Action (server-side validation)
D) In the IG column validation

**Answer: C**

**Explanation**: Server-side validation in the Dynamic Action's PL/SQL block is the correct place. It runs in the database transaction, can raise `RAISE_APPLICATION_ERROR` with user-friendly messages, and cannot be bypassed. JavaScript (A) is easily bypassed. CHECK constraints (B) can't reference old/new values for transition logic. IG validation (D) applies to line items, not order status.

---

## Question 10: Debugging Non-Refreshing Detail
**The detail IG does not refresh when clicking a master row. The Dynamic Action fires (visible in debug). What is the most likely cause?**

A) The detail region's "Server-side Condition" is `P1_SELECTED_ORDER IS NULL`
B) The Dynamic Action's "Affected Elements" for Refresh does not include the detail region
C) The page item `P1_SELECTED_ORDER` has "Value Protected = Yes"
D) The master IR link column has no `class="select-order-link"`

**Answer: B**

**Explanation**: If the DA fires but the region doesn't refresh, the Refresh true action's "Affected Elements" selection is likely wrong (wrong region selected, or region has no Static ID). A) would hide the region when item HAS a value (opposite of needed). C) prevents URL tampering but doesn't block DA Set Value. D) only affects the jQuery selector for the DA trigger.

---

## Scoring Guide
| Score | Level |
|-------|-------|
| 90-100 | Master — Ready to build production master-detail apps |
| 70-89 | Proficient — Can implement with minor reference checks |
| 50-69 | Developing — Review THEORY.md and PROBLEM_WALKTHROUGH.md |
| < 50 | Beginner — Re-do Exercises 1-3 with guidance |

---

## Answer Key Summary
1. A | 2. B | 3. A | 4. B | 5. A | 6. C | 7. B | 8. B | 9. C | 10. B