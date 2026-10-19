# 03-eigenvalues-svd - Eigenvalues and SVD
## Overview
Eigenvalues solve det(A - lI)=0; eigenvectors satisfy Av = lv. Singular values are sqrt of eigenvalues of A^T A; their ratio is the condition number; count of nonzero values is the rank.
## Key formulas
- 2x2: l = (tr +- sqrt(tr^2-4det))/2.
- cond = s_max/s_min; Frobenius = sqrt(sum a_ij^2).
## What the snippets show
- Mt03A: eigenpair with zero residual certificate.
- Mt03B: singular [3,1], cond 3.0, Frobenius 3.1623.
## Try it
Try A=[[2,1],[1,2]] (eigenvalues 3 and 1) and verify by hand.
## Formula reference
- Characteristic det(A - lI) = 0; trace = sum l, det = prod l.
- Symmetric A: orthogonal eigenvectors, real eigenvalues.
- SVD A = U S V^T; singular values sqrt(eig(A^T A)); rank = nonzero count.
## Worked example
- Same C as PCA lab: l = 5.5616/1.4384, sum 7, product 8.
- Eigenvector [2, 1.5616]: first eq 4*2+2*1.5616 = 11.123 = 5.5616*2.
- diag(3,1): singular values |3|,|1|; cond 3; Frobenius sqrt(9+1) = 3.1623.
## Pitfalls
- Nonsymmetric: complex/defective cases; Schur instead of diagonal.
- Repeated eigenvalues: eigenspace dimension can mislead solvers.
- Small singular values + inversion = noise blowup (regularize).
## Connections
- PCA keeps top eigen-directions of covariance.
- Condition number governs GD convergence speed.
## Exercises
1. Solve [[2,1],[1,2]]; expect 3 and 1.
2. Verify trace/det identities on your result.
3. Compute cond of diag(4,2).
