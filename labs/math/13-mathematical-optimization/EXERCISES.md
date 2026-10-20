# Exercises — Optimization, Worked

Five problems; each solution's numbers were confirmed by a run.

## Problem 1. Gradient Descent by Hand, Four Steps

For f(x) = x² starting at x₀ = 3 with η = 1/5, compute four iterates
exactly and give the general formula.

**Solution**: x⁺ = x − (1/5)·2x = (3/5)x: the run printed
9/5, 27/25, 81/125 as steps 1–3 from x₀ = 3, so step 4 is
3·(3/5)⁴ = 243/625. In general xₖ = 3·(3/5)ᵏ — the geometric factor
(1 − 2η) = 3/5 is the whole story, since |3/5| < 1 gives convergence
without any extra assumption.

## Problem 2. Convex or Not? Decide by Hessian, Prove by Direction

Classify f = x² + 4xy + y² and exhibit a direction along which the
function dives.

**Solution**: H = [[2, 4], [4, 2]]; leading minors printed 2, −12, so
the Hessian is indefinite — f is NOT convex. Eigenvalues solve
λ² − 4λ − 12 = 0, giving 6 and −2 (the run confirmed H·(1, 1) =
(6, 6) and H·(1, −1) = (−2, 2)). Along the eigen-direction (1, −1):
f(t, −t) = t² − 4t² + t² = −2t² → the surface dives for ANY t ≠ 0
while f(0, 0) = 0, so the midpoint sits strictly above sub-level
values on the segment. The "convex-looking" formula hides a −2
eigenvalue.

## Problem 3. An LP Whose Champion Is the Corner

Maximize 3x + 2y over {x + y ≤ 4, x + 3y ≤ 6, x ≥ 0, y ≥ 0}.

**Solution**: The paired-intersection values printed:
(0, 0) → 0, (4, 0) → 12, (3, 1) → 11, (0, 2) → 4, with vertex
(0, 4) and (6, 0) infeasible — run both cases. Optimum: (4, 0) with
z = 12. Notice the difference from the deep dive (which maximized
2x + 3y and chose (3, 1), z = 9): swapping the objective's weights
moved the champion from the interior vertex to the axis corner.
Enumerating all five vertices is what makes the LP answer immune
to weight-swap surprises.

## Problem 4. Predicting Basins on the Tilted Quartic

For f = x⁴/4 − 2x² + x/4, GD with η = 0.1, predict the basin (left
global at f ≈ −4.5038, right local at f ≈ −3.5040) for starts
−2, 1/2, and 1, using the sign of f' = x³ − 4x + 1/4 at the start.

**Solution**: f'(−2) = −8 + 8 + 1/4 = 1/4 > 0 → x decreases → left
basin (run confirmed: lands at x = −2.0305). f'(1/2) = 1/8 − 2 + 1/4
= −13/8 < 0 → x increases → right basin (run: 1.9680). f'(1) =
−11/4 < 0 → right (run: 1.9680). Sign of the gradient at the start
determines the basin here because the unstable equilibrium (near
x = 0.063) is the only separator: everything below falls left,
everything above falls right.

## Problem 5. Programming: The Critical Step Size From Below

Implement two-scalar GD in exact fractions for f = x² + 10y² from
(5, 1) with η = 1/20 — the exact y-direction stability boundary
(where 1 − 20η = 0) — and print four steps.

**Solution**: The run printed:

```python
from fractions import Fraction as F

print("P5: eta = 1/20 on x^2 + 10*y^2 from (5, 1):")
eta = F(1, 20)
x, y = F(5), F(1)
for k in range(4):
    print("step %d: (x, y) = (%s, %s)" % (k, x, y))
    x, y = x - eta * 2 * x, y - eta * 20 * y
```

Output: steps (5, 1), (9/2, 0), (81/20, 0), (729/200, 0). The y
factor is exactly 0 (1 − 20/20), so y dies in one step and never
wobbles — the boundary case between converging (η < 1/20) and
oscillating (η > 1/20). x keeps marching with factor 9/10.
