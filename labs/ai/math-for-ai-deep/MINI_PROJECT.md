# math-for-ai-deep — Mini Project

## Project: A Mathematical Toolkit for Machine Learning

Build a numerical toolkit in Java 21 that every other lab in this repository depends on:
linear algebra with stability guarantees, eigendecomposition and SVD, automatic
differentiation, distributions, Bayesian inference, information measures, optimization, and
numerically stable primitives — all verified against mathematical identities rather than
against a reference library.

## Goal

`Main` runs a self-test suite that verifies every identity in `MATH_FOUNDATION.md` numerically,
then builds three small models on top of the toolkit (PCA, a Bayesian logistic regression,
and an AD-trained MLP) and writes `REPORT.md` with the verification table.

## Requirements

### Phase 1: Linear Algebra Core
- [ ] `Vector`, `Matrix` with shape assertions; matmul, transpose, add, scale.
- [ ] Norms: `L1`, `L2`, `Linf`, Frobenius, spectral (via SVD); induced 1- and infinity-norms.
- [ ] Verify `||Av||_2 <= ||A||_2 ||v||_2` on random matrices.
- [ ] Determinant by LU; verify invertibility iff `det != 0` iff rank `= n`.
- [ ] Inverse via Gauss-Jordan and via LU solves; verify `A A^-1 = I`.

### Phase 2: Stability
- [ ] LU with partial pivoting; report the pivot count and growth factor.
- [ ] QR via Householder; verify `Q'Q = I` and `R` upper triangular.
- [ ] Cholesky; verify `L L' = A` and that it fails on non-SPD input.
- [ ] Demonstrate `cond(A'A) = cond(A)^2` on a matrix with known singular values.
- [ ] Solve an ill-conditioned system by normal equations, LU, and QR; report all three
      answers and the residuals.

### Phase 3: Gram-Schmidt
- [ ] Classical and modified, with and without re-orthogonalization.
- [ ] Orthogonality error as a function of conditioning; plot the three curves.
- [ ] QR from Gram-Schmidt versus Householder; report the difference.

### Phase 4: Eigendecomposition and SVD
- [ ] Jacobi eigendecomposition; verify `A P = P D` and orthogonality.
- [ ] One-sided Jacobi SVD; verify reconstruction error equals the tail sum of squares.
- [ ] Power iteration and deflation; verify against Jacobi.
- [ ] Characteristic polynomial versus QR iteration on a 4x4; report the precision
      difference.
- [ ] Truncated SVD optimality: construct a matrix where a non-optimal rank-`k`
      approximation is measurably worse.

### Phase 5: Vector Calculus and AD
- [ ] Gradient, Jacobian, Hessian with shape assertions.
- [ ] Verify `grad f` is orthogonal to level sets using finite-difference tangents.
- [ ] Forward-mode AD on a computation graph.
- [ ] Reverse-mode AD on a tape; verify it agrees with forward mode and with finite
      differences to 1e-9.
- [ ] Build a small MLP and train it **using only the AD tape** — no hand-written backward.

### Phase 6: Distributions and the Exponential Family
- [ ] Bernoulli, Binomial, Poisson, Exponential, Gaussian, Categorical with PMF/PDF and
      log-pmf.
- [ ] Verify normalization by numerical integration or summation.
- [ ] Verify the memoryless property and the Poisson inter-arrival relationship.
- [ ] Derive maximum entropy: solve for the distribution with fixed mean and variance;
      verify it is Gaussian.
- [ ] Verify the exponential family table (sufficient statistics, log-partition, mean,
      variance) for all six families.

### Phase 7: Bayesian Inference
- [ ] Bayes theorem by enumeration.
- [ ] Beta-Binomial and Normal-Normal conjugacy with closed-form updates.
- [ ] MAP vs MLE with a flat prior; verify equality.
- [ ] Posterior predictive versus plug-in prediction.
- [ ] Laplace approximation; compare credible intervals with the exact ones.
- [ ] Variational inference with a Gaussian family; assert ELBO monotonicity and report
      the variational gap against the exact log marginal likelihood.

### Phase 8: Information Theory
- [ ] Entropy, conditional entropy, mutual information, KL, JS, cross-entropy.
- [ ] Verify the entropy chain rule, the cross-entropy identity, `D_KL >= 0`, and JS
      bounds.
- [ ] Construct the KL-asymmetry example; report both directions and the JS.
- [ ] Perplexity; verify a uniform model over `V` gives exactly `V`.
- [ ] Data processing inequality on a concrete channel.

### Phase 9: Optimization
- [ ] Convexity checkers for sets and functions (Hessian PSD via Cholesky).
- [ ] Lagrangian and KKT for a QP; verify at the optimum.
- [ ] GD, momentum, Nesterov, RMSProp, Adam with the analytic contraction factors.
- [ ] Show GD stalls at a saddle point and SGD escapes it.
- [ ] Learning-rate range test by doubling until divergence.

### Phase 10: Numerical Primitives
- [ ] `logSumExp`, `softmax`, `logSigmoid`, `log1p` with accuracy checks.
- [ ] Kahan summation; recover the value naive summation loses.
- [ ] Scaled matrix multiply; demonstrate the naive version overflowing.
- [ ] Condition versus stability: a well-conditioned problem solved unstably.

### Phase 11: Consumers Built on the Toolkit
- [ ] PCA via eigendecomposition and via SVD; verify agreement to 1e-12.
- [ ] Bayesian logistic regression with a Normal-Inverse-Gamma posterior.
- [ ] A Gaussian process: kernel matrix, Cholesky, marginal likelihood, posterior mean and
      variance; verify against a closed-form 1D case.
- [ ] Kernel ridge regression using the SVD path.

### Phase 12: Report
- [ ] `REPORT.md` with the full verification table.

## Directory Layout

```
math-for-ai-deep/
  src/com/ailab/math/
    linalg/{Vector,Matrix,Linalg,GramSchmidt}.java
    decomp/{Jacobi,Svd,PowerIter,Cholesky,Lr}.java
    ad/{Tape,ForwardMode,ReverseMode}.java
    prob/{Distributions,ExponentialFamily,MaxEnt}.java
    bayes/{Bayes,BetaBinomial,NormalNormal,Laplace,Vi,Gp}.java
    info/Info.java
    opt/{Convex,Kkt,Optimizers}.java
    numeric/{Stable,Kahan,Scaled}.java
    apps/{Pca,BayesianLogreg,Gp}.java
    verify/SelfTest.java
  Main.java
  out/verification.txt
  REPORT.md
```

## Milestones

1. **M1** — matrix core, norms, determinant, inverse.
2. **M2** — LU, QR, Cholesky; the ill-conditioned comparison.
3. **M3** — Gram-Schmidt variants with the orthogonality curves.
4. **M4** — Jacobi eigendecomposition verified.
5. **M5** — SVD verified; truncated-SVD optimality demonstrated.
6. **M6** — power iteration and deflation verified against Jacobi.
7. **M7** — vector calculus; gradient orthogonality verified.
8. **M8** — forward-mode and reverse-mode AD agreeing with finite differences.
9. **M9** — an MLP trained by the AD tape alone.
10. **M10** — six distributions with the exponential family table verified.
11. **M11** — maximum entropy derivation verified numerically.
12. **M12** — conjugacy, MAP, posterior predictive.
13. **M13** — Laplace approximation with credible intervals.
14. **M14** — VI with ELBO monotonicity and the variational gap reported.
15. **M15** — information measures; all identities verified.
16. **M16** — convexity, KKT, optimizers with analytic contraction factors.
17. **M17** — numerical primitives and the stability demonstrations.
18. **M18** — PCA, Bayesian logistic regression, and Gaussian process on top.
19. **M19** — `REPORT.md` written.

## Acceptance Criteria

- [ ] Every identity in `MATH_FOUNDATION.md` has a numeric test and a recorded result.
- [ ] `A A^-1` within 1e-12; `Q'Q` within 1e-12; `L L'` within 1e-12.
- [ ] `cond(A'A) = cond(A)^2` verified to within a factor of 2.
- [ ] Modified Gram-Schmidt orthogonality error at least 100x below classical on an
      ill-conditioned basis.
- [ ] SVD reconstruction error equals the tail sum of squared singular values to 1e-12.
- [ ] Reverse-mode AD matches finite differences to 1e-9 on a 20-parameter network.
- [ ] An MLP trains to a target loss using only the AD tape.
- [ ] All distributions normalized; the exponential family mean/variance relations verified.
- [ ] Maximum-entropy solution numerically matches the Gaussian.
- [ ] Posterior predictive degrades gracefully with small samples relative to MLE.
- [ ] VI ELBO strictly increasing; the variational gap reported against the exact value.
- [ ] `D_JS` bounded by `log 2` and zero iff equal.
- [ ] Perplexity of a uniform model equals the vocabulary size exactly.
- [ ] Gradient descent contraction factor matches the analytic prediction.
- [ ] SGD escapes a saddle point where GD stalls.
- [ ] Kahan summation recovers a value naive summation loses.
- [ ] Self-test suite exits non-zero on any failure.

## Stretch Goals

- [ ] Complex eigenvalues of a general (non-symmetric) matrix.
- [ ] Fractional PCA on a two-moons dataset via kernel PCA.
- [ ] Variational inference for a Gaussian mixture, with component-collapse monitoring.
- [ ] Natural gradient / conjugate gradient on a quadratic; compare iteration counts.
- [ ] A second-order optimizer (Newton or L-BFGS) with a line search.
- [ ] Log-sum-exp over a long logit sequence without overflow at any point.
- [ ] Condition number estimation by randomized probing (Hutchinson).
- [ ] A Kalman filter built on the Gaussian-Normal update.
- [ ] Reproduce a published closed-form result (e.g. the softmax variance relation) as a
      test.

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| Gram-Schmidt loses orthogonality | Classical form; use modified with re-orthogonalization |
| Eigenvalues wrong | Rotation applied to only one side |
| Singular values in wrong order | Forgot to sort descending |
| `cond(A'A)` not matching theory | Computing the condition number of `A'A` via a poorly conditioned route |
| Normal equations lose digits | Exactly the expected failure; compare against QR |
| Cholesky throws on a valid matrix | Symmetry tolerance too strict, or a genuine non-SPD matrix |
| Reverse-mode gradients wrong | Edge list not applied in reverse topological order |
| Forward and reverse AD disagree | One of them missing a partial derivative term |
| `softmax` returns NaN | Max shift missing; `exp(>709)` overflows to `Infinity` |
| KL returns NaN | Dividing by zero instead of returning infinity |
| ELBO decreases during VI | Sign error in the entropy or prior term |
| GD stalls at a saddle point | Expected; add noise or use momentum |
| Naive summation loses a value | Use Kahan; running statistics inherit this bias |
| Verification suite passes but should fail | A test with a tolerance too loose to detect the error |

## Definition of Done

`REPORT.md` contains: the verification table mapping each identity to its test and numeric
result, the linear algebra core results (determinant, inverse residual, norm identities), the
stability comparison across LU/QR/Cholesky with the ill-conditioned system showing all three
answers and residuals, the `cond(A'A)` demonstration, the Gram-Schmidt orthogonality-error
curves, the eigendecomposition and SVD verification with reconstruction errors, the
truncated-SVD optimality demonstration, the AD verification table (forward vs reverse vs
finite differences), the AD-trained MLP result, the distribution normalization results and
the full exponential family table, the maximum-entropy derivation result, the Bayesian
update results with credible intervals, the VI result with the variational gap, the
information identity verifications including the KL-asymmetry example and the perplexity
baseline, the convexity and KKT verification, the optimizer convergence against analytic
contraction factors, the saddle-point escape demonstration, the numerical stability
demonstrations, the three consumer applications (PCA, Bayesian logistic regression,
Gaussian process) with their results, and a list of known numerical failure modes with
mitigations.
