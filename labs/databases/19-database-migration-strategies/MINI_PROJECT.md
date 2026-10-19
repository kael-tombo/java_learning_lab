# Database Migration Strategies — Mini Project

## Scenario
A teammate needs a runnable example of zero-downtime migration with expand-contract patterns by end of day, small enough to review in one sitting.

## What you ship
A scripted walkthrough covering the expand, backfill, and contract steps, with seed data, ordered steps, and a verification section at the end.

## Working sequence
1. First, frame the expand step adding the new profile column safely, then note the one surprise worth remembering.
2. Next, trace the dual-write sketch covering the transition window, and capture the check query beside it.
3. Then, draft the batched backfill plan for existing profile rows, then explain the result to a reviewer aloud.
4. After that, load the contract step dropping the old column after cutover, and file the script where the next step finds it.
5. Further, run the rollback note valid at each expand-contract stage, while keeping every statement re-runnable.
6. Finally, shape the verification query comparing old and new columns, and record what changes in the output.

## Reference snippet
```text
expand  -> ALTER TABLE profiles ADD COLUMN ...
backfill -> bounded batches over profile_history
contract -> ALTER TABLE profiles DROP COLUMN ...
```

## Verification
- Rerun the full sequence twice; the second pass must stay green.
- Show how expand-contract adds the new shape before removing the old one, and point to the line where that shows up in the results.
- Demonstrate that dual writes keep old and new columns consistent mid-migration, backed by one concrete observation.
- Keep the profile_history row counts consistent across every rerun.

## Concept tie-in
This drill exercises the staged migration end to end: backfills populate new columns in bounded batches.

## Setup checklist
- This work runs in a scratch schema isolated from any shared database.
- Seed rows for profiles and profile_history loaded and counted.
- Anything surprising enough to quote goes into the open notes file.
- Confirm the rollback or re-seed path before the first edit.

## Next step
Carry these scripts into the real-world project as the starting scaffold.

## Hand-off
- The finished scripts folder gets tagged so the next lab skips re-reading every file.
- Whoever reruns the exercises receives the notes file, keeping the surprises alive through the handoff.
- Checklist completion waits for a peer rerun of every script, unedited.

