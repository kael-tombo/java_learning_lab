# Aggregation — Real World Project

## Context
A service blueprint placing GROUP BY aggregation with legal select lists on the critical path between users and durable state.

## Service sketch
Backups, replicas, and dashboards surround the query path so failures stay visible and recoverable.

## Delivery phases
- M1: Phase 1: model regions and sales with seed data plus contract tests.
- M2: Phase 2: harden the reporting path with indexes, guards, and load probes.
- M3: phase three runs a backup, restore, and rollback rehearsal.
- M4: Phase 4: hand over runbooks so on-call owns the reports without paging the author.

## Reliability checklist
- Attach the rollback script before any schema change lands.
- The query path earns monitoring for errors, saturation, and slow statements.
- A scheduled job restores the backup to a scratch host.
- Gate deploys on contract tests covering sales behavior.

## Failure drills
- grouping errors from selecting an ungrouped plain column — quote the legality rule from the checklist above and fix the select list.
- double counting after joining before aggregating; deduplicate at the join or pre-aggregate in a subquery.
- HAVING predicates accidentally written against ungrouped rows; move the filter to WHERE and retest totals.
- Fact reminder: every non-aggregated SELECT column must appear in the GROUP BY list. Guides every response above.

## Requirements
- F1: the service answers regions reads with contract tests proving the shape.
- F2: the service guards sales writes against invalid input.
- NF1: error counts and slow-statement signals from the query path are visible on the dashboard.
- NF2: release sign-off waits until the restore drill passes on a scratch host.

## Verification
- Replay production-like sales traffic against the staging store.
- Inject one fault (grouping errors from selecting an ungrouped plain column) and confirm the runbook resolves it.
- Row counts must reconcile against the restored backup before any success claim.

## Exit criteria
Three things gate sign-off: milestones green, restore drill passed, runbook read by the team.
