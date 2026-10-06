# math-for-ai-deep — Exercises

Difficulty: **E** easy, **M** medium, **H** hard. Java 21, no dependencies. Write the maths
first, then the code, then check the two agree.

## Module 01 — Vectors and Spaces

- [ ] **E1.1** Vector addition, scalar multiplication, and the eight axioms; verify each on
      random vectors.
- [ ] **E1.2** Span, basis, and dimension of `{(1,2,3), (2,4,6), (0,1,1)}`. Report the
      basis and dimension.
- [ ] **E1.3** Verify whether a set is a subspace of `R^3`; write a checker that returns a
      reason, not just a boolean.
- [ ] **E1.4** Dot product, cosine similarity, and the angle between vectors.
- [ ] **M1.5** Gram-Schmidt orthogonalization; verify orthogonality to 1e-12.
- [ ] **M1.6** Modified Gram-Schmidt with re-orthogonalization; compare orthogonality loss
      against classical on an ill-conditioned basis.
- [ ] **M1.7** Orthogonal projection onto a subspace; verify the residual is orthogonal to
      the projection.
- [ ] **M1.8** Norms `||.||_1`, `||.||_2`, `||.||_inf` and the triangle inequality on
      random vectors.
- [ ] **H1.9** Demonstrate rank loss: build a matrix with two nearly identical columns and
      report the condition number and the singular values.

## Module 02 — Matrix Operations

- [ ] **E2.1** Matrix multiplication and transpose; verify `A(A'x) = (AA')x`.
- [ ] **E2.2** Determinant by cofactor expansion (3x3) and by LU; verify agreement.
- [ ] **M2.3** Inverse via Gauss-Jordan and via LU solves; verify `A A^-1 = I` to 1e-12.
- [ ] **M2.4** Verify the rank condition: `det(A) != 0` iff `A^-1` exists iff `rank(A) = n`.
- [ ] **M2.5** LU with partial pivoting; solve a system; report the pivot count.
- [ ] **M2.6** Cholesky for a symmetric positive definite matrix; verify `L L' = A`.
- [ ] **M2.7** Verify that Cholesky fails (as it should) on a matrix that is not positive
      definite.
- [ ] **M2.8** Compute `cond(A)` via SVD and via `||A||_inf * ||A^-1||_inf`; compare.
- [ ] **H2.9** Numerically demonstrate `cond(A'A) = cond(A)^2` on a known matrix.
- [ ] **H2.10** Frobenius and spectral norms; verify `||Av||_2 <= ||A||_2 ||v||_2`.

## Module 03 — Eigenvalues and SVD

- [ ] **E3.1** Jacobi eigendecomposition of a symmetric matrix; verify `A P = P D` and
      orthogonality of `P`.
- [ ] **E3.2** Verify that a symmetric matrix has real eigenvalues and an orthogonal
      eigenbasis.
- [ ] **E3.3** One-sided Jacobi SVD; verify `A = U D V'` by reconstruction error.
- [ ] **M3.4** Verify `sigma_i = sqrt(lambda_i(A'A))`.
- [ ] **M3.5** Verify `cond(A) = sigma_max / sigma_min` against `cond(A^-1)`.
- [ ] **M3.6** Rank-revealing: singular values below a tolerance give the numerical rank.
- [ ] **M3.7** Low-rank approximation by truncated SVD; verify the optimality theorem on a
      constructed matrix where a different rank-`k` approximation is deliberately worse.
- [ ] **M3.8** PCA by eigendecomposition of the covariance matrix and by SVD; verify the
      two agree.
- [ ] **M3.9** Power iteration for the dominant eigenpair; verify convergence.
- [ ] **H3.10** Deflation to get all eigenpairs by power iteration; verify against Jacobi.
- [ ] **H3.11** Show the characteristic polynomial route loses all precision on a 4x4
      symmetric matrix, while QR iteration does not.

## Module 04 — Gradient and Vector Calculus

- [ ] **E4.1** Partial derivatives and the gradient of `f(x,y) = x^2 y + sin(y)`.
- [ ] **E4.2** Verify the gradient is orthogonal to any level set: `grad f . t = 0` for
      `t` tangent to the curve `f = c`.
- [ ] **M4.3** Jacobian of a vector-valued function; verify the chain rule
      `d/dx g(f(x)) = J_f' grad g`.
- [ ] **M4.4** Hessian; verify symmetry for a twice-differentiable function.
- [ ] **M4.5** Verify the second-derivative test: Hessian positive definite at a critical
      point implies a local minimum.
- [ ] **M4.6** Directional derivative as `grad f . u`; verify for several directions.
- [ ] **M4.7** Forward-mode automatic differentiation on a computation graph.
- [ ] **M4.8** Reverse-mode automatic differentiation; verify it agrees with forward mode.
- [ ] **H4.9** Jacobian condition number for a two-layer network; show it grows with depth.
- [ ] **H4.10** Implement a tiny reverse-mode AD tape and build backprop out of it.

## Module 05 — Probability Distributions

- [ ] **E5.1** Verify each distribution's PMF/PDF integrates or sums to 1.
- [ ] **E5.2** Verify the binomial PMF equals `C(n,k) p^k (1-p)^(n-k)` by convolution of
      Bernoulli.
- [ ] **E5.3** Verify the memoryless property of the exponential distribution.
- [ ] **E5.4** Verify that a Poisson process's inter-arrival times are exponential.
- [ ] **M5.5** Central limit theorem: sum 1,000 uniforms and compare to the normal.
- [ ] **M5.6** Maximum-entropy derivation: solve for the distribution on the reals with
      fixed mean and variance maximizing entropy; verify it is Gaussian.
- [ ] **M5.7** Verify the exponential family form for Bernoulli, Gaussian, Poisson, and
      categorical; identify the sufficient statistics.
- [ ] **M5.8** Moment matching: fit a Gaussian to a skewed dataset by matching mean and
      variance; report the KL to the true distribution.
- [ ] **H5.9** Prove the softmax is the maximum-entropy distribution on the simplex with a
      given mean vector.

## Module 06 — Bayesian Inference

- [ ] **E6.1** Bayes theorem on a discrete example; verify by direct enumeration.
- [ ] **E6.2** Beta-Binomial conjugacy: verify the posterior is Beta with
      `alpha + s, beta + f`.
- [ ] **E6.3** Normal-Normal conjugacy for a known variance; verify the posterior mean is a
      precision-weighted average.
- [ ] **E6.4** Verify that with a flat prior, MAP equals MLE.
- [ ] **M6.5** Compute the posterior predictive and compare with a plug-in prediction.
- [ ] **M6.6** Credible interval versus confidence interval on a concrete example; explain
      the difference.
- [ ] **M6.7** Model evidence `p(D)` by numerical integration; report marginal likelihoods
      for two models.
- [ ] **M6.8** Bayes factor interpretation; show it is not a p-value and behaves differently
      under a null prior.
- [ ] **H6.9** Implement Laplace approximation to the posterior; compare the credible
      interval with the exact one.
- [ ] **H6.10** Variational inference for a Beta-Bernoulli model; verify the ELBO increases
      monotonically and report the variational gap.

## Module 07 — Information Theory

- [ ] **E7.1** Entropy of fair and biased Bernoulli; verify `H <= 1` bit.
- [ ] **E7.2** Verify the chain rule `H(X,Y) = H(X) + H(Y|X)`.
- [ ] **E7.3** Verify `I(X;Y) = H(X) - H(X|Y) = H(X) + H(Y) - H(X,Y)`.
- [ ] **E7.4** Verify `D_KL(p||q) >= 0` with equality iff `p = q`.
- [ ] **M7.5** Construct `p, q` where `D_KL(p||q)` is large and `D_KL(q||p)` is small; report
      both.
- [ ] **M7.6** Jensen-Shannon divergence; verify symmetry, bounds, and zero iff equal.
- [ ] **M7.7** Cross-entropy `H(p,q) = H(p) + D_KL(p||q)`; verify numerically.
- [ ] **M7.8** Data processing inequality on a concrete channel; verify mutual information
      does not increase.
- [ ] **M7.9** Perplexity of a model: verify `perplexity = exp(cross_entropy)` and that a
      uniform model over `V` words gives perplexity `V`.
- [ ] **H7.10** Maximum entropy: verify the uniform distribution maximizes entropy over a
      finite set by perturbation argument.

## Module 08 — Optimization Fundamentals

- [ ] **E8.1** Verify convexity of a set by the definition on sample points.
- [ ] **E8.2** Verify a function is convex via the Hessian (symmetric positive semidefinite).
- [ ] **E8.3** Find a local-but-not-global minimum of a non-convex function.
- [ ] **M8.4** Lagrangian of a constrained problem; verify weak duality on sample points.
- [ ] **M8.5** KKT conditions; verify they hold at the optimum of a QP.
- [ ] **M8.6** Prove that any first-order stationary point of a convex differentiable function
      is global.
- [ ] **M8.7** Saddle point detection by Hessian eigenvalues on `x - x^3`.
- [ ] **M8.8** Verify the `O(1/k)` rate for gradient descent on an `mu`-strongly convex
      quadratic.
- [ ] **H8.9** Verify strong duality for a convex QP by solving both the primal and the
      dual.
- [ ] **H8.10** Prove gradient descent converges for an `L`-smooth `mu`-strongly convex
      function with `eta = 1/L`.

## Module 09 — Gradient Descent Variants

- [ ] **E9.1** Batch GD on a quadratic; find the exact analytic step count for
      `eta = 1/L`.
- [ ] **M9.2** Show that `eta > 2/L` diverges on the same quadratic.
- [ ] **M9.3** SGD with a fixed seed; report the gradient noise scale versus batch size `B`.
- [ ] **M9.4** Momentum: show oscillation damping on an ill-conditioned quadratic.
- [ ] **M9.5** Nesterov: verify the look-ahead form and compare convergence.
- [ ] **M9.6** AdaGrad: show the accumulator monotonically decays the effective step.
- [ ] **M9.7** RMSProp: sweep `rho`.
- [ ] **M9.8** Adam with bias correction; show the first step without correction is enormous
      when the gradient magnitude is near `eps`.
- [ ] **M9.9** AdamW versus Adam plus L2; compare final weight norms.
- [ ] **H9.10** Learning rate range test: double the rate until divergence; report the
      boundary.
- [ ] **H9.11** Saddle-point escape: show SGD escapes `x - x^3` while batch GD stalls.

## Module 10 — Numerical Computing

- [ ] **E10.1** Print `Math.ulp(1.0)` and explain the 53-bit mantissa.
- [ ] **E10.2** Demonstrate catastrophic cancellation: `(1 + 1e-16) - 1` versus the exact
      result.
- [ ] **E10.3** Compare summation orders for `1e16 + 1 - 1e16`; show naive summation loses
      the 1.
- [ ] **M10.4** Kahan compensated summation; verify the recovered result.
- [ ] **M10.5** Log-sum-exp: compute `log(sum exp(x))` for `x` containing 800, with and
      without the shift.
- [ ] **M10.6** Softmax stability: compute it with values near 800, both ways.
- [ ] **M10.7** Verify `log1p(x)` is accurate for tiny `x` where `log(1+x)` is not.
- [ ] **M10.8** Solve a nearly singular system two ways and report the differing answers;
      compute the condition number.
- [ ] **M10.9** Classical versus modified Gram-Schmidt on an ill-conditioned basis; compare
      orthogonality.
- [ ] **M10.10** Eigenvalues of a symmetric matrix: characteristic polynomial versus QR
      iteration; compare precision.
- [ ] **H10.11** Implement scaled matrix multiplication that is robust to overflow, and
      show the naive version failing.
- [ ] **H10.12** Condition-versus-stability: a well-conditioned problem solved by an unstable
      algorithm; demonstrate the wrong answer.

## Cross-Module

- [ ] **X1** Build reverse-mode AD, then train a small MLP with it — no hand-written
      backprop.
- [ ] **X2** Implement PCA from scratch with SVD and with eigendecomposition; verify both
      match to 1e-12.
- [ ] **X3** Implement a Gaussian process: kernel matrix, Cholesky, marginal likelihood, and
      posterior mean/variance. Verify against a closed-form 1D case.
- [ ] **X4** Derive softmax cross-entropy and verify `dL/dz = p - y` numerically.
- [ ] **X5** Implement an ELBO for a Gaussian variational posterior and verify it increases
      monotonically.
