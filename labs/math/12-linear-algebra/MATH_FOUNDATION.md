# Linear Algebra — Math Foundation

All figures come from captured runs of the two CODE_DEEP_DIVE
programs; the fractions were also re-multiplied by hand.

## 1. Elimination on the Demo 3x3, in Exact Fractions

System: 2x + y − z = 8, −3x − y + 3z = −11, −2x + y + 2z = −3 (the
augmented rows shown in the run). Multipliers printed: −3/2, −1, 4.
Row 2 − (−3/2)·row 1 leaves (0, 1/2, 3/2 | 1); row 3 − (−1)·row 1
leaves (0, 2, 1 | 5); row 3 − 4·row 2 leaves (0, 0, −5 | 1).
Back-substitution: z = 1/(−5) = −1/5, y = (1 − 3z/2)·2 = 13/5,
x = (8 − y + z)/2 = 13/5. The residual triples printed
`[True, True, True]`: putting (13/5, 13/5, −1/5) back through A
reproduces b exactly. Placement rules to remember: the multiplier
is a_ij/a_pivot always, it never shrinks the pivot row, and the
arithmetic ran entirely in `Fraction` so nothing rounded mid-elimination.

## 2. Pivot Product, Cofactor Expansion, det Laws

The diagonal pivots 2, 1/2, −5 multiply to 2 · 1/2 · (−5) = −5, and
the row-1 cofactor expansion also printed −5 — the same value by two
routes (expanding row 1 by hand: 2·[(−1)·2 − 3·1] − 1·[(−3)·2 −
3·(−2)] + (−1)·[(−3)·1 − (−1)·(−2)] = 2·(−5) − 0 − (−5)). On 2x2
matrices C = [[3, 1], [1, 1]], D = [[2, 0], [1, 2]] the run checked
det(C)·det(D) = 2·4 = 8 = det(CD). Also det(Aᵀ) = det(A): the
expansion formula is symmetric in the indices, so transposition just
reorders cofactors while preserving signs.

## 3. Transpose and Trace Laws, from the Entry Bookkeeping

(AB)ᵀ = BᵀAᵀ: entry (i, j) of AB is Σₖ aᵢₖbₖⱼ, so the (i, j) entry of (AB)ᵀ is
Σₖ aₖᵢbⱼₖ — row i of Aᵀ times column j of Bᵀ, which is precisely
(BᵀAᵀ)ᵢⱼ. The run verified it on A = [[1, 2, 3], [0, −1, 4]]
against B = [[2, 1], [1, 3], [−1, 1]]. For trace:
(AB)ᵢᵢ = Σₖ aᵢₖbₖᵢ, hence trace(AB) = ΣᵢΣₖ aᵢₖbₖᵢ = ΣₖΣᵢ bₖᵢaᵢₖ =
trace(BA): the double sum only needed its order swapped. The
comparison printed True for (AB)ᵀ == BᵀAᵀ and True for the trace law.

## 4. Two Eigenproblems by Hand

A₂ = [[2, 1], [1, 2]]: det(A₂ − λI) = (2−λ)² − 1 = λ² − 4λ + 3 =
(λ−1)(λ−3). For λ = 1 the null pair (1, −1) works: A₂(1, −1) =
(1, −1) printed equal to 1·v with `equal: [True, True]`; for λ = 3
the vector (1, 1) gives (3, 3) = 3·v. Sum check: λ₁ + λ₂ = 4 =
trace, product λ₁λ₂ = 3 = det. Matrix C = [[3, 1], [1, 1]]
has λ² − 4λ + 2 = 0 with irrational roots λ = 2 ± √2, printed at 24
decimals (0.58578643762690495119831 and 3.41421356237309504880169);
its exact eigenvector for λ = 2 ± √2 is (1, λ − 3) = (1, −1 ∓ √2),
and the run validated A·v − λv = 0E−23 — exact to the 24-digit
contract. Same sums: trace 4, det 2, since λ₁λ₂ = (2−√2)(2+√2) = 4 − 2.

## 5. Near-Singular Magnification, Exact

A₃ = [[1, 2], [2, 4.001]] has det = 0.001 = 1/1000 while its entries
run to 4 — small determinant relative to scale. Its exact inverse is
[[4001, −2000], [−2000, 1000]] (scaling the adjugate by 1000), and
the program multiplied the two and compared against the identity:
True. Solving Ax = b for the three RHS rows printed solutions
(1, 1), (−1, 2), (−5, 4) as b₂ went 6.001 → 6.002 → 6.004: a 0.001
nudge moved x by 2 units, a 0.003 nudge by 6 units. The magnification
is ||A₃||₁·||A₃⁻¹||₁ = (6001/1000)·6001 = 36012001/1000 =
κ₁ = 36012.001: worst-case input error δ is amplified up to κ₁·δ
in the output. Nothing here is floating-point noise — the exact solve
itself is genuinely this sensitive to the input, which is why a
clean-looking float residual can no longer certify an answer.
