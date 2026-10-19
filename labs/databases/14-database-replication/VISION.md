# Database Replication — Vision

## Where this points
Grow from first queries toward dependable judgment about streaming copies and safe promotion, measured by artifacts rather than hours studied.

## Capabilities gained
- Command of replication running turns on-call database surprises into routine checklist work.
- Concretely: replicas replay the primary log and always trail by some lag.
- Concretely: lag measurement compares applied positions between primary and replica.

## Sequence
1. Foundations: start from a blank schema and reproduce the mini project.
2. Depth: extend one item (the lag-measurement query comparing primary and replica positions) until a reviewer asks for simplification.
3. Production: close the real-world milestones once a restore drill is on record.

## Honest assessment
- Strong after this lab: reasoning about trailing reads, since replay lag is now measurable.
- Strong after this lab: applying position comparison during replication reviews.
- Still fragile: stale reads served from a lagging replica remains the most likely incident for beginners.
- Still fragile: split brain after two nodes both accept writes still needs a senior eye on the promotion design.

## Anti-patterns to drop
- Do not reuse canned snippets until their results have been reproduced locally.
- Stop skipping the ledger_replica row-count reconciliation after each change.
- Stop treating the failover drill promoting the replica step by step as optional when the review depends on it.

## Out of scope
- This lab does not cover vendor-specific replication view names; treat those as separate tracks.
- It also skips invented lag benchmarks, which add noise rather than judgment.
- Skipping by design: benchmarks that were invented, version trivia, and reused view names.

## Checkable milestones
- [ ] Rebuild the seed schema on a blank host without peeking at notes.
- [ ] Explain the read-routing sketch sending reports to the replica to a peer without notes.
- [ ] Trigger replay backlogs growing faster than catch-up capacity in staging, and recover using the runbook.
- [ ] Say where lag practice ends and vendor-specific replication view names begin in a design review.

## Study guidance
Take the items in order, keep every script rerunnable, and honor the non-coverage boundary above.
