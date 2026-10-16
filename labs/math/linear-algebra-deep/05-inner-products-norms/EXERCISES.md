# Inner Products and Norms — Exercises

## 1. Gram-Schmidt

Q: Orthogonalize (1,1,0), (0,1,1), (1,0,1).
A: u1 = (1,1,0); u2 = (-1/2,1/2,1); u3 = (2/3,-2/3,2/3), with
norms-squared 2, 3/2, 4/3 and all pairwise dots 0.

## 2. Orthonormal basis

Q: Normalize the triple.
A: e1 = (1/sqrt2)(1,1,0); e2 = u2/sqrt(3/2); e3 = (1/sqrt3)(1,-1,1),
since |u3| = 2/sqrt3, so u3/|u3| = (2/3,-2/3,2/3)/(2/sqrt3)
= (1/sqrt3)(1,-1,1). Check: 3*(1/3) = 1.

## 3. Projection

Q: Project (1,2,3) onto span{u1,u2}.
A: (1/3,8/3,7/3) with coefficients 3/2, 7/3. Residual (2/3,-2/3,2/3)
is orthogonal to both u1 and u2.

## 4. Cauchy-Schwarz

Q: Verify it for (1,2,3) and (1,1,0), and name the equality case.
A: 9 <= 28. Equality iff the vectors are linearly dependent.

## 5. Best approximation

Q: Why is the projection the closest point in the subspace?
A: For any s in the subspace, |w-s|^2 = |w-p|^2 + |p-s|^2 by
orthogonality (Pythagoras), minimized at s = p. Here the gap is
|residual|^2 = 4/3.

## 6. Orthogonal matrix check

Q: Is (1/sqrt2)[[1,1],[1,-1]] orthogonal?
A: Yes: columns have norm 1 and dot (1-1)/2 = 0; Q^T Q = I.

## 7. Coordinates via dots

Q: Coordinates of (3,7) in the orthonormal basis from Exercise 2's
2D analogue — i.e. dot instead of solve?
A: Dots with (1/sqrt2)(1,1) and (1/sqrt2)(1,-1) give 10/sqrt2 = 5
sqrt2 and -4/sqrt2 = -2 sqrt2; dividing by 1 (unit norms) and
comparing with 5(1,1)-2(1,-1) = (3,7) confirms coefficients 5, -2.
