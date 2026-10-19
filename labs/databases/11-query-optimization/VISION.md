# Query Optimization B — Vision

## Direction
Grow from first queries toward dependable judgment about the optimizer's plans, measured by artifacts rather than hours studied.

## Why it matters here
- Command of plan reading turns on-call database surprises into routine checklist work.
- Concretely: EXPLAIN shows the optimizer's chosen access path before execution.
- Concretely: nested-loop joins suit selective lookups while hash joins suit bulk matches.

## Growth path
1. Foundations: start from a blank schema and reproduce the mini project.
2. Depth: extend one item (the EXPLAIN read of a shipment lookup identifying the access path) until a reviewer asks for simplification.
3. Production: deliver the real-world milestones and keep a restore drill on file.

## Honest assessment
- Strong after this lab: reasoning about access-path previews, since the chosen plan is visible before execution.
- Strong after this lab: applying the join-selection heuristic during plan reviews.
- Still fragile: misread plans blamed on the wrong operator remains the most likely incident for beginners.
- Still fragile: wrong composite order leaving the second column unusable still needs a senior eye on the index design.

## Anti-patterns to drop
- Snippets stay unused until the results reappear from a local run.
- Stop skipping the stops row-count reconciliation after each index change.
- Stop treating the composite index ordered by depot then departure time as optional when the review depends on it.

## Non-coverage
- This lab does not cover invented timing benchmarks on shipment queries; treat those as separate tracks.
- It also skips optimizer source-code internals, which sit below the plan output.
- Skipping by design: benchmarks that were invented, version trivia, and reused view names.

## Checkable milestones
- [ ] Blank host first, then rebuild the seed schema from memory.
- [ ] Explain the nested-loop versus hash-join comparison on stop matching to a peer without notes.
- [ ] Trigger sort spills when ORDER BY columns miss the supporting index in staging, and recover using the runbook.
- [ ] Say where plan reading ends and invented timing benchmarks on shipment queries begin in a design review.

## How to use this lab
Work through the items in sequence with rerunnable scripts, and stop where the non-coverage boundary above says.
