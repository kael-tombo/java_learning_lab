# Database Security — Real World Project

## Situation
A deployable slice proving least-privilege roles, masking, and audit trails survives contact with production load and operator error.

## Topology
Schema changes roll out behind review gates with a rehearsed rollback route.

## Build stages
- M1: Phase 1: model patients and access_log with seed data plus contract tests.
- M2: Phase 2: harden the access path with indexes, guards, and load probes.
- M3: phase three runs a backup, restore, and rollback rehearsal.
- M4: Phase 4: hand over runbooks so on-call owns the grant matrix without paging the author.

## Operations list
- Attach the rollback script before any schema change lands.
- Monitor the access path for errors, saturation, and slow statements.
- The backup gets restored to a scratch host on a fixed schedule.
- Gate deploys on contract tests covering access_log behavior.

## What breaks
- over-broad grants exposing patient data to every analyst — revoke to the role matrix, per the checklist above.
- unmasked exports leaking sensitive columns into files; route analyst exports through the masked view.
- missing audit rows leaving a breach unexplainable; verify trail coverage after every sensitive-read change.
- Fact reminder: audit trails record who touched sensitive patient rows. Guides every response above.

## Requirements
- F1: the service answers patients reads with contract tests proving the shape.
- F2: the service guards access_log writes against invalid input.
- NF1: dashboards show error counts and slow-statement signals from the query path.
- NF2: the release is signed off only after the scratch-host restore drill passes.

## Verification
- Replay production-like access_log traffic against the staging store.
- Inject one fault (over-broad grants exposing patient data to every analyst) and confirm the runbook resolves it.
- Success is declared only after a backup restore matches row counts.

## Definition of done
Three things gate sign-off: milestones green, restore drill passed, runbook read by the team.
