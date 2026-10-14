# Vision: Linear Programming

## Direction

This lab covers linear programming at concept level: vertex geometry of
optima, the simplex idea of walking improving vertices, weak duality as a
certificate, and the three solver statuses. The practical skill is solving a
2-variable program by hand and certifying it with a dual point.

## What to learn

- Vertex geometry: bounded optima sit at feasible corners.
- Simplex concept: move along improving edges until no improvement exists.
- Weak duality: feasible dual values bound the primal optimum from above.
- Statuses: optimal, infeasible, and unbounded with detection rules.
- Formulation: objective plus linear constraints from a word problem.

## Non-coverage

- This lab does not implement the simplex tableau or pivot selection.
- It does not cover strong duality proofs or complementary slackness.
- It does not cover interior-point methods or integer programming.
- It does not cover sensitivity analysis or parametric programming.
- No invented pivot traces appear here; programs are 2-variable only.

## How to use this lab

Solve the Q1 program graphically on paper, certify the Q2 pair by checking
both feasibility statements, then classify three programs of your own with
the Q3 status routine before starting MINI_PROJECT.

## Pitfalls

- Scoring only axis vertices and missing the slanted intersection.
- Claiming optimal without a dual bound to back it.
- Confusing unbounded (ray improves forever) with infeasible (empty set).

## Done when

- You can list and score all vertices of a 2-constraint program by hand.
- You can write the dual of a 2-variable max program from memory.
- You can classify any 2-variable program into the three statuses.
- You can explain the simplex walk in two sentences without a tableau.
