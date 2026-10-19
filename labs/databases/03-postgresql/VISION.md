# PostgreSQL — Vision

## Where this points
Grow from first queries toward dependable judgment about schema layout, column typing, and transactional DDL, measured by artifacts rather than hours studied.

## Capabilities gained
- Command of these habits turns on-call database surprises into routine checklist work.
- Concretely: schemas namespace tables so tenants and shared objects stay separated.
- Concretely: PostgreSQL data types include serial-style identity, text, numeric, and timestamps.

## Sequence
1. Foundations: from a blank schema, reproduce the mini project.
2. Depth: extend one item (the tenant schema layout separating shared and private tables) until a reviewer asks for simplification.
3. Production: real-world milestones delivered, restore drill documented.

## Honest assessment
- Strong after this lab: reasoning about namespace boundaries, because the separation rules are explicit.
- Strong after this lab: applying the type checklist — identity, text, numeric, timestamps — during schema reviews.
- Still fragile: objects landing in the wrong schema when search-path surprises writers remains the most likely incident for beginners.
- Still fragile: money rounding drift from choosing floating point over numeric still needs a senior eye on the design.

## Anti-patterns to drop
- Snippets stay unused until the results reappear from a local run.
- Stop skipping the invoices row-count reconciliation after each migration.
- Stop treating the timestamp discipline for time-zone storage as optional when the review depends on it.

## Out of scope
- This lab does not cover version-specific extension catalogs; treat those as separate tracks.
- It also skips replication slot administration, which belongs to operations tracks.
- The deliberate omissions: invented benchmarks, version trivia, and view names not our own.

## Checkable milestones
- [ ] From memory, rebuild the seed schema on a blank host.
- [ ] Explain the invoice table with identity key and numeric totals to a peer without notes.
- [ ] Trigger half-applied migrations from DDL issued outside one transaction in staging, and recover using the runbook.
- [ ] Say where this scope ends and version-specific extension catalogs begin in a design review.

## Study guidance
Follow the items in sequence, keep scripts rerunnable, and respect the non-coverage boundary stated above.
