# SQL Solutions — Mini Project

## Objective
Produce a working exercise following graded SQL solution walkthroughs from basics to analytics in about ninety minutes, ending with scripts a peer can rerun.

## Core facts
- Graded solutions move from single-table filters toward multi-table analytics. The ladder below leans on that ordering.
- Each walkthrough names the pattern before showing the query — that is what keeps the steps checkable.
- Common mistakes accompany every solution with a fix; that is the acceptance bar.

## Build
Create one scratch schema dedicated to this drill, seed a handful of rows, then work the task list in order.

## Task list
1. Load the Level 1 filter solution on user status, then explain the result to a reviewer aloud.
2. Run the Level 2 join solution linking users to orders, and file the script where the next step finds it.
3. Shape the Level 3 aggregation solution totaling orders per user, while keeping every statement re-runnable.
4. Assemble the Level 4 subquery solution finding users without orders, and record what changes in the output.
5. Compose the Level 5 window solution ranking orders per user, then note the one surprise worth remembering.
6. Frame the mistake gallery pairing each error with its correction, and capture the check query beside it.

## Reference snippet
```sql
SELECT id FROM sol_users
WHERE id IS NOT NULL
ORDER BY id
FETCH FIRST 10 ROWS ONLY;
```

## Checks
- Every script reruns cleanly on a fresh schema without manual edits.
- Row counts reconcile before and after each transformation step.
- One observed ladder behavior is written down with its cause.
- The snippet above executes (or the sketch reads correctly) against the seeded sol_users data.

## Stretch
- Break one grading assumption deliberately, then document the error message verbatim.
- Remove one helper and show the exercise still passes without it.

## Done
The folder holds scripts, seed data, and a short note naming the trickiest step.

## Hand-off
- Tag the finished scripts folder so the next lab picks it up without re-reading every file.
- Hand the notes file to whoever reruns the exercises, so the surprises survive the handoff.
- Mark this checklist done only after a peer has rerun every script without edits.

