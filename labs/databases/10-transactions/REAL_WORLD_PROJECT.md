# Transactions — Real World Project

## Situation
A deployable slice proving ACID transactions across READ COMMITTED and REPEATABLE READ isolation survives contact with production load and operator error.

## Topology
Schema changes roll out behind review gates with a rehearsed rollback route.

## Build stages
- M1: Phase 1: model accounts and transfers with seed data plus contract tests.
- M2: Phase 2: harden the write path with indexes, guards, and load probes.
- M3: rehearse the store's backup, restore, and rollback paths.
- M4: Phase 4: hand over runbooks so on-call owns the transfer flow without paging the author.

## Operations list
- Attach the rollback script before any schema change lands.
- Errors, saturation, and slow statements from the query path get watched.
- Restore the backup onto a scratch host at a steady cadence.
- Gate deploys on contract tests covering transfers behavior.

## What breaks
- lost updates when two debits read the same balance concurrently — add the guarded decrement the checklist above demands.
- deadlocks from transfers locking accounts in opposite order; order every lock acquisition by account id.
- long transactions holding locks while users think; keep user think-time outside the transaction boundary.
- Fact reminder: REPEATABLE READ guards repeated reads against phantom changes. Guides every response above.

## Requirements
- F1: the service answers accounts reads with contract tests proving the shape.
- F2: the service guards transfers writes against invalid input.
- NF1: dashboards light up with query-path error counts and slow statements.
- NF2: release sign-off waits until the restore drill passes on a scratch host.

## Verification
- Replay production-like transfers traffic against the staging store.
- Inject one fault (lost updates when two debits read the same balance concurrently) and confirm the runbook resolves it.
- Bring the backup back and reconcile row counts before calling it done.

## Definition of done
Nobody signs off until milestones are green, the restore drill passed, and the team read the runbook.
