# Query Optimization B — Real World Project

## Problem
A production-flavored specification where EXPLAIN plan reading and index reasoning in the shipments domain carry real traffic, real failure, and real on-call pages.

## Architecture
```text
app -> service -> shipments / stops store -> replica + backup -> dashboard
```
Client requests reach a service layer, which routes queries the optimizer plans for the shipments and stops stores.

## Milestones
- M1: Phase 1: model shipments and stops with seed data plus contract tests.
- M2: Phase 2: harden the lookup path with indexes, guards, and load probes.
- M3: rehearse backup, restore, and rollback with the store data.
- M4: Phase 4: hand over runbooks so on-call owns the plan reviews without paging the author.

## Operations checklist
- Attach the rollback script before any schema change lands.
- The query path earns monitoring for errors, saturation, and slow statements.
- The backup gets restored to a scratch host on a fixed schedule.
- Gate deploys on contract tests covering stops behavior.

## Failure modes
- misread plans blamed on the wrong operator — re-read the operator row before concluding, per the checklist above.
- wrong composite order leaving the second column unusable; reorder the index and re-explain.
- sort spills when ORDER BY columns miss the supporting index; align the index with the sort or accept the spill knowingly.
- Fact reminder: EXPLAIN shows the optimizer's chosen access path before execution. Guides every response above.

## Requirements
- F1: the service answers shipments reads with contract tests proving the shape.
- F2: the service guards stops writes against invalid input.
- NF1: the query path reports error counts and slow statements to the dashboard.
- NF2: a scratch-host restore drill is a precondition for release sign-off.

## Verification
- Replay production-like stops traffic against the staging store.
- Inject one fault (misread plans blamed on the wrong operator) and confirm the runbook resolves it.
- Row counts must reconcile against the restored backup before any success claim.

## Sign-off
Sign-off happens when milestones are green, the restore drill has passed, and the runbook has been read.
