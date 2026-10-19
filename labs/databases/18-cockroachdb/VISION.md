# CockroachDB — Vision

## Direction
Grow from first queries toward dependable judgment about range survival and retry correctness, measured by artifacts rather than hours studied.

## Why it matters here
- Command of distributed-SQL behavior turns on-call database surprises into routine checklist work.
- Concretely: distributed SQL spreads ranges across nodes for survival.
- Concretely: serializable intent means retried transactions stay correct.

## Growth path
1. Foundations: reproduce the mini project, beginning with a blank schema.
2. Depth: extend one item (the multi-node sketch placing account ranges on three nodes) until a reviewer asks for simplification.
3. Production: deliver the real-world milestones with a restore drill on file.

## Honest assessment
- Strong after this lab: reasoning about range placement, because node survival follows from it.
- Strong after this lab: applying the retry-safety rule when reviewing payment writes.
- Still fragile: retry storms when clients hammer contended accounts remains the most likely incident for beginners.
- Still fragile: hot ranges forming behind sequential keys still needs a senior eye on the key design.

## Anti-patterns to drop
- Snippets stay unused until the results reappear from a local run.
- Stop skipping the r_payments row-count reconciliation after each change.
- Stop treating the hot-range review spreading sequential payment keys as optional when the review depends on it.

## Non-coverage
- This lab does not cover product version numbers; treat those as separate tracks.
- It also skips invented latency benchmarks, which add noise rather than judgment.
- The deliberate omissions: invented benchmarks, version trivia, and view names not our own.

## Checkable milestones
- [ ] Rebuild the seed schema, working from memory, on a blank host.
- [ ] Explain the retry-loop sketch re-running one contended payment to a peer without notes.
- [ ] Trigger missing retry loops surfacing transient aborts to users in staging, and recover using the runbook.
- [ ] Say where range design ends and product version numbers begin in a design review.

## How to use this lab
Follow the items in sequence, keep scripts rerunnable, and respect the non-coverage boundary stated above.
