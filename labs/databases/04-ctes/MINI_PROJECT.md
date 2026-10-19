# CTEs — Mini Project

## Objective
Produce a working exercise on non-recursive and recursive common table expressions in about ninety minutes, ending with scripts a peer can rerun.

## Core facts
- A CTE names an intermediate result so the main query stays readable. Every step below leans on that clarity.
- Chained CTEs build pipelines where each step reads the previous one — that shapes how the pipeline behaves under checks.
- A recursive CTE pairs an anchor query with a UNION ALL expansion step; that is the acceptance bar for the drills.

## Build
Create one scratch schema dedicated to this drill, seed a handful of rows, then work the task list in order.

## Task list
1. Frame the readable CTE replacing a nested derived table, and record what changes in the output.
2. Trace the two-step chained CTE cleaning then ranking employees, then note the one surprise worth remembering.
3. Draft the recursive mentorship chain from the anchor mentor outward, and capture the check query beside it.
4. Load the depth column added to the recursive expansion leg, then explain the result to a reviewer aloud.
5. Run the termination review proving the recursion cannot cycle forever, and file the script where the next step finds it.
6. Shape the CTE-versus-subquery readability comparison on one report, while keeping every statement re-runnable.

## Reference snippet
```sql
WITH base AS (
  SELECT id, mentor_id FROM mentorships
  WHERE mentor_id IS NULL
)
SELECT id FROM base
ORDER BY id
FETCH FIRST 20 ROWS ONLY;
```

## Checks
- Every script reruns cleanly on a fresh schema without manual edits.
- Row counts reconcile before and after each transformation step.
- One observed pipeline behavior is written down with its cause.
- The snippet above executes (or the sketch reads correctly) against the seeded employees data.

## Stretch
- Break one recursion assumption deliberately, then document the error message verbatim.
- Remove one helper and show the exercise still passes without it.

## Done
The folder holds scripts, seed data, and a short note naming the trickiest step.

## Hand-off
- Tag the finished scripts folder so the next lab picks it up without re-reading every file.
- Hand the notes file to whoever reruns the exercises, so the surprises survive the handoff.
- Mark this checklist done only after a peer has rerun every script without edits.

