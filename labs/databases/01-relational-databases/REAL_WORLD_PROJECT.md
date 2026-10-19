# Relational Databases — Real World Project

## Problem
A production-flavored specification where relational modeling with primary keys, foreign keys, and normal forms carries real traffic, real failure, and real on-call pages.

## Architecture
```text
app -> service -> authors / books store -> replica + backup -> dashboard
```
Client requests reach a service layer, which enforces the key and dependency rules of the model against the authors and books stores.

## Milestones
- M1: Phase 1: model authors and books with seed data plus contract tests.
- M2: Phase 2: harden the schema path with indexes, guards, and load probes.
- M3: phase three runs a backup, restore, and rollback rehearsal.
- M4: Phase 4: hand over runbooks so on-call owns the design without paging the author.

## Operations checklist
- A schema change ships only with its rollback script.
- Watch the query path for errors, saturation, and statements running slow.
- The backup gets restored to a scratch host on a fixed schedule.
- Gate deploys on contract tests covering books behavior.

## Failure modes
- orphaned book rows after an author delete without a referential action — the delete path ignored the foreign key; re-run the checklist above.
- duplicate publisher cities drifting out of sync across denormalized rows; caught during restore rehearsals, then fixed with a single source of truth.
- ambiguous natural keys colliding when two authors share one name; blocked before deploy by contract tests.
- Fact reminder: a primary key uniquely identifies each row and never repeats across the table. Guides every response above.

## Requirements
- F1: the service answers authors reads with contract tests proving the shape.
- F2: the service guards books writes against invalid input.
- NF1: dashboards light up with query-path error counts and slow statements.
- NF2: a scratch-host restore drill is a precondition for release sign-off.

## Verification
- Replay production-like books traffic against the staging store.
- Inject one fault (orphaned book rows after an author delete without a referential action) and confirm the runbook resolves it.
- The success call waits for a backup restore with row counts reconciled.

## Sign-off
Three things gate sign-off: milestones green, restore drill passed, runbook read by the team.
