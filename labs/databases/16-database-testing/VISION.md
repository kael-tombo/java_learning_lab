# Database Testing — Vision

## Direction
Grow from first queries toward dependable judgment about deterministic test data and safe schema changes, measured by artifacts rather than hours studied.

## Why it matters here
- Command of these test habits turns on-call database surprises into routine checklist work.
- Concretely: fixtures load a known dataset so assertions stay deterministic.
- Concretely: rolling each test back keeps suites independent and repeatable.

## Growth path
1. Foundations: reproduce the mini project, beginning with a blank schema.
2. Depth: extend one item (the fixture script seeding three deterministic rows) until a reviewer asks for simplification.
3. Production: complete the real-world milestones with a restore drill on the record.

## Honest assessment
- Strong after this lab: reasoning about determinism, because a fixed dataset makes failures reproducible.
- Strong after this lab: applying the rollback wrapper during suite reviews.
- Still fragile: order-dependent tests passing alone and failing together remains the most likely incident for beginners.
- Still fragile: fixture drift hiding real regressions behind stale data still needs a senior eye on the test design.

## Anti-patterns to drop
- Snippets stay unused until the results reappear from a local run.
- Stop skipping the assertions row-count reconciliation after each suite change.
- Stop treating the constraint test asserting duplicate keys fail loudly as optional when the review depends on it.

## Non-coverage
- This lab does not cover vendor-specific test framework versions; treat those as separate tracks.
- It also skips production data cloning procedures, which belong to privacy and ops tracks.
- Skipping by design: benchmarks that were invented, version trivia, and reused view names.

## Checkable milestones
- [ ] Rebuild the seed schema on a blank host from memory.
- [ ] Explain the rollback-wrapped test proving isolation between cases to a peer without notes.
- [ ] Trigger untested downgrades trapping production on a bad migration in staging, and recover using the runbook.
- [ ] Say where suite discipline ends and vendor-specific test framework versions begin in a design review.

## How to use this lab
Take the items in order, keep every script rerunnable, and honor the non-coverage boundary above.
