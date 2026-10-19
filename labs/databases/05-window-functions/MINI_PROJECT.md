# Window Functions — Mini Project

## Objective
Produce a working exercise on ROW_NUMBER, RANK, LEAD, and LAG window analytics in about ninety minutes, ending with scripts a peer can rerun.

## Core facts
- ROW_NUMBER assigns a unique sequence inside each partition. Every ranking step below leans on that guarantee.
- RANK shares numbers across ties and then skips the next positions — that is how the ladder behaves under checks.
- LEAD and LAG peek at neighboring rows without collapsing the result. The drills depend on it.

## Build
Create one scratch schema dedicated to this drill, seed a handful of rows, then work the task list in order.

## Task list
1. Load the ROW_NUMBER ranking of deals inside each seller partition, then explain the result to a reviewer aloud.
2. Run the RANK comparison showing tie gaps on equal amounts, and file the script where the next step finds it.
3. Shape the LAG query computing month-over-month deal deltas, while keeping every statement re-runnable.
4. Assemble the LEAD query flagging the next scheduled follow-up, and record what changes in the output.
5. Compose the running total with an explicit ROWS frame, then note the one surprise worth remembering.
6. Frame the first-versus-last deal comparison per seller partition, and capture the check query beside it.

## Reference snippet
```sql
SELECT id, amount,
  ROW_NUMBER() OVER (PARTITION BY seller_id ORDER BY amount DESC) AS rn,
  LAG(amount) OVER (PARTITION BY seller_id ORDER BY id) AS prev_amount
FROM deals
ORDER BY seller_id, rn
FETCH FIRST 20 ROWS ONLY;
```

## Checks
- Every script reruns cleanly on a fresh schema without manual edits.
- Row counts reconcile before and after each transformation step.
- One observed ranking behavior is written down with its cause.
- The snippet above executes (or the sketch reads correctly) against the seeded sellers data.

## Stretch
- Break one frame assumption deliberately, then document the error message verbatim.
- Remove one helper and show the exercise still passes without it.

## Done
The folder holds scripts, seed data, and a short note naming the trickiest step.

## Hand-off
- Tag the finished scripts folder so the next lab picks it up without re-reading every file.
- Hand the notes file to whoever reruns the exercises, so the surprises survive the handoff.
- Mark this checklist done only after a peer has rerun every script without edits.

