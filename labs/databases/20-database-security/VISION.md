# Database Security — Vision

## Trajectory
Grow from first queries toward dependable judgment about grant discipline and traceable access, measured by artifacts rather than hours studied.

## Payoff
- Command of these controls turns on-call database surprises into routine checklist work.
- Concretely: least privilege grants each role only the access it needs.
- Concretely: masking hides sensitive columns from roles that must not see them.

## Milestones
1. Foundations: start from a blank schema and reproduce the mini project.
2. Depth: extend one item (the role matrix separating reader, writer, and admin grants) until a reviewer asks for simplification.
3. Production: a recorded restore drill travels with the real-world milestones.

## Honest assessment
- Strong after this lab: reasoning about access boundaries, since every role's reach is spelled out.
- Strong after this lab: applying column masking during analyst access reviews.
- Still fragile: over-broad grants exposing patient data to every analyst remains the most likely incident for beginners.
- Still fragile: unmasked exports leaking sensitive columns into files still needs a senior eye on the export design.

## Anti-patterns to drop
- Snippets stay unused until the results reappear from a local run.
- Stop skipping the access_log row-count reconciliation after each grant change.
- Stop treating the masking sketch hiding diagnosis codes from analysts as optional when the review depends on it.

## Not covered
- This lab does not cover CVE numbers and vendor advisories; treat those as separate tracks.
- It also skips product-specific vault integrations, which belong to platform tracks.
- Not included on purpose: invented benchmarks, version trivia, and borrowed view names.

## Checkable milestones
- [ ] Rebuild the seed schema on a blank host from memory.
- [ ] Explain the revoke drill removing one over-broad patient grant to a peer without notes.
- [ ] Trigger missing audit rows leaving a breach unexplainable in staging, and recover using the runbook.
- [ ] Say where role design ends and CVE numbers and vendor advisories begin in a design review.

## Working agreement
The items run in order, scripts remain rerunnable, and the non-coverage boundary above holds.
