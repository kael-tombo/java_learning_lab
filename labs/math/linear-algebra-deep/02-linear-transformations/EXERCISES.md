# Linear Transformations — Exercises

## 1. Kernel

Q: Find ker of T(x) = (x1+2x2+3x3, x2+4x3).
A: x2 = -4t, x1 = 5t. ker = span{(5,-4,1)}, nullity 1.
Check: 5+2(-4)+3 = 0; -4+4 = 0.

## 2. Rank-nullity

Q: State the rank and verify rank-nullity for the same T.
A: Columns (1,0),(2,1) independent (minor 1), rank 2, image R^2.
1 + 2 = 3 = dim(domain).

## 3. Matrix of a map

Q: T: R^2 -> R^2 fixes (1,0) and sends (0,1) to (1,1). Matrix?
A: Columns are images of e1,e2: [[1,1],[0,1]]. T(2,3) = (5,3).

## 4. Composition

Q: With A = [[2,1],[0,3]], B = [[1,1],[0,1]], compute BA and BA(1,1).
A: BA = [[2,4],[0,3]]. BA(1,1) = (6,3), matching B(A(1,1)) = B(3,3).

## 5. Change of basis

Q: For A = [[2,1],[0,3]] in basis {(1,1),(1,-1)}, find the matrix.
A: P^{-1}AP = [[3,-1],[0,2]] (Section 3 of MATH_FOUNDATION).
Trace 5, det 6 preserved.

## 6. Kernel or not

Q: Can a linear T: R^3 -> R^2 be injective?
A: No: nullity = 3 - rank >= 3 - 2 = 1, so ker always holds a nonzero
vector; e.g. (5,-4,1) above.

## 7. Spectrum under similarity

Q: Eigenvalues and eigenvectors of A_P = [[3,-1],[0,2]]?
A: Triangular: 3 and 2. A_P(1,0) = (3,0); A_P(1,1) = (2,2) = 2(1,1).
Same spectrum as A — similarity preserves eigenvalues.

## 8. Invertibility of P

Q: Verify P^{-1} for P = [[1,1],[1,-1]].
A: [[1/2,1/2],[1/2,-1/2]] times P: (1,0) row-wise — (1/2+1/2,
1/2-1/2) = (1,0); second row (0,1). det P = -2 != 0.
