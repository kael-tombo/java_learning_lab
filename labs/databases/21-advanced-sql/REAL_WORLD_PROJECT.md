# Advanced SQL — Real World Project

## Problem
A production-flavored specification where advanced grouping, pivoting, and set-operation SQL carries real traffic, real failure, and real on-call pages.

## Architecture
```text
app -> service -> channels / conversions store -> replica + backup -> dashboard
```
Client requests reach a service layer, which builds reports over the channels and conversions stores.

## Milestones
- M1: Phase 1: model channels and conversions with seed data plus contract tests.
- M2: Phase 2: harden the reporting path with indexes, guards, and load probes.
- M3: the phase-3 rehearsal covers backup, restore, and rollback.
- M4: Phase 4: hand over runbooks so on-call owns the report suite without paging the author.

## Operations checklist
- Pair each schema change with the script that undoes it.
- Keep watch on the query path: errors, saturation, slow statements.
- A scheduled job restores the backup to a scratch host.
- Gate deploys on contract tests covering conversions behavior.

## Failure modes
- misread subtotal rows mistaken for real channels — flag the ROLLUP rows, per the checklist above.
- UNION silently dropping rows the report needed twice; switch the affected leg to UNION ALL and recount.
- pivot columns drifting whenever a new channel appears; generate the column list dynamically in tests.
- Fact reminder: ROLLUP adds subtotal and grand-total rows to grouped output. Guides every response above.

## Requirements
- F1: the service answers channels reads with contract tests proving the shape.
- F2: the service guards conversions writes against invalid input.
- NF1: the dashboard surfaces query-path error counts and slow-statement signals.
- NF2: a scratch-host restore drill is a precondition for release sign-off.

## Verification
- Replay production-like conversions traffic against the staging store.
- Inject one fault (misread subtotal rows mistaken for real channels) and confirm the runbook resolves it.
- Restore from the backup first, then reconcile row counts before the success call.

## Sign-off
Three things gate sign-off: milestones green, restore drill passed, runbook read by the team.
