# Joins — Real World Project

## Situation
A deployable slice proving INNER, LEFT, RIGHT, and FULL joins plus lateral reads survives contact with production load and operator error.

## Topology
Schema changes roll out behind review gates with a rehearsed rollback route.

## Build stages
- M1: Phase 1: model teams and players with seed data plus contract tests.
- M2: Phase 2: harden the query path with indexes, guards, and load probes.
- M3: backup, restore, and rollback all get a rehearsal this phase.
- M4: Phase 4: hand over runbooks so on-call owns the slice without paging the author.

## Operations list
- Pair each schema change with the script that undoes it.
- Errors, saturation, and slow statements from the query path get watched.
- Restore the backup onto a scratch host at a steady cadence.
- Gate deploys on contract tests covering players behavior.

## What breaks
- row multiplication when the join key is not unique on one side — add the missing uniqueness rule the checklist above demands.
- vanishing teams after an INNER JOIN drops unmatched parents; switch the statement to a LEFT JOIN and re-verify counts.
- lateral lookups degrading when the inner query ignores its index; lock the index into the contract tests before deploy.
- Fact reminder: a lateral join lets the right side reference columns of the current left row. Guides every response above.

## Requirements
- F1: the service answers teams reads with contract tests proving the shape.
- F2: the service guards players writes against invalid input.
- NF1: error counts and slow-statement signals from the query path are visible on the dashboard.
- NF2: a scratch-host restore drill is a precondition for release sign-off.

## Verification
- Replay production-like players traffic against the staging store.
- Inject one fault (row multiplication when the join key is not unique on one side) and confirm the runbook resolves it.
- Success is declared only after a backup restore matches row counts.

## Definition of done
Sign-off requires green milestones, a restore drill that passed, and a runbook someone on the team has read.
