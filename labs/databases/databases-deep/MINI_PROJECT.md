# Databases Deep — Mini Project

## Scenario
A teammate needs a runnable example of end-to-end database internals from storage to optimizer by end of day, small enough to review in one sitting.

## What you ship
A scripted walkthrough following one query down through every layer, with seed data, ordered steps, and a verification section at the end.

## Working sequence
1. First, assemble the storage sketch tracing one document to its page, then note the one surprise worth remembering.
2. Next, compose the index trade-off worksheet pricing one extra index, and capture the check query beside it.
3. Then, frame the statistics note explaining a surprising plan choice, then explain the result to a reviewer aloud.
4. After that, trace the concurrency sketch showing two writers on one row, and file the script where the next step finds it.
5. Further, draft the durability walkthrough from commit to recoverable log, while keeping every statement re-runnable.
6. Finally, load the end-to-end trace of one query through every layer, and record what changes in the output.

## Reference snippet
```sql
SELECT id FROM deep_docs
WHERE id IS NOT NULL
ORDER BY id
FETCH FIRST 10 ROWS ONLY;
```

## Verification
- Rerun the full sequence twice; the second pass must stay green.
- Show how storage lays rows or documents onto persistent pages, and point to the line where that shows up in the results.
- Demonstrate that indexes trade write cost for dramatically faster lookups, backed by one concrete observation.
- Keep the deep_postings row counts consistent across every rerun.

## Concept tie-in
This drill exercises the layer stack end to end: the optimizer picks access paths using statistics about the data.

## Setup checklist
- This work runs in a scratch schema isolated from any shared database.
- Seed rows for deep_docs and deep_postings loaded and counted.
- An open notes file catches surprises worth quoting later.
- Confirm the rollback or re-seed path before the first edit.

## Next step
Carry these scripts into the real-world project as the starting scaffold.

## Hand-off
- Tag the finished scripts folder; the next lab can pick it up without re-reading everything.
- The notes file goes to whoever reruns the exercises, and the surprises survive the handoff that way.
- The checklist gets its done mark after a peer reruns every script, edits free.

