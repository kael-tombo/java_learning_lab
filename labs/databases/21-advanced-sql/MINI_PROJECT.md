# Advanced SQL — Mini Project

## Objective
Produce a working exercise on advanced grouping, pivoting, and set-operation SQL in about ninety minutes, ending with scripts a peer can rerun.

## Core facts
- ROLLUP adds subtotal and grand-total rows to grouped output. Every report step below leans on that.
- Pivoting turns row values into columns for cross-tab reports — that is how the shapes behave under checks.
- UNION removes duplicates while UNION ALL keeps every row; that is the acceptance bar for the drills.

## Build
Create one scratch schema dedicated to this drill, seed a handful of rows, then work the task list in order.

## Task list
1. Frame the ROLLUP report subtotaling conversions by channel and month, and record what changes in the output.
2. Trace the pivot sketch turning channels into columns, then note the one surprise worth remembering.
3. Draft the UNION versus UNION ALL comparison on duplicated conversions, and capture the check query beside it.
4. Load the INTERSECT hunt for channels converting in both halves, then explain the result to a reviewer aloud.
5. Run the EXCEPT list of channels lost between quarters, and file the script where the next step finds it.
6. Shape the grouping-sets sketch mixing two granularities in one pass, while keeping every statement re-runnable.

## Reference snippet
```sql
SELECT channel, COUNT(*) AS n FROM conversions
GROUP BY ROLLUP (channel)
ORDER BY channel
FETCH FIRST 20 ROWS ONLY;
```

## Checks
- Every script reruns cleanly on a fresh schema without manual edits.
- Row counts reconcile before and after each transformation step.
- One observed grouping behavior is written down with its cause.
- The snippet above executes (or the sketch reads correctly) against the seeded channels data.

## Stretch
- Break one pivot assumption deliberately, then document the error message verbatim.
- Remove one helper and show the exercise still passes without it.

## Done
The folder holds scripts, seed data, and a short note naming the trickiest step.

## Hand-off
- Tag the finished scripts folder so the next lab picks it up without re-reading every file.
- Hand the notes file to whoever reruns the exercises, so the surprises survive the handoff.
- Mark this checklist done only after a peer has rerun every script without edits.

