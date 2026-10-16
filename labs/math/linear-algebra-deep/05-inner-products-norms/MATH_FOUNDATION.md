# Inner Products and Norms — Math Foundation

All values computed in exact rational arithmetic (Python `fractions`).

## 1. Gram-Schmidt coefficients

v1 = (1,1,0), v2 = (0,1,1): <v2,u1> = 1, <u1,u1> = 2, ratio 1/2.
u2 = (0,1,1) - (1/2)(1,1,0) = (-1/2,1/2,1).
v3 = (1,0,1): <v3,u1> = 1, ratio 1/2. <v3,u2> = -1/2 + 0 + 1 = 1/2;
|u2|^2 = 1/4+1/4+1 = 3/2, ratio (1/2)/(3/2) = 1/3.
u3 = (1,0,1) - (1/2)(1,1,0) - (1/3)(-1/2,1/2,1)
   = (1 - 1/2 + 1/6, 0 - 1/2 - 1/6, 1 - 1/3) = (2/3,-2/3,2/3).
|u3|^2 = 3*(4/9) = 4/3.

## 2. Orthogonality dots

<u1,u2> = -1/2 + 1/2 + 0 = 0. <u1,u3> = 2/3 - 2/3 + 0 = 0.
<u2,u3> = -1/3 - 1/3 + 2/3 = 0.

## 3. Projection of (1,2,3)

<w,u1> = 3, ratio 3/2. <w,u2> = -1/2 + 1 + 3 = 7/2, ratio (7/2)/(3/2)
= 7/3. Projection = (3/2)(1,1,0) + (7/3)(-1/2,1/2,1)
= (3/2 - 7/6, 3/2 + 7/6, 7/3) = (1/3, 8/3, 7/3).
Residual: (2/3,-2/3,2/3) = u3 direction; dot vs u1: 2/3-2/3 = 0;
vs u2: -1/3-1/3+2/3 = 0.

## 4. Cauchy-Schwarz numbers

<x,y> = 3; |x|^2 = 1+4+9 = 14; |y|^2 = 2; 3^2 = 9 <= 28 = 14*2.
Triangle check: |x+y|^2 = | (2,3,3) |^2 = 22 <= (|x|+|y|)^2.

## 5. Determinant

det with rows (1,1,0),(0,1,1),(1,0,1) = 1*(1-0) - 1*(0-1) + 0 = 2.

## 6. Angle between x and y

cos theta = 3/(sqrt14 sqrt2) = 3/sqrt28. Positive and well below 1,
consistent with 9 <= 28 — the vectors are far from parallel, which is
why the projection (1/3,8/3,7/3) differs markedly from w itself.
Residual norm-squared 4/3 is the leftover.

## 7. Pythagoras ledger

|p|^2 = (1+64+49)/9 = 38/3; |r|^2 = (4+4+4)/9 = 4/3;
38/3 + 4/3 = 42/3 = 14 = 1+4+9 = |w|^2. Closed exactly.
