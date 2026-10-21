# Dual Spaces and Tensors — Math Foundation

All values computed in exact rational arithmetic (Python `fractions`).

## 1. Dual basis verification

e1 = (1,1), e2 = (1,-1). phi1(x,y) = (x+y)/2, phi2(x,y) = (x-y)/2.
phi1(e1) = 2/2 = 1; phi1(e2) = 0/2 = 0.
phi2(e1) = 0/2 = 0; phi2(e2) = 2/2 = 1. Duality table is the identity.
Expansion: (x,y) = phi1(x,y) e1 + phi2(x,y) e2. Check x = 1: LHS x;
RHS (x+y)/2 + (x-y)/2 = x. Check y: (x+y)/2 - (x-y)/2 = y.

## 2. Functional expansion

f(x,y) = 3x - y: f(e1) = 2, f(e2) = 4, so f = 2 phi1 + 4 phi2.
Test at (5,1): LHS 15-1 = 14; RHS 2*3 + 4*2 = 14.

## 3. Kronecker product

(1,2) (x) (3,-1) = (1*3, 1*(-1), 2*3, 2*(-1)) = (3,-1,6,-2).

## 4. Mixed product, exhibited

Au = (1+2, 2) = (3,2). Bv = (6, 3-1) = (6,2).
(Au) (x) (Bv) = (18, 6, 12, 4).
Direct: A (x) B = [[2,0,2,0],[1,1,1,1],[0,0,2,0],[0,0,1,1]]; times
w = (3,-1,6,-2): row 1: 6+0+12+0 = 18; row 2: 3-1+6-2 = 6;
row 3: 0+0+12+0 = 12; row 4: 0+0+6-2 = 4. Agreement: (18,6,12,4).

## 5. Rank-one matrix

[[3,-1],[6,-2]]: det = -6 + 6 = 0, nonzero matrix, so rank 1.

## 6. Annihilator basis check

z(x,y) = (x-y)/2 vanishes on W = span{(1,1)}: z(1,1) = 0/2 = 0.
z is not the zero functional: z(1,-1) = 2/2 = 1. A nonzero functional
killed on a 1-dim subspace of R^2 spans the 1-dim annihilator:
dim W^0 = 2-1 = 1.

## 7. Outer-product columns

u v^T = [[3,-1],[6,-2]] has columns (3,6) = 3(1,2) and (-1,-2) =
-1(1,2): every column is a multiple of u. Column space = span{u},
one-dimensional — rank 1 seen directly, no determinant needed.
