# Database Replication — Real World Project

## Context
A service blueprint placing primary and replica lag measurement with failover drills on the critical path between users and durable state.

## Service sketch
Backups, replicas, and dashboards surround the replication path so failures stay visible and recoverable.

## Delivery phases
- M1: Phase 1: model ledger and ledger_replica with seed data plus contract tests.
- M2: Phase 2: harden the stream path with indexes, guards, and load probes.
- M3: Phase 3: rehearse backup, restore, and rollback for the cluster.
- M4: Phase 4: hand over runbooks so on-call owns promotion without paging the author.

## Reliability checklist
- No schema change goes in without its rollback script.
- Monitor the replication stream for errors, saturation, and slow statements.
- Backup restores to a scratch host run on a calendar.
- Gate deploys on contract tests covering ledger_replica behavior.

## Failure drills
- stale reads served from a lagging replica — quarantine the replica until it catches up, per the checklist above.
- split brain after two nodes both accept writes; enforce the fencing rule before retrying promotion.
- replay backlogs growing faster than catch-up capacity; raise replay parallelism or throttle the primary.
- Fact reminder: lag measurement compares applied positions between primary and replica. Guides every response above.

## Requirements
- F1: the service answers ledger reads with contract tests proving the shape.
- F2: the service guards ledger_replica writes against invalid input.
- NF1: error counts and slow-statement signals from the query path are visible on the dashboard.
- NF2: release sign-off waits until the restore drill passes on a scratch host.

## Verification
- Replay production-like ledger_replica traffic against the staging store.
- Inject one fault (stale reads served from a lagging replica) and confirm the runbook resolves it.
- Restore from the backup first, then reconcile row counts before the success call.

## Exit criteria
Nobody signs off until milestones are green, the restore drill passed, and the team read the runbook.
