# Database Migration Strategies — Real World Project

## Context
A service blueprint placing zero-downtime migration with expand-contract patterns on the critical path between users and durable state.

## Service sketch
Backups, replicas, and dashboards surround the migration window so failures stay visible and recoverable.

## Delivery phases
- M1: Phase 1: model profiles and profile_history with seed data plus contract tests.
- M2: Phase 2: harden the transition path with indexes, guards, and load probes.
- M3: the phase-3 rehearsal covers backup, restore, and rollback.
- M4: Phase 4: hand over runbooks so on-call owns the cutover without paging the author.

## Reliability checklist
- Pair each schema change with the script that undoes it.
- Monitor the transition path for errors, saturation, and slow statements.
- A scheduled job restores the backup to a scratch host.
- Gate deploys on contract tests covering profile_history behavior.

## Failure drills
- big-bang alters locking profiles during peak traffic — schedule the expand step off-peak, per the checklist above.
- old code crashing on a column dropped too early; contract only after every writer has cut over.
- unbounded backfills saturating the primary; run the backfill in bounded batches with sleeps between them.
- Fact reminder: dual writes keep old and new columns consistent mid-migration. Guides every response above.

## Requirements
- F1: the service answers profiles reads with contract tests proving the shape.
- F2: the service guards profile_history writes against invalid input.
- NF1: the dashboard surfaces query-path error counts and slow-statement signals.
- NF2: a passing restore drill on a scratch host gates release sign-off.

## Verification
- Replay production-like profile_history traffic against the staging store.
- Inject one fault (big-bang alters locking profiles during peak traffic) and confirm the runbook resolves it.
- Restore from the backup first, then reconcile row counts before the success call.

## Exit criteria
Green milestones plus a passed restore drill plus a read runbook together amount to sign-off.
