# Reinforcement Learning — Mini Project

**Goal**: a tiny deterministic grid-world solver with assertions, built entirely on the
JDK, no third-party libraries.

## World spec

- 3x3 grid; start `(0,0)`; two terminal cells: goal `(2,2)` with entry reward `+1`, and a
  penalty cell `(1,2)` with entry reward `-1`.
- Actions: up, down, left, right; bumping a wall leaves the agent in place.
- `gamma` configurable, default `0.9`.

## Required components

1. `record Transition(int s2, int reward)` — deterministic dynamics, encoded as a 9x4
   table built at startup.
2. `ValueIteration.solve(...)` running the optimality sweeps until the max change is
   under `1e-9`; also print how many sweeps that took.
3. `Policy.extract(...)` — greedy extraction with ties broken by action order
   (up, down, left, right).
4. A `main` that prints the value table rows, the extracted policy arrows (`^ v < >`),
   and then **asserts** three hand-derived facts: `V(goal)=0`, the two-step start value
   equals `gamma^2 * 1.0` under a reward-on-entry convention, and no non-terminal state
   has value above 1.0.

## Deliverables

- One source file, compiles with `javac --release 21`.
- A captured stdout log committed next to the source in your notes (not into git).
- A short README paragraph stating the reward convention (reward on entering a cell) so
  the numbers are interpretable.

## Stretch

Add slippery transitions: with probability 0.1 each action moves perpendicular to the
intended direction. The solver needs the full `sum_{s'}` expectation form of the Bellman
sweep; verify that the goal-adjacent state values drop accordingly.
