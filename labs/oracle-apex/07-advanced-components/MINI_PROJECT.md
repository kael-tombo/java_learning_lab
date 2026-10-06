# Lab 07: APEX Advanced Components — Mini Project

## Goal
Build an Excel-like order-line entry grid with validation, computed totals,
control breaks, master-detail, and per-user state in 90 minutes.

## Requirements
- R1: An editable IG with a configured primary key.
- R2: Editable columns restricted to three business fields.
- R3: Three cell validations with messages naming the bad value.
- R4: A recalculated computed column, including on new rows.
- R5: One row validation for a rule that spans rows.
- R6: A save guard that refuses over 500 changed rows.
- R7: A master IG with a detail IG bound through the master's selection.
- R8: Per-user state with a reset action and a tidying query.

## Steps
1. Create order, order_line, item, and customer tables with keys.
2. Build the detail IG with editing enabled and `LINE_ID` as the primary key.
3. Mark quantity, unit_price, and discount editable; the rest read-only.
4. Add a popup LOV on item_code showing unit_price on select.
5. Add the three cell validations and test each.
6. Add the JavaScript to recalculate `line_total` on cell change and new row.
7. Add the order-level discount row validation.
8. Add the save process with the 500-row guard.
9. Build the master IG and the Dynamic Action that refreshes the detail.
10. Enable saved state, add a reset action, and write the tidying query.

## Acceptance criteria
- Editing works only because the primary key is configured.
- Each cell validation fires during editing with a specific message.
- The computed column updates live and is not persisted.
- The row validation fires on Save, not during editing.
- A submission of over 500 changed rows is refused.
- Selecting a master row loads that order's lines without a page submit.
- The reset action restores the default layout.

## Stretch
- Add an aggregation and a control break, and change the grouping interactively.
- Write an item-type plugin and compare its cost against a shared component.