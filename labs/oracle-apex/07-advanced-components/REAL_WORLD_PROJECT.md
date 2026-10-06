# Lab 07: APEX Advanced Components — Real World Project

## Scenario
A distributor's sales team enters order lines from customer phone calls. Today
they open one APEX form per line — 12 lines per order means 12 page loads and 12
save round trips, roughly 4 minutes per order. Errors are frequent because the
team member cannot see the order total while entering lines, so they routinely
discover at the end that a discount was mis-keyed. The business wants an
Excel-like grid: type the lines, see the total change, save once. A second
requirement is an analytics browser for the commercial team with multi-level
drill-down and Oracle JET charts.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (Interactive Grid)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (Oracle JET charts)
- https://docs.oracle.com/en/database/oracle/oracle-database/21/lnpls/

## Architecture
```
Order Entry page
   ├─ Master IG: orders (aggregated net_amount), no editing
   │     └─ Dynamic Action on selection → set P1_ORDER_ID → Refresh detail
   │
   └─ Detail IG: order_line WHERE order_id = :P1_ORDER_ID
         ├─ Editable: item_code (popup LOV), quantity, unit_price, discount_pct
         ├─ Computed (recalculated, NOT stored): line_total
         ├─ Cell validation: qty > 0 · price > 0 · discount 0-100
         ├─ Row validation: order total discount ≤ 20%  (fires on Save)
         ├─ Save guard: ≤ 500 changed rows
         ├─ Control break: category; aggregations: SUM(line_total)
         └─ Per-user state + reset action + scheduled tidying

Analytics page: master-detail IG pair + Oracle JET charts (≤ 12 points each)
```

## Implementation sketch
```sql
-- Recalculate, never store: a stored line_total can disagree with its inputs
SELECT ol.line_id, ol.item_code, i.description,
       ol.quantity, ol.unit_price, ol.discount_pct,
       ROUND(ol.quantity * ol.unit_price * (1 - ol.discount_pct/100), 2) line_total
  FROM order_line ol
  JOIN item i ON i.item_code = ol.item_code
 WHERE ol.order_id = :P1_ORDER_ID;

-- Row validation: spans rows, so it cannot be a cell rule
SELECT SUM(NVL(discount_pct,0)) INTO l_total FROM order_line
 WHERE order_id = :P1_ORDER_ID;
IF l_total > 20 THEN
  RAISE_APPLICATION_ERROR(-20200,
    'Total discount is '||l_total||'%, exceeding the 20% limit.');
END IF;
```

## Requirements
- F1: Editable IG with primary key configured on the source query.
- F2: Editable columns restricted to item, quantity, price, and discount.
- F3: Popup LOV on item showing the standard price on select.
- F4: Live recalculation of line total on cell change and new row.
- F5: Three cell validations with messages naming the entered value.
- F6: Row validation for the order discount limit, firing on Save.
- F7: Save guard refusing more than 500 changed rows.
- F8: Aggregations and control break for interactive grouping.
- F9: Master-detail IG pair bound through the master's selection.
- F10: Per-user state with a reset action and scheduled tidying.
- F11: Oracle JET charts with series limited to 12 points.
- F12: At least one plugin replacing framework-copied code.
- F13: Undiscarded-changes warning on navigation.
- NF1: Order entry reduced from ~4 minutes to under 60 seconds.
- NF2: Entry errors reduced by at least 80%.
- NF3: Bulk save of 50 rows under 2 seconds.
- NF4: Security baseline — the grid cannot address another order's rows.
- NF5: No partial or inconsistent state from a failed save.
- NF6: Documented rollback for every configuration and plugin change.

## Milestones
- Week 1: IG configuration, editable columns, LOV, cell validations.
- Week 1: Live recalculation and row validation.
- Week 2: Save guard, aggregations, control break.
- Week 2: Master-detail pair and per-user state.
- Week 3: Analytics page with JET charts; plugin adoption.
- Week 3: User acceptance testing with the sales team.

## Verification
- Timing of order entry before and after with the same user and order.
- Error rate comparison over a week of live entries.
- Attempt to address a row from another order; confirm the query prevents it.
- Force a save failure; confirm no partial state.
- Submit over 500 changed rows; confirm refusal.
- Test the reset action after deliberately breaking the layout.
- Verify tidying reduces state rows without affecting active sessions.

## Rollback
Grid configuration is exportable; validations disable individually; the plugin is
installed as a component and removable; the per-line form pages remain available
until cutover sign-off. Document rollback steps for every change.