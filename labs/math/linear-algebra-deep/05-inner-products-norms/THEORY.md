# Inner Products and Norms — Theory

## 1. Inner product and norm

The standard inner product on R^n is <x,y> = sum x_i y_i; the norm is
|x| = sqrt(<x,x>). Norm properties: |x| >= 0 with equality only at 0,
|ax| = |a||x|, triangle inequality |x+y| <= |x|+|y|.

## 2. Cauchy-Schwarz

|<x,y>| <= |x||y|, equality iff dependent. Instance: x = (1,2,3),
y = (1,1,0) give <x,y> = 3, |x|^2 = 14, |y|^2 = 2, and 9 <= 28.

## 3. Gram-Schmidt

For independent v1 = (1,1,0), v2 = (0,1,1), v3 = (1,0,1):

    u1 = v1 = (1,1,0), |u1|^2 = 2.
    u2 = v2 - (1/2)u1 = (-1/2,1/2,1), |u2|^2 = 3/2.
    u3 = v3 - (1/2)u1 - (1/3)u2 = (2/3,-2/3,2/3), |u3|^2 = 4/3.

Pairwise dots are 0, 0, 0. Normalizing gives an orthonormal basis;
det of the triple is 2, nonzero, confirming independence.

## 4. Projection and best approximation

Projection of w onto span{u1,u2} is sum (<w,u_i>/<u_i,u_i>) u_i.
For w = (1,2,3): coefficients 3/2 and 7/3, projection
(1/3, 8/3, 7/3). The residual w - proj is orthogonal to the subspace,
and the projection is the closest point (best approximation theorem).

## 5. Orthogonal matrices

Q preserves inner products iff Q^T Q = I; then |Qx| = |x| and
Q^{-1} = Q^T.

## 6. Full orthonormal basis

Normalizing the Section 3 triple: e1 = (1/sqrt2)(1,1,0),
e2 = u2/sqrt(3/2), e3 = u3/(2/sqrt3) = (1/sqrt3)(1,-1,1).
Norm check: 3*(1/3) = 1. The change-of-basis matrix
E = [e1 e2 e3] satisfies E^T E = I: orthogonal, so coordinates in
this basis are just dots, no solve needed.

## 7. Pythagoras in numbers

|p|^2 = (1+64+49)/9 = 114/9 = 38/3. |r|^2 = 4/3. Sum: 38/3+4/3 =
42/3 = 14 = |w|^2 = 1+4+9. The orthogonal split accounts for every
unit of squared length.
