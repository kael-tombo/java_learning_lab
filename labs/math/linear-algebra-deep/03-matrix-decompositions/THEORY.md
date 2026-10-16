# Matrix Decompositions — Theory

## 1. LU without pivoting

If all leading principal minors of A are nonzero, A = LU with L unit
lower-triangular and U upper-triangular, uniquely. det A is then the
product of U's diagonal. Running example:

    A = [[2,1,1],[4,3,3],[8,7,9]], L = [[1,0,0],[2,1,0],[4,3,1]],
    U = [[2,1,1],[0,1,1],[0,0,2]], det A = 2*1*2 = 4.

Elimination multipliers are L's subdiagonal: 4/2 = 2, 8/2 = 4, then
3/1 = 3. Zero pivots or row swaps break this form — that is what
partial pivoting (PA = LU) repairs.

## 2. QR

Every real m x n matrix with independent columns factors as A = QR:
Q has orthonormal columns, R is upper-triangular with positive
diagonal. Example on a1 = (1,1,0), a2 = (0,1,1):

    e1 = (1/sqrt2, 1/sqrt2, 0),
    u2 = a2 - (a2.e1)e1 = (-1/2, 1/2, 1), |u2|^2 = 3/2,
    R = [[sqrt2, 1/sqrt2],[0, sqrt(3/2)]].

R's diagonal entries are the successive residual norms.

## 3. SVD

Every real m x n matrix factors as A = U Sigma V^T with U, V
orthogonal and Sigma diagonal holding singular values
s1 >= s2 >= ... >= 0 (square roots of eigenvalues of A^T A).
Example: A = [[3,0],[4,0]] has A^T A = [[25,0],[0,0]], so singular
values 5 and 0, u1 = (3/5,4/5), v1 = (1,0): A v1 = (3,4) = 5 u1.
Rank equals the number of nonzero singular values — here 1.

## 4. Shapes and existence

- LU (with pivoting): always exists for square A; no-pivot form needs
  nonzero leading minors.
- QR: always exists (Gram-Schmidt); Q is m x m (full) or m x n (thin).
- SVD: always exists for any shape; U is m x m, Sigma m x n, V n x n.
