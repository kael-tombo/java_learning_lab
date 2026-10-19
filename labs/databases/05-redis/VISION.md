# Redis — Vision

## Trajectory
Grow from first commands toward dependable judgment about Redis structures and their lifecycle, measured by artifacts rather than hours studied.

## Payoff
- Command of these structures turns on-call database surprises into routine checklist work.
- Concretely: strings hold counters and tokens while hashes group related fields.
- Concretely: lists queue work, sets dedupe members, and sorted sets rank scores.

## Milestones
1. Foundations: reproduce the mini project from a blank host.
2. Depth: extend one item (the session hash storing user id, role, and login stamp) until a reviewer asks for simplification.
3. Production: deliver the real-world milestones with a restore drill on record.

## Honest assessment
- Strong after this lab: reasoning about which structure fits which job, since counters, tokens, and grouped fields each have a home.
- Strong after this lab: applying the queue-dedupe-rank trio during design reviews.
- Still fragile: stale reads served after a write forgets to invalidate the cache remains the most likely incident for beginners.
- Still fragile: thundering-herd reloads when a hot key expires still needs a senior eye on the cache design.

## Anti-patterns to drop
- Stop cargo-culting canned snippets without reproducing their results first.
- Stop skipping the leaderboard row-count reconciliation after each change.
- Stop treating notification list pushing and trimming recent events as optional when the review depends on it.

## Not covered
- This lab does not cover Redis server version numbers and release claims; treat those as separate tracks.
- It also skips cluster slot administration, which belongs to operations tracks.
- Skipped deliberately: invented benchmarks, version trivia, and borrowed view names.

## Checkable milestones
- [ ] Rebuild the seed data from memory on a blank host.
- [ ] Explain the rate-limit counter with a short expiry window to a peer without notes.
- [ ] Trigger memory pressure from keys created without any expiry in staging, and recover using the runbook.
- [ ] Say where this scope ends and Redis server version numbers and release claims begin in a design review.

## Working agreement
Work the items in order, keep scripts rerunnable, and stop at the non-coverage boundary above.
