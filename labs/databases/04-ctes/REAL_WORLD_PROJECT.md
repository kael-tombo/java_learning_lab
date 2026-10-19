# CTEs — Real World Project

## Problem
A production-flavored specification where non-recursive and recursive common table expressions carry real traffic, real failure, and real on-call pages.

## Architecture
```text
app -> service -> employees / mentorships store -> replica + backup -> dashboard
```
Client requests reach a service layer, which runs the query pipelines built on common table expressions against the employees and mentorships stores.

## Milestones
- M1: Phase 1: model employees and mentorships with seed data plus contract tests.
- M2: Phase 2: harden the query path with indexes, guards, and load probes.
- M3: phase three runs a backup, restore, and rollback rehearsal.
- M4: Phase 4: hand over runbooks so on-call owns the pipelines without paging the author.

## Operations checklist
- No schema change goes in without its rollback script.
- The query path earns monitoring for errors, saturation, and slow statements.
- Backup restores to a scratch host run on a calendar.
- Gate deploys on contract tests covering mentorships behavior.

## Failure modes
- infinite recursion when the expansion leg never exhausts new rows — the depth guard from the checklist above has to be in place first.
- cyclic hierarchies looping until a depth guard stops them; cap the leg and verify the stop count.
- over-chained CTEs hiding a simple join behind five layers; flatten during review before shipping.
- Fact reminder: a CTE names an intermediate result so the main query stays readable. Guides every response above.

## Requirements
- F1: the service answers employees reads with contract tests proving the shape.
- F2: the service guards mentorships writes against invalid input.
- NF1: the dashboard surfaces query-path error counts and slow-statement signals.
- NF2: a passing restore drill on a scratch host gates release sign-off.

## Verification
- Replay production-like mentorships traffic against the staging store.
- Inject one fault (infinite recursion when the expansion leg never exhausts new rows) and confirm the runbook resolves it.
- Row counts must reconcile against the restored backup before any success claim.

## Sign-off
Nobody signs off until milestones are green, the restore drill passed, and the team read the runbook.
