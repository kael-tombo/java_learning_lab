# Query Optimization A — Real World Project

## Situation
A deployable slice proving B-tree index choice and sargable predicate design in the orders domain survives contact with production load and operator error.

## Topology
Schema changes roll out behind review gates with a rehearsed rollback route.

## Build stages
- M1: Phase 1: model orders and order_lines with seed data plus contract tests.
- M2: Phase 2: harden the lookup path with indexes, guards, and load probes.
- M3: backup, restore, and rollback all get a rehearsal this phase.
- M4: Phase 4: hand over runbooks so on-call owns the plan reviews without paging the author.

## Operations list
- Pair each schema change with the script that undoes it.
- Watch the query path for errors, saturation, and statements running slow.
- Restore the backup onto a scratch host at a steady cadence.
- Gate deploys on contract tests covering order_lines behavior.

## What breaks
- function-wrapped predicates forcing full scans over indexed dates — unwrap the column, as the checklist above demands.
- over-indexing slowing every order insert to a crawl; keep only indexes the traces justify.
- stale statistics steering the optimizer toward a bad plan; refresh them before each release and re-check the plan.
- Fact reminder: selectivity decides whether the optimizer prefers a seek or a scan. Guides every response above.

## Requirements
- F1: the service answers orders reads with contract tests proving the shape.
- F2: the service guards order_lines writes against invalid input.
- NF1: error counts and slow-statement signals from the query path are visible on the dashboard.
- NF2: a scratch-host restore drill is a precondition for release sign-off.

## Verification
- Replay production-like order_lines traffic against the staging store.
- Inject one fault (function-wrapped predicates forcing full scans over indexed dates) and confirm the runbook resolves it.
- Row counts must reconcile against the restored backup before any success claim.

## Definition of done
Sign-off happens when milestones are green, the restore drill has passed, and the runbook has been read.
