# Math Foundation — Geometry Algorithms

Derivations, applicability, and counter-examples for the formulas this lab relies on.

---

## Orientation as signed area

Twice the signed area of triangle ABC is the determinant | B.x-A.x  C.x-A.x ; B.y-A.y  C.y-A.y | = cross(B-A, C-A). Its sign matches the handedness of A→B→C.

Zero area ⟺ collinear; the sign is a complete orientation predicate.

## Closest-pair packing bound

In the strip, two points closer than δ in x must lie within δ of the midline; in y they can differ by at most δ. A δ×2δ rectangle can hold at most 8 points pairwise ≥ δ apart (one per quadrant sub-square of side δ/2).

Hence each point needs to check only a constant number of y-neighbours — the merge is Θ(n).

## Closest-pair Master theorem

T(n) = 2T(n/2) + Θ(n) (split + merge) = Θ(n log n) by case 2 of the Master theorem.

A naive merge that rescans all points is Θ(n²) — the y-sorted 7-neighbour bound is what makes the merge linear.

## Ray casting parity

Each crossing of the polygon boundary toggles inside/outside. Starting outside, inside ⟺ odd number of crossings.

A ray through a vertex toggles twice unless the half-open rule counts it once — that is why the rule is needed for correctness.

## Monotone-chain correctness sketch

After processing, the lower chain is the lower convex boundary: every popped point lies below or on the segment joining its neighbours, so it is not needed for the convex boundary.

Each point is pushed and popped at most once, so the scan is Θ(n).
