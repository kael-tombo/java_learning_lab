# Query Optimization C — Real World Project

## Situation
A deployable slice proving join order and covering-index reasoning in the events domain survives contact with production load and operator error.

## Topology
Schema changes roll out behind review gates with a rehearsed rollback route.

## Build stages
- M1: Phase 1: model events and attendees with seed data plus contract tests.
- M2: Phase 2: harden the reporting path with indexes, guards, and load probes.
- M3: rehearse backup, restore, and rollback with the store data.
- M4: Phase 4: hand over runbooks so on-call owns the plan reviews without paging the author.

## Operations list
- Every schema change carries its rollback script from day one.
- Error, saturation, and slow-statement monitoring covers the query path.
- Restore the backup onto a scratch host at a steady cadence.
- Gate deploys on contract tests covering attendees behavior.

## What breaks
- bad join order scanning the huge side first — lead from the selective filter, as the checklist above demands.
- covering indexes bloating write paths beyond their read value; price each index per insert and drop the unjustified ones.
- residual filters hiding inside a seemingly indexed plan; audit leftover predicate work after each change.
- Fact reminder: residual predicates filter rows that the index cannot eliminate. Guides every response above.

## Requirements
- F1: the service answers events reads with contract tests proving the shape.
- F2: the service guards attendees writes against invalid input.
- NF1: dashboards show error counts and slow-statement signals from the query path.
- NF2: no release sign-off while the scratch-host restore drill still fails.

## Verification
- Replay production-like attendees traffic against the staging store.
- Inject one fault (bad join order scanning the huge side first) and confirm the runbook resolves it.
- The success call waits for a backup restore with row counts reconciled.

## Definition of done
Sign-off requires green milestones, a restore drill that passed, and a runbook someone on the team has read.
