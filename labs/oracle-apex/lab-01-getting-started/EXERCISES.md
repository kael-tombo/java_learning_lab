# Lab 01: APEX Getting Started — Exercises

Grounded in `THEORY.md` and `CODE_DEEP_DIVE.md`. Schema: `department`, `app_user`,
`expense` with `ix_exp_dept_date` and `ix_exp_cat`.

## 1. Schema and seed (15 min)
Create `department`, `app_user`, `expense`, plus the two indexes. Insert 4
departments, 8 users, and 200 expenses spread over the last 6 months.
*Check:* `SELECT COUNT(*) FROM expense;` returns 200. `SELECT COUNT(*) FROM
expense WHERE amount <= 0;` returns 0 — the `CHECK` is already working.

## 2. First Interactive Report (15 min)
Build page 1 with an Interactive Report on `expense`, joined to `department` for
the name. Columns: date, department name, category, amount, status.
*Do not* add filters yet — count the queries the page issues using the APEX
debugger. Record the number.
*Check:* the page loads and the query count matches the region count.

## 3. Pagination is not a filter (10 min)
Turn on APEX debug and compare `rows processed` on page 1 with page 10.
*Check:* the rows processed grows with page depth even though 25 rows are
displayed on both. Record both numbers. This is the observation the whole
performance story rests on.

## 4. Sargable date filter (15 min)
Add page items `P1_DATE_FROM` and `P1_DATE_TO`. Write the predicate two ways and
time each in SQL Workshop with 50,000 rows loaded:

```sql
-- A: non-sargable
WHERE TRUNC(e.expense_date) = :p_date
-- B: sargable
WHERE e.expense_date >= :p_date AND e.expense_date < :p_date + 1
```
*Check:* B reads roughly 24,000 rows where A reads 50,000. Then apply B in the
IR with a Dynamic Action refreshing the region on change.

## 5. Bind variables (10 min)
Add the category filter as a bind and then, temporarily, as a concatenation
(`'&P1_CATEGORY'`). Fire the Dynamic Action 20 times with different values.
*Check:* with concatenation the debug log shows 20 hard parses; with binds it
shows 1 hard parse and 20 executions. Revert to binds.

## 6. Session state and linking (15 min)
Create page 2 (form). Make the ID column a link column passing `P2_EXPENSE_ID`,
then move the value to session state with an After-Authentication computation and
a Before Process on page 2 that copies it into the page item.
*Check:* open the address bar. The expense ID is no longer there, and there is
nothing in the browser to edit.

## 7. Save process for both modes (20 min)
Write one PL/SQL process branching on `:P2_EXPENSE_ID` — NULL means insert, set
means update. Use `RETURNING ... INTO` to populate the item after insert.
*Check:* create a row, edit it, and confirm the URL and messages make it obvious
which mode ran.

## 8. Three validations (20 min)
Server-side validation on submit, before processing:
1. Amount greater than zero.
2. Description required when the amount exceeds 500.
3. Category must be one of the five allowed values.

Each message names the field and the entered value.
*Check:* submit each bad case and confirm the message text. Then submit the same
payload with curl, bypassing the browser, and confirm the server still rejects it.

## 9. Scoping, including the leak (25 min)
Write `current_department()` returning `NVL(context, -1)`. Set the context at
login. Add the predicate to the detail region. **Temporarily omit it from the
category summary region** and log in as two managers in different departments.
*Check:* the summary shows duplicate category labels with identical totals, and
you can infer the other department's spend. Restore the predicate and confirm the
duplicates are gone. Then clear the session context and confirm the list returns
zero rows rather than all rows.

## 10. Delete with audit (15 min)
Add a delete process behind a confirmation dialog that inserts the row snapshot
into `expense_audit` before deleting.
*Check:* delete a row, confirm it is gone, confirm the audit row contains the
full prior state including the amount and category.

## Stretch
- Load 50,000 rows and time page 1 before and after adding
  `ix_exp_date ON expense(expense_date DESC)`. Report the ratio.
- Add a materialized view `mv_expense_summary` and rewrite both summaries
  against it. Confirm the totals match `SELECT SUM(amount) FROM expense;`.
- Prove that `NVL(:P_DEPT, e.department_id)` is sargable and
  `NVL(e.department_id, :P_DEPT)` is not, by comparing execution plans.
- Build a second summary region with no predicate deliberately, and write a
  200-word explanation of what it discloses and why no row was displayed.
