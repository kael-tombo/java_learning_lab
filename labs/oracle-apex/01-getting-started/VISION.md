# Lab 01: APEX Getting Started — VISION

## Where this lab takes you
From an empty schema to a secure CRUD application in a week — with the three
early decisions that determine whether it is safe and supportable.

## The Arc
1. **The model** — workspace, schema, application, page, region.
2. **Queries per render** — every region is a query, every time.
3. **State** — session state for context, not URL parameters.
4. **DML** — in processes with conditions, never in a region query.
5. **Validation** — server-side, with messages that tell the user what to fix.
6. **Row security** — every region, including summaries, and failing closed.
7. **Deletion** — confirmation plus an audit snapshot.
8. **Portability** — export as the rollback path.

## Milestones (checkable)
- [ ] M1: Draw the workspace/schema/application/page/region hierarchy.
- [ ] M2: Build the IR and count how many queries the page issues.
- [ ] M3: Prove that pagination does not reduce rows examined.
- [ ] M4: Replace a URL ID with session state and confirm it is not editable.
- [ ] M5: Implement create/update in one process with a branching condition.
- [ ] M6: Add validation and confirm the messages name the bad value.
- [ ] M7: Scope every region and demonstrate the summary leak before fixing it.
- [ ] M8: Confirm the context fails closed, then add delete audit.

## Anti-Goals
- Adding row security at the end rather than with the first query.
- Scoping detail regions but leaving the summary unscoped.
- Passing record IDs in the URL.
- Putting INSERT or UPDATE in a region query.
- Relying on client-side validation.
- Deleting with no confirmation and no audit record.
- Delivering without testing at 375 px width.

## The one-sentence thesis
Build the security predicate into the first query and the application is safe by
construction — retrofitting it means re-reading every query, and the one you
miss is the disclosure.