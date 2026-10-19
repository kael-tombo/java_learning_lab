# SQL Basics — Vision

## Where this points
Grow from first queries toward dependable judgment about everyday SELECT work — filtering, sorting, and paging — measured by artifacts rather than hours studied.

## Capabilities gained
- Command of these statements turns on-call database surprises into routine checklist work.
- Concretely: WHERE filters rows before any grouping or ordering takes place.
- Concretely: ORDER BY controls presentation order and accepts several sort keys.

## Sequence
1. Foundations: from a blank schema, reproduce the mini project.
2. Depth: extend one item (the member roster filtered by status and city) until a reviewer asks for simplification.
3. Production: a recorded restore drill travels with the real-world milestones.

## Honest assessment
- Strong after this lab: reasoning about WHERE clauses, since a filter runs before any grouping or ordering.
- Strong after this lab: applying the sort-key rule — ORDER BY controls presentation order — during reviews.
- Still fragile: missing rows because NULL comparisons silently filter everything out remains the most likely incident for beginners.
- Still fragile: unstable paging when the ORDER BY key contains duplicate values still needs a senior eye on the query design.

## Anti-patterns to drop
- Reproduce a snippet's results before adopting it anywhere.
- Stop skipping the loans row-count reconciliation after each query edit.
- Stop treating the paged directory query with OFFSET plus FETCH FIRST as optional when the review depends on it.

## Out of scope
- This lab does not cover window analytics and recursive queries; treat those as separate tracks.
- It also skips procedural extensions and trigger logic, which sit outside basic query work.
- Left out on purpose: made-up benchmarks, version trivia, and view names borrowed from elsewhere.

## Checkable milestones
- [ ] Blank host first, then rebuild the seed schema from memory.
- [ ] Explain the loan list sorted by due date descending to a peer without notes.
- [ ] Trigger runaway full-table scans from leading-wildcard LIKE patterns in staging, and recover using the runbook.
- [ ] Say where these fundamentals end and window analytics and recursive queries begin in a design review.

## Study guidance
Work through the items in sequence with rerunnable scripts, and stop where the non-coverage boundary above says.
