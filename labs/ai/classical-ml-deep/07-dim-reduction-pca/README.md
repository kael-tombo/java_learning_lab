# 07-dim-reduction-pca - PCA
## Overview
PCA diagonalizes the covariance: principal components are its eigenvectors, variances are eigenvalues. Keep top-k for max-variance projection; explained ratio is lambda_i / sum lambda.
## Key formulas
- 2x2 eigenvalues: (tr +- sqrt(tr^2 - 4 det))/2.
- Projection: z = v^T (x - mean); ratio = lambda_1 / (lambda_1 + lambda_2).
## What the snippets show
- Cml07A: full solve with trace/det cross-check (5.5616, 1.4384).
- Cml07B: projection energies giving ratio 0.8000.
## Try it
Use C=[[5,0],[0,1]] and confirm eigenvalues 5 and 1 by hand.
## Formula reference
- Covariance C = X^T X/(n-1) centered; eigenpairs give components/variances.
- 2x2: l = (tr +- sqrt(tr^2 - 4det))/2; explained = l_i/sum l.
- Reconstruction with k PCs minimizes squared error among rank-k projections.
## Worked example
- tr = 7, det = 8; disc = sqrt(49-32) = sqrt(17) = 4.1231.
- l1 = (7+4.1231)/2 = 5.5616; l2 = 1.4384; ratio 5.5616/7 = 0.7945.
- Eigenvector check: residual [0,-0] printed by snippet.
## Pitfalls
- Unstandardized units let large-scale features dominate; z-score first.
- PCA is linear; curved manifolds need kernels or nonlinear methods.
- Sign of eigenvectors arbitrary; compare spans, not signs.
## Connections
- SVD of centered X gives the same components (singular values sqrt((n-1) l)).
- Eigen math reused in spectral clustering and neural net analysis.
## Exercises
1. Solve C = diag(5,1) and name both PCs.
2. Project [2,1] onto PC1 of the snippet matrix.
3. Standardize two different-unit features, then redo.
