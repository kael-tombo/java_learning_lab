# Redis — Real World Project

## Situation
A deployable slice proving Redis strings, hashes, lists, sets, sorted sets, and expiry survives contact with production load and operator error.

## Topology
One Redis instance plus the application tier keeps the slice auditable; cluster mode waits for a later lab.

## Build stages
- M1: Phase 1: model sessions and leaderboard with seed data plus contract tests.
- M2: Phase 2: harden the hot path with indexes, guards, and load probes.
- M3: phase three runs a backup, restore, and rollback rehearsal.
- M4: Phase 4: hand over runbooks so on-call owns the slice without paging the author.

## Operations list
- Pair each schema change with the script that undoes it.
- Monitor the command path for errors, saturation, and slow statements.
- Schedule backup restores onto a scratch host.
- Gate deploys on contract tests covering leaderboard behavior.

## What breaks
- stale reads served after a write forgets to invalidate the cache — wire the explicit invalidation demanded by the checklist above.
- thundering-herd reloads when a hot key expires; stagger expiry or warm the cache in the background.
- memory pressure from keys created without any expiry; audit TTLs and let eviction do the cleanup.
- Fact reminder: expiry automatically removes keys so caches cannot grow forever. Guides every response above.

## Requirements
- F1: the service answers sessions reads with contract tests proving the shape.
- F2: the service guards leaderboard writes against invalid input.
- NF1: error counts and slow-statement signals from the query path are visible on the dashboard.
- NF2: no release sign-off while the scratch-host restore drill still fails.

## Verification
- Replay production-like leaderboard traffic against the staging store.
- Inject one fault (stale reads served after a write forgets to invalidate the cache) and confirm the runbook resolves it.
- The success call waits for a backup restore with row counts reconciled.

## Definition of done
Three things gate sign-off: milestones green, restore drill passed, runbook read by the team.
