# Matrix Decompositions — Exercises

## 1. LU multipliers

Q: Factor A = [[2,1,1],[4,3,3],[8,7,9]] as LU.
A: Pivot 2: multipliers 2 and 4. Remaining pivot 1: multiplier 3.
L = [[1,0,0],[2,1,0],[4,3,1]], U = [[2,1,1],[0,1,1],[0,0,2]].
det = 4, confirmed by expansion 12-12+4.

## 2. Solve with LU

Q: Solve Ax = (3,7,18) using the factors.
A: Ly = b: y1 = 3, y2 = 7-6 = 1, y3 = 18-12-3 = 3. Ux = y:
2x3 = 3 so x3 = 3/2; x2 = 1-3/2 = -1/2; x1 = (3+1/2-3/2)/2 = 1.
Check row 1: 2-1/2+3/2 = 3.

## 3. QR

Q: QR of columns (1,1,0),(0,1,1) (thin form).
A: e1 = (1/sqrt2,1/sqrt2,0); u2 = (-1/2,1/2,1), e2 = u2/sqrt(3/2);
R = [[sqrt2,1/sqrt2],[0,sqrt(3/2)]].

## 4. SVD

Q: Singular values and vectors of [[3,0],[4,0]]?
A: A^T A = [[25,0],[0,0]]; singular values 5, 0; v1 = (1,0),
u1 = (3/5,4/5); rank 1.

## 5. Shapes

Q: Shapes in the SVD of a 5x3 rank-2 matrix?
A: U 5x5, Sigma 5x3 (diagonal 3x3 block with s1,s2,0), V 3x3.

## 6. When LU fails

Q: Give a matrix with no no-pivot LU and its fix.
A: [[0,1],[1,0]]: zero pivot. Swap rows first: PA = LU with
P = [[0,1],[1,0]], L = I, U = [[1,0],[0,1]].

## 7. Verify an LU solve

Q: Check x = (1,-1/2,3/2) against Ax = (3,7,18).
A: Row 1: 2-1/2+3/2 = 3. Row 2: 4-3/2+9/2 = 7. Row 3: 8-7/2+27/2
= 18. Exact.
