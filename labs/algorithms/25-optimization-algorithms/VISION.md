# Vision: Optimization Algorithms

## Direction

This lab covers continuous optimization at concept level: gradient descent as
stepping against the slope, ternary-style bracketing for unimodal functions,
and the vertex geometry of small linear programs. The practical skill is
running each method by hand on a toy function and stating its cost and its
failure mode.

## What to learn

- Gradient descent: update rule, step-size tradeoff, linear convergence idea.
- Unimodal bracketing: how two interior points shrink the search interval.
- LP vertex geometry: optima of bounded LPs sit at feasible vertices.
- Cost statements: per-iteration work and what drives iteration count.
- Failure modes: overshoot, local valleys, unbounded or infeasible LPs.

## Non-coverage

- This lab does not cover simplex tableaux or interior-point methods.
- It does not cover duality theory; that belongs to the LP lab.
- It does not cover stochastic gradients, momentum, or adaptive steps.
- It does not cover constrained nonlinear programming or Lagrange theory.
- All functions here are one- or two-dimensional teaching examples.

## How to use this lab

Run the descent from MOCK_INTERVIEW Q1 with three step sizes and record
which diverges, bracket the quadratic from Q2 starting at two widths, then
verify the LP vertices of Q3 by solving the line intersections yourself.

## Pitfalls

- Tuning the function instead of the step size when descent diverges.
- Bracketing a multimodal function and trusting the valley found.
- Reporting an LP optimum without checking vertex feasibility.

## Done when

- You can write the gradient update from memory and explain the step role.
- You can state the 2/3 shrink factor of ternary bracketing.
- You can list LP vertices from constraints and score them by hand.
- You can name one failure mode per method with a concrete trigger.
