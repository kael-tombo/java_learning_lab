# Math Foundation: Cross Products and Hull Cost
> Orientation determinant, straddle logic, monotone-chain O(n log n) derivation.

## Definitions
- cross(o, a, b) = (a-o) x (b-o) = (ax-ox)(by-oy) - (ay-oy)(bx-ox).
- Sign: positive = counter-clockwise turn, negative = clockwise, zero = collinear.
- Proper intersection: strict straddling both ways (no touching cases).
- Hull: smallest convex set containing the points; output in boundary order.

## Counting argument
- Orientation: O(1) integer ops per test; exact with 64-bit products.
- Segment test: 4 orientations = O(1); collinear overlap adds bounding-box O(1).
- Monotone chain: sort O(n log n) dominates; the scan is O(n) (each point pushed/popped once).
- Total O(n log n) time, O(n) space for points plus hull.

## Recurrence
- No divide step in Andrew's version: sort once, then two linear passes.
- Stack invariant per chain: last two plus candidate always make a clockwise turn.
- Pop condition cross <= 0 maintains the invariant (strict < keeps collinear points).
- Join drops the doubled endpoints: total vertices plus at most 2 overlap.

## Derivation of the bound
- Sorting lower bound Omega(n log n) applies (hull solves sorting via parabola lifting).
- Scan linearity: 2n pushes max, each pop charged to its push: O(n).
- Exactness: integer cross products decide signs with no rounding error.
- Overflow guard: coordinates bounded so products fit in long (documented cap).

## Worked mini-proofs
- Proof 1: scan linearity by push/pop charging. (3 lines)
- Proof 2: straddle-both-ways equivalent to proper intersection. (4 lines)
- Proof 3: pop rule preserves the clockwise-chain invariant inductively. (4 lines)

## Exercises with answers
- 1. cross((0,0),(1,0),(1,1)). Answer: 1 (CCW).
- 2. Hull of square plus center. Answer: the 4 corners.
- 3. Sort cost share for n = 10000. Answer: dominates; scan is ~2n pushes.

## Pitfalls
- int products overflowing before the long cast (cast operands first).
- Epsilon comparisons on predicates integers decide exactly.
- Collinear inputs handled by accident instead of by the pop-rule choice.

## Checklist
- Derive the chain bound (sort + linear scan) cold.
- Prove scan linearity by push/pop charging.
