# Common Mistakes — Optimization

Errors below cite the exact run values from this lab that refute or
demonstrate them.

## 1. Fixed-Rate Steps That Overshoot or Orbit

On x² the update factor is (1 − 2η). At η = 1 and above there is no
decay at all: the run printed the closed orbit 5 → −5 → 5 → −5 for
η = 1 and divergence −11/2 → 121/20 → −1331/200 for η = 21/20.
"More progress per step" is false comfort: η = 1/2 feels twice as
aggressive as the safe η = 1/5 yet merely annihilates in one step
(factor 0), and η = 1 already loses all decay (factor −1) — because
x²'s curvature is uniform and its stability bound is exact.

## 2. Judging Convexity From Plot Shape

A formula's positive-looking terms bury negative curvature:
x² + 6xy + y² hides the pair of eigenvalues (8, −4) — computed as
λ² − 4λ − 32 = 0 in the run — and factors as (x + 3y)² − 8y². A
plot rotated to look like a bowl cannot reveal that crossing
channels exist along (1, −1); the minors 2, −32 (printed) are the
law, not the eyeball.

## 3. Trusting the Landed Point Instead of the Landscape

Quartic starts 1/5 and 3 stabilized at f = −3.5040, and that IS an
excellent-looking endpoint — yet the left basin holds −4.5038.
Declaring "descent converged to the minimum" for the right-basin
starts confuses a local claim with the global one; only basin
bookkeeping (two minima, boundary near x ≈ 0.063) licenses the
word global.

## 4. Assuming Gradient Zero Means a Halt That Announces Success

On the untilted quartic x⁴/4 − 2x², f'(0) = 0 with f(1) = −7/4
below f(0) = 0: zero gradient at a maximum is still zero gradient.
Any implementation relying only on |f'| < tol without a curvature
or basin check will happily report victory at a saddle point —
precisely what the tilted quartic's split start-run demonstrates
from the other side.

## 5. Finding an LP Optimum Without Enumerating the Vertices

Feasible pairs from the run: (3, 1) → z = 9, (4, 0) → z = 8 for
max 2x + 3y. A projection heuristic that prefers the larger first
coordinate would answer (4, 0) and lose to (3, 1); swapping the
objective (max 3x + 2y) flips the champion to (4, 0) with z = 12
against (3, 1)'s 11. Only the full vertex census, including both
infeasible intersections (0, 4) and (6, 0), is weight-proof.

## 6. Reading Oscillation as Progress or as Failure

At η = 9/100 on x² + 10y², the y chain prints
1 → −4/5 → 16/25 → −64/125 → 256/625: alternating signs, each |y|
multiplied by exactly 4/5 — solid convergence, and the zigzag is
the first three printed terms' reason to distrust a "the iterate
obviously hit the minimum" reading. Conversely η = 3/40 flips the
factor to −1/2: oscillation persists EVERY step (sign flips never
stop), so a "still bouncing, so bump the rate up" reflex would
push η past the 1/20 stability edge where the run's divergence
begins.

## 7. Newton on a Nonconvex Quadratic, Handed a Saddle as Victory

For f = x² + 4xy + y² the Hessian is [[2, 4], [4, 2]] with minors
2, −12 — indefinite. Newton's step x⁺ = x − H⁻¹∇f lands at the
origin in ONE step from anywhere (from (2, 2): ∇f = (12, 12) and
H⁻¹∇f = (2, 2)), and f(0, 0) = 0 beats f(2, 2) = 4 + 16 + 4 = 24 —
so the run-of-thumb "f went down, therefore minimum" is wrong: the
origin is a saddle (along (1, −1) the form f(t, −t) = −2t² dives),
and the true infimum is −∞. Stationary-point bookkeeping must
precede any Newton claim on nonconvex targets.
