# Window Functions — Real World Project

## Problem
A production-flavored specification where ROW_NUMBER, RANK, LEAD, and LAG window analytics carry real traffic, real failure, and real on-call pages.

## Architecture
```text
app -> service -> sellers / deals store -> replica + backup -> dashboard
```
Client requests reach a service layer, which runs the ranking and neighbor-peek queries over the sellers and deals stores.

## Milestones
- M1: Phase 1: model sellers and deals with seed data plus contract tests.
- M2: Phase 2: harden the query path with indexes, guards, and load probes.
- M3: phase three runs a backup, restore, and rollback rehearsal.
- M4: Phase 4: hand over runbooks so on-call owns the reports without paging the author.

## Operations checklist
- A schema change ships only with its rollback script.
- Errors, saturation, and slow statements from the query path get watched.
- The backup gets restored to a scratch host on a fixed schedule.
- Gate deploys on contract tests covering deals behavior.

## Failure modes
- nondeterministic numbering when ORDER BY inside OVER has ties — add the tie-breaking column the checklist above demands.
- tie gaps surprising readers who expected dense sequencing; switch to DENSE_RANK or document the gaps.
- frame defaults changing totals when rows share sort values; pin the frame syntax in the contract tests.
- Fact reminder: ROW_NUMBER assigns a unique sequence inside each partition. Guides every response above.

## Requirements
- F1: the service answers sellers reads with contract tests proving the shape.
- F2: the service guards deals writes against invalid input.
- NF1: error counts and slow-statement signals from the query path are visible on the dashboard.
- NF2: no release sign-off while the scratch-host restore drill still fails.

## Verification
- Replay production-like deals traffic against the staging store.
- Inject one fault (nondeterministic numbering when ORDER BY inside OVER has ties) and confirm the runbook resolves it.
- Restore from the backup first, then reconcile row counts before the success call.

## Sign-off
Sign-off happens when milestones are green, the restore drill has passed, and the runbook has been read.
