# Eigenvalues Advanced

Micro-lab on characteristic polynomials, diagonalization, the symmetric
spectral theorem, and one defective matrix showing the limits.

## Contents

- THEORY.md: eigenvalue definition, worked polynomial t^2-7t+10 with
  eigenvalues 5 and 2, diagonalization criterion, spectral theorem on
  [[2,1],[1,2]], defective J = [[2,1],[0,2]].
- MATH_FOUNDATION.md: eigenspace bases, A^2 trace 29 two ways,
  Cayley-Hamilton product giving the zero matrix entry by entry.
- CODE_DEEP_DIVE.md: fractions checks of both eigenpairs, A^2, and
  the Cayley-Hamilton zero.
- EXERCISES.md: six problems with computed solutions.
- FLASHCARDS.md: twelve recall cards.

## How to use

Multiply out A(1,1) and A(1,-2) by hand before reading further; the
whole lab hangs on those two products.

## Worked anchors (all values executed)

- p(t) = t^2-7t+10; eigenvalues 5 (vector (1,1)) and 2 (vector (1,-2)).
- Diagonalizer det -3; A^2 trace 29; A^3 trace 133 = 125+8.
- Spectral: [[2,1],[1,2]] = Q diag(3,1) Q^T, orthonormal columns.
- Defective: [[2,1],[0,2]] has only one eigenvector direction.
- Cayley-Hamilton product is the zero matrix entry by entry.

## Study sequence

1. Multiply A(1,1) and A(1,-2) by hand; factor t^2-7t+10.
2. Build P, compute its det -3, and confirm diagonalizability.
3. Verify A^2's trace 29 both ways; extend to A^3's 133.
4. Contrast with J = [[2,1],[0,2]]: one eigenvector direction only.
5. Do EXERCISES.md 1-9; cards 6 and 13 test the power traces.

## Notes

- det A = 10 reads off p(0); det(A-I) = 4 reads off p(1).
- Geometric never exceeds algebraic multiplicity; J shows 1 < 2.
