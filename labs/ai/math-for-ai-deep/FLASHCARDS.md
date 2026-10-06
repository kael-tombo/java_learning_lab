# math-for-ai-deep — Flashcards

60 rows. Cover the answer, recall it, then check. Last column is the module.

| # | Question | Answer | Module |
|---|----------|--------|--------|
| 1 | Basis definition? | A linearly independent spanning set; its size is the dimension | 01 |
| 2 | Subspace test? | Contains zero, closed under addition and scalar multiplication | 01 |
| 3 | Inner product? | `x'y = sum x_i y_i`; generalizes to cosine similarity and kernels | 01 |
| 4 | Norm choices? | `L1 = sum|x|`, `L2 = sqrt(x'x)`, `Linf = max|x|`; each defines a distance | 01 |
| 5 | Gram-Schmidt? | Turns a basis into an orthonormal one by successive projection | 01 |
| 6 | Rank loss means? | Columns became linearly dependent; information was discarded | 01 |
| 7 | `A B` shape rule? | `(n x p)(p x m) = (n x m)`, with `C_ij = sum_k A_ik B_kj` | 02 |
| 8 | Invertible iff? | `det(A) != 0` iff rank `= n` iff columns linearly independent | 02 |
| 9 | Condition number? | `cond(A) = sigma_max/sigma_min`; the relative-error amplification factor | 02 |
| 10 | Why QR, not normal equations? | `cond(A'A) = cond(A)^2`; inverting squares the ill-conditioning | 02 |
| 11 | LU with partial pivoting? | `PA = LU`; `O(n^3)` stable solve by back-substitution | 02 |
| 12 | Cholesky? | `A = LL'` for symmetric positive definite; half the cost, doubles as a definiteness test | 02 |
| 13 | Spectral norm? | `||A||_2 = sigma_max`; bounds how much a layer amplifies | 02 |
| 14 | Frobenius norm? | `||A||_F = sqrt(sum A_ij^2)`; unitarily invariant | 02 |
| 15 | Eigen equation? | `A v = lambda v` | 03 |
| 16 | Symmetric matrix guarantee? | Real eigenvalues and an orthogonal eigenbasis (spectral theorem) | 03 |
| 17 | SVD form? | `A = U D V'` with `U, V` orthogonal and `D` sorted nonnegative | 03 |
| 18 | Singular values and eigenvalues? | `sigma_i = sqrt(lambda_i(A'A))` | 03 |
| 19 | Numerical rank? | Count of singular values above a tolerance | 03 |
| 20 | Truncated SVD optimality? | The best rank-`k` approximation in both spectral and Frobenius norm | 03 |
| 21 | PCA via SVD? | Project the centered data onto the top right singular vectors | 03 |
| 22 | Partial derivatives? | `df/dx_i`; the gradient stacks them into a vector | 04 |
| 23 | Jacobian? | `m x n` matrix of partials for a vector-valued function | 04 |
| 24 | Hessian? | Matrix of second partials; symmetric when twice differentiable | 04 |
| 25 | Gradient direction? | Perpendicular to level sets: `grad f . t = 0` for tangent `t` | 04 |
| 26 | Chain rule for Jacobians? | `d/dx g(f(x)) = J_f' grad g` | 04 |
| 27 | Hessian and critical points? | Positive definite at a critical point implies a local minimum | 04 |
| 28 | Hessian and convergence rate? | Newton converges in proportion to `lambda_max/lambda_min` | 04 |
| 29 | AD modes? | Forward for few inputs, reverse for few outputs — which is why backprop is reverse | 04 |
| 30 | Beta-Binomial conjugacy? | Prior `Beta(a,b)` plus `s` successes, `f` failures gives `Beta(a+s, b+f)` | 05 |
| 31 | Poisson process? | Counts follow Poisson; inter-arrivals are exponential | 05 |
| 32 | Memoryless property? | `P(X > s + t | X > s) = P(X > t)`; exponential only | 05 |
| 33 | Exponential family form? | `h(x) exp(eta' T(x) - A(eta))`; fixed sufficient statistics `T(x)` give conjugacy | 05 |
| 34 | Categorical as exponential family? | `h = 1`, `T(x) = one-hot(x)`, log-partition `log sum exp(eta)` | 05 |
| 35 | Exponential's log-partition? | `A(eta) = -log(1 - e^eta)`; its derivative is the mean | 05 |
| 36 | Normal's log-partition? | `A(eta) = eta^2/2` (natural parameter `eta = mu/sigma^2`) | 05 |
| 37 | Bayes theorem? | Posterior proportional to likelihood times prior; normalize over the parameter | 06 |
| 38 | MAP vs MLE? | MAP includes the prior; with a flat prior they coincide | 06 |
| 39 | Full Bayes vs MAP? | Full Bayes integrates over the parameter; MAP picks a point | 06 |
| 40 | Credible interval? | A posterior probability interval (`P(theta in I) = 0.95`) | 06 |
| 41 | Laplace approximation? | Posterior approximated by a Gaussian at the mode, with the Hessian as precision | 06 |
| 42 | ELBO? | `E_q[log p(D|theta)] - KL(q(theta) || p(theta))`; a tractable lower bound | 06 |
| 43 | Variational gap? | True log marginal likelihood minus ELBO; report it | 06 |
| 44 | Entropy? | `H(X) = -sum p log p`, maximized by uniform | 07 |
| 45 | Chain rule for entropy? | `H(X,Y) = H(X) + H(Y|X)` | 07 |
| 46 | Mutual information? | `I(X;Y) = H(X) - H(X|Y)`; KL between the joint and the product of marginals | 07 |
| 47 | KL properties? | Non-negative, zero iff equal, asymmetric, no triangle inequality | 07 |
| 48 | Jensen-Shannon? | `(KL(p||m) + KL(q||m))/2` with `m = (p+q)/2`; symmetric and bounded | 07 |
| 49 | Cross-entropy identity? | `H(p,q) = H(p) + D_KL(p||q)` | 07 |
| 50 | Perplexity? | `exp(cross_entropy)`; uniform over `V` gives exactly `V` | 07 |
| 51 | Data processing inequality? | Any channel cannot increase mutual information | 07 |
| 52 | Convex set? | The segment between any two points is in the set | 08 |
| 53 | Strong convexity definition? | `f(y) >= f(x) + grad f(x)'(y-x) + (mu/2)||y-x||^2` | 08 |
| 54 | KKT conditions? | Stationarity, primal and dual feasibility, complementary slackness | 08 |
| 55 | Saddle point? | Stationary with a negative curvature direction; stalls first-order methods | 08 |
| 56 | Convex critical point? | Any stationary point of a convex differentiable function is global | 08 |
| 57 | Gradient noise scale? | `sigma/sqrt(B)` per component; smaller batch is noisier and more regularizing | 09 |
| 58 | Stable step for L-smooth? | `eta <= 2/L`; above that, divergence | 09 |
| 59 | Adam bias correction? | `m/(1-beta1^t)`, `v/(1-beta2^t)`; running averages start biased toward zero | 09 |
| 60 | Catastrophic cancellation? | Subtracting near-equal floats destroys significant digits; use log1p, logsumexp, Kahan | 10 |
