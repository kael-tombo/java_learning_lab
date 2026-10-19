# Relational Databases — Vision

## Direction
Grow from first queries toward dependable judgment about relational modeling — keys, references, and normal forms — measured by artifacts rather than hours studied.

## Why it matters here
- Command of data modeling turns on-call database surprises into routine checklist work.
- Concretely: a primary key uniquely identifies each row and never repeats across the table.
- Concretely: a foreign key references a parent primary key and preserves referential integrity.

## Growth path
1. Foundations: reproduce the mini project, beginning with a blank schema.
2. Depth: extend one item (the author-book key diagram with sample rows) until a reviewer asks for simplification.
3. Production: the restore drill gets recorded alongside the real-world milestones.

## Honest assessment
- Strong after this lab: reasoning about key choice, because the uniqueness rule holds even under load.
- Strong after this lab: applying the parent-child reference rule during schema reviews.
- Still fragile: orphaned book rows after an author delete without a referential action remains the most likely incident for beginners.
- Still fragile: duplicate publisher cities drifting out of sync across denormalized rows still needs a senior eye on the design.

## Anti-patterns to drop
- Reproduce a snippet's results before adopting it anywhere.
- Stop skipping the books row-count reconciliation after schema edits.
- Stop treating the 2NF split that removes the partial dependency on book category as optional when the review depends on it.

## Non-coverage
- This lab does not cover physical storage engines and page layouts; treat those as separate tracks.
- It also skips vendor-specific partitioning syntax, which sits outside this scope.
- Not included on purpose: invented benchmarks, version trivia, and borrowed view names.

## Checkable milestones
- [ ] Blank host first, then rebuild the seed schema from memory.
- [ ] Explain the 1NF cleanup of a repeating-group spreadsheet to a peer without notes.
- [ ] Trigger ambiguous natural keys colliding when two authors share one name in staging, and recover using the runbook.
- [ ] Say where this design work ends and physical storage engines and page layouts begin in a review.

## How to use this lab
Follow the items in sequence, keep scripts rerunnable, and respect the non-coverage boundary stated above.
