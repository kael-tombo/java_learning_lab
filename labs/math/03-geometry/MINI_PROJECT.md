# MINI_PROJECT — Geometry: Shape Toolkit & Area Verifier
> Implement + verify + test. ~3 hours.

## Goal
Build a small Java library computing areas/perimeters/volumes for classic shapes,
a point-in-polygon test, and a collision helper for circles, with property tests.

## Build Steps
1. `Shapes.java`: triangle (Heron), rectangle, circle, trapezoid, sphere/cone/cylinder volumes.
2. `Polygon.java`: shoelace area, centroid, point-in-polygon (ray casting).
3. `Collision.java`: circle-circle, circle-rect (clamp method), point-in-triangle (barycentric).
4. `Epsilon.java`: `approxEquals(a,b,eps)`; use for all float comparisons.
5. Tests: 20 cases, degenerate shapes (zero area) must not throw, only report.

## Sample Run
```
triangle (3,4,5) area = 6.0 ✓ Heron agrees
circle r=5 area ≈ 78.5398
polygon pentagon shoelace = 14.5
point (2,2) in square [0,3]² → true; circle-circle (r1=2,r2=3,d=4) → overlap
```

## Benchmark Table (fill)
| operation | n ops | total ms | per op ns |
|-----------|-------|----------|-----------|
| heron area | 1e6 | | |
| shoelace (20-gon) | 1e6 | | |
| ray-cast point | 1e6 | | |

## Acceptance
- [ ] Shoelace matches Heron decomposition on convex cases.
- [ ] Degenerate input returns 0 area, not exception.
- [ ] Epsilon-based equality used everywhere.

## Extensions
- Add polygon union area via grid sampling.
- Visualize polygons as ASCII.
