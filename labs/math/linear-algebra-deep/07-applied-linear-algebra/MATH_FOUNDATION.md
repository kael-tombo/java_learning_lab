# Applied Linear Algebra — Math Foundation

All values computed in exact rational arithmetic (Python `fractions`).

## 1. Normal matrix assembly

X rows (1,0),(1,1),(1,2). X^T X entry (1,1): 1+1+1 = 3; (1,2): 0+1+2
= 3; (2,2): 0+1+4 = 5. X^T y: 1+3+2 = 6; 0+3+4 = 7.

## 2. 2x2 solve

det = 3*5-9 = 6. Inverse = (1/6)[[5,-3],[-3,3]].
a = (5*6-3*7)/6 = 9/6 = 3/2. b = (-3*6+3*7)/6 = 3/6 = 1/2.

## 3. Residual ledger

Predictions: 3/2, 3/2+1/2 = 2, 3/2+1 = 5/2.
Residuals: 1-3/2 = -1/2; 3-2 = 1; 2-5/2 = -1/2.
|r|^2 = 1/4+1+1/4 = 3/2. Orthogonality: sum = -1/2+1-1/2 = 0;
x-weighted: 0+1-1 = 0.

## 4. Power iteration rationals

S(1,0) = (2,1). S(2,1) = (4+1, 2+2) = (5,4).
Rayleigh at (1,0): 2. At (2,1): ((2,1).(5,4))/(4+1) = 14/5 = 2.8.
At (1,1): 6/2 = 3. Convergence toward 3 exhibited.

## 5. Eigenvalues of X^T X

t^2 - 8t + 6 = 0 gives 4 +- sqrt10. Product 6 = det; sum 8 = trace.

## 6. Inverse entries and Pythagorean split

Inverse = (1/6)[[5,-3],[-3,3]]: diagonal (5/6, 1/2), off-diagonal
-1/2. Check against XtX: row 1: (15-9, -9+15)/6 = (1, 0); row 2:
(15-15, -9+15)/6 = (0, 1). Identity confirmed.
|y|^2 = 1+9+4 = 14; |X b_hat|^2 = 9/4+4+25/4 = 50/4;
|r|^2 = 6/4; 50/4+6/4 = 56/4 = 14. Pythagoras holds exactly.

## 7. Prediction table and mean-only comparison

x: 0 -> 3/2 (residual -1/2); 1 -> 2 (residual 1); 2 -> 5/2
(residual -1/2). Mean-only fit y-bar = (1+3+2)/3 = 2 gives residuals
(-1,1,0), norm-squared 1+1+0 = 2 > 3/2: the slope earns its keep.

## 8. Column-sum seed

X column sums: ones-column 1+1+1 = 3; x-column 0+1+2 = 3. These are
row 1 of X^T X = (3,3): the normal matrix's first row counts and sums
the design — the Section 1 assembly read left-to-right.
