# Matrix Decompositions

Micro-lab on LU, QR, and SVD: existence, shapes, and one fully checked
numeric instance of each.

## Contents

- THEORY.md: no-pivot LU conditions, QR via Gram-Schmidt, SVD from
  A^T A, shape table for all three.
- MATH_FOUNDATION.md: LU product verified row by row with det 4 both
  ways, QR residual norm-squared 3/2, SVD singular values 5 and 0
  with A v1 = 5 u1.
- CODE_DEEP_DIVE.md: fractions snippets for the LU product, the
  orthogonality dot (0), and the A^T A entries.
- EXERCISES.md: six problems with computed solutions, including an
  LU solve giving x = (1,-1/2,3/2).
- FLASHCARDS.md: twelve recall cards.

## How to use

Recompute the LU rows by hand; they are small enough to check in under
a minute, and everything else builds on the same arithmetic.

## Worked anchors (all values executed)

- LU: L=[[1,0,0],[2,1,0],[4,3,1]], U=[[2,1,1],[0,1,1],[0,0,2]].
- det = 4 both from the U diagonal and from 12-12+4.
- QR: R = [[sqrt2,1/sqrt2],[0,sqrt(3/2)]]; residual norm-squared 3/2.
- SVD of [[3,0],[4,0]]: singular values 5, 0; A(1,0) = 5*(3/5,4/5).
- Solve: Ax=(3,7,18) gives x=(1,-1/2,3/2) via y=(3,1,3).

## Study sequence

1. Reproduce the LU product rows by hand; confirm det 4 both ways.
2. Run snippet 1; then solve Ly = b on paper for y = (3,1,3).
3. Derive u2 = (-1/2,1/2,1) yourself; check the dot is 0 in code.
4. Compute A^T A for [[3,0],[4,0]] and read off singular values 5, 0.
5. Do EXERCISES.md 1-7; attempt the no-pivot failure case last.

## Notes

- Multipliers live below L's diagonal: 2, 4, 3 — elimination recorded.
- Thin QR of a 3x2 is Q 3x2 with R 2x2; full SVD of 2x2 is all 2x2.
