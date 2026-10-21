# Linear Transformations — Math Foundation

All values computed in exact rational arithmetic (Python `fractions`).

## 1. Kernel of A = [[1,2,3],[0,1,4]]

Row 2: x2 = -4x3. Row 1: x1 = -2x2 - 3x3 = 8x3 - 3x3 = 5x3.
Basis vector (5,-4,1). Verification:

    A(5,-4,1) = (5 - 8 + 3, -4 + 4) = (0,0).

Nullity 1.

## 2. Image and rank

Columns c1 = (1,0), c2 = (2,1): det [[1,2],[0,1]] = 1*1 - 0 = 1 != 0,
so independent; rank 2, image = R^2. Rank-nullity: 1 + 2 = 3 = dim R^3.

## 3. Change of basis, exhibited

A = [[2,1],[0,3]], P = [[1,1],[1,-1]], det P = -2.
P^{-1} = [[1/2,1/2],[1/2,-1/2]] (check: P^{-1}P = I).
AP = [[2*1+1*1, 2*1-1*1],[0+3, 0-3]] = [[3,1],[3,-3]].
P^{-1}(AP): row 1 = (3+3, 1-3)/2 = (3,-1); row 2 = (3-3, 1+3)/2 = (0,2).
So A_P = [[3,-1],[0,2]]. Trace: 2+3 = 5 = 3+2. Determinant:
2*3-0 = 6; 3*2-0 = 6.

## 4. Composition check

R = rotation-free test pair: B = [[1,1],[0,1]] (shear), A as above.
BA = [[2,4],[0,3]]: apply A then B. Acting on (1,1):
A(1,1) = (3,3), B(3,3) = (6,3); directly BA(1,1) = (2+4, 3) = (6,3).

## 6. Column coordinates in the image basis

T(e1) = (1,0), T(e2) = (2,1), T(e3) = (3,4). In the image basis
{(1,0),(2,1)}: (3,4) = -5(1,0) + 4(2,1), since -5+8 = 3 and 4 = 4.
Every output column is accounted for — the image really is spanned by
the first two columns.

## 5. Inverse of P and spectrum of A_P

P^{-1}P = [[1/2+1/2, 1/2-1/2],[1/2-1/2, 1/2+1/2]] = I.
A_P = [[3,-1],[0,2]]: triangular, eigenvalues 3 and 2 — the same
{2,3} as A = [[2,1],[0,3]]. Eigenvectors: A_P(1,0) = (3,0);
A_P(1,1) = (3-1, 2) = (2,2) = 2(1,1).
