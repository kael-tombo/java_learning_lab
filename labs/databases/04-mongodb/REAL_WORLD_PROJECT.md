# MongoDB — Real World Project

## Context
A service blueprint placing MongoDB document modeling and find query patterns on the critical path between users and durable state.

## Service sketch
Backups, replicas, and dashboards surround the query path so failures stay visible and recoverable.

## Delivery phases
- M1: Phase 1: model customers and tickets with seed data plus contract tests.
- M2: Phase 2: harden the read path with indexes, guards, and load probes.
- M3: the phase-3 rehearsal covers backup, restore, and rollback.
- M4: Phase 4: hand over runbooks so on-call owns the document shapes without paging the author.

## Reliability checklist
- Every schema change carries its rollback script from day one.
- Errors, saturation, and slow statements from the query path get watched.
- The backup gets restored to a scratch host on a fixed schedule.
- Gate deploys on contract tests covering tickets behavior.

## Failure drills
- unbounded arrays bloating documents past comfortable sizes — cap the list or split the collection, per the checklist above.
- duplicated customer data drifting after an embedded copy changes; reference the parent instead and reconcile.
- collection scans from unindexed filter fields; add the index to the contract tests before deploy.
- Fact reminder: embedding suits contained children while referencing suits shared entities. Guides every response above.

## Requirements
- F1: the service answers customers reads with contract tests proving the shape.
- F2: the service guards tickets writes against invalid input.
- NF1: the dashboard surfaces query-path error counts and slow-statement signals.
- NF2: the release is signed off only after the scratch-host restore drill passes.

## Verification
- Replay production-like tickets traffic against the staging store.
- Inject one fault (unbounded arrays bloating documents past comfortable sizes) and confirm the runbook resolves it.
- Row counts must reconcile against the restored backup before any success claim.

## Exit criteria
Nobody signs off until milestones are green, the restore drill passed, and the team read the runbook.
