# JDBC and JPA — Vision

## Trajectory
Grow from first queries toward dependable judgment about direct JDBC access and JPA entity work, measured by artifacts rather than hours studied.

## Payoff
- Command of these access layers turns on-call database surprises into routine checklist work.
- Concretely: DriverManager opens direct connections while DataSource enables pooling.
- Concretely: try-with-resources guarantees connections and statements always close.

## Milestones
1. Foundations: start from a blank schema and reproduce the mini project.
2. Depth: extend one item (the DriverManager query reading product rows with closed resources) until a reviewer asks for simplification.
3. Production: close the real-world milestones once a restore drill is on record.

## Honest assessment
- Strong after this lab: reasoning about connection ownership, since the direct-versus-pooled split is explicit.
- Strong after this lab: applying the always-close guarantee during code reviews.
- Still fragile: leaked connections from statements never closed remains the most likely incident for beginners.
- Still fragile: injection holes opened by string-concatenated SQL still needs a senior eye on the data access design.

## Anti-patterns to drop
- Reproduce a snippet's results before adopting it anywhere.
- Stop skipping the stock row-count reconciliation after each change.
- Stop treating parameterized statement binding a product id safely as optional when the review depends on it.

## Not covered
- This lab does not cover provider-specific performance flags; treat those as separate tracks.
- It also skips framework version numbers, which sit outside access-layer fundamentals.
- Left out on purpose: made-up benchmarks, version trivia, and view names borrowed from elsewhere.

## Checkable milestones
- [ ] Blank host first, then rebuild the seed schema from memory.
- [ ] Explain the DataSource sketch routing through a pool to a peer without notes.
- [ ] Trigger detached-entity confusion when edits happen outside a transaction in staging, and recover using the runbook.
- [ ] Say where access fundamentals end and provider-specific performance flags begin in a design review.

## Working agreement
Items go in order, scripts stay rerunnable, and the non-coverage boundary above is not crossed.
