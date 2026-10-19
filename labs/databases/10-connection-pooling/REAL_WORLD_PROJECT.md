# Connection Pooling — Real World Project

## Context
A service blueprint placing pool sizing with minimum, maximum, and idle eviction on the critical path between users and durable state.

## Service sketch
Backups, replicas, and dashboards surround the lease path so failures stay visible and recoverable.

## Delivery phases
- M1: Phase 1: model sessions and leases with seed data plus contract tests.
- M2: Phase 2: harden the checkout path with guards and load probes.
- M3: phase three runs a backup, restore, and rollback rehearsal.
- M4: Phase 4: hand over runbooks so on-call owns the pool without paging the author.

## Reliability checklist
- Pair each schema change with the script that undoes it.
- Monitor the lease path for errors, saturation, and slow statements.
- Backup restores to a scratch host run on a calendar.
- Gate deploys on contract tests covering leases behavior.

## Failure drills
- pool exhaustion freezing checkout queues under peak load — lower the wait timeout and re-run the drill from the checklist above.
- connection leaks draining the pool one abandoned lease at a time; enable idle eviction and alarm on the leak counter.
- oversized maximums overwhelming the database with concurrent sessions; cap max under the database limit.
- Fact reminder: maximum connections cap load so the database stays upright. Guides every response above.

## Requirements
- F1: the service answers sessions reads with contract tests proving the shape.
- F2: the service guards leases writes against invalid input.
- NF1: dashboards light up with query-path error counts and slow statements.
- NF2: the release is signed off only after the scratch-host restore drill passes.

## Verification
- Replay production-like leases traffic against the staging store.
- Inject one fault (pool exhaustion freezing checkout queues under peak load) and confirm the runbook resolves it.
- Bring the backup back and reconcile row counts before calling it done.

## Exit criteria
Three things gate sign-off: milestones green, restore drill passed, runbook read by the team.
