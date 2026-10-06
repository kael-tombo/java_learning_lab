# Lab 01: APEX Getting Started — Mini Project

## Goal
Build a secure department expense application with IR, form, summaries, and row
security in 90 minutes.

## Requirements
- R1: Schema for departments, users, and expenses with a `CHECK` on amount.
- R2: Session context set once at authentication.
- R3: A fail-closed `current_department()` function.
- R4: IR list region with date and category filters, scoped.
- R5: Two summary regions — by category and by month — both scoped.
- R6: Form page with a read query and a save process handling both modes.
- R7: Three server-side validations with messages naming the bad value.
- R8: Delete with confirmation and an audit snapshot.

## Steps
1. Create the schema, constraints, and indexes; load 200 test rows.
2. Write `current_department()` returning `-1` when the context is NULL.
3. Set the session context on login.
4. Build the list page with the IR and filters; bind all filters into the query.
5. Add the two summary regions — confirm both carry the scoping predicate.
6. Build the form page with a scoped read query.
7. Write the save process branching on `P1_EXPENSE_ID`.
8. Add the three validations and test each with bad input.
9. Add delete with a confirmation dialog and an audit insert.
10. Demonstrate the summary leak by temporarily removing the predicate, then
    restore it.

## Acceptance criteria
- Every region touching `expense` contains `current_department()`.
- With the context cleared, the list returns zero rows rather than all rows.
- The scoped UPDATE cannot modify another department's row.
- Each validation message names the field and the value entered.
- Deleting writes an audit row containing the row snapshot.
- The application exports and re-imports successfully.

## Stretch
- Load 50,000 rows and time the list page before and after adding an index.
- Demonstrate that `TRUNC(expense_date)` disables the index.