# PLSQL Fundamentals — Real World Project

## Situation
A deployable slice proving PL/SQL DECLARE, BEGIN, EXCEPTION, and END blocks with cursors survives contact with production load and operator error.

## Topology
Schema changes roll out behind review gates with a rehearsed rollback route.

## Build stages
- M1: Phase 1: model clerks and tasks with seed data plus contract tests.
- M2: Phase 2: harden the block path with indexes, guards, and load probes.
- M3: the phase-3 rehearsal covers backup, restore, and rollback.
- M4: Phase 4: hand over runbooks so on-call owns the procedures without paging the author.

## Operations list
- Every schema change carries its rollback script from day one.
- Monitor the call path for errors, saturation, and slow statements.
- Schedule backup restores onto a scratch host.
- Gate deploys on contract tests covering tasks behavior.

## What breaks
- unhandled NO_DATA_FOUND escaping a lookup block — catch the named handler the checklist above demands.
- cursors left open across repeated executions; close every cursor on every exit path.
- commits accidentally placed inside a row loop; move COMMIT after the loop and re-verify counts.
- Fact reminder: explicit cursors fetch rows one at a time inside a controlled loop. Guides every response above.

## Requirements
- F1: the service answers clerks reads with contract tests proving the shape.
- F2: the service guards tasks writes against invalid input.
- NF1: the call path exposes error counts and slow-statement signals on the dashboard.
- NF2: release sign-off waits until the restore drill passes on a scratch host.

## Verification
- Replay production-like tasks traffic against the staging store.
- Inject one fault (unhandled NO_DATA_FOUND escaping a lookup block) and confirm the runbook resolves it.
- Bring the backup back and reconcile row counts before calling it done.

## Definition of done
Sign-off happens when milestones are green, the restore drill has passed, and the runbook has been read.
