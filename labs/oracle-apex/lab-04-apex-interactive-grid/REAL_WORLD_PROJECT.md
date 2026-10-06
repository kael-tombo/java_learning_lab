# Lab 04: APEX Interactive Grid — Real World Project

## Scenario
A distributor's sales team enters order lines from a customer phone call. Today
they open one APEX form per line: 12 lines on a typical order means 12 page
loads, 12 save round trips, and roughly 4 minutes per order. Errors are common
because the team member has no view of the order total while entering lines,
so they routinely discover at the end that a discount was mis-keyed. The
business wants an Excel-like grid: type the lines, see the total change as they
type, and save once.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (Interactive Grid)
- https://docs.oracle.com/en/database/oracle/oracle-database/19/lnpls/

## Architecture
```
Order Entry page
   │
   ├─ Order header region (read-only, order number, customer, ship date)
   │
   └─ Interactive Grid: order_item WHERE order_id = :P1_ORDER_ID
        │
        ├─ Editable: quantity, unit_price, discount_pct
        ├─ Computed (no save): line_total = quantity × unit_price × (1 − discount)
        ├─ Cell validation: quantity > 0 · unit_price > 0 · discount 0–100
        ├─ Row validation: line_total ≤ order line credit limit
        ├─ Aggregation: order total across all lines
        ├─ Control break: group by product category
        └─ Save: single AJAX round trip for all edited rows

Primary key on order_item_id — mandatory for addressing updates
```

## Implementation sketch
```sql
-- Grid source: bind variable, never a literal
SELECT oi.order_item_id,
       oi.product_id,
       p.category_name,
       oi.quantity,
       oi.unit_price,
       oi.discount_pct,
       -- computed: display only, not saved
       ROUND(oi.quantity * oi.unit_price * (1 - oi.discount_pct/100), 2) line_total
  FROM order_item oi
  JOIN product  p ON p.product_id = oi.product_id
 WHERE oi.order_id = :P1_ORDER_ID     -- required; otherwise the grid is unbounded
 ORDER BY p.category_name, oi.order_item_id;
```

```sql
-- Row-level validation: a rule that spans columns cannot be a cell rule
-- Total discount on an order must not exceed 20%
SELECT SUM(discount_pct) FROM order_item WHERE order_id = :P1_ORDER_ID;
```

## Requirements
- F1: IG with insert, update, and delete enabled.
- F2: Primary key defined on the grid source.
- F3: Editable columns restricted to the three business fields.
- F4: Computed line total, display-only, recalculating on edit.
- F5: Cell validations with specific, actionable messages.
- F6: Row-level validation for the order discount limit.
- F7: Aggregation of order total and control break by category.
- F8: Single bulk save for all edited rows.
- F9: Column layout preference persisted per user.
- F10: Guard on rows saved per operation with a clear limit message.
- NF1: Order entry time reduced from ~4 minutes to under 60 seconds.
- NF2: Entry errors reduced by at least 80% through inline validation.
- NF3: Bulk save of 50 rows completes in under 2 seconds.
- NF4: Security baseline — the grid cannot address another order's rows.
- NF5: No data loss from a partial save failure.
- NF6: Documented rollback — validation and configuration are reversible.

## Milestones
- Week 1: Grid configuration, source query, and editing model.
- Week 2: Computed column, cell validations, and row validation.
- Week 3: Aggregations, control break, and layout persistence.
- Week 4: Bulk save with failure handling; user acceptance testing.

## Verification
- Enter invalid values in each editable field; confirm rejection messages.
- Save 50 rows in one operation; verify with a database query.
- Force a mid-save failure; confirm no partial, inconsistent state.
- Attempt to address a row from another order; confirm the source query prevents it.
- Time order entry before and after with the same user and order.

## Rollback
Grid configuration is exportable; validations can be disabled individually; the
old per-line form pages remain available until cutover. Document rollback steps
for every change.