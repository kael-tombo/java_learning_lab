# Mathematical Optimization — Math Foundation

Figures below come from captured runs of the three CODE_DEEP_DIVE
programs; every fraction was verified in exact arithmetic.

## 1. The One-Dimensional Update Is a Geometric Series

For f(x) = x², descent gives x⁺ = x − η·2x = (1 − 2η)x, from x₀ = 5.
Printed six-step chains:

  η = 1/5:  5 → 3 → 9/5 → 27/25 → 81/125 → 243/625     (ratio 3/5)
  η = 2/5:  5 → 1 → 1/5 → 1/25 → 1/125 → 1/625        (ratio 1/5)
  η = 11/20: 5 → −1/2 → 1/20 → −1/200 → 1/2000 → −1/20000  (ratio −1/10)
  η = 1:    5 → −5 → 5 → −5 → 5 → −5                  (ratio −1, a closed orbit)
  η = 21/20: 5 → −11/2 → 121/20 → −1331/200 → ...      (ratio −11/10, diverging)

The factor (1 − 2η) summarizes convergence (0 < 1−2η < 1), overshoot
oscillation (−1 < 1−2η < 0), eternal bouncing (−1), and divergence
(1−2η < −1); the useful exact boundary for x² is η = 1/2, not
something seen — it is computed from the factor's absolute value.

## 2. Two Curvatures Pull One Step Apart

f(x, y) = x² + 10y² from (5, 1): direction factors are (1 − 2η) for x
and (1 − 20η) for y. At η = 9/100: x shrinks with factor 41/50
(chain 5 → 41/10 → 1681/500 → ...) while y bounces with factor −4/5
(chain 1 → −4/5 → 16/25 → −64/125 → 256/625 → −1024/3125 → ...):
alternating ±4/5 multiples of the seed are the zigzag on records.
At η = 3/40, x slows to factor 17/20 (5 → 17/4 → 289/80 → ...) and y
bounces at −1/2 (1 → −1/2 → 1/4 → −1/8 → ...). A single scalar η
cannot shrink both curvature directions at once unless it respects
the fast direction's stability bound η < 1/20 here.

## 3. Convexity Is a Hessian Question, Not a Shape One

Leading minors of each Hessian on the run (a₁₁ first, then det):

  x² + y²:      minors 2, 4    → positive definite → convex
  x² − y²:      minors 2, −4   → indefinite → not convex (saddle)
  xy:           minors 0, −1   → indefinite → not convex
  x² + 6xy + y²: minors 2, −32  → indefinite → not convex
  x² + 4y²:     minors 2, 16   → positive definite → convex

The fourth case is the trap: (x + 3y)² − 8y² expands to exactly
x² + 6xy + y², so purely positive-looking quadratic terms hide the
−4 eigenvalue (λ² − 4λ − 32 = 0 gives 8 and −4). A 3-D plot can
never do this bookkeeping; the minors and eigenvalues can.

## 4. An LP Solved by Enumerating Its Vertices

Maximize 2x + 3y over {x + y ≤ 4, x + 3y ≤ 6, x ≥ 0, y ≥ 0}.
Pairwise line intersections printed: (3, 1) feasible with z = 9;
(0, 4) infeasible; (4, 0) feasible with z = 8; (0, 2) feasible with
z = 6; (6, 0) infeasible; (0, 0) feasible (and duplicated once when
the x = 0 / y = 0 pair was re-derived). Optimum: (3, 1) with z = 9 —
the interior vertex beats the axis-adjacent corner (4, 0) by
converting one unit of the second resource into more value than the
first. The LP fundamental theorem needed no solver: five
intersections, two infeasible, three feasible, evaluate, take the
max.

## 5. Local Versus Global on a Tilted Quartic

f(x) = x⁴/4 − 2x² + x/4 has f' = x³ − 4x + 1/4; the exact critical
values straddle the symmetric quartic's: f(−2) = −9/2 but f(2) = −7/2,
so tiles the +x/4 term: the left basin is lower. Two minima exist.
Descent with η = 0.1 in floating point (exact first step from x₀ = −1
printed as x₁ = −53/40) landed:

  starts −3, −1, 0  →  x = −2.0305, f = −4.5038 (global)
  starts 1/5, 3     →  x =  1.9680, f = −3.5040 (a local min)

The basin boundary sits where the unstable equilibrium of the
gradient flow lies, near x ≈ 0.063 — starts from 0 fall left, starts
from 1/5 fall right, and the two answers differ by 1.0 units of f.
This is local-versus-global in the wild: the optimizer is faithful
to the basin it sits in, not to the global claim.
