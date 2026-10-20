# Exercises — Linear Algebra, Worked

Five problems; solutions carry numbers extracted from exact runs.

## Problem 1. Elimination That Demands a Row Swap

Solve x + y + z = 6, 2x + 2y + z = 9, 2x + y + 2z = 10 in exact
fractions; note where naive elimination breaks.

**Solution**: After row 2 − 2·row 1 the tableau read
(0, 0, −1 | −3), (0, −1, 0 | −2): entry (2,2) is zero, so the next
multiplier would divide by nothing. The run printed
`zero pivot at column 2 -> swap rows 2 and 3`, leaving
[[1, 1, 1 | 6], [0, −1, 0 | −2], [0, 0, −1 | −3]]. Backwards:
z = 3, y = 2, x = 1 — the exact solution (1, 2, 3) printed as
Fractions 1, 2, 3. Partial pivoting (swap for a nonzero pivot) is
not decoration; without it the algorithm here simply stops.

## Problem 2. Fresh Transpose Check

Given A = [[1, 2], [3, 4]], B = [[0, 1], [1, 0]], compute AB, (AB)ᵀ
and BᵀAᵀ and reconcile.

**Solution**: The run printed AB = [[2, 1], [4, 3]], (AB)ᵀ =
[[2, 4], [1, 3]], BᵀAᵀ = [[2, 4], [1, 3]], `equal: True`. Bᵀ = B here
(the swap matrix is its own inverse), which turns the check into
B·Aᵀ = (AB)ᵀ — a one-line special case of the general law.

## Problem 3. An Integer Eigenpair, Closed-Form

Find the eigenvalues and eigenvectors of [[4, 1], [1, 4]] and verify
exactly.

**Solution**: det(A − λI) = (4−λ)² − 1 = λ² − 8λ + 15 = (λ−3)(λ−5).
The program verified A·(1, −1) = (3, −3) = 3·(1, −1) and A·(1, 1) =
(5, 5) = 5·(1, 1) with `True` on all four coordinate comparisons and
det 15 = λ₁λ₂, trace 8 = λ₁ + λ₂. Rule of thumb: symmetric matrices
like this admit orthogonal eigenvector bases — here the two vectors
have dot product 1·1 + (−1)·1 = 0.

## Problem 4. Trace and Determinant, Not the Same Report

Using [[2, 1], [1, 2]] (eigenvalues 1, 3) state what trace and
determinant each report, then invert the question: given only
trace 4 and det 2, name the matrix's eigenvalues.

**Solution**: trace(λI) pattern: the trace is the SUM λ₁ + λ₂ and the
determinant the PRODUCT λ₁λ₂ — adding them would report 4 but
multiplying 3; they are distinct statistics. Given trace 4 with
det 2, λ satisfies λ² − 4λ + 2 = 0, so λ = 2 ± √2 — precisely the
irrational pair the deep-dive run certified to 24 digits. The
quadratic is reconstructable from the two witnesses alone.

## Problem 5. Programming: Magnification Table for a Near-Singular 2x2

Implement a 2x2 exact solver, apply it to A = [[1, 2], [2, 4001/1000]]
with right-hand sides (3, 6.001), (3, 6.002), (3, 6.004), and print
how far the solution travels per unit change in b₂.

**Solution**: The exact runs printed (1, 1), (−1, 2), (−5, 4):
x moves −2 per +0.001 of b₂ and −4 per +0.002. General form follows
from the run's algebra: y = 1000·(b₂ − 6), x = 3 − 2y, since the
elimination reduces to 0.001·y = b₂ − 6. With the demonstrated
condition number κ₁ = ||A||₁·||A⁻¹||₁ = (6001/1000)·6001 =
36012001/1000 = 36012.001 and the verified identity
A·[[4001, −2000], [−2000, 1000]] = I, the lesson stands: sensitivity
is a property of the exact problem, not of rounding — even an
ungodly-accurate float solve inherits a 36000-fold error budget.
