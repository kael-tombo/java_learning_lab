# Vision: Computational Geometry
> Exact integer predicates: orientation, intersection, hulls - no floating point required.

## Where this leads
- Hull computation, segment intersection, and point-in-polygon tests.
- Robustness thinking: exact predicates instead of epsilon comparisons.
- Sweep-line ideas that build on the ordering used in hull algorithms.
## What mastering it unlocks
- Evaluate the cross-product orientation test and interpret its sign.
- Test proper segment intersection from four orientation signs.
- Run Andrew's monotone chain and justify the pop condition.
- Explain why integer arithmetic with long products is exact here.
- Handle collinear and degenerate inputs without crashing or looping.
## What it does not cover
- 3D geometry, rotations, and spatial transforms.
- Robust geometric libraries and exact arithmetic beyond 64-bit products.
- Graphics pipelines, triangulation, and mesh processing.
## Core questions you will answer
- Why does the sign of the cross product decide clockwise vs counter-clockwise?
- Why do both straddle conditions matter for proper intersection?
- Why pop on non-clockwise turns, and what do collinear edge points do?
- At what coordinate magnitude do int products overflow, and what is the fix?
## How to judge progress
- Hand-evaluate orientations and intersections on new point sets.
- Implement monotone chain that handles collinear points deliberately.
- Name the overflow bound and the cast that prevents it.
## Common misuse
- Using doubles and epsilon for predicates that integers decide exactly.
- Ignoring collinear cases, which then fail on axis-aligned test data.
## After this lab
- 33-matrix-algorithms for the linear-algebra side of coordinates.
- 09-divide-and-conquer for closest-pair style divide-and-conquer geometry.
One-line self-test: Explain the pop rule of monotone chain using the orientation sign.
