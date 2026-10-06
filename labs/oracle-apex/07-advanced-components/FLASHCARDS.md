# Lab 07: APEX Advanced Components — Flashcards

## IG vs IR

---
**Q**: The deciding question?
**A**: Does the user edit the data?

---
**Q**: Why does IG require a primary key?
**A**: Editing means the database must address rows. Without a key APEX cannot.

---
**Q**: Synthetic key as a warning sign?
**A**: It suggests the data model is missing an identity that should exist. Ask why.

---
**Q**: IG capabilities IR lacks?
**A**: Editing, pivot/group-by, chart view, popup LOV and select-list column types.

---
**Q**: Cost of getting it wrong, IG for read-only?
**A**: Extra configuration, larger payload, no benefit.

---

## The Save Contract

---
**Q**: When does an IG write?
**A**: On one AJAX call at Save. Not per cell, not on navigation.

---
**Q**: Why does that matter?
**A**: It inverts user expectation. Users must be told edits are pending until Save.

---
**Q**: Add undiscarded-changes warning?
**A**: Yes — a browser confirmation on navigation.

---
**Q**: Payload for 50 changed rows?
**A**: ~25 KB. 5,000 rows is ~2.5 MB — a timeout risk before the DML cost.

---
**Q**: Row guard threshold?
**A**: 500 changed rows. Refuse with a message.

---

## Validation

| Rule type | Fires | Feedback |
|-----------|-------|----------|
| Cell | During editing | Immediate |
| Row | On Save | Delayed |

---
**Q**: Why prefer cell where possible?
**A**: ~3 s resolution versus ~40 s. The user still has context.

---
**Q**: Why can't a row rule be a cell rule?
**A**: It spans rows or aggregate state; a cell validation sees one cell.

---
**Q**: Classic cross-row rule?
**A**: "Total discount on this order ≤ 20%" — a sum over lines.

---
**Q**: Every validation message must?
**A**: Name the field, the rule, and the value entered.

---

## Computed Columns

---
**Q**: Recalculate or store?
**A**: Recalculate unless it must be independent of its inputs.

---
**Q**: Risk of storing?
**A**: It can disagree with its inputs after an edit, requiring a reconciliation
job nobody remembers to build.

---
**Q**: Cell validation on programmatic setValue?
**A**: Does not reliably fire — recalculate the computed column explicitly in JavaScript.

---
**Q**: New-row case?
**A**: Handle `iggridcelladded` to initialise defaults and recalculate.

---

## Aggregations and Master-Detail

---
**Q**: Control break purpose?
**A**: Rollups and interactive re-grouping with no page round trip.

---
**Q**: IG chart view vs separate chart region?
**A**: IG for exploration (interactive grouping); separate region for communication
(linkable from elsewhere).

---
**Q**: Master-detail wiring?
**A**: DA on master selection sets an item; detail IG SQL binds it.

---
**Q**: Master-detail latency gain?
**A**: ~900 ms submit → ~180 ms AJAX refresh. ~5×.

---

## Per-User State

---
**Q**: What does IG state include?
**A**: Column order, widths, visibility, sort, filters, aggregations.

---
**Q**: Size for 1,200 users × 7 IGs?
**A**: ~42 MB. ~4 MB/year growth.

---
**Q**: Is growth the real crisis?
**A**: No. The crisis is a user whose layout drifted and cannot self-recover.

---
**Q**: Therefore?
**A**: Provide a **reset** action. Add tidying for 30-day-old state as hygiene.

---
**Q**: Saved-filter cap?
**A**: 5. Above what users keep, below what creates support load.

---

## Oracle JET

---
**Q**: Readable point count?
**A**: ≤ 12 comfortably; ≤ 52 marginal; > 200 unreadable and slow.

---
**Q**: Where should the cap be enforced?
**A**: In the SQL (`FETCH FIRST 12 ROWS ONLY`), not by hoping the data stays small.

---
**Q**: A 400-point chart on 1,200 px?
**A**: Each point ~0.09 px — a solid block. Aggregate it.

---

## Plugins

| Plugin type | Extends |
|-------------|---------|
| Item | Page item control |
| Region | Region rendering |
| Process | Server-side logic |
| Dynamic Action | Client-side behaviour |

---
**Q**: When does a plugin beat a shared component?
**A**: Three or more pages. ~2 days vs ~1 day; break-even at ~6 APEX upgrades.

---
**Q**: Why never copy framework files?
**A**: Breaks at the next upgrade and leaves you maintaining Oracle's code.

---
**Q**: How to verify no framework edits?
**A**: Query `user_tab_updates` for modified `APEX_%` tables.

---

## Quick Reference

| Task | Mechanism |
|------|-----------|
| Row addressing | IG primary key |
| Live recompute | `cellchanged` handler + `setValueAndStash` |
| New row | `iggridcelladded` |
| LOV return | DA on Selection |
| Layout reset | `grid.resetColumnState()` |
| Progress | `APEX_APPLICATION.PROCESS` |
| Plugin install | `APEX_APPLICATION.CREATE_PLUGIN` |

---

## Numbers to Remember

| Metric | Value |
|--------|-------|
| Order entry, per-line → grid | 4 min → 50 s (4.8×) |
| Entry errors | 15% → 1% (15× fewer) |
| Save payload, 50 rows | ~25 KB |
| Save row guard | 500 |
| Cell vs row validation resolution | ~3 s vs ~40 s |
| Chart readable limit | ≤ 12 points |
| Per-user state, 1,200 users | ~42 MB |
| Plugin break-even | ~6 upgrades |

**The 15× error reduction is the number that matters** — it comes from the editing
model making errors visible while the user is still looking at the cause.

---

## Anti-Patterns

1. Editing on a keyless query.
2. Row validation for a cell-level rule.
3. Storing a computed column.
4. No warning that edits are pending until Save.
5. No row guard on save.
6. Charts with hundreds of points.
7. Copied framework files.
8. Unbounded per-user state, no reset action.

---

## Study Tips
1. Classify 8 scenarios IG vs IR from the editing question.
2. Explain why a row rule cannot be a cell rule.
3. State the four places a validation rule can live.
4. Recompute the plugin break-even for a different reuse count.