# Advanced SQL — Vision

## Direction
Grow from first queries toward dependable judgment about report shapes and set logic, measured by artifacts rather than hours studied.

## Why it matters here
- Command of these constructs turns on-call database surprises into routine checklist work.
- Concretely: ROLLUP adds subtotal and grand-total rows to grouped output.
- Concretely: pivoting turns row values into columns for cross-tab reports.

## Growth path
1. Foundations: rebuild the mini project starting from an empty schema.
2. Depth: extend one item (the ROLLUP report subtotaling conversions by channel and month) until a reviewer asks for simplification.
3. Production: complete the real-world milestones with a restore drill on the record.

## Honest assessment
- Strong after this lab: reasoning about subtotal placement, because ROLLUP marks the summary rows explicitly.
- Strong after this lab: applying the dedupe-versus-keep rule when reviewing set operations.
- Still fragile: misread subtotal rows mistaken for real channels remains the most likely incident for beginners.
- Still fragile: UNION silently dropping rows the report needed twice still needs a senior eye on the set design.

## Anti-patterns to drop
- Every canned snippet gets its results reproduced before reuse.
- Stop skipping the conversions row-count reconciliation after each report change.
- Stop treating the UNION versus UNION ALL comparison on duplicated conversions as optional when the review depends on it.

## Non-coverage
- This lab does not cover procedural extensions; treat those as separate tracks.
- It also skips engine-specific pivot syntax, which varies by dialect.
- The deliberate omissions: invented benchmarks, version trivia, and view names not our own.

## Checkable milestones
- [ ] From memory, rebuild the seed schema on a blank host.
- [ ] Explain the pivot sketch turning channels into columns to a peer without notes.
- [ ] Trigger pivot columns drifting whenever a new channel appears in staging, and recover using the runbook.
- [ ] Say where report SQL ends and procedural extensions begin in a design review.

## How to use this lab
Take the items in order, keep every script rerunnable, and honor the non-coverage boundary above.
