# Joins — Vision

## Trajectory
Grow from first queries toward dependable judgment about join selection — inner, outer, and lateral — measured by artifacts rather than hours studied.

## Payoff
- Command of these join types turns on-call database surprises into routine checklist work.
- Concretely: an INNER JOIN keeps only rows with a match on both sides.
- Concretely: a LEFT JOIN keeps every left row and fills gaps with NULLs.

## Milestones
1. Foundations: start from a blank schema and reproduce the mini project.
2. Depth: extend one item (the team roster via INNER JOIN on team id) until a reviewer asks for simplification.
3. Production: real-world milestones delivered, restore drill documented.

## Honest assessment
- Strong after this lab: reasoning about which join keeps which rows, since the matching rules are now explicit.
- Strong after this lab: applying the left-join fill rule during query reviews.
- Still fragile: row multiplication when the join key is not unique on one side remains the most likely incident for beginners.
- Still fragile: vanishing teams after an INNER JOIN drops unmatched parents still needs a senior eye on the query design.

## Anti-patterns to drop
- Snippets stay unused until the results reappear from a local run.
- Stop skipping the players row-count reconciliation after query edits.
- Stop treating the FULL JOIN reconciliation of two independently kept lists as optional when the review depends on it.

## Not covered
- This lab does not cover distributed join execution strategies; treat those as separate tracks.
- It also skips graph traversal query languages, which sit outside relational joins.
- Not included on purpose: invented benchmarks, version trivia, and borrowed view names.

## Checkable milestones
- [ ] From memory, rebuild the seed schema on a blank host.
- [ ] Explain the bench report via LEFT JOIN exposing players without teams to a peer without notes.
- [ ] Trigger lateral lookups degrading when the inner query ignores its index in staging, and recover using the runbook.
- [ ] Say where relational joins end and distributed join execution strategies begin in a design review.

## Working agreement
Items go in order, scripts stay rerunnable, and the non-coverage boundary above is not crossed.
