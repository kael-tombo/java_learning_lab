# Lab 07: APEX Advanced Components — VISION

## Where this lab takes you
From per-line Forms screens to a single spreadsheet-style grid — choosing the
component, requiring a real primary key, and placing validation so errors surface
while the user is still looking at the cause.

## The Arc
1. **IG or IR** — the editing question decides it.
2. **Primary key** — editing requires row addressability.
3. **Save contract** — one request, nothing written until Save.
4. **Cell vs row validation** — immediate feedback where possible.
5. **Computed columns** — recalculate unless it must be stored.
6. **Control breaks** — rollups without a round trip.
7. **Master-detail** — bind the master's selection into the detail's SQL.
8. **Per-user state** — with tidying and a reset action.
9. **JET and plugins** — power with a data limit; extension without forking.

## Milestones (checkable)
- [ ] M1: Classify 8 scenarios as IG or IR from the editing question.
- [ ] M2: Build an editable IG and prove the primary key configuration matters.
- [ ] M3: Add three cell validations and confirm immediate feedback.
- [ ] M4: Add a row validation for a rule that genuinely spans rows.
- [ ] M5: Recalculate a computed column on edit, including new rows.
- [ ] M6: Guard the save with a row limit and confirm it refuses.
- [ ] M7: Build a master-detail pair bound through the master's selection.
- [ ] M8: Add state tidying, a reset action, and a plugin-based item.

## Anti-Goals
- Enabling editing on a keyless query.
- Row validation for a rule that could be cell-level.
- Storing a computed column that can disagree with its inputs.
- Leaving users unclear that edits are pending until Save.
- Saving thousands of rows with no guard.
- Charts with hundreds of points.
- Forking framework files instead of writing a plugin.
- Per-user state growth with no tidying or reset.

## The one-sentence thesis
An Interactive Grid is a spreadsheet over your table — its power and its hazard
are the same thing, and the primary key plus the save contract are what make it
safe.