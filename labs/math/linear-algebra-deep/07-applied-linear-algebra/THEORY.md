# Applied Linear Algebra — Theory

## 1. Least squares and normal equations

For overdetermined Xb ~= y, the minimizer of |Xb - y|^2 solves
X^T X b = X^T y. With independent columns, X^T X is invertible and
b_hat = (X^T X)^{-1} X^T y; the residual is orthogonal to col(X).

## 2. Running fit

Points (0,1), (1,3), (2,2), model y = a + bx:

    X = [[1,0],[1,1],[1,2]], y = (1,3,2),
    X^T X = [[3,3],[3,5]], X^T y = (6,7), det = 15-9 = 6,
    a = (6*5-3*7)/6 = 3/2, b = (3*7-3*6)/6 = 1/2.

Fitted values (3/2, 2, 5/2); residual r = (-1/2, 1, -1/2),
|r|^2 = 1/4 + 1 + 1/4 = 3/2. Normal-equation check: sum r = 0 and
0*(-1/2) + 1*1 + 2*(-1/2) = 0, i.e. X^T r = (0,0).

## 3. Projection view

b_hat gives the projection of y onto col(X); r is the orthogonal
complement. Same geometry as Lab 05, now with a data matrix.

## 4. Power iteration

For symmetric S = [[2,1],[1,2]] (eigenvalues 3, 1), iterating
x_{k+1} = Sx_k/|Sx_k| from (1,0) gives (2,1)/sqrt5, then
(5,4)/sqrt41, aligning toward (1,1)/sqrt2. Rayleigh quotients climb
2 -> 14/5 = 2.8 -> toward 3, the dominant eigenvalue.

## 5. Conditioning note

X^T X has eigenvalues 4 +- sqrt10 (~7.16, ~0.84); forming X^T X
squares sensitivity versus QR on X — fine at this size, relevant
at scale.

## 6. Fitted values as projection

X b_hat = (3/2, 2, 5/2): each entry a + b x_i. The Pythagorean split
|y|^2 = |X b_hat|^2 + |r|^2 reads 1+9+4 = 14 on the left and
(9/4+4+25/4) + 3/2 = 50/4+6/4 = 56/4 = 14 on the right. Exact.

## 7. Degrees of freedom

Three points minus two fitted parameters leaves 1 degree of freedom;
the residual norm-squared 3/2 on 1 dof is the variance-scale estimate.
Fitting only the mean (y-bar = 2) leaves residuals (-1,1,0) with
norm-squared 2 — adding the slope reduces 2 to 3/2, as it must.
