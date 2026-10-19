# Multi-Model Databases — Real World Project

## Context
A service blueprint placing multi-model polyglot persistence choices on the critical path between users and durable state.

## Service sketch
Backups, replicas, and dashboards surround the persistence layer so failures stay visible and recoverable.

## Delivery phases
- M1: Phase 1: model catalog and reviews with seed data plus contract tests.
- M2: Phase 2: harden each model's read path with indexes, guards, and load probes.
- M3: Phase 3: rehearse backup, restore, and rollback for the stores.
- M4: Phase 4: hand over runbooks so on-call owns the boundary map without paging the author.

## Reliability checklist
- No schema change goes in without its rollback script.
- Monitor each model's path for errors, saturation, and slow statements.
- The backup gets restored to a scratch host on a fixed schedule.
- Gate deploys on contract tests covering reviews behavior.

## Failure drills
- one model stretched to serve every workload badly — re-route the outlier to its best fit, per the checklist above.
- cross-model reads with no defined consistency story; document the read contract and add a reconciliation probe.
- dual writes diverging with no reconciliation job; schedule the job and alarm on divergence counts.
- Fact reminder: document stores fit variable review payloads with evolving fields. Guides every response above.

## Requirements
- F1: the service answers catalog reads with contract tests proving the shape.
- F2: the service guards reviews writes against invalid input.
- NF1: the dashboard surfaces query-path error counts and slow-statement signals.
- NF2: a passing restore drill on a scratch host gates release sign-off.

## Verification
- Replay production-like reviews traffic against the staging store.
- Inject one fault (one model stretched to serve every workload badly) and confirm the runbook resolves it.
- Restore from the backup first, then reconcile row counts before the success call.

## Exit criteria
Sign-off requires green milestones, a restore drill that passed, and a runbook someone on the team has read.
