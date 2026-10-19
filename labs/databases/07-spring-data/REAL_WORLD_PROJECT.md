# Spring Data — Real World Project

## Problem
A production-flavored specification where Spring Data repository derivation and query methods carry real traffic, real failure, and real on-call pages.

## Architecture
```text
app -> service -> drivers / routes store -> replica + backup -> dashboard
```
Client requests reach a service layer, which runs the derived and custom finders against the drivers and routes stores.

## Milestones
- M1: Phase 1: model drivers and routes with seed data plus contract tests.
- M2: Phase 2: harden the read path with indexes, guards, and load probes.
- M3: backup, restore, and rollback all get a rehearsal this phase.
- M4: Phase 4: hand over runbooks so on-call owns the repositories without paging the author.

## Operations checklist
- Every schema change carries its rollback script from day one.
- The query path earns monitoring for errors, saturation, and slow statements.
- The backup gets restored to a scratch host on a fixed schedule.
- Gate deploys on contract tests covering routes behavior.

## Failure modes
- wrong queries generated from misread method-name keywords — pin the generated SQL in contract tests, per the checklist above.
- unbounded findAll calls loading entire tables into memory; page every listing and cap the fetch size.
- method names growing so long nobody dares to change them; replace with a custom query during review.
- Fact reminder: derived query methods translate method names into generated queries. Guides every response above.

## Requirements
- F1: the service answers drivers reads with contract tests proving the shape.
- F2: the service guards routes writes against invalid input.
- NF1: the query path reports error counts and slow statements to the dashboard.
- NF2: the release is signed off only after the scratch-host restore drill passes.

## Verification
- Replay production-like routes traffic against the staging store.
- Inject one fault (wrong queries generated from misread method-name keywords) and confirm the runbook resolves it.
- Restore from the backup first, then reconcile row counts before the success call.

## Sign-off
Green milestones plus a passed restore drill plus a read runbook together amount to sign-off.
