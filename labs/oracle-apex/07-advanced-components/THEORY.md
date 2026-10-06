# Lab 07: APEX Advanced Components — Theory

## The Scenario

A client needs an Excel-like editable grid for order entry: a user types order
lines, sees the line total recalculate, gets per-cell validation, and saves once.
Separately, an analytics page needs Oracle JET charts and master-detail browsing.

## Principle 1: IG and IR are the same lineage with different intents

Both descend from the classic report, both render in the browser, both support
filtering and export. The difference is one question: **does the user edit?**

| | Interactive Report | Interactive Grid |
|---|---|---|
| Intent | Display and analyse | Display and edit |
| Editing | No | Yes |
| Save model | N/A | One AJAX call for changed rows |
| Row addressing | Not required | **Primary key required** |
| Column types | Text, links, images, JSON | Text, number, date, popup LOV, checkbox, rich text |
| Layout | Row display options | Pivot, group by, aggregate, chart view |
| Best for | Read-only analysis | Spreadsheet-style data entry |

**The primary key requirement is the practical consequence.** Editing means the
database must know which row to update. Without a key, APEX cannot address rows,
so an editable grid over a keyless query is not editable.

## Principle 2: The Save contract is one request

When a user edits 50 cells in an IG, nothing is written until Save. Then:

```
One AJAX request carries the changed rows
One DML statement (or set of statements) applies them
One commit
```

**Nothing is saved per cell.** This is the single most important property to
communicate to users, because it inverts their expectation from a grid where
typing commits.

```
User expectation: "I typed, so it's saved"
Reality:          "I typed, so it's pending until I press Save"
```

Both the UI and the training must make this explicit. Undiscarded changes on
navigation need a browser confirmation.

## Principle 3: Cell validation and row validation are different problems

```
Cell validation:  one field is invalid on its own terms
                  quantity <= 0

Row validation:   the row is invalid in combination with other rows or columns
                  total discount on this order exceeds 20%
                  line total exceeds the order credit limit
```

**Rules that span rows cannot be cell validations.** A cell validation sees one
cell. Any rule involving sums, cross-row comparisons, or aggregate state must be
row-level — and row-level rules only fire on Save, not during editing.

This distinction determines user experience:

| Rule type | When it fires | User experience |
|-----------|---------------|-----------------|
| Cell | During editing | Immediate feedback |
| Row | On Save | Feedback at the end |

**Put as much as possible in cell validation** so the user gets immediate
feedback, and reserve row validation for what genuinely requires it.

## Principle 4: Computed columns — recalculated or saved is a design decision

A computed column can either:

```
Recalculate (display only):  computed in the grid, never persisted
Save (editable):             written by a process on Save
```

Choose by asking whether the value is a property of the record or a consequence of
its columns.

```
line_total = quantity × unit_price × (1 − discount/100)
  → consequence of columns. Recalculate. Never store it.

discount_amount
  → could be stored (audit) or recalculated. Depends on whether the business
    needs it independent of the current quantity.
```

**Storing a computed value risks it disagreeing with its inputs.** A stored
`line_total` that no longer matches `quantity × unit_price` is a data integrity
problem that will surface in a report nobody expected to be wrong.

## Principle 5: Editing without a primary key

```
IG source:  SELECT order_id, item_code, quantity FROM order_item
Editing:    ENABLED

APEX cannot address rows. Saves either fail or match rows by position.
```

Every editable IG needs:

```
1. A primary key column in the source query
2. That key configured as the IG's primary key
3. DML applied through the key, never through row position
```

For a query without a natural key, generate one:

```sql
SELECT ROW_NUMBER() OVER (ORDER BY o.order_id, i.item_code) AS row_key,
       o.order_id, i.item_code, l.quantity
  FROM ...
```

**This is a warning sign.** If an editable grid needs a synthetic key, the data
model is missing an identity that should exist. Ask why before proceeding.

## Principle 6: Aggregation and control breaks answer "by what" without extra regions

```
Group by region, aggregate SUM(net_amount)
```

In APEX you could build a separate chart region for this. Or, on the same IG:

```
Control break: GROUP BY region
Aggregations:  SUM(net_amount), COUNT(*) per region
```

**The advantage is interaction**: the user changes the grouping without a round
trip. The disadvantage is that the chart region cannot be linked from elsewhere on
the page.

Rule: aggregation for **exploration** belongs on the IG; a fixed chart for
**communication** belongs in its own region.

## Principle 7: Master-detail grids replace joins-on-demand

A detail grid that depends on the row selected in a master grid:

```
Master IG:  orders
Detail IG:  order lines, filtered by :P_ORDER_ID from the master selection
```

**The dependency must be in the detail's SQL**, not applied client-side:

```sql
-- Master IG: return the order_id
SELECT order_id, order_number, customer_name, order_date, net_amount
  FROM orders WHERE customer_id = :P_CUSTOMER_ID

-- Detail IG: bind the master's selection
SELECT line_id, order_id, item_code, description, quantity, unit_price
  FROM order_line
 WHERE order_id = :P1_ORDER_ID      -- set by the master's Dynamic Action
 ORDER BY line_id
```

A Dynamic Action on the master's selection sets `P1_ORDER_ID` and refreshes the
detail. This is the same pattern as Lab 02's master-detail, applied to grids.

## Principle 8: Per-user state is a usability feature with a cost

IG state includes:

```
Column order · column widths · visibility · sort · filters · aggregations
```

**State is stored per user in the database.** That is convenient and it grows.

```
State per user per IG: roughly 2-10 KB
Users: 1,200
IGs per user: 5-8

Total state: 1,200 × 7 × 5 KB = ~42 MB
```

Tidying removes the growth. Also provide a **Reset** action so a user whose
layout has drifted can recover without a DBA.

**Offer saved filters too**, so a user can name a filter rather than rebuilding
it — but cap the number per user, or the same growth problem appears.

## Principle 9: Oracle JET charts — power with a data limit

Oracle JET is APEX's modern charting library. It supports combinations, axes,
legends, and interactions that classic charts cannot.

**The limits are the same as any charting:**

| Data points | Result |
|--------------|--------|
| ≤ 12 | Readable |
| 12–52 | Acceptable |
| 52–200 | Busy but usable |
| > 200 | Unreadable and slow |

A chart is not a data viewer. If a series has 400 points, aggregate it or use a
table. This is a design decision, not a rendering limitation.

## Principle 10: Plugins extend APEX without forking it

Customising APEX by copying framework code creates an upgrade problem. Plugins are
the supported extension point.

| Plugin type | Extends | Use for |
|-------------|---------|---------|
| Item | A page item control | A custom widget (map, date picker, editor) |
| Region | Region rendering | A custom visualisation |
| Process | Server-side logic | Reusable business logic invoked from a page |
| Dynamic Action | Client-side behaviour | A reusable interactive behaviour |

```
Forking a framework file:  works today, breaks at the next APEX upgrade,
                          and you maintain a copy of Oracle's code
Plugin:                    supported, versioned, upgrade-safe
```

**Write a plugin when the same non-standard behaviour appears on three or more
pages.** Below that, a shared component or a Dynamic Action is less ceremony.

## Principle 11: Row limits on save are a correctness concern

An IG can accumulate thousands of changed rows. Saving them all in one statement
is possible and risky:

```
50 rows   — fine
500 rows  — fine
5,000 rows — one enormous statement, long lock duration, possible ORA-1555
```

Guard it:

```
If changed rows > N: refuse with a message, or process in batches
```

**Refusing is correct.** A user who has changed 5,000 cells has almost certainly
made an error, and the save succeeding would apply all of it.

## Design Order

1. Decide IG vs IR from the editing question alone.
2. Confirm a primary key exists; resolve the data-model question if not.
3. Push as much validation as possible to cell level.
4. Use row validation only for what genuinely spans rows.
5. Decide computed columns: recalculate unless it must be stored.
6. Choose one save model and communicate it clearly to users.
7. Guard the row count on save.
8. Use control breaks for exploration; separate regions for communication.
9. Master-detail via the master's selection bound into the detail's SQL.
10. Per-user state with tidying and a reset action.
11. Aggregate any chart series over ~52 points.
12. Plugin only when the same behaviour appears on three or more pages.

## Anti-Patterns

- Enabling editing on a keyless query.
- Row-level validation for a rule that could be cell-level.
- Storing a computed column that can disagree with its inputs.
- Leaving users unclear that edits are pending until Save.
- Saving thousands of rows without a guard.
- Charts with hundreds of points.
- Forking framework files instead of writing a plugin.
- Unbounded per-user state growth with no tidying or reset.

## Summary

The order-entry grid worked because four decisions came first: IG over IR
because the user edits, a real primary key because editing requires one, cell
validation for everything that can be immediate and row validation only for what
genuinely spans rows, and computed columns recalculated rather than stored so
they can never disagree with their inputs. Everything else — control breaks,
master-detail, per-user state — is convenience built on a sound editing model.