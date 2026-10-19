# SQL Solutions — Real World Project

## Problem
A production-flavored specification where graded SQL solution walkthroughs from basics to analytics carry real traffic, real failure, and real on-call pages.

## Architecture
```text
app -> service -> sol_users / sol_orders store -> replica + backup -> dashboard
```
Client requests reach a service layer, which runs the graded report queries over the sol_users and sol_orders stores.

## Milestones
- M1: Phase 1: model sol_users and sol_orders with seed data plus contract tests.
- M2: Phase 2: harden the report path with indexes, guards, and load probes.
- M3: backup, restore, and rollback all get a rehearsal this phase.
- M4: Phase 4: hand over runbooks so on-call owns the walkthrough suite without paging the author.

## Operations checklist
- Attach the rollback script before any schema change lands.
- Keep watch on the query path: errors, saturation, slow statements.
- Restore the backup onto a scratch host at a steady cadence.
- Gate deploys on contract tests covering sol_orders behavior.

## Failure modes
- jumping to analytics before filters and joins are solid — re-grade the query first, per the checklist above.
- copying solutions without reproducing the reasoning steps; require the pattern name before the query in reviews.
- mistaking a working query for an efficient one; check the plan beside the correct result.
- Fact reminder: graded solutions move from single-table filters toward multi-table analytics. Guides every response above.

## Requirements
- F1: the service answers sol_users reads with contract tests proving the shape.
- F2: the service guards sol_orders writes against invalid input.
- NF1: error counts and slow-statement signals from the query path are visible on the dashboard.
- NF2: release sign-off waits until the restore drill passes on a scratch host.

## Verification
- Replay production-like sol_orders traffic against the staging store.
- Inject one fault (jumping to analytics before filters and joins are solid) and confirm the runbook resolves it.
- Restore from the backup first, then reconcile row counts before the success call.

## Sign-off
Sign-off requires green milestones, a restore drill that passed, and a runbook someone on the team has read.
