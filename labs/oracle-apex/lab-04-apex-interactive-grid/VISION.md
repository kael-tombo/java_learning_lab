# Lab 04: APEX Interactive Grid — Vision

## Where this lab takes you
From "Interactive Reports are for reading, Interactive Grid is for editing" to
building a spreadsheet-grade grid with cell validation, aggregation, and bulk
save.

## The Arc
1. **IR vs IG** — the same lineage, different purposes.
2. **Configuration** — table attributes, layout, and where the SQL lives.
3. **Columns** — type, formatting, and computed versus editable.
4. **Editing** — insert, update, delete, and the Save model.
5. **Validation** — cell-level, row-level, and why both are needed.
6. **Aggregation** — control breaks and computed rollups.
7. **Bulk save** — one AJAX call for many rows.
8. **State** — saving a user's layout preference.

## Milestones (checkable)
- [ ] M1: Explain when to choose IG over IR and justify with a case.
- [ ] M2: Build an IG and locate its source query.
- [ ] M3: Distinguish editable from display-only columns.
- [ ] M4: Add a calculated column and decide whether it saves.
- [ ] M5: Add cell validation and row validation and test both.
- [ ] M6: Add aggregations and a control break.
- [ ] M7: Save 50 edited rows in one operation and verify.
- [ ] M8: Persist a user's column layout preference.

## Anti-Goals
- Using IG for read-only reports where IR is simpler.
- Editing rows without a primary key.
- Relying on cell validation alone for a rule that spans rows.
- Saving thousands of rows in one interaction without a stated limit.

## The one-sentence thesis
An Interactive Grid is a spreadsheet over your table — that is its power and its
hazard, because the database still enforces every rule you think the client has
been given.