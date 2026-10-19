# Query Optimization A — Vision

## Trajectory
Grow from first queries toward dependable judgment about index selection and predicate design, measured by artifacts rather than hours studied.

## Payoff
- Command of these tuning habits turns on-call database surprises into routine checklist work.
- Concretely: B-tree indexes accelerate equality and range lookups on leading columns.
- Concretely: sargable predicates keep index seeks possible by avoiding wrapped columns.

## Milestones
1. Foundations: from a blank schema, reproduce the mini project.
2. Depth: extend one item (the order lookup index on customer id plus order date) until a reviewer asks for simplification.
3. Production: deliver the real-world milestones and keep a restore drill on file.

## Honest assessment
- Strong after this lab: reasoning about leading-column rules, since seek-versus-scan behavior follows from them.
- Strong after this lab: applying the sargability check during predicate reviews.
- Still fragile: function-wrapped predicates forcing full scans over indexed dates remains the most likely incident for beginners.
- Still fragile: over-indexing slowing every order insert to a crawl still needs a senior eye on the index set.

## Anti-patterns to drop
- Every canned snippet gets its results reproduced before reuse.
- Stop skipping the order_lines row-count reconciliation after each change.
- Stop treating the covering-index sketch for the open-orders list as optional when the review depends on it.

## Not covered
- This lab does not cover invented timing benchmarks on order queries; treat those as separate tracks.
- It also skips storage-engine page internals, which sit below the planner.
- Not included on purpose: invented benchmarks, version trivia, and borrowed view names.

## Checkable milestones
- [ ] Rebuild the seed schema on a blank host without peeking at notes.
- [ ] Explain the sargability rewrite removing a function around order date to a peer without notes.
- [ ] Trigger stale statistics steering the optimizer toward a bad plan in staging, and recover using the runbook.
- [ ] Say where predicate design ends and invented timing benchmarks on order queries begin in a design review.

## Working agreement
Items go in order, scripts stay rerunnable, and the non-coverage boundary above is not crossed.
