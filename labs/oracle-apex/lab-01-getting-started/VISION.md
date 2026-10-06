# Lab 01: APEX Getting Started — VISION

## Where this lab takes you

From an empty schema to a secure, supportable CRUD application — and, more
importantly, the habit of making the three early decisions that determine whether
it stays safe: the scoping predicate in the first query, server-side DML in
processes, and the export committed to source control.

## The Arc

1. **The model** — workspace, schema, application, page, region, item.
2. **Queries per render** — every region is a query, every time.
3. **Sargability** — the column is compared to a value, not to a function of one.
4. **Selectivity** — dates are the lever; status is not.
5. **State** — session state for context, URL only for shareable links.
6. **DML** — in a process with a condition, never in a region query.
7. **Validation** — server-side, with a message naming the bad value.
8. **Row security** — every region including summaries, and failing closed.
9. **Deletion** — confirmation plus an audit snapshot.
10. **Portability** — the YAML export as the rollback path.

## Milestones (checkable)

- [ ] M1: Draw the workspace → schema → application → page → region hierarchy.
- [ ] M2: Build the IR and count the queries the page issues.
- [ ] M3: Prove pagination does not reduce rows examined — record the numbers.
- [ ] M4: Time a sargable and a non-sargable date predicate side by side.
- [ ] M5: Show one hard parse with literals, one with binds.
- [ ] M6: Replace a URL ID with session state and confirm nothing is editable.
- [ ] M7: Implement create and update in one process branching on the primary key.
- [ ] M8: Add three validations; confirm each message names the value entered.
- [ ] M9: Scope every region, and *demonstrate* the summary leak before fixing it.
- [ ] M10: Clear the context and confirm zero rows, not all rows.
- [ ] M11: Confirm a cross-department `UPDATE` reports zero rows affected.
- [ ] M12: Delete with confirmation and audit; verify the snapshot holds the row.
- [ ] M13: Export, re-import to a clean workspace, and run a smoke test.

## Anti-Goals

- Adding row security at the end rather than with the first query.
- Scoping detail regions and leaving a summary or chart unscoped.
- Passing record IDs in the URL.
- Putting `INSERT` or `UPDATE` in a region query.
- Relying on client-side validation, or on page validation alone.
- Using `NVL` on the *column* and wondering why the index stopped being used.
- Deleting with no confirmation and no audit record.
- Delivering without testing at 375 px width.
- Delivering without an export in source control.

## The traps this lab is designed around

- **"Only 25 rows are displayed."** Pagination is not a filter; the database still
  reads the range.
- **"The button is hidden, so they cannot use it."** Hidden is not denied.
- **"The summary shows no other rows."** Duplicate aggregate labels still disclose.
- **"Validation is in place."** Client-side validation is bypassable; page
  validation is omittable; only the constraint is authoritative.
- **"It will not scale."** It scales or it does not, and the difference is decided
  by selectivity and region count — both measurable on day one.

## The one-sentence thesis

Build the security predicate into the first query and the application is safe by
construction; retrofitting it means re-reading every query, and the one you miss
is the disclosure.
