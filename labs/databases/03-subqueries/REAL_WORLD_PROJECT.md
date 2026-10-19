# Subqueries — Real World Project

## Situation
A deployable slice proving scalar, IN and EXISTS, plus derived-table subqueries survives contact with production load and operator error.

## Topology
Schema changes roll out behind review gates with a rehearsed rollback route.

## Build stages
- M1: Phase 1: model courses and results with seed data plus contract tests.
- M2: Phase 2: harden the query path with indexes, guards, and load probes.
- M3: rehearse backup, restore, and rollback with the store data.
- M4: Phase 4: hand over runbooks so on-call owns the slice without paging the author.

## Operations list
- Attach the rollback script before any schema change lands.
- Watch the query path for errors, saturation, and statements running slow.
- Schedule backup restores onto a scratch host.
- Gate deploys on contract tests covering results behavior.

## What breaks
- NULL poison in NOT IN silently returning zero rows — swap to NOT EXISTS, as the checklist above implies.
- scalar subqueries erroring when more than one row comes back; constrain the inner row count and re-test.
- correlated subqueries re-running once per outer row without an index; add the covering index to the contract tests.
- Fact reminder: a derived table in FROM lets outer queries filter computed columns. Guides every response above.

## Requirements
- F1: the service answers courses reads with contract tests proving the shape.
- F2: the service guards results writes against invalid input.
- NF1: dashboards show error counts and slow-statement signals from the query path.
- NF2: release sign-off waits until the restore drill passes on a scratch host.

## Verification
- Replay production-like results traffic against the staging store.
- Inject one fault (NULL poison in NOT IN silently returning zero rows) and confirm the runbook resolves it.
- Row counts must reconcile against the restored backup before any success claim.

## Definition of done
Sign-off happens when milestones are green, the restore drill has passed, and the runbook has been read.
