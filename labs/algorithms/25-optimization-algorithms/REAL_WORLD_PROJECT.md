# Real-World Project: Budget Allocation Helper

## Problem

A team splits a fixed budget between two channels with linear returns and
linear caps (spend limits, headcount limits). Build a helper that enumerates
the feasible vertices and recommends the allocation with the best return.

## Inputs

- `program.txt`: objective coefficients and constraints, one per line, e.g.
  `max 3x + 2y`, `x + y <= 4`, `2x + y <= 6`, `x >= 0`, `y >= 0`.
- All coefficients are plain decimals; at most 4 constraints.

## Steps

1. Parse the objective and each constraint; reject malformed lines.
2. Compute all pairwise intersections of the constraint boundary lines.
3. Keep points satisfying every constraint (with 1e-9 tolerance).
4. Score each feasible vertex with the objective function.
5. Detect infeasibility (no feasible vertex) and report it plainly.
6. Detect unboundedness by checking whether the feasible set is open along
   an improving direction; report it instead of a fake optimum.
7. Emit `allocation.txt` with vertices, scores, and the recommendation.
8. Write a two-paragraph note stating the chosen mix and its return.

## Acceptance criteria

1. Reference program recommends x=2.0, y=2.0 with value 10.0.
2. Every listed vertex satisfies all constraints within tolerance.
3. Infeasible fixture reports infeasible with no recommended point.
4. Unbounded fixture reports unbounded with no recommended point.
5. Scores recomputed by the checker match the emitted scores.
6. Malformed input lines exit with a message naming the line.
7. All output uses plain ASCII characters.

## Constraints

- Plain Java only, no external libraries; 2 variables only.
- Tolerance 1e-9 documented in the file header comment.
- No simplex implementation required; enumeration is the method.
