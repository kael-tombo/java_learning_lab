# Database Sharding — Real World Project

## Problem
A production-flavored specification where shard key selection and cross-shard query costs carry real traffic, real failure, and real on-call pages.

## Architecture
```text
app -> service -> shoppers / baskets store -> replica + backup -> dashboard
```
Client requests reach a service layer, which routes writes and reads across the shards holding shoppers and baskets data.

## Milestones
- M1: Phase 1: model shoppers and baskets with seed data plus contract tests.
- M2: Phase 2: harden the routing path with indexes, guards, and load probes.
- M3: Phase 3: rehearse backup, restore, and rollback for the shard set.
- M4: Phase 4: hand over runbooks so on-call owns the key ranges without paging the author.

## Operations checklist
- Pair each schema change with the script that undoes it.
- Monitor each node for errors, saturation, and slow statements.
- Restore the backup onto a scratch host at a steady cadence.
- Gate deploys on contract tests covering baskets behavior.

## Failure modes
- hot shards melting under a celebrity-tenant key — split the range before the season peak, per the checklist above.
- cross-shard joins timing out during peak baskets; pre-compute the shared report or co-locate the keyed data.
- resharding stalls when the key cannot split evenly; pick a finer-grained hash for the next migration.
- Fact reminder: the shard key decides which node owns each row. Guides every response above.

## Requirements
- F1: the service answers shoppers reads with contract tests proving the shape.
- F2: the service guards baskets writes against invalid input.
- NF1: dashboards show error counts and slow-statement signals from the query path.
- NF2: the release is signed off only after the scratch-host restore drill passes.

## Verification
- Replay production-like baskets traffic against the staging store.
- Inject one fault (hot shards melting under a celebrity-tenant key) and confirm the runbook resolves it.
- Restore from the backup first, then reconcile row counts before the success call.

## Sign-off
Sign-off requires green milestones, a restore drill that passed, and a runbook someone on the team has read.
