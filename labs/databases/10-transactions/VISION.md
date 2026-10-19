# Transactions — Vision

## Trajectory
Grow from first queries toward dependable judgment about isolation levels and atomic writes, measured by artifacts rather than hours studied.

## Payoff
- Command of ACID transactions across READ COMMITTED and REPEATABLE READ isolation turns on-call database surprises into routine checklist work.
- Concretely: atomicity groups statements so partial transfers never persist.
- Concretely: READ COMMITTED hides uncommitted rows from concurrent readers.

## Milestones
1. Foundations: start from a blank schema and reproduce the mini project.
2. Depth: extend one item (the transfer script moving funds between two accounts atomically) until a reviewer asks for simplification.
3. Production: deliver the real-world milestones with a restore drill on file.

## Honest assessment
- Strong after this lab: reasoning about atomic boundaries, because the all-or-nothing rule is explicit.
- Strong after this lab: applying the committed-read guarantee when reviewing concurrent access.
- Still fragile: lost updates when two debits read the same balance concurrently remains the most likely incident for beginners.
- Still fragile: deadlocks from transfers locking accounts in opposite order still needs a senior eye on the locking design.

## Anti-patterns to drop
- Every canned snippet gets its results reproduced before reuse.
- Stop skipping the transfers row-count reconciliation after each change.
- Stop treating the non-repeatable-read comparison across two isolation levels as optional when the review depends on it.

## Not covered
- This lab does not cover distributed two-phase commit protocols; treat those as separate tracks.
- It also skips engine-specific lock view names, which differ per database.
- Deliberately omitted: invented benchmarks, version trivia, borrowed view names.

## Checkable milestones
- [ ] Rebuild the seed schema on a blank host from memory.
- [ ] Explain the dirty-read demonstration blocked by READ COMMITTED to a peer without notes.
- [ ] Trigger long transactions holding locks while users think in staging, and recover using the runbook.
- [ ] Say where local isolation ends and distributed two-phase commit protocols begin in a design review.

## Working agreement
Items go in order, scripts stay rerunnable, and the non-coverage boundary above is not crossed.
