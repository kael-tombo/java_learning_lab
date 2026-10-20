# Linear Algebra — Flashcards, Run-Backed

Ten cards. Numbers here were printed by captured runs or verified in
exact integer arithmetic before landing on the card.

### Card L1
**Ask**: In elimination, what exactly is a multiplier and what does it never do?
**Say**: m_ij = a_ij / (pivot), applied as row_j ← row_j − m_ij · row_pivot.
The run collected −3/2, −1, 4 for the demo 3x3. A multiplier never
touches the pivot row and never divides by anything but the live pivot.

### Card L2
**Ask**: Why did the (1,1,1)/(2,2,1)/(2,1,2) system stall, and what fixed it?
**Say**: Column 1 left row 2 as (0, 0, −1 | −3) — pivot slot (2,2) was
zero; dividing by it is impossible. The printed fix was
`zero pivot at column 2 -> swap rows 2 and 3`; the answer still came
out exact: (1, 2, 3).

### Card L3
**Ask**: Which product equals det(A), and how was it checked two ways?
**Say**: The product of diagonal pivots: 2 · 1/2 · (−5) = −5, matched
by a row-1 cofactor expansion printing −5 as well. Two independent
bookkeepings agreeing is the point — not one lucky route.

### Card L4
**Ask**: State the transpose law and the sum-swap that proves the trace law.
**Say**: (AB)ᵀ = BᵀAᵀ — verified True on a 2x3/3x2 pair. trace(AB) =
Σᵢ Σₖ aᵢₖbₖᵢ = trace(BA): the double sum's order is swappable. Also
True in the run, though the naive one-index slice of trace(BA) is a
trap (three diagonal entries, not two).

### Card L5
**Ask**: Eigenpair of [[2, 1], [1, 2]], and the two witnesses to trust?
**Say**: λ² − 4λ + 3 = 0 → λ = 1, 3; vectors (1, −1) and (1, 1)
verified with Av = λv exactly ([True, True] twice). λ₁ + λ₂ = 4 =
trace; λ₁λ₂ = 3 = det — the pair is fully determined by those two
summary statistics.

### Card L6
**Ask**: How does 2 ± √2 certify an eigenvector of [[3, 1], [1, 1]]?
**Say**: v = (1, λ − 3) is exact: row 1 gives 3 + λ − 3 = λ, row 2
gives 1 + λ − 3 = λ − 2 = λ(λ − 3) since λ² = 4λ − 2. The run's
residual 0E−23 at 24 decimals is the print, not the proof.

### Card L7
**Ask**: What does det = 0.001 with entries of order 4 announce?
**Say**: Near-singularity. The exact inverse [[4001, −2000],
[−2000, 1000]] satisfies A·A⁻¹ = I (printed True), and κ₁ =
||A||₁·||A⁻¹||₁ = 6001/1000 · 6001 = 36012001/1000 = 36012.001.

### Card L8
**Ask**: How big was the 0.001 perturbation's effect in the run?
**Say**: b₂ from 6.001 to 6.002 (a 0.001 change) moved the solution
from (1, 1) to (−1, 2) — a 2-unit swing; 6.004 pushed it to (−5, 4).
Exact fractions: y = 1000·(b₂ − 6), x = 3 − 2y.

### Card L9
**Ask**: Sensitivity — property of rounding, or of the problem itself?
**Say**: Of the problem. The exact solve is already sensitive; even a
perfect solver inherits the 36012-fold error budget from the
condition number on perturbed inputs. A tiny float residual cannot
certify an answer for an ill-conditioned system.

### Card L10
**Ask**: When can a float residual be trusted as evidence?
**Say**: When the system is well-conditioned and the scaled residual
sits well below the amplification the problem could produce. The
run's exact residual printed `True` three times over — the honest
comparison for ill-conditioned data is exact arithmetic, as this lab
keeps showing.
