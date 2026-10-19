# PL SQL Foundations — Real World Project

## Context
A service blueprint placing PL/SQL procedures, functions, and explicit transaction control on the critical path between users and durable state.

## Service sketch
Backups, replicas, and dashboards surround the call path so failures stay visible and recoverable.

## Delivery phases
- M1: Phase 1: model f_staff and f_shifts with seed data plus contract tests.
- M2: Phase 2: harden the call path with indexes, guards, and load probes.
- M3: phase three runs a backup, restore, and rollback rehearsal.
- M4: Phase 4: hand over runbooks so on-call owns the subprograms without paging the author.

## Reliability checklist
- Pair each schema change with the script that undoes it.
- Monitor the call path for errors, saturation, and slow statements.
- A scheduled job restores the backup to a scratch host.
- Gate deploys on contract tests covering f_shifts behavior.

## Failure drills
- functions with hidden commits breaking caller transactions — forbid commits inside functions, per the checklist above.
- OUT parameters masking failed computations with stale values; clear OUT arguments before the work begins.
- partial rosters persisting after a missing ROLLBACK; complete the handler so faults restore the batch.
- Fact reminder: IN, OUT, and IN OUT modes define parameter direction. Guides every response above.

## Requirements
- F1: the service answers f_staff reads with contract tests proving the shape.
- F2: the service guards f_shifts writes against invalid input.
- NF1: error counts and slow-statement signals from the query path are visible on the dashboard.
- NF2: no release sign-off while the scratch-host restore drill still fails.

## Verification
- Replay production-like f_shifts traffic against the staging store.
- Inject one fault (functions with hidden commits breaking caller transactions) and confirm the runbook resolves it.
- Restore from the backup first, then reconcile row counts before the success call.

## Exit criteria
Sign-off requires green milestones, a restore drill that passed, and a runbook someone on the team has read.
