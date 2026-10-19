# Flyway and Liquibase — Real World Project

## Context
A service blueprint placing versioned Flyway and Liquibase schema migrations on the critical path between users and durable state.

## Service sketch
Backups, replicas, and dashboards surround the migration path so failures stay visible and recoverable.

## Delivery phases
- M1: Phase 1: model ledgers and entries with seed data plus contract tests.
- M2: Phase 2: harden the deploy path with indexes, guards, and load probes.
- M3: rehearse backup, restore, and rollback with the store data.
- M4: Phase 4: hand over runbooks so on-call owns the migration pipeline without paging the author.

## Reliability checklist
- No schema change goes in without its rollback script.
- Monitor the migration path for errors, saturation, and slow statements.
- Schedule backup restores onto a scratch host.
- Gate deploys on contract tests covering entries behavior.

## Failure drills
- checksum mismatches after editing an already-applied migration — never edit applied files; add a new migration per the checklist above.
- out-of-order migrations applied by two branches simultaneously; renumber and rerun in version order.
- missing rollback path discovered during a failed deploy; write the undo files before the next release.
- Fact reminder: repeatable migrations re-run when their checksum changes. Guides every response above.

## Requirements
- F1: the service answers ledgers reads with contract tests proving the shape.
- F2: the service guards entries writes against invalid input.
- NF1: the query path reports error counts and slow statements to the dashboard.
- NF2: a scratch-host restore drill is a precondition for release sign-off.

## Verification
- Replay production-like entries traffic against the staging store.
- Inject one fault (checksum mismatches after editing an already-applied migration) and confirm the runbook resolves it.
- Restore from the backup first, then reconcile row counts before the success call.

## Exit criteria
Nobody signs off until milestones are green, the restore drill passed, and the team read the runbook.
