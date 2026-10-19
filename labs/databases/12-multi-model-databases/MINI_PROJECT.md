# Multi-Model Databases — Mini Project

## Scenario
A teammate needs a runnable example of multi-model polyglot persistence choices by end of day, small enough to review in one sitting.

## What you ship
A scripted walkthrough assigning each workload to its best-fit model, with seed data, ordered steps, and a verification section at the end.

## Working sequence
1. First, compose the catalog facts modeled relationally with keys, and file the script where the next step finds it.
2. Next, frame the review payloads modeled as flexible documents, while keeping every statement re-runnable.
3. Then, trace the session state assigned to a key-value sketch, and record what changes in the output.
4. After that, draft the search workload routed to a text index sketch, then note the one surprise worth remembering.
5. Further, load the boundary map marking which model owns each write, and capture the check query beside it.
6. Finally, run the consistency note for reads spanning two models, then explain the result to a reviewer aloud.

## Reference snippet
```text
-- conceptual sketch for this lab
-- keep each statement re-runnable and small
```

## Verification
- Rerun the full sequence twice; the second pass must stay green.
- Show how relational stores fit ledger-like catalog facts with strict integrity, and point to the line where that shows up in the results.
- Demonstrate that document stores fit variable review payloads with evolving fields, backed by one concrete observation.
- Keep the reviews row counts consistent across every rerun.

## Concept tie-in
This drill exercises the model-choice rules end to end: key-value and search stores serve session and full-text workloads respectively.

## Setup checklist
- This work runs in a scratch schema isolated from any shared database.
- Seed rows for catalog and reviews loaded and counted.
- Anything surprising enough to quote goes into the open notes file.
- The rollback or re-seed path is confirmed before any edit.

## Next step
Carry these scripts into the real-world project as the starting scaffold.

## Hand-off
- Tag the scripts folder when done, so the next lab starts without re-reading all files.
- The notes file changes hands with the exercises, and the surprises survive with it.
- Peer reruns all scripts, no edits, then the checklist can be marked done.

