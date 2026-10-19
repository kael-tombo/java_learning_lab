# Subqueries — Vision

## Trajectory
Grow from first queries toward dependable judgment about nested queries — scalar, IN and EXISTS, and derived tables — measured by artifacts rather than hours studied.

## Payoff
- Command of these subquery forms turns on-call database surprises into routine checklist work.
- Concretely: a scalar subquery returns one value and fits inside a SELECT or WHERE clause.
- Concretely: EXISTS stops at the first match and ignores NULL comparison pitfalls.

## Milestones
1. Foundations: reproduce the mini project, beginning with a blank schema.
2. Depth: extend one item (the scalar subquery fetching the top course score inline) until a reviewer asks for simplification.
3. Production: real-world milestones delivered, restore drill documented.

## Honest assessment
- Strong after this lab: reasoning about the one-value rule, since a scalar return must fit inside a SELECT or WHERE clause.
- Strong after this lab: applying the early-stop behavior of EXISTS during query reviews.
- Still fragile: NULL poison in NOT IN silently returning zero rows remains the most likely incident for beginners.
- Still fragile: scalar subqueries erroring when more than one row comes back still needs a senior eye on the query design.

## Anti-patterns to drop
- Do not reuse canned snippets until their results have been reproduced locally.
- Stop skipping the results row-count reconciliation after each edit.
- Stop treating the EXISTS check for courses that actually have results as optional when the review depends on it.

## Not covered
- This lab does not cover recursive query hierarchies; treat those as separate tracks.
- It also skips lateral join syntax variants, which sit outside nested queries.
- Left out on purpose: made-up benchmarks, version trivia, and view names borrowed from elsewhere.

## Checkable milestones
- [ ] Blank host first, then rebuild the seed schema from memory.
- [ ] Explain the IN-list filter for results in a chosen course set to a peer without notes.
- [ ] Trigger correlated subqueries re-running once per outer row without an index in staging, and recover using the runbook.
- [ ] Say where nested queries end and recursive query hierarchies begin in a design review.

## Working agreement
Take the items in order, keep every script rerunnable, and honor the non-coverage boundary above.
