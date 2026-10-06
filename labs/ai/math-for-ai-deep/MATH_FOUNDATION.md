# math-for-ai-deep — Math Foundation

This module is the mathematical spine of the track. Every derivation is followed by the
numeric check that catches the mistake.

## 1. Norms and the Geometry of Regularization

```
||x||_1   = sum |x_i|              L1 ball: a diamond, corners on the axes
||x||_2   = sqrt(sum x_i^2)       L2 ball: a sphere
||x||_p   = (sum |x_i|^p)^(1/p)
||A||_F   = sqrt(sum A_ij^2)       Frobenius
||A||_2   = sigma_max(A)           spectral, induced 2-norm
||A||_inf = max_i sum_j |A_ij|     induced infinity-norm
```

The penalty ball *is* the geometric statement of the regularizer. An L2 ball has no corners
on the axes, so the optimum never lands on one and no coefficient is exactly zero. An L1
ball has corners exactly on the axes, and the optimum frequently does land on one — that is
where sparsity comes from, geometrically.

Spectral norm matters beyond linear algebra: `||W||_2` bounds how much a single layer can
amplify a perturbation, so `||W||_2 <= 1` layers are 1-Lipschitz, and a stack of `L` such
layers is `L`-Lipschitz. That is the foundation of both spectral normalization and many
adversarial-robustness arguments.

## 2. The Condition Number Is the Whole Story

```
cond(A) = sigma_max / sigma_min
```

It is the largest ratio of output stretching to input stretching. For a linear solve, a
relative input perturbation of `eps` produces a relative output error of up to
`cond(A) * eps`.

```
cond(A'A) = cond(A)^2
```

This is why the normal equations are dangerous. A matrix with `cond(A) = 1e6` gives
`cond(A'A) = 1e12`; in double precision (~1.1e-16 machine epsilon) only about 4 digits
survive. QR or SVD on `A` directly keeps all 10.

Verify numerically: build `A` from known singular values `sigma = (1e6, 1)`, then compare
the residual of the normal-equation solve against the QR solve.

## 3. LU, Cholesky, QR: Who Solves What

```
LU with partial pivoting:  PA = LU, O(n^3)/3, stable in practice, works for any matrix
Cholesky:                   A = LL', A SPD, ~n^3/3 (half of LU), doubles as an SPD test
QR:                        A = QR, solves least squares, gives the best rank-k approximation
```

Cholesky failing on a symmetric matrix is not a bug — it is the cheapest reliable test for
positive definiteness, and it is exactly the test used to verify that a Hessian is
positive definite at a candidate minimum.

QR is the right tool for least squares because it does not square the condition number. Its
column form (`A = Q R`, thin QR) gives the top-`k` columns of `Q` as an orthonormal basis of
the column space, which is the geometric content of PCA.

## 4. Eigendecomposition and SVD

```
A v = lambda v            eigenvalues of a general matrix may be complex
A = P D P^-1              diagonalizable iff there are n independent eigenvectors
A = P D P'               symmetric: always diagonalizable, P orthogonal, lambda real
A = U D V'               SVD: always exists, U and V orthogonal, D >= 0
```

For a real symmetric matrix, `lambda_i(A'A) = sigma_i(A)^2`. Proof: if `A = U D V'` then
`A'A = V D^2 V'`.

**Truncated SVD optimality**: the best rank-`k` approximation in spectral norm is `A_k`
with the top-`k` singular values, and in Frobenius norm
`||A - A_k||_F = sqrt(sum_{i>k} sigma_i^2)`. Both are theorems, so low-rank approximation
is not a heuristic — which is why truncated SVD is used for compression and denoising with
a guarantee rather than a hope.

**Symmetric positive definite** eigenvalues are all positive, which makes `A = LL'` and
Gaussian covariance matrices possible.

## 5. Gradient, Jacobian, Hessian

```
grad f = (df/dx_1, ..., df/dx_n)                  column vector
J (m x n):  J_ij = d f_i / d x_j
H (n x n):  H_ij = d^2 f / d x_i d x_j           symmetric
```

Chain rule for vector functions: `d/dx g(f(x)) = J_f' grad g`.

Key consequences:

- `grad f` is orthogonal to every level set of `f`. Verify numerically with a tangent vector
  from finite differences.
- At a critical point (`grad f = 0`), positive-definite `H` implies a strict local minimum.
- The singular values of `J` bound how much the map can stretch; `||J||_2` is the Lipschitz
  constant.
- The singular values of `H` predict convergence: Newton's rate degrades with
  `cond(H) = lambda_max/lambda_min`.

## 6. Automatic Differentiation Is Bookkeeping

Forward mode carries a tangent value alongside every primal value:

```
primal:  c = a * b
tangent: dc = da * b + a * db
```

One pass, cost proportional to the number of inputs. Reverse mode carries adjoints:

```
c = a * b  ->  a_bar += c_bar * b,  b_bar += c_bar * a
```

One pass, cost proportional to the number of outputs. Backpropagation in deep learning is
reverse mode applied to a computation graph — the reason it is efficient is that there are
millions of parameters but only one scalar loss.

## 7. The Exponential Family

```
p(x) = h(x) exp( eta'T(x) - A(eta) )
A'(eta) = E[T(X)],   A''(eta) = Var[T(X)]
```

| Family | `h(x)` | `T(x)` | `A(eta)` |
|--------|--------|--------|----------|
| Bernoulli | 1 | `x` | `-log(1 - e^eta)` |
| Categorical | 1 | one-hot(x) | `log sum_k e^{eta_k}` |
| Gaussian (mean) | `exp(-x^2/2)` | `x` | `eta^2/2` |
| Poisson | 1 | `x` | `-e^eta` |
| Exponential | 1 | `x` | `-log(-eta)` |

The consequence for ML: conjugate priors work because `T(x)` is fixed, so the posterior is
again exponential family and the update is just adding sufficient statistics. This one table
explains Bayesian logistic regression, LDA, and Poisson regression.

## 8. Maximum Entropy and Why Gaussians Are the Default

Maximize `H(p) = -sum p log p` subject to `E_p[X] = mu` and `Var_p[X] = sigma^2`. The
stationarity condition with Lagrange multipliers gives `log p(x) = -(a x^2 + b x + c)`, and
applying the constraints yields

```
p(x) = 1/(sigma sqrt(2 pi)) * exp( -(x - mu)^2 / (2 sigma^2) )
```

So the Gaussian is the *least informative* distribution consistent with the first two
moments. That is the reason `L2` regularization corresponds to a Gaussian prior, and the
reason moment matching is a reasonable approximate fitting strategy.

On the simplex with a fixed mean vector, the same argument gives softmax — which is why
softmax is the maximum-entropy choice for next-token prediction.

## 9. Conjugacy and the Beta-Binomial

```
Prior:      theta ~ Beta(alpha, beta)
Data:       s successes, f failures
Posterior:  theta | D ~ Beta(alpha + s, beta + f)
Predictive: P(next = 1 | D) = (alpha + s) / (alpha + beta + s + f)
```

The predictive is the posterior mean of the Bernoulli likelihood. Compare with the
plug-in estimate `s/(s+f)`: the Bayesian version degrades gracefully with small samples
because the prior contributes pseudo-counts.

Normal-Normal with known `sigma^2`:

```
Prior:      mu ~ Normal(mu_0, sigma_0^2)
Data:       n observations, sample mean xbar
Posterior:  mu | D ~ Normal(m, tau^2)
            tau^2 = 1/(1/sigma_0^2 + n/sigma^2)
            m = tau^2 (mu_0/sigma_0^2 + n*xbar/sigma^2)
```

The posterior mean is a precision-weighted average — a low-variance prior pulls harder. Every
Bayesian update in the Gaussian family has this shape.

## 10. The ELBO and the Variational Gap

```
log p(D) = ELBO + gap,   gap >= 0
ELBO = E_{q}[ log p(D|theta) ] - KL( q(theta) || p(theta|D) )
```

Minimizing `KL(q || posterior)` maximizes the ELBO, and the optimum `q = posterior` is
uncomputable — hence the approximation. The gap is measurable (when the true
`log p(D)` is computable, e.g. with a small discrete latent) and **should be reported**.
Reporting only the ELBO hides how loose the approximation is.

## 11. Cross-Entropy, KL, and Perplexity

```
H(p,q) = -sum p log q
H(p,q) = H(p) + D_KL(p||q)
```

Minimizing `H(p,q)` in `q` with a fixed `p` is maximum likelihood. With a uniform
predictive over `V` classes, cross-entropy is `log V` and perplexity is exactly `V` — the
baseline every language model must beat.

KL is asymmetric and unbounded, so it is not a distance. Jensen-Shannon fixes both:

```
D_JS(p,q) = ( D_KL(p||m) + D_KL(q||m) ) / 2,   m = (p+q)/2
```

It lies in `[0, log 2]` and is zero only when `p = q`. For drift monitoring, this matters: a
tiny amount of mass moving from the tail of `p` into a region `q` never covers produces a
huge asymmetric KL and a small JS, so the choice of divergence is a monitoring decision, not
a detail.

## 12. Convexity, Strong Convexity, and KKT

```
Convex:           f(tx + (1-t)y) <= t f(x) + (1-t) f(y)
mu-strongly convex:
    f(y) >= f(x) + grad f(x)'(y-x) + (mu/2)||y-x||^2
Lagrangian:        L(x, lambda) = f(x) + lambda'(c(x) - b),  lambda >= 0
KKT:               grad_x L = 0,  c(x) - b <= 0,  lambda >= 0,  lambda_i (c_i(x) - b_i) = 0
```

Strong duality (primal optimum = dual optimum) holds for convex problems with Slater's
condition. For non-convex problems, duality gives only a bound — which is the formal reason
"train the relaxation" is a heuristic rather than a solution.

For `mu`-strongly convex `L`-smooth functions, gradient descent with `eta = 1/L` satisfies

```
f(x_k) - f* <= (L/2) * exp( -k mu / L ) * ||x_0 - x*||^2
```

i.e. `O(1/k)` in distance-to-optimality, which becomes linear with momentum. This is the
guarantee people mean when they say "convex problems converge"; applying it to a neural
network requires saying "convex" out loud.

## 13. Numerical Analysis Essentials

**Machine epsilon**: double precision has 53 mantissa bits, `eps = 2^-52 = 2.22e-16`.

**Catastrophic cancellation**: relative error in `a - b` is
`~ eps * |a| / |a - b|`. With `a = 1.0`, `b = 1 - 1e-16`, the true difference `1e-16`
inherits a relative error around 1.2 — no digits survive.

**Log-sum-exp**:

```
log sum_i exp(x_i) = m + log sum_i exp(x_i - m),   m = max_i x_i
```

Exact after normalization, and the difference between a working softmax and an overflow to
`Infinity` when any logit exceeds ~709.

**Kahan summation**: maintain a running compensation term so that summing `1e16 + 1 - 1e16`
recovers the `1` that naive summation loses.

**Eigenvalues by characteristic polynomial**: expanding `det(A - lambda I)` produces a
polynomial whose coefficients involve cancellations of large terms; for `n >= 4` in double
precision the results are unreliable. QR iteration with shifts is the standard stable
method.

## 14. Optimization Convergence Rates

For an `L`-smooth quadratic `f(x) = 0.5 x'A x - b'x` with `eta = 1/L`:

```
error_{k+1} = (I - A/L)^k error_0
convergence factor = max_i |1 - lambda_i/L|
```

With `eta = 2/L` the factor is `max|1 - 2 lambda_i/L|`, which exceeds 1 whenever the
spectrum is not a single point — so `2/L` is a boundary, and `1/L` is the safe choice.
With momentum `beta`, the factor for the extreme modes becomes
`(1 - beta*sqrt(mu/L)) / (1 + beta*sqrt(mu/L))`, which is how momentum improves the rate on
ill-conditioned problems.

## Worked Numbers

- **Condition number**: `A` with singular values `(1e6, 1)`, `cond = 1e6`. Normal equations:
  `cond(A'A) = 1e12`; with `eps = 2.2e-16`, relative accuracy `~ 1/1e12 / 2.2e-16 = 4.5e-9` —
  about 8 correct digits lost to a factor of `1e6` in conditioning.
- **Cancellation**: `sqrt(2)^2 - 2` in double gives `-4.44e-16`; the exact value is 0.
  Relative error is infinite in the strict sense — a reminder to test `x*x - 2 == 0` with a
  tolerance.
- **Gradient norm at init**: a 20-layer sigmoid net with unit-norm weight matrices and
  `phi' <= 0.25` gives `0.25^20 = 9.1e-13` at the bottom layer; with ReLU (`phi' = 1`) it is
  `1.0`.
- **Exponential family, categorical**: `A(eta) = log sum_k e^{eta_k}`,
  `A'(eta)_k = e^{eta_k} / sum_j e^{eta_j} = softmax_k`, `A''(eta)_k = p_k(1 - p_k)`. The
  variance relation gives the logistic-regression Hessian weight for free.
- **Softmax overflow**: logits `(800, 800)`. `exp(800) = Infinity` in double (overflow at
  ~709.78). With the shift: `m = 800`, `exp(0) + exp(0) = 2`, `800 + log 2 = 800.693`,
  probabilities `0.5, 0.5`. Without: `Infinity/Infinity = NaN`.
- **Beta-Binomial**: `alpha = 1, beta = 1`, 3 successes and 17 failures.
  Posterior `Beta(4, 18)`; predictive `4/22 = 0.1818`. Plug-in MLE: `3/20 = 0.15`. The prior
  moves a small-sample estimate toward 0.5, which is the intended behaviour.
- **Normal-Normal**: `sigma_0 = 1` (prior variance), `sigma = 0.5` (data variance,
  `1/sigma^2 = 4`), `n = 10`, `xbar = 2`. `tau^2 = 1/(1 + 40) = 0.0244`.
  `m = 0.0244 * (0*1 + 10*2*4) = 1.951`. The prior pulled the estimate from `2.0` to `1.95`,
  with weight `1/41`.
- **Perplexity**: a model with cross-entropy `2.303` nats per token gives perplexity `e^2.303
  = 10`. A uniform model over a 10,000-token vocabulary gives cross-entropy `log 10000 =
  9.21` and perplexity exactly 10,000.
- **KL asymmetry**: `p = (0.99, 0.01)`, `q = (0.5, 0.5)`.
  `D_KL(p||q) = 0.99*log(1.98) + 0.01*log(0.02) = 0.676 + 0.039 = 0.715`.
  `D_KL(q||p) = 0.5*log(0.505) + 0.5*log(50) = -0.342 + 1.956 = 1.614`.
  JS with `m = (0.745, 0.255)` is about 0.15 — bounded and moderate, where the two KLs
  disagree by more than a factor of two.
- **Convex rate**: `mu = 0.1`, `L = 10`, `eta = 1/L = 0.1`. The contraction factor per step is
  `1 - mu/L = 0.99`. To get within 1e-3 of optimality: `0.99^k = 1e-3` -> `k ≈ 687` steps.
  With momentum `beta = 0.9`: factor `= (1 - 0.9*sqrt(0.01))/(1 + 0.9*sqrt(0.01)) = 0.818` ->
  `k ≈ 71` steps. Nearly 10x fewer, from a `mu` and `L` that are both known.
- **Saddle point**: `f(x) = x - x^3` has `f'(0) = 0` and `f''(0) = 0`, with
  `f''(x) = -6x` so `f''(0) = 0` — degenerate. Perturbing by `+eps` escapes; GD from an
  exact `x = 0` start never moves. SGD's noise escapes it. This is the standard argument for
  noise as an implicit regularizer.
- **Eigenvalue precision**: a symmetric 4x4 with integer entries has a characteristic
  polynomial with coefficients near 100. Coefficient rounding at 1e-16 relative gives
  absolute error ~1e-14, and root-finding amplifies that; reported eigenvalues differ from the
  QR results in the 8th to 10th digit. QR iteration agrees to machine precision.

## Self-Check Questions

1. Compute the condition number of `A'A` for `cond(A) = 1e4`, and state how many digits of
   accuracy survive in double precision.
2. Compute `A'A` eigenvalues from `A`'s singular values `(4, 2, 0.5)`.
3. Verify `H(p,q) = H(p) + D_KL(p||q)` for `p = (0.3, 0.7)`, `q = (0.5, 0.5)`.
4. Compute `D_JS` for the same `p, q`.
5. Compute the Beta-Binomial predictive for `alpha = 2, beta = 3`, 5 successes, 2 failures.
6. Compute the posterior mean and variance of `mu` for a Normal-Normal update with
   `mu_0 = 0, sigma_0^2 = 4, sigma^2 = 1, n = 8, xbar = 1.5`.
7. Compute softmax for logits `(1000, 0, 0)` with and without the max shift; report both.
8. Compute the gradient descent contraction factor for `mu = 1, L = 100` at `eta = 1/L`, and
   the step count to reach 1e-6.
9. Compute the momentum contraction factor for the same problem with `beta = 0.95`.
10. Compute the exponential-family mean and variance for the categorical distribution with
    logits `(0, log 3)`.
11. Verify `cond(A'A) = cond(A)^2` numerically for a 3x3 with known singular values.
12. Compute the relative error in `1.0 - 0.9999999999999999` and explain.
