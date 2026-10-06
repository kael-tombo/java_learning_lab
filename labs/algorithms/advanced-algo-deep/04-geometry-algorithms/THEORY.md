# Theory — Computational Geometry

Geometric algorithms replace approximate reasoning with exact predicates.
Almost every algorithm in this lab reduces to one primitive: the sign of an
orientation predicate. Get that primitive right, and convex hull, line
intersection, and point-in-polygon follow mechanically.

## Orientation from the cross product

For points A, B, C, the cross product of the vectors AB and AC is

```
cross(B-A, C-A) = (B.x - A.x)(C.y - A.y) - (B.y - A.y)(C.x - A.x)
```

Its sign classifies the turn at B on the way A→B→C: positive = counter-
clockwise, negative = clockwise, zero = collinear. This is the *only*
arithmetic primitive you need for hulls and intersection tests, and it is
exact in integer arithmetic — no trig, no slopes, no division.

## Convex hull by monotone chain (Andrew, 1979)

Sort the points by (x, y). Build the lower hull left-to-right: repeatedly
remove the last point while the last three make a non-left turn, then append.
Build the upper hull right-to-left the same way. Concatenate. The result is
the hull in counter-clockwise order, with collinear edge points removable by
flipping the `<= 0` test to `< 0`. Sorting costs Θ(n log n); the two scans
are Θ(n) because each point is pushed and popped at most once.

## Robustness of the orientation predicate

With integer coordinates up to 10⁹, `(B.x-A.x)·(C.y-A.y)` is up to (2·10⁹)²,
which overflows 32-bit but fits in 64-bit. Use `long` for the products. In
floating point, the predicate is unreliable near collinearity; the standard
cure is an *exact* predicate (long arithmetic, or a filtered exact kernel).
Decide the degenerate rule up front: strict `< 0` keeps collinear points on
the hull boundary; `<= 0` drops them.

## Line-segment intersection

Two segments AB and CD intersect iff the orientations `orient(A,B,C)` and
`orient(A,B,D)` have opposite signs **and** `orient(C,D,A)` and
`orient(C,D,B)` have opposite signs. The strict inequality gives a proper
crossing; the inclusive version also counts touching endpoints and collinear
overlaps. Encode the rule once and reuse it everywhere — this is the same
orientation primitive.

## Point in polygon: ray casting

Cast a ray from the query point to +∞ in x and count how many polygon edges
it crosses; the point is inside iff the count is odd. Each edge crossing is
decided by an inclusive-x-range and a sign test on orientation — again the
same primitive. Edge cases: the ray through a vertex counts twice unless you
use the standard half-open y-interval rule (`(yi > y) != (yj > y)`), which
counts it once. With the half-open rule, the count is exact.

## Closest pair, divide and conquer

Sort points by x once. Recurse on the two halves, let δ be the smaller of
the two half-solutions. Build the vertical strip of width 2δ around the
midline, sort its points by y, and for each point test only the next 7 in
y-order — a packing argument shows at most 7 can lie in the relevant δ×2δ
rectangle. Total work is Θ(n log n) by the Master theorem
(`T(n) = 2T(n/2) + Θ(n)`).

## Degenerate-case policy

Every geometric routine needs an explicit policy for: duplicate points (dedup
before sorting), all points collinear (hull is a segment — decide whether
that is an error), vertical/horizontal segments (the orientation rule handles
them if you avoid slopes), and zero-area input. Pick the rule and enforce it
in one place.

## Pitfalls

- Computing slopes (`(y2-y1)/(x2-x1)`) divides by zero on vertical segments
  and loses exactness in floating point — use the cross product instead.
- Forgetting the `<= 0` vs `< 0` collinearity choice changes the hull by the
  boundary points; document which you use.
- Ray casting on a vertex must use the half-open y-interval rule or every
  vertex crossing is double-counted.
- 32-bit intermediate overflow in the orientation product — use long.
