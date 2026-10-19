# Database Sharding — Mini Project

## Objective
Produce a working exercise on shard key selection and cross-shard query costs in about ninety minutes, ending with scripts a peer can rerun.

## Core facts
- The shard key decides which node owns each row. Every placement decision below leans on that.
- Good keys spread writes evenly and keep hot tenants apart — that is how the distribution behaves under checks.
- Cross-shard queries fan out and merge, costing far more; that is the acceptance bar for the drills.

## Build
Create one scratch schema dedicated to this drill, seed a handful of rows, then work the task list in order.

## Task list
1. Compose the shard-key comparison scoring shopper id versus region, then explain the result to a reviewer aloud.
2. Frame the hotspot analysis on a celebrity-shopper key choice, and file the script where the next step finds it.
3. Trace the single-shard basket write path diagram, while keeping every statement re-runnable.
4. Draft the scatter-gather read sketch for a cross-shard report, and record what changes in the output.
5. Load the rebalancing note for splitting one overloaded shard, then note the one surprise worth remembering.
6. Run the routing-table sketch mapping key ranges to nodes, and capture the check query beside it.

## Reference snippet
```text
key-range A-C -> node 1
key-range D-F -> node 2
rule: single-shard writes, fanned reads
```

## Checks
- Every script reruns cleanly on a fresh schema without manual edits.
- Row counts reconcile before and after each transformation step.
- One observed distribution behavior is written down with its cause.
- The snippet above executes (or the sketch reads correctly) against the seeded shoppers data.

## Stretch
- Break one keying assumption deliberately, then document the error message verbatim.
- Remove one helper and show the exercise still passes without it.

## Done
The folder holds scripts, seed data, and a short note naming the trickiest step.

## Hand-off
- Tag the finished scripts folder so the next lab picks it up without re-reading every file.
- Hand the notes file to whoever reruns the exercises, so the surprises survive the handoff.
- Mark this checklist done only after a peer has rerun every script without edits.

