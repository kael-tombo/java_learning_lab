# JDBC and JPA — Real World Project

## Situation
A deployable slice proving JDBC DriverManager and DataSource access with JPA EntityManager mapping survives contact with production load and operator error.

## Topology
Schema changes roll out behind review gates with a rehearsed rollback route.

## Build stages
- M1: Phase 1: model products and stock with seed data plus contract tests.
- M2: Phase 2: harden the data path with indexes, guards, and load probes.
- M3: phase three runs a backup, restore, and rollback rehearsal.
- M4: Phase 4: hand over runbooks so on-call owns the access layer without paging the author.

## Operations list
- Attach the rollback script before any schema change lands.
- Watch the query path for errors, saturation, and statements running slow.
- The backup gets restored to a scratch host on a fixed schedule.
- Gate deploys on contract tests covering stock behavior.

## What breaks
- leaked connections from statements never closed — enforce try-with-resources everywhere, as the checklist above demands.
- injection holes opened by string-concatenated SQL; bind every parameter and block ad-hoc SQL in review.
- detached-entity confusion when edits happen outside a transaction; keep the boundary note next to the persistence code.
- Fact reminder: EntityManager maps entity state changes onto relational rows. Guides every response above.

## Requirements
- F1: the service answers products reads with contract tests proving the shape.
- F2: the service guards stock writes against invalid input.
- NF1: the query path reports error counts and slow statements to the dashboard.
- NF2: a passing restore drill on a scratch host gates release sign-off.

## Verification
- Replay production-like stock traffic against the staging store.
- Inject one fault (leaked connections from statements never closed) and confirm the runbook resolves it.
- Bring the backup back and reconcile row counts before calling it done.

## Definition of done
Sign-off happens when milestones are green, the restore drill has passed, and the runbook has been read.
