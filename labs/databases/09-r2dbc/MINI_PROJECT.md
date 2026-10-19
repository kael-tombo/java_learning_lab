# R2DBC — Mini Project

## Objective
Produce a working exercise in R2DBC reactive non-blocking database access in about ninety minutes, ending with scripts a peer can rerun.

## Core facts
- R2DBC exposes non-blocking publishers instead of blocking result sets. Every flow below leans on that.
- Backpressure lets slow consumers throttle fast database producers — that is how the streams behave under checks.
- Connection factories replace DataSources in the reactive stack; that is the acceptance bar.

## Build
Create one scratch schema dedicated to this drill, seed a handful of rows, then work the task list in order.

## Task list
1. Trace the reactive reading query streaming sensor rows, then explain the result to a reviewer aloud.
2. Draft the backpressure sketch bounding an unbounded reading feed, and file the script where the next step finds it.
3. Load the connection-factory configuration separating pool from pipeline, while keeping every statement re-runnable.
4. Run the error-mapping review translating driver errors, and record what changes in the output.
5. Shape the blocking-call hunt removing one hidden block from the path, then note the one surprise worth remembering.
6. Assemble the cancellation drill abandoning a slow reading stream, and capture the check query beside it.

## Reference snippet
```text
factory: connection-factory with bounded pool
query: stream readings with demand limits
rule: zero blocking calls on event threads
```

## Checks
- Every script reruns cleanly on a fresh schema without manual edits.
- Row counts reconcile before and after each transformation step.
- One observed stream behavior is written down with its cause.
- The snippet above executes (or the sketch reads correctly) against the seeded sensors data.

## Stretch
- Break one reactive assumption deliberately, then document the error message verbatim.
- Remove one helper and show the exercise still passes without it.

## Done
The folder holds scripts, seed data, and a short note naming the trickiest step.

## Hand-off
- Tag the finished scripts folder so the next lab picks it up without re-reading every file.
- Hand the notes file to whoever reruns the exercises, so the surprises survive the handoff.
- Mark this checklist done only after a peer has rerun every script without edits.

