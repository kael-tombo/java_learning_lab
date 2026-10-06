# Lab 01: APEX Getting Started — Quiz

15 questions on the theory, code, and arithmetic of a first APEX application.
Answers follow; no peeking.

## Questions

1. In the workspace/schema/application hierarchy, where does an APEX application's
   data actually live?
2. How many SQL statements does a page with 8 regions issue on a render, and why
   does that number matter?
3. Your IR displays 25 rows per page. Does that mean the database reads 25 rows?
   Explain what the database actually does.
4. Why is `WHERE TRUNC(expense_date) = :p_date` slower than
   `WHERE expense_date >= :p_date AND expense_date < :p_date + 1`?
5. `NVL(:P_DEPT_ID, e.department_id)` versus `NVL(e.department_id, :P_DEPT_ID)` —
   which is sargable, and what is the rule?
6. Why does passing the record ID in session state not make an application secure?
7. Where must DML live in APEX, and what goes wrong if it is placed in a region
   query instead?
8. Why is a `CHECK` constraint still needed when page validation exists?
9. Roughly how many invalid rows per day does a client-side-only validation allow
   through at 1,000 submissions/day and a 0.5% non-browser share?
10. What does "fail closed" mean for `current_department()`, and what does the
    opposite behaviour return?
11. A manager's scoped detail region is correct but the category summary region is
    not. What exactly is disclosed, given that no other department's row appears?
12. Why is a date range described as the highest-value filter in most APEX
    applications?
13. What is the difference between Automatic Row Processing and a hand-written
    PL/SQL save process for a form supporting insert and update?
14. Your application is 12 pages. What is the rollback path after a bad change,
    and how long does it take?
15. Your delete process has a confirmation dialog but no audit. What protection is
    missing and what does its absence cost?

## Answers

1. In the assigned database schema. The application is metadata in the APEX
   instance; tables, constraints, and indexes are yours in the schema.
2. At least 8 — one per region, plus a `COUNT(*)` for each IR configured with a
   row count. It matters because a slow region is invisible until you count
   queries, and removing a region removes a query.
3. No. The database filters and sorts until it has 25 matching rows, which on a
   low-selectivity filter means reading most of the table. Pagination reduces
   returned bytes, never rows examined.
4. `TRUNC()` is applied to the *indexed column*, so the index cannot be used and
   the whole table is scanned and the function evaluated per row. The range form
   compares the column directly to a value, so the index is usable and only the
   matching range is read — roughly 24,000 rows instead of 1,000,000 in the lab.
5. The first. The rule is which side the function is on: a function on the bind
   is fine, a function on the column is not.
6. It prevents trivial URL tampering only. It does not prevent an unscoped
   `UPDATE` or an unscoped region query. Session state removes tampering; the
   scoped predicate enforces authorisation.
7. In a page process with a `When` condition, branching on whether the primary key
   is set. In a region query it runs on *render*, so merely loading the page can
   write data — and the render then does two jobs at once.
8. Because page validation is code that can be omitted and the client can be
   bypassed. The constraint is enforced by the database regardless of which
   client or code path wrote the row. At 1,000 submissions/day with 0.5% outside
   the browser, client-only validation lets about 5 invalid rows/day through; the
   constraint makes that zero.
9. About 5. At 1,000 submissions/day and a 0.5% share of requests arriving from
   outside the browser (curl, Postman, a script), a client-side-only check is
   bypassed roughly 5 times a day.
10. That a missing or unset context yields **no data**, never all data — the
    function returns `-1`, so the predicate matches nothing. The opposite
    behaviour (`NVL(context, column)` with NULL context) matches every row and
    discloses the entire table.
11. The existence and value of the other department's spending. Duplicate category
    labels with identical totals let a reader infer totals they were never
    authorised to see. The inference is the disclosure — which is why summary
    regions must carry the same predicate as detail regions.
12. Because it is simultaneously selective and index-friendly. On the lab dataset,
    department alone matches 83,000 rows while department plus seven days matches
    1,600 — a 52× reduction that a status filter cannot approach.
13. ARP fetches the row on load and issues INSERT or UPDATE based on whether the
    primary key is populated, with no branching to write. A hand-written process
    gives control over the SQL, error messages, and audit, at the cost of you
    getting both branches right.
14. Import the previous YAML export: roughly 400 KB, about 5 seconds, and it
    restores every page exactly. Reconstructing by hand takes hours. That is why
    the export belongs in source control from day one, not at delivery.
15. Accountability and recoverability. A delete destroys the only record, so
    without an audit snapshot the action is neither attributable nor reversible.
    Storage for 7,280 deletes over a 7-year retention is under 3 MB — negligible
    against the cost of an unrecoverable deletion.
