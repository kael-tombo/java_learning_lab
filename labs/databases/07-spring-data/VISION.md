# Spring Data — Vision

## Direction
Grow from first queries toward dependable judgment about generated finders and custom queries, measured by artifacts rather than hours studied.

## Why it matters here
- Command of repository derivation turns on-call database surprises into routine checklist work.
- Concretely: derived query methods translate method names into generated queries.
- Concretely: paging and sorting parameters keep large result sets bounded.

## Growth path
1. Foundations: reproduce the mini project, beginning with a blank schema.
2. Depth: extend one item (the driver repository with a derived status finder) until a reviewer asks for simplification.
3. Production: a recorded restore drill travels with the real-world milestones.

## Honest assessment
- Strong after this lab: reasoning about name-to-query translation, because the generation rules are explicit.
- Strong after this lab: applying bounded-result parameters during listing reviews.
- Still fragile: wrong queries generated from misread method-name keywords remains the most likely incident for beginners.
- Still fragile: unbounded findAll calls loading entire tables into memory still needs a senior eye on the repository design.

## Anti-patterns to drop
- Snippets stay unused until the results reappear from a local run.
- Stop skipping the routes row-count reconciliation after each finder change.
- Stop treating the paged driver listing with explicit sort order as optional when the review depends on it.

## Non-coverage
- This lab does not cover framework version numbers; treat those as separate tracks.
- It also skips native SQL dialect specifics, which belong to vendor tracks.
- Left out on purpose: made-up benchmarks, version trivia, and view names borrowed from elsewhere.

## Checkable milestones
- [ ] From memory, rebuild the seed schema on a blank host.
- [ ] Explain the route search combining two criteria in one name to a peer without notes.
- [ ] Trigger method names growing so long nobody dares to change them in staging, and recover using the runbook.
- [ ] Say where derivation ends and framework version numbers begin in a design review.

## How to use this lab
Take the items in order, keep every script rerunnable, and honor the non-coverage boundary above.
