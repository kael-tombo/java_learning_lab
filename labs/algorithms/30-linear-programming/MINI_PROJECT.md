# Mini-Project: Diet Mix Solver

## Goal

Solve a 2-food least-cost diet program by vertex enumeration and verify the
answer against a hand-drawn feasible polygon.

## Inputs

- Minimize 2x + 3y (cost) subject to x + y >= 4, x + 2y >= 6, x >= 0, y >= 0.
- Rewrite as max -2x - 3y for the enumeration routine from this lab.

## Steps

1. Convert the two nutrition constraints to <= form by negating.
2. List the boundary lines: -x-y=-4, -x-2y=-6, -x=0, -y=0.
3. Compute pairwise intersections; keep the feasible ones.
4. Score each with cost 2x + 3y (equivalently -2x - 3y maximized).
5. Identify the cheapest feasible vertex with its cost.
6. Verify by checking cost against the two neighboring vertices.
7. Print vertices, costs, winner, and the two-neighbor comparison.
8. Sketch the polygon on paper and confirm the winner is a corner.

## Acceptance criteria

1. Winner reported as x=2.0, y=2.0 with cost 10.0.
2. Neighbor vertices (0,4) cost 12 and (6,0) cost 12 both shown higher.
3. Every listed vertex satisfies both nutrition constraints.
4. Conversion to <= form shown in code comments.
5. Two-neighbor comparison printed with all three costs.
6. No vertex with lower cost omitted from the listing.
7. All output uses plain ASCII characters.

## Grading note

- Winner x=2.0, y=2.0 with cost 10.0 required.
- Both neighbors shown higher at cost 12 each.
- Conversion of >= to <= form visible in code comments.

## Stretch

- Add constraint x <= 3 and re-run; state the new winner.
- Price y at 5 instead of 3 and report which vertex wins now.
