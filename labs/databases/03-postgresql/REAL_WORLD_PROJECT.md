# PostgreSQL — Real World Project

## Context
A service blueprint placing PostgreSQL schemas, data types, and transactional DDL habits on the critical path between users and durable state.

## Service sketch
Backups, replicas, and dashboards surround the query path so failures stay visible and recoverable.

## Delivery phases
- M1: Phase 1: model tenants and invoices with seed data plus contract tests.
- M2: Phase 2: harden the read path with indexes, guards, and load probes.
- M3: rehearse the store's backup, restore, and rollback paths.
- M4: Phase 4: hand over runbooks so on-call owns the schema work without paging the author.

## Reliability checklist
- No schema change goes in without its rollback script.
- Error, saturation, and slow-statement monitoring covers the query path.
- A scheduled job restores the backup to a scratch host.
- Gate deploys on contract tests covering invoices behavior.

## Failure drills
- objects landing in the wrong schema when search-path surprises writers — pin search_path in the migration runner per the checklist above.
- money rounding drift from choosing floating point over numeric; switch the column and backfill the affected rows.
- half-applied migrations from DDL issued outside one transaction; wrap each migration in a transaction before shipping.
- Fact reminder: PostgreSQL data types include serial-style identity, text, numeric, and timestamps. Guides every response above.

## Requirements
- F1: the service answers tenants reads with contract tests proving the shape.
- F2: the service guards invoices writes against invalid input.
- NF1: error counts and slow-statement signals from the query path are visible on the dashboard.
- NF2: a scratch-host restore drill is a precondition for release sign-off.

## Verification
- Replay production-like invoices traffic against the staging store.
- Inject one fault (objects landing in the wrong schema when search-path surprises writers) and confirm the runbook resolves it.
- Row counts must reconcile against the restored backup before any success claim.

## Exit criteria
Nobody signs off until milestones are green, the restore drill passed, and the team read the runbook.
