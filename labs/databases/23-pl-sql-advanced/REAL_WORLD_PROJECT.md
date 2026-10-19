# PL SQL Advanced — Real World Project

## Situation
A deployable slice proving PL/SQL packages, bulk binds, and autonomous-transaction logging survives contact with production load and operator error.

## Topology
Schema changes roll out behind review gates with a rehearsed rollback route.

## Build stages
- M1: Phase 1: model a_orders and a_audit with seed data plus contract tests.
- M2: Phase 2: harden the call path with indexes, guards, and load probes.
- M3: the phase-3 rehearsal covers backup, restore, and rollback.
- M4: Phase 4: hand over runbooks so on-call owns the package suite without paging the author.

## Operations list
- No schema change goes in without its rollback script.
- Monitor the call path for errors, saturation, and slow statements.
- Restore the backup onto a scratch host at a steady cadence.
- Gate deploys on contract tests covering a_audit behavior.

## What breaks
- row-by-row loops stalling on large order volumes — switch the path to FORALL, per the checklist above.
- audit rows vanishing when tied to a rolled-back transaction; move the logger into an autonomous transaction.
- package state leaking between sessions unexpectedly; reset variables at entry or avoid them entirely.
- Fact reminder: autonomous transactions log audit rows independently of the caller. Guides every response above.

## Requirements
- F1: the service answers a_orders reads with contract tests proving the shape.
- F2: the service guards a_audit writes against invalid input.
- NF1: the call path exposes error counts and slow-statement signals on the dashboard.
- NF2: a scratch-host restore drill is a precondition for release sign-off.

## Verification
- Replay production-like a_audit traffic against the staging store.
- Inject one fault (row-by-row loops stalling on large order volumes) and confirm the runbook resolves it.
- Success is declared only after a backup restore matches row counts.

## Definition of done
Sign-off happens when milestones are green, the restore drill has passed, and the runbook has been read.
