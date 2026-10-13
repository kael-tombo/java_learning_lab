# Mini Project: Hull in a Script
> Monotone-chain hull with ASCII rendering and convexity self-check.

## Background
- Sort by x, build lower then upper hull, popping non-clockwise turns.
- Integer cross products keep every predicate exact.
- The ASCII plot makes wrong hulls visible instantly.
## Goal
Implement the chain, render ASCII art, and self-check convexity.
Verify square, collinear, and triangle-with-interior fixtures.
## Tasks
1. Parse integer points with duplicate removal and counts.
2. Sort by x then y and run the lower/upper chain with the pop rule.
3. Render hull plus interior points as ASCII art on a normalized grid.
4. Check uniform turn signs over the hull as a convexity assertion.
5. Verify square fixture yields exactly 4 corners in order.
6. Verify collinear fixture yields exactly 2 endpoints.
## Acceptance criteria
- Square fixture returns 4 ordered corners.
- Collinear fixture returns 2 endpoints.
- Convexity assertion passes on all fixtures.
- ASCII art matches the vertex list on the square fixture.
- Duplicate counts are reported and excluded from the hull.
## Pitfalls
- Double arithmetic with epsilon instead of exact integer signs.
- Popping on the wrong inequality and keeping collinear edge points by accident.
- Forgetting to drop the doubled endpoints when joining chains.
- Overflow from int cross products on large coordinates (use long).
## Stretch
- Segment-intersection query mode with the four-sign test.
- Shoelace area printed under the hull.
## Timebox
One evening session, roughly 2 hours with rendering.
