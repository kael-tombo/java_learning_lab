# Linear Transformations — Theory

## 1. Definition

T: V -> W is linear iff T(au + bv) = aT(u) + bT(v) for all scalars
a,b and vectors u,v. Equivalently: T preserves addition and scalar
multiplication. Every linear T: R^n -> R^m is multiplication by a
unique m x n matrix A, whose j-th column is T(e_j).

## 2. Running example

T(x1,x2,x3) = (x1 + 2x2 + 3x3, x2 + 4x3), matrix

    A = [[1,2,3],[0,1,4]].

## 3. Kernel and image

- ker T = {x : Ax = 0}. Here x2 + 4x3 = 0 and x1 + 2x2 + 3x3 = 0
  give x2 = -4t, x1 = 5t: ker T = span{(5,-4,1)}, nullity 1.
- im T = column space of A. Columns (1,0) and (2,1) are independent
  (2x2 determinant 1), so im T = R^2, rank 2.

## 4. Rank-nullity

For T: V -> W with V finite-dimensional:
dim ker T + dim im T = dim V. Here 1 + 2 = 3.

## 5. Composition and matrix product

(S compose T)(x) = S(T(x)); matrices multiply: [S compose T] = [S][T].
Dimensions must chain: (m x k)(k x n) = m x n.

## 6. Change of basis and similarity

If P is the change-of-basis matrix (columns = new basis in old
coordinates), the same operator reads A_P = P^{-1} A P.
Example: A = [[2,1],[0,3]], P = [[1,1],[1,-1]]. Then
P^{-1} = [[1/2,1/2],[1/2,-1/2]] and

    A_P = [[3,-1],[0,2]].

Trace 5 and determinant 6 are unchanged (tr 2+3 = 3+2; det 6 = 6),
as the theorem promises: similar matrices share trace, determinant,
characteristic polynomial, and eigenvalues.

## 7. Eigenvalue preview

A_P = [[3,-1],[0,2]] is upper-triangular, so its eigenvalues read off
the diagonal: 3 with eigenvector (1,0) (A_P(1,0) = (3,0)), and 2 with
eigenvector (1,1) (A_P(1,1) = (2,2)). Same spectrum {2,3} as A —
similarity preserves eigenvalues, as claimed.
