# Database Migration Strategies — Vision

## Where this points
Grow from first queries toward dependable judgment about staging schema changes behind live traffic, measured by artifacts rather than hours studied.

## Capabilities gained
- Command of staged migration turns on-call database surprises into routine checklist work.
- Concretely: expand-contract adds the new shape before removing the old one.
- Concretely: dual writes keep old and new columns consistent mid-migration.

## Sequence
1. Foundations: rebuild the mini project starting from an empty schema.
2. Depth: extend one item (the expand step adding the new profile column safely) until a reviewer asks for simplification.
3. Production: the real-world milestones go out once a restore drill is recorded.

## Honest assessment
- Strong after this lab: reasoning about safe sequencing, since old readers keep working while new columns appear.
- Strong after this lab: applying the dual-write rule during transition reviews.
- Still fragile: big-bang alters locking profiles during peak traffic remains the most likely incident for beginners.
- Still fragile: old code crashing on a column dropped too early still needs a senior eye on the cutover design.

## Anti-patterns to drop
- Every canned snippet gets its results reproduced before reuse.
- Stop skipping the profile_history row-count reconciliation after each stage.
- Stop treating the batched backfill plan for existing profile rows as optional when the review depends on it.

## Out of scope
- This lab does not cover vendor-specific online DDL flags; treat those as separate tracks.
- It also skips managed-service migration products, which belong to platform tracks.
- Skipping by design: benchmarks that were invented, version trivia, and reused view names.

## Checkable milestones
- [ ] Rebuild the seed schema, working from memory, on a blank host.
- [ ] Explain the dual-write sketch covering the transition window to a peer without notes.
- [ ] Trigger unbounded backfills saturating the primary in staging, and recover using the runbook.
- [ ] Say where staged migration ends and vendor-specific online DDL flags begin in a design review.

## Study guidance
The items run in order, scripts remain rerunnable, and the non-coverage boundary above holds.
