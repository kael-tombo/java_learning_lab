# Flashcards: Master-Detail Pages with Dynamic Actions

## Core Concepts

---
**Q**: What page item pattern enables single-page master-detail in APEX?
**A**: A hidden, protected page item (e.g., `P1_SELECTED_ORDER`) that holds the master PK. Detail region queries bind to it: `WHERE order_id = :P1_SELECTED_ORDER`.

---
**Q**: What are the three True Actions in the standard master-detail click DA?
**A**: 1) Set Value (page item), 2) Refresh Detail Region, 3) Refresh Summary Region. Order matters!

---
**Q**: Why use Interactive Grid (not Interactive Report) for detail?
**A**: IG supports inline editing, add row, multi-delete, toolbar, and declarative save processing. IR is read-only.

---
**Q**: What is a virtual column and why use it for `line_total`?
**A**: `GENERATED ALWAYS AS (expr) VIRTUAL` — computed on read, zero storage, consistent between DB and APEX, indexable, no PL/SQL overhead.

---
**Q**: How do you make master selection bookmarkable and survive F5?
**A**: Link column target: `f?p=&APP_ID.:1:&SESSION.:::P1_SELECTED_ORDER:#ORDER_ID#` — sets item via URL.

---

## Dynamic Actions

---
**Q**: In a click DA on `.select-order-link`, what is `this.triggeringElement`?
**A**: The `<a>` (link) element that was clicked. Use `$(this.triggeringElement).closest('tr')` to get the row.

---
**Q**: When should a Refresh DA have "Fire on Page Load = Yes"?
**A**: When the page item might already have a value on initial load (e.g., from bookmark URL). Ensures detail loads on entry.

---
**Q**: How do you highlight the selected master row?
**A**: DA Execute JS: `$('tr.highlight-row').removeClass('highlight-row'); $(this.triggeringElement).closest('tr').addClass('highlight-row');`

---
**Q**: What custom event pattern enables decoupled region communication?
**A**: `apex.event.trigger(document, 'custom-event', { data: 'value' });` — subscriber DA listens for 'custom-event'.

---
**Q**: How to set a page item value from JavaScript without triggering change event?
**A**: `apex.item('P1_ITEM').setValue('val', null, true);` — third param `suppressChangeEvent = true`.

---

## Interactive Grid

---
**Q**: How to access the IG JavaScript model from a Dynamic Action?
**A**: `var model = apex.region('STATIC_ID').widget().interactiveGrid('getViews').grid.model;`

---
**Q**: What process type handles IG row inserts/updates/deletes declaratively?
**A**: "Interactive Grid - Save Data" — set Primary Key to table PK (e.g., `ITEM_ID`).

---
**Q**: How to default new IG row's foreign key to selected master?
**A**: Column `ORDER_ID` → Default Value → Type: PL/SQL Expression → Value: `:P1_SELECTED_ORDER`

---
**Q**: Client-side line total recalculation in IG — what event and code?
**A**: DA: Change on QUANTITY, UNIT_PRICE columns → Execute JS: `model.setValue(record, 'LINE_TOTAL', qty * price);`

---
**Q**: How to refresh summary region after IG save?
**A**: DA: Event "After Refresh" on IG region → True Action: Refresh "Order Summary" region.

---

## PL/SQL & Database

---
**Q**: How to recalc order total after detail changes?
**A**: `UPDATE orders SET total_amount = (SELECT NVL(SUM(line_total),0) FROM order_items WHERE order_id = :P1_SELECTED_ORDER) WHERE order_id = :P1_SELECTED_ORDER;`

---
**Q**: How to validate no negative quantities in detail before save?
**A**: Page Validation (PL/SQL Function Body Returning Error): query `order_items WHERE order_id = :P1_SELECTED_ORDER AND quantity <= 0`.

---
**Q**: How to enforce valid status transitions (SHIPPED ↛ PENDING)?
**A**: In "Update Status" button DA PL/SQL: `SELECT status INTO l_old ... CASE WHEN l_old='SHIPPED' AND :P1_NEW='PENDING' THEN RAISE...`

---
**Q**: What DDL ensures detail rows auto-delete when master deleted?
**A**: `FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE`

---
**Q**: How to log API calls with response/error for audit?
**A**: Insert into `api_call_log` (endpoint, request, response, http_status, duration, created_date) in PL/SQL block.

---

## Performance & Debugging

---
**Q**: Two indexes critical for master-detail performance?
**A**: `CREATE INDEX idx_orders_customer ON orders(customer_id);` and `CREATE INDEX idx_items_order ON order_items(order_id);`

---
**Q**: How to trace Dynamic Action execution?
**A**: URL: `&p_debug=YES&p_debug_level=9` → Query `apex_debug_messages` for session.

---
**Q**: Detail region not refreshing but DA fires — first check?
**A**: Refresh true action's "Affected Elements" — is the correct region selected? Does it have a Static ID?

---
**Q**: Stale data in detail after save — likely cause?
**A**: Process order wrong. Ensure: 1) IG Save, 2) Recalc Total, 3) DA Refresh — all in same transaction.

---
**Q**: How to implement connection drain before node maintenance?
**A**: F5: set pool member to "user-down" → wait 30 min for sessions to complete → maintenance.

---

## Advanced Patterns

---
**Q**: Multi-level master-detail (Order → Items → Serials) — what's needed?
**A**: Second page item `P1_SELECTED_ITEM`, third region `WHERE item_id = :P1_SELECTED_ITEM`, DA on IG row click → Set Value → Refresh.

---
**Q**: Keyboard accessibility for master IR rows?
**A**: Add `tabindex="0"` to links. DA: Key Down (Enter/Space) on link → trigger click. DA: Focus/Blur for visual ring.

---
**Q**: How to batch-process 1000+ records from CSV in APEX?
**A**: `APEX_DATA_PARSER.PARSE(p_content => ..., p_format => 'CSV')` → loop batches of 100 → `APEX_WEB_SERVICE.MAKE_REST_REQUEST` for each batch.

---
**Q**: Retry logic for external API calls?
**A**: PL/SQL procedure with `FOR attempt IN 1..3 LOOP ... EXCEPTION WHEN OTHERS THEN DBMS_LOCK.SLEEP(attempt*2); END LOOP; RAISE;`

---
**Q**: What is the EBS R12.2 online patching file system model?
**A**: Dual file systems (Run edition / Patch edition). `adop` cycles: prepare → apply → finalize → cutover. Rolling cutover per region.

---

## Quick Reference: DA Cheat Sheet

| Task | Event | Selection | True Actions |
|------|-------|-----------|--------------|
| Click master row | Click | jQuery: `.select-order-link` | Set Value → Refresh Detail → Refresh Summary → JS Highlight |
| Page load restore | Page Load | — | Refresh Detail → Refresh Summary (Fire on Load=Yes) |
| IG cell change | Change | IG Columns: QTY, PRICE | JS: recalc LINE_TOTAL |
| IG save done | After Refresh | Region: Order Items | Refresh Summary |
| Status button | Click | Button: UPDATE_STATUS | PL/SQL validate+update → Refresh All |
| Keyboard select | Key Down | jQuery: `.select-order-link` | Condition: Enter/Space → Click |

---

## Quick Reference: SQL Patterns

| Pattern | SQL |
|---------|-----|
| Virtual column | `line_total NUMBER GENERATED ALWAYS AS (qty * price) VIRTUAL` |
| Master query | `SELECT o.*, c.name FROM orders o JOIN customers c ON ... ORDER BY o.order_date DESC` |
| Detail query | `SELECT * FROM order_items WHERE order_id = :P1_SELECTED_ORDER` |
| Summary query | `SELECT o.*, COUNT(oi.item_id), SUM(oi.line_total) FROM orders o LEFT JOIN order_items oi ... WHERE o.order_id = :P1_SELECTED_ORDER GROUP BY ...` |
| Recalc total | `UPDATE orders SET total = (SELECT SUM(line_total) FROM order_items WHERE order_id = :P1_SEL) WHERE order_id = :P1_SEL` |
| Status transition | `CASE WHEN old='SHIPPED' AND new='PENDING' THEN RAISE ELSE UPDATE ... END CASE` |
| Inventory check | `SELECT product, qty FROM order_items WHERE order_id=:P1_SEL AND qty > (SELECT stock FROM inventory WHERE product=...)` |

---

## Study Tips
1. **Build it once** — Do Exercise 1 end-to-end without looking
2. **Break it** — Remove a True Action, predict what breaks, verify
3. **Explain aloud** — Teach the Set Value → Refresh sequence to a rubber duck
4. **Debug mode** — Run with `&p_debug=YES`, trace DA execution
5. **Extend** — Add Exercise 8 (multi-level) to cement the pattern