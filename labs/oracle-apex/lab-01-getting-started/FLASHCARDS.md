# Lab 01: APEX Getting Started — Flashcards

60 quick-reference cards. Format: `Q:` question | `A:` answer.

## The Model
1. Q: Where does APEX application data live? | A: In the assigned database schema — the application is only metadata.
2. Q: What is the containment order? | A: Workspace → Schema → Application → Page → Region → Item.
3. Q: What is a region? | A: A unit of display backed by its own query, rendered on every page load.
4. Q: What is a page item? | A: A form field or button on a page; in SQL it is referenced as `:P<n>_<NAME>`.
5. Q: What does the shared prefix `P<n>_` mean? | A: The item belongs to page n.
6. Q: What prefix marks a global/application item? | A: `G_` — e.g. `G_DEPT_ID` — available on every page.
7. Q: Why is debugging APEX straightforward? | A: There is no hidden framework layer; your SQL is the SQL.
8. Q: Why can APEX not protect you from a bad query? | A: It is transparent by design — row security is yours to write.

## Regions and Queries
9. Q: How many queries does a page with N regions issue? | A: N, plus a `COUNT(*)` for each IR configured with a row count.
10. Q: Does pagination reduce rows examined? | A: No. It reduces returned bytes only.
11. Q: What does the database actually do for a page of 25 rows? | A: Filters and sorts until it has 25 matches.
12. Q: Roughly how much of a fast page load is framework overhead? | A: About 400 ms — which dominates until roughly 20 regions.
13. Q: When is removing a region a real optimisation? | A: When its query was expensive. Removing a 15 ms query from a 585 ms page saves 2.6%.
14. Q: What is the fix for a 900 ms region on a 1,400 ms page? | A: Optimise that region — it is 64% of the load.

## Sargability and Selectivity
15. Q: What is a sargable predicate? | A: One the optimizer can turn into an index range scan — the column is compared to a value.
16. Q: Which is sargable: `NVL(:P, col)` or `NVL(col, :P)`? | A: `NVL(:P, col)` — a function on the bind is fine, on the column is not.
17. Q: Why does `TRUNC(expense_date) = :d` disable the index? | A: The function is applied to the indexed column.
18. Q: What is the sargable rewrite for a single day? | A: `expense_date >= :d AND expense_date < :d + 1`.
19. Q: What is the sargable rewrite for a month? | A: `expense_date >= :p_month AND expense_date < ADD_MONTHS(:p_month,1)`.
20. Q: Selectivity ratio formula? | A: `total rows / rows matched`.
21. Q: Why are date filters the highest-value filter? | A: Selective *and* index-friendly — a 52× reduction that a status filter cannot match.
22. Q: A filter applied by JavaScript rather than in SQL — is it a filter? | A: No. It is a display preference.
23. Q: When is `TRUNC()` on a date column acceptable? | A: For group-by month labels in a summary — not in a row-filtering predicate.

## Binds and Plans
24. Q: Bind syntax in a region query? | A: `:P1_DATE_FROM`, `:G_DEPT_ID`.
25. Q: Why never concatenate into SQL? | A: One hard parse per value, plus injection risk.
26. Q: Hard-parse cost vs soft-parse cost? | A: About 1.8 ms versus 0.02 ms — a 90× difference.
27. Q: 40 executions of a literal query — how many hard parses? | A: 40. With binds: 1 hard parse and 40 soft parses.
28. Q: What does a repeating literal variant do to the shared pool? | A: Grows it with cursors that cannot be shared and are rarely evicted.

## State
29. Q: Where does session state live? | A: Server side, in the APEX session table, keyed by an opaque session cookie.
30. Q: Is session state user-editable? | A: No — there is no browser control for it.
31. Q: Is session state an authorisation control? | A: No. It stops tampering, not unscoped DML.
32. Q: When must the URL be used instead? | A: When the link must be shareable or bookmarkable.
33. Q: Where is session context set? | A: Once, at authentication — an After-Login computation or a page 0 process.
34. Q: How do you read session state in SQL/PLSQL? | A: `APEX_UTIL.SESSION_STATE('MY_CTX_DEPARTMENT_ID')`.

## DML and Processes
35. Q: Where does DML belong? | A: A page process with a `When` condition — never a region query.
36. Q: Why not in a region query? | A: Region SQL runs on render, so loading the page would write.
37. Q: How does one form handle insert and update? | A: Branch on `:P2_EXPENSE_ID` — NULL is insert, set is update.
38. Q: What is Automatic Row Processing? | A: Declarative DML that fetches the row on load and picks INSERT/UPDATE by primary key.
39. Q: How do you get the new key after an insert? | A: `INSERT ... RETURNING expense_id INTO :P2_EXPENSE_ID;`
40. Q: When does a process run — `When = Page Load`? | A: On every render. Use `When = Submit` for write operations.
41. Q: Processing position `When Processing = Before Header/Body` — which runs first? | A: Before Header.
42. Q: What is the processing order for submit? | A: Validations (Before Processing) → Processes → After Processing.

## Validation
43. Q: How many validation layers exist? | A: Three: client-side, page validation, database constraint.
44. Q: Which layer is authoritative? | A: The database constraint.
45. Q: Roughly how many invalid rows/day slip past a client-only check? | A: About 5 at 1,000 submissions/day and 0.5% non-browser traffic.
46. Q: What is a good validation message? | A: It names the field *and* the value entered: "Amount must be > 0. Entered: -50".
47. Q: What is the backstop for a positive amount? | A: `CHECK (amount > 0)` on the column.
48. Q: Does a `NOT NULL` constraint count as validation? | A: It is the last line of validation, enforced regardless of application code.

## Row Security
49. Q: What does fail-closed mean? | A: Missing context returns no rows, never all rows.
50. Q: The fail-closed sentinel value? | A: `-1` via `NVL(context, -1)`, wrapped in an exception handler.
51. Q: Which regions must carry the scoping predicate? | A: All of them — including summary, chart, and LOV regions.
52. Q: What leaks when a summary region is unscoped? | A: Duplicate group labels with identical totals reveal another group's spend.
53. Q: Is "no row was displayed" proof of no disclosure? | A: No. Inference from duplicate aggregates is disclosure.
54. Q: How does a manager pass `NVL(:G_DEPT_ID, e.department_id)`? | A: Admin NULL context sees all rows; manager context sees only their own.
55. Q: What enforces scoping regardless of the query written? | A: A VPD policy on the table.
56. Q: Predicate vs VPD — which depends on whom? | A: Predicate on reviewer discipline; VPD on nothing.

## Deletion and Export
57. Q: Two protections a delete needs? | A: A confirmation dialog (against accidents) and an audit snapshot (against irreversibility).
58. Q: What should the audit row contain? | A: The full prior state of the deleted row.
59. Q: What is the rollback path for an application change? | A: Re-import the previous YAML export — about 5 seconds for 400 KB.
60. Q: Why export to source control from day one? | A: Because a rollback plan that is not a file is not a plan.
