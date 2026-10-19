# Query Optimization C — Vision

## Trajectory
Grow from first queries toward dependable judgment about selective joins and index-only reads, measured by artifacts rather than hours studied.

## Payoff
- Command of these plan habits turns on-call database surprises into routine checklist work.
- Concretely: join order starts from the most selective event filter.
- Concretely: covering indexes answer queries without touching the table.

## Milestones
1. Foundations: the mini project gets reproduced after clearing the schema.
2. Depth: extend one item (the join-order rewrite leading from the selective event filter) until a reviewer asks for simplification.
3. Production: the real-world milestones go out once a restore drill is recorded.

## Honest assessment
- Strong after this lab: reasoning about selectivity-first ordering, since the plan follows from it.
- Strong after this lab: applying the table-bypass check when reviewing list queries.
- Still fragile: bad join order scanning the huge side first remains the most likely incident for beginners.
- Still fragile: covering indexes bloating write paths beyond their read value still needs a senior eye on the index set.

## Anti-patterns to drop
- Snippets stay unused until the results reappear from a local run.
- Stop skipping the attendees row-count reconciliation after each change.
- Stop treating the residual-predicate audit on one event report as optional when the review depends on it.

## Not covered
- This lab does not cover invented timing benchmarks on event queries; treat those as separate tracks.
- It also skips cost-model source internals, which sit below the plan output.
- The deliberate omissions: invented benchmarks, version trivia, and view names not our own.

## Checkable milestones
- [ ] From memory, rebuild the seed schema on a blank host.
- [ ] Explain the covering index for the attendee check-in list to a peer without notes.
- [ ] Trigger residual filters hiding inside a seemingly indexed plan in staging, and recover using the runbook.
- [ ] Say where join reasoning ends and invented timing benchmarks on event queries begin in a design review.

## Working agreement
The items run in order, scripts remain rerunnable, and the non-coverage boundary above holds.
