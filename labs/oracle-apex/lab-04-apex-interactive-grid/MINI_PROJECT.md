# Lab 04: APEX Interactive Grid — Mini Project

## Goal
Build an Excel-like editable grid for order line entry with cell validation, a
calculated total, and bulk save, in 90 minutes.

## Requirements
- R1: An IG region sourced from `order_item` filtered by a bind variable.
- R2: Editing enabled for insert, update, and delete.
- R3: A primary key defined so updates are addressable.
- R4: Cell validation: quantity > 0, unit price > 0, discount 0–100.
- R5: A calculated line total column that does not save.
- R6: A row-level validation for a business rule spanning columns.
- R7: An aggregation and a control break on category.
- R8: Bulk save of at least 50 rows in one operation.

## Steps

1. Create the `order_item` table with `order_item_id` as the primary key.
2. Load 200 rows across five orders.
3. Create the page and the IG region with `:P_ORDER_ID` as a bind variable.
4. Enable editing for insert, update, and delete.
5. Mark quantity, unit price, and discount editable; mark the rest read-only.
6. Add cell validations and test each by entering a bad value.
7. Add the calculated line total as a display-only column.
8. Add a row-level validation (e.g. total discount per order ≤ 20%).
9. Add an aggregation and a control break on category.
10. Edit 50 rows and save in one operation; verify with a query.

## Acceptance criteria
- Invalid cell values are rejected before save with a specific message.
- The calculated total updates as cells change but is not persisted.
- The row-level validation fires on save, not on cell edit.
- 50 rows save in a single interaction.
- The primary key is defined; updates do not duplicate rows.

## Stretch
- Persist a user's column layout and re-open to confirm it restored.
- Add a row-level validation that references another row and test it.