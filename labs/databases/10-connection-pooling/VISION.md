# Connection Pooling — Vision

## Where this points
Grow from first queries toward dependable judgment about lease budgets and eviction policy, measured by artifacts rather than hours studied.

## Capabilities gained
- Command of pool sizing turns on-call database surprises into routine checklist work.
- Concretely: minimum connections keep warm capacity ready for bursts.
- Concretely: maximum connections cap load so the database stays upright.

## Sequence
1. Foundations: start from a blank schema and reproduce the mini project.
2. Depth: extend one item (the pool sizing worksheet deriving min and max from measured concurrency) until a reviewer asks for simplification.
3. Production: close the real-world milestones once a restore drill is on record.

## Honest assessment
- Strong after this lab: reasoning about warm-capacity and load-cap trade-offs, because the min/max rules are explicit.
- Strong after this lab: applying eviction policy during lease reviews.
- Still fragile: pool exhaustion freezing checkout queues under peak load remains the most likely incident for beginners.
- Still fragile: connection leaks draining the pool one abandoned lease at a time still needs a senior eye on the pool design.

## Anti-patterns to drop
- Do not reuse canned snippets until their results have been reproduced locally.
- Stop skipping the leases row-count reconciliation after each configuration change.
- Stop treating the wait-queue drill observing checkout under saturation as optional when the review depends on it.

## Out of scope
- This lab does not cover vendor-specific pool parameter names; treat those as separate tracks.
- It also skips network proxy internals, which belong to infrastructure tracks.
- Deliberately omitted: invented benchmarks, version trivia, borrowed view names.

## Checkable milestones
- [ ] Rebuild the seed schema on a blank host from memory.
- [ ] Explain the idle-timeout experiment proving eviction reclaims leases to a peer without notes.
- [ ] Trigger oversized maximums overwhelming the database with concurrent sessions in staging, and recover using the runbook.
- [ ] Say where pool tuning ends and vendor-specific pool parameter names begin in a design review.

## Study guidance
Work through the items in sequence with rerunnable scripts, and stop where the non-coverage boundary above says.
