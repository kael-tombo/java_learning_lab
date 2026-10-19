# Flyway and Liquibase — Vision

## Where this points
Grow from first queries toward dependable judgment about version-controlled schema changes, measured by artifacts rather than hours studied.

## Capabilities gained
- Command of these tools turns on-call database surprises into routine checklist work.
- Concretely: migrations apply in version order and record checksums after success.
- Concretely: repeatable migrations re-run when their checksum changes.

## Sequence
1. Foundations: reproduce the mini project, beginning with a blank schema.
2. Depth: extend one item (the V1 migration creating the ledger table) until a reviewer asks for simplification.
3. Production: a recorded restore drill travels with the real-world milestones.

## Honest assessment
- Strong after this lab: reasoning about deterministic apply order, since checksums and versions make it auditable.
- Strong after this lab: applying the repeatable-migration rule during release reviews.
- Still fragile: checksum mismatches after editing an already-applied migration remains the most likely incident for beginners.
- Still fragile: out-of-order migrations applied by two branches simultaneously still needs a senior eye on the design.

## Anti-patterns to drop
- Do not reuse canned snippets until their results have been reproduced locally.
- Stop skipping the entries row-count reconciliation after each migration.
- Stop treating the repeatable view migration for a balance summary as optional when the review depends on it.

## Out of scope
- This lab does not cover tool version numbers; treat those as separate tracks.
- It also skips cloud-managed migration services, which belong to platform tracks.
- Deliberately omitted: invented benchmarks, version trivia, borrowed view names.

## Checkable milestones
- [ ] Rebuild the seed schema, working from memory, on a blank host.
- [ ] Explain the V2 migration adding the entry foreign key to a peer without notes.
- [ ] Trigger missing rollback path discovered during a failed deploy in staging, and recover using the runbook.
- [ ] Say where migration practice ends and tool version numbers begin in a design review.

## Study guidance
Take the items in order, keep every script rerunnable, and honor the non-coverage boundary above.
