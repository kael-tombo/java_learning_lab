# Real-World Project: Production Mix Planner

## Problem

A workshop makes two products with per-unit profit and shared machine-hour
caps. Management wants the profit-maximizing mix with a certificate. Build a
planner that enumerates vertices and pairs the answer with a dual bound.

## Inputs

- `program.txt`: objective line plus at most 4 constraint lines, e.g.
  `max 2x + 3y`, `x + 2y <= 8`, `3x + y <= 9`, `x >= 0`, `y >= 0`.
- Coefficients are plain decimals; strict inequalities are rejected.

## Steps

1. Parse the objective and constraints; reject malformed lines by number.
2. Compute all pairwise boundary intersections for the 2 variables.
3. Keep intersections satisfying every constraint within 1e-9.
4. Score each feasible vertex; recommend the best with its value.
5. Construct the dual program and exhibit one feasible dual point.
6. Show the dual value equals the recommended primal value (gap zero).
7. Detect empty vertex sets (infeasible) and improving rays (unbounded).
8. Emit `mix.txt` with vertices, recommendation, dual point, and gap.

## Acceptance criteria

1. Reference program (max 2x+3y, x+2y<=8, 3x+y<=9) recommends x=2.0, y=3.0 value 13.0.
2. Every listed vertex satisfies all constraints within tolerance.
3. Dual point feasible with value equal to the recommendation.
4. Infeasible fixture reports INFEASIBLE with no recommendation.
5. Unbounded fixture reports UNBOUNDED with no recommendation.
6. Malformed lines exit with a message naming the line number.
7. All output uses plain ASCII characters.

## Constraints

- Plain Java only, no external libraries; 2 variables only.
- Tolerance 1e-9 documented in the file header comment.
- No simplex code required; enumeration plus duality is the method.
