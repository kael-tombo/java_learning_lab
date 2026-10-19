# Query Optimization B — Mini Project

## Objective
Produce a working exercise on EXPLAIN plan reading and index reasoning in the shipments domain, in about ninety minutes, ending with scripts a peer can rerun.

## Core facts
- EXPLAIN shows the optimizer's chosen access path before execution. Every judgment below leans on that preview.
- Nested-loop joins suit selective lookups while hash joins suit bulk matches — that shapes what the plan implies.
- Composite index order must match the query's filter and sort pattern; that is the acceptance bar.

## Build
Create one scratch schema dedicated to this drill, seed a handful of rows, then work the task list in order.

## Task list
1. Run the EXPLAIN read of a shipment lookup identifying the access path, and record what changes in the output.
2. Shape the nested-loop versus hash-join comparison on stop matching, then note the one surprise worth remembering.
3. Assemble the composite index ordered by depot then departure time, and capture the check query beside it.
4. Compose the sort-spill diagnosis when ordering ignores the index, then explain the result to a reviewer aloud.
5. Frame the predicate-ordering rewrite aligning filters with the index, and file the script where the next step finds it.
6. Trace the regression check re-reading the plan after each index change, while keeping every statement re-runnable.

## Reference snippet
```sql
SELECT id, status FROM shipments
WHERE status = 'open'
ORDER BY id
FETCH FIRST 50 ROWS ONLY;
```

## Checks
- Every script reruns cleanly on a fresh schema without manual edits.
- Row counts reconcile before and after each transformation step.
- One observed plan behavior is written down with its cause.
- The snippet above executes (or the sketch reads correctly) against the seeded shipments data.

## Stretch
- Break one plan assumption deliberately, then document the error message verbatim.
- Remove one helper and show the exercise still passes without it.

## Done
The folder holds scripts, seed data, and a short note naming the trickiest step.

## Hand-off
- Tag the finished scripts folder so the next lab picks it up without re-reading every file.
- Hand the notes file to whoever reruns the exercises, so the surprises survive the handoff.
- Mark this checklist done only after a peer has rerun every script without edits.

