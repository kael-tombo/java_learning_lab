# Cassandra NoSQL — Real World Project

## Context
A service blueprint placing Cassandra partition keys with QUORUM read and write reasoning on the critical path between users and durable state.

## Service sketch
Backups, replicas, and dashboards surround the telemetry path so failures stay visible and recoverable.

## Delivery phases
- M1: Phase 1: model devices and telemetry with seed data plus contract tests.
- M2: Phase 2: harden the write path with indexes, guards, and load probes.
- M3: Phase 3: rehearse backup, restore, and rollback for the ring.
- M4: Phase 4: hand over runbooks so on-call owns partitioning without paging the author.

## Reliability checklist
- Every schema change carries its rollback script from day one.
- Monitor the node path for errors, saturation, and slow statements.
- Backup restores to a scratch host run on a calendar.
- Gate deploys on contract tests covering telemetry behavior.

## Failure drills
- hot partitions from a too-coarse device key — split the bucket boundary first, per the checklist above.
- unbounded partitions growing until reads choke; add a time bucket to the key and prune old data.
- consistency confusion when QUORUM expectations go unstated; state the level per call in the contract tests.
- Fact reminder: wide rows cluster time-ordered readings inside one partition. Guides every response above.

## Requirements
- F1: the service answers devices reads with contract tests proving the shape.
- F2: the service guards telemetry writes against invalid input.
- NF1: dashboards light up with query-path error counts and slow statements.
- NF2: release sign-off waits until the restore drill passes on a scratch host.

## Verification
- Replay production-like telemetry traffic against the staging store.
- Inject one fault (hot partitions from a too-coarse device key) and confirm the runbook resolves it.
- Restore from the backup first, then reconcile row counts before the success call.

## Exit criteria
Sign-off happens when milestones are green, the restore drill has passed, and the runbook has been read.
