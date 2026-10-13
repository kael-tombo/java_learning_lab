# Real-World Project: Hull Plotter and Segment Checker
> Convex hulls from point CSVs plus exact segment-intersection queries.

## Problem
Field teams submit surveyed points; the tool returns the boundary polygon.
Fence-line plans need exact crossing tests between proposed segments.
## Inputs
- points.csv with integer x,y rows; queries.csv with segment pairs.
- Fixtures: square with interior points, collinear set, triangle with duplicate.
- Output: hull vertices in order plus per-query CROSS/DISJOINT verdicts.
## Steps
1. Parse points as integers (exact arithmetic, no floats anywhere).
2. Sort by x then y and run Andrew's monotone chain with the pop rule.
3. Emit hull vertices starting from the lowest-leftmost point.
4. Answer each segment query with the four-orientation proper-intersection test.
5. Render the hull as ASCII art on a normalized grid for visual checking.
6. Verify hull convexity by checking uniform turn signs on the output.
## Acceptance criteria
- Square-plus-interior fixture returns exactly the 4 corners in order.
- Collinear fixture returns exactly the 2 endpoints.
- Crossing query returns CROSS and disjoint collinear query returns DISJOINT.
- Convexity check passes on all hull outputs including duplicates fixture.
- 10000-point random fixture (fixed seed) finishes in under 5 seconds.
## Failure modes
- Duplicate points are removed once with a reported count.
- Single-point and two-point inputs return them directly with a note.
- Coordinates beyond 1e6 are rejected to keep int products overflow-safe.
## Extensions
- Shoelace area of the hull printed alongside vertices.
- Point-in-polygon query mode using the same orientation predicate.
## How to demo
- Show the ASCII hull of the square fixture next to the vertex list.
- Walk one pop decision of the chain on the triangle fixture by hand.
