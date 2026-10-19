# SQL Fundamentals — Real World Project

## Problem
A production-flavored specification where constraints, keys, and disciplined DML carry real traffic, real failure, and real on-call pages.

## Architecture
```text
app -> service -> students / enrollments store -> replica + backup -> dashboard
```
Client requests reach a service layer, which enforces the constraints and keys of the model against the students and enrollments stores.

## Milestones
- M1: Phase 1: model students and enrollments with seed data plus contract tests.
- M2: Phase 2: harden the write path with indexes, guards, and load probes.
- M3: phase three runs a backup, restore, and rollback rehearsal.
- M4: Phase 4: hand over runbooks so on-call owns the guardrails without paging the author.

## Operations checklist
- No schema change goes in without its rollback script.
- Keep watch on the query path: errors, saturation, slow statements.
- Restore the backup onto a scratch host at a steady cadence.
- Gate deploys on contract tests covering enrollments behavior.

## Failure modes
- duplicate emails slipping past a missing unique constraint — restore the constraint first, then re-run the checklist above.
- enrollments pointing at deleted students after an unguarded delete; add the documented delete rule to the foreign key.
- half-applied multi-statement edits committed without a transaction; wrap the change and verify count parity before shipping.
- Fact reminder: NOT NULL plus CHECK constraints reject bad data at the gate. Guides every response above.

## Requirements
- F1: the service answers students reads with contract tests proving the shape.
- F2: the service guards enrollments writes against invalid input.
- NF1: the query path reports error counts and slow statements to the dashboard.
- NF2: release sign-off waits until the restore drill passes on a scratch host.

## Verification
- Replay production-like enrollments traffic against the staging store.
- Inject one fault (duplicate emails slipping past a missing unique constraint) and confirm the runbook resolves it.
- Success is declared only after a backup restore matches row counts.

## Sign-off
Sign-off requires green milestones, a restore drill that passed, and a runbook someone on the team has read.
