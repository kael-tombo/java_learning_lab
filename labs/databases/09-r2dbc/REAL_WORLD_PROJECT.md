# R2DBC — Real World Project

## Problem
A production-flavored specification where R2DBC reactive non-blocking database access carries real traffic, real failure, and real on-call pages.

## Architecture
```text
app -> service -> sensors / readings store -> replica + backup -> dashboard
```
Client requests reach a service layer, which streams publisher chains over the sensors and readings stores.

## Milestones
- M1: Phase 1: model sensors and readings with seed data plus contract tests.
- M2: Phase 2: harden the streaming path with indexes, guards, and load probes.
- M3: the phase-3 rehearsal covers backup, restore, and rollback.
- M4: Phase 4: hand over runbooks so on-call owns the pipelines without paging the author.

## Operations checklist
- Pair each schema change with the script that undoes it.
- The query path earns monitoring for errors, saturation, and slow statements.
- The backup gets restored to a scratch host on a fixed schedule.
- Gate deploys on contract tests covering readings behavior.

## Failure modes
- hidden blocking calls freezing the event loop — run the blocking-call hunt, per the checklist above.
- unbounded streams exhausting memory without demand limits; cap demand and re-test the hot feed.
- transaction boundaries leaking across reactive operators; scope the boundary to one publisher chain and verify rollback.
- Fact reminder: R2DBC exposes non-blocking publishers instead of blocking result sets. Guides every response above.

## Requirements
- F1: the service answers sensors reads with contract tests proving the shape.
- F2: the service guards readings writes against invalid input.
- NF1: the query path reports error counts and slow statements to the dashboard.
- NF2: no release sign-off while the scratch-host restore drill still fails.

## Verification
- Replay production-like readings traffic against the staging store.
- Inject one fault (hidden blocking calls freezing the event loop) and confirm the runbook resolves it.
- Bring the backup back and reconcile row counts before calling it done.

## Sign-off
Nobody signs off until milestones are green, the restore drill passed, and the team read the runbook.
