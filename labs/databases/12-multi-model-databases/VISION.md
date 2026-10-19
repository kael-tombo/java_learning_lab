# Multi-Model Databases — Vision

## Where this points
Grow from first queries toward dependable judgment about which store serves which shape of data, measured by artifacts rather than hours studied.

## Capabilities gained
- Command of model selection turns on-call database surprises into routine checklist work.
- Concretely: relational stores fit ledger-like catalog facts with strict integrity.
- Concretely: document stores fit variable review payloads with evolving fields.

## Sequence
1. Foundations: reproduce the mini project, beginning with a blank schema.
2. Depth: extend one item (catalog facts modeled relationally with keys) until a reviewer asks for simplification.
3. Production: a recorded restore drill travels with the real-world milestones.

## Honest assessment
- Strong after this lab: reasoning about workload-to-model fit, because ledger facts and evolving payloads each have a home.
- Strong after this lab: applying the fit rules when reviewing new feature data.
- Still fragile: one model stretched to serve every workload badly remains the most likely incident for beginners.
- Still fragile: cross-model reads with no defined consistency story still needs a senior eye on the design.

## Anti-patterns to drop
- Do not reuse canned snippets until their results have been reproduced locally.
- Stop skipping the reviews row-count reconciliation after each change.
- Stop treating session state assigned to a key-value sketch as optional when the review depends on it.

## Out of scope
- This lab does not cover product version numbers; treat those as separate tracks.
- It also skips managed-service pricing claims, which belong to procurement discussions.
- Left out on purpose: made-up benchmarks, version trivia, and view names borrowed from elsewhere.

## Checkable milestones
- [ ] From memory, rebuild the seed schema on a blank host.
- [ ] Explain review payloads modeled as flexible documents to a peer without notes.
- [ ] Trigger dual writes diverging with no reconciliation job in staging, and recover using the runbook.
- [ ] Say where polyglot persistence ends and product version numbers begin in a design review.

## Study guidance
Work through the items in sequence with rerunnable scripts, and stop where the non-coverage boundary above says.
