# Matrix Decompositions — Math Foundation

All values computed in exact rational arithmetic (Python `fractions`).

## 1. LU product check

A = [[2,1,1],[4,3,3],[8,7,9]], L = [[1,0,0],[2,1,0],[4,3,1]],
U = [[2,1,1],[0,1,1],[0,0,2]].

Row by row: row 1 of LU = row 1 of U = (2,1,1). Row 2 =
2*(2,1,1) + (0,1,1) = (4,3,3). Row 3 = 4*(2,1,1) + 3*(0,1,1) +
(0,0,2) = (8,7,9). LU = A exactly. det = 2*1*2 = 4.

## 2. QR numbers

a1 = (1,1,0), a2 = (0,1,1). |a1|^2 = 2, so R_11 = sqrt2 and
e1 = (1/sqrt2,1/sqrt2,0). a2.e1 = 1/sqrt2, so R_12 = 1/sqrt2 and
u2 = (0,1,1) - (1/2)(1,1,0) = (-1/2,1/2,1). |u2|^2 = 1/4+1/4+1 = 3/2,
R_22 = sqrt(3/2). Orthogonality: u2.e1 = (-1+1)/(2 sqrt2) = 0.

## 3. SVD numbers

A = [[3,0],[4,0]]. A^T A = [[25,0],[0,0]] (entry (1,1): 9+16 = 25).
Eigenvalues 25, 0; singular values 5, 0. A(1,0) = (3,4) = 5*(3/5,4/5),
so u1 = (3/5,4/5) with |(3/5,4/5)|^2 = 9/25+16/25 = 1. Rank 1.

## 4. Determinant cross-check

det A from LU is 4. Direct expansion: 2*(27-21) - 1*(36-24) +
1*(28-24) = 12 - 12 + 4 = 4. Agreement.

## 6. QR column-norm ledger

|a1|^2 = 2 = R_11^2 = (sqrt2)^2. |a2|^2 = 0+1+1 = 2, and
R_12^2 + R_22^2 = 1/2 + 3/2 = 2. QR preserves column norms through
the triangular factor — the e1 unit check 1/2+1/2 = 1 underwrites
every entry of R.

## 5. Forward and back substitution

Solve Ax = (3,7,18). Ly = b: y1 = 3; 2*3 + y2 = 7 gives y2 = 1;
4*3 + 3*1 + y3 = 18 gives y3 = 3. Ux = y: 2x3 = 3, x3 = 3/2;
x2 + 3/2 = 1, x2 = -1/2; 2x1 - 1/2 + 3/2 = 3, x1 = 1.
Direct check: row 1: 2 - 1/2 + 3/2 = 3; row 2: 4 - 3/2 + 9/2 = 7;
row 3: 8 - 7/2 + 27/2 = 18.
