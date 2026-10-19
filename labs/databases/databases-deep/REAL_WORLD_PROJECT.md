# Databases Deep — Real World Project

## Context
A service blueprint placing end-to-end database internals from storage to optimizer on the critical path between users and durable state.

## Service sketch
Backups, replicas, and dashboards surround the engine so failures stay visible and recoverable.

## Delivery phases
- M1: Phase 1: model deep_docs and deep_postings with seed data plus contract tests.
- M2: Phase 2: harden the read path with indexes, guards, and load probes.
- M3: the phase-3 rehearsal covers backup, restore, and rollback.
- M4: Phase 4: hand over runbooks so on-call owns layer triage without paging the author.

## Reliability checklist
- Pair each schema change with the script that undoes it.
- Monitor each layer for errors, saturation, and slow statements.
- Schedule backup restores onto a scratch host.
- Gate deploys on contract tests covering deep_postings behavior.

## Failure drills
- treating the database as a black box during outages — open the layer trace, per the checklist above.
- adding indexes without pricing their write cost; run the worksheet before any new index ships.
- ignoring statistics until every plan goes wrong; refresh stats on a schedule and re-explain the hot queries.
- Fact reminder: indexes trade write cost for dramatically faster lookups. Guides every response above.

## Requirements
- F1: the service answers deep_docs reads with contract tests proving the shape.
- F2: the service guards deep_postings writes against invalid input.
- NF1: dashboards show error counts and slow-statement signals from the query path.
- NF2: release sign-off waits until the restore drill passes on a scratch host.

## Verification
- Replay production-like deep_postings traffic against the staging store.
- Inject one fault (treating the database as a black box during outages) and confirm the runbook resolves it.
- Success is declared only after a backup restore matches row counts.

## Exit criteria
Three things gate sign-off: milestones green, restore drill passed, runbook read by the team.
