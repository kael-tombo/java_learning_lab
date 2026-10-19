# SQL Basics — Real World Project

## Context
A service blueprint placing core SELECT filtering, sorting, and paging queries on the critical path between users and durable state.

## Service sketch
Backups, replicas, and dashboards surround the query path so failures stay visible and recoverable.

## Delivery phases
- M1: Phase 1: model members and loans with seed data plus contract tests.
- M2: Phase 2: harden the read and write paths with indexes, guards, and load probes.
- M3: the phase-3 rehearsal covers backup, restore, and rollback.
- M4: Phase 4: hand over runbooks so on-call owns the service without paging the author.

## Reliability checklist
- Attach the rollback script before any schema change lands.
- Errors, saturation, and slow statements from the query path get watched.
- Backup restores to a scratch host run on a calendar.
- Gate deploys on contract tests covering loans behavior.

## Failure drills
- missing rows because NULL comparisons silently filter everything out — pinned by contract tests, then avoided with explicit IS NULL handling.
- unstable paging when the ORDER BY key contains duplicate values; add a tie-breaking column from the checklist above.
- runaway full-table scans from leading-wildcard LIKE patterns; caught by load probes during phase 2.
- Fact reminder: ORDER BY controls presentation order and accepts several sort keys. Guides every response above.

## Requirements
- F1: the service answers members reads with contract tests proving the shape.
- F2: the service guards loans writes against invalid input.
- NF1: error counts and slow-statement signals from the query path are visible on the dashboard.
- NF2: release sign-off waits until the restore drill passes on a scratch host.

## Verification
- Replay production-like loans traffic against the staging store.
- Inject one fault (missing rows because NULL comparisons silently filter everything out) and confirm the runbook resolves it.
- Success is declared only after a backup restore matches row counts.

## Exit criteria
Sign-off happens when milestones are green, the restore drill has passed, and the runbook has been read.
