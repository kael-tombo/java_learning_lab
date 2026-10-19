# Oracle Architecture — Real World Project

## Situation
A deployable slice proving Oracle instance-versus-database layout with tablespaces and SGA/PGA roles survives contact with production load and operator error.

## Topology
Schema changes roll out behind review gates with a rehearsed rollback route.

## Build stages
- M1: Phase 1: model o_emps and o_depts with seed data plus contract tests.
- M2: Phase 2: harden the access path with indexes, guards, and load probes.
- M3: rehearse backup, restore, and rollback with the store data.
- M4: Phase 4: hand over runbooks so on-call owns the layout without paging the author.

## Operations list
- Attach the rollback script before any schema change lands.
- Monitor the instance for errors, saturation, and slow statements.
- Restore the backup onto a scratch host at a steady cadence.
- Gate deploys on contract tests covering o_depts behavior.

## What breaks
- tablespace-full errors freezing employee inserts — size the store before the import, per the checklist above.
- instance-versus-database confusion during outage triage; keep the legend from the diagram inside the runbook.
- undersized shared memory starving concurrent sessions; watch hit rates and raise the cache before the peak.
- Fact reminder: SGA memory is shared across sessions while PGA memory serves one process. Guides every response above.

## Requirements
- F1: the service answers o_emps reads with contract tests proving the shape.
- F2: the service guards o_depts writes against invalid input.
- NF1: error counts and slow-statement signals from the query path are visible on the dashboard.
- NF2: release sign-off waits until the restore drill passes on a scratch host.

## Verification
- Replay production-like o_depts traffic against the staging store.
- Inject one fault (tablespace-full errors freezing employee inserts) and confirm the runbook resolves it.
- Success is declared only after a backup restore matches row counts.

## Definition of done
Nobody signs off until milestones are green, the restore drill passed, and the team read the runbook.
