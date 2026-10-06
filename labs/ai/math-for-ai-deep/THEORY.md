# math-for-ai-deep — Theory

Track-level theory for the ten mathematics modules. Every section states the object, the
property that matters, and where AI actually breaks against it.

## 1. Vector Spaces

A vector space over `F` is a set with addition and scalar multiplication satisfying eight
axioms. For ML the practically important consequences:

- **Subspace**: closed under linear combination. In a neural network, the span of the
  activations is a subspace, and rank loss means the network has thrown information away.
- **Basis and dimension**: every vector is a unique combination of basis vectors. The number
  of basis vectors is the dimension — this is what "rank 3" means when a matrix loses rank.
- **Inner product**: `x'y = sum x_i y_i`, generalizing to cosine similarity, dot-product
  attention, and kernel methods.
- **Norm**: `||x||_2 = sqrt(x'x)`, `||x||_1 = sum |x_i|`, `||x||_inf = max |x_i|`. The choice
  of norm defines what "distance" means and which regularizer you get.
- **Orthogonality and Gram-Schmidt**: projection onto an orthonormal basis. Gram-Schmidt
  is what QR decomposition implements, and QR is what stable least squares uses.

## 2. Matrix Operations

```
A B  (n x p)(p x m) = (n x m):   C_ij = sum_k A_ik B_kj
A'   transpose; (A')_ij = A_ji
A^-1 exists iff det(A) != 0 iff rank(A) = n iff columns are linearly independent
```

- **Condition number** `cond(A) = sigma_max/sigma_min`: how much a vector can be stretched
  relative to the smallest direction. `cond(A'A) = cond(A)^2`, which is why nobody forms
  `A'A` to solve a least squares problem.
- **LU decomposition** with partial pivoting: `PA = LU`. Back-substitution gives an
  `O(n^3)` solve with a stability guarantee.
- **Cholesky** for positive definite matrices: `A = LL'`, half the cost, and the positive
  definiteness check is free.
- **Norms**: Frobenius `||A||_F = sqrt(sum A_ij^2)`, spectral `||A||_2 = sigma_max`, induced
  1-norm and infinity-norm. Spectral norm is the one that controls how much a layer can
  amplify — the quantity weight decay and Lipschitz arguments actually bound.

## 3. Eigenvalues and SVD

```
A v = lambda v        eigenvector v, eigenvalue lambda
A = P D P^-1         (diagonalizable)
A = U D V'            SVD, always exists, U and V orthogonal, D >= 0 sorted
```

- **Singular values** `sigma_i` are the `sqrt` of the eigenvalues of `A'A` — so SVD is
  numerically superior to the eigenvalue route and is what production code uses.
- **PCA** falls out directly: project onto the top right singular vectors of the centered
  data.
- **Condition number** `cond(A) = sigma_max / sigma_min`. A large value means the matrix is
  nearly singular: the inverse amplifies noise enormously.
- **Truncated SVD** `A_k = sum_{i<=k} sigma_i u_i v_i'` is the best rank-`k` approximation
  in both spectral and Frobenius norm — a theorem, not a heuristic, and the reason truncated
  SVD is the right low-rank approximation.
- **Symmetric vs general**: for a general matrix, eigenvalues can be complex, and the
  eigenvector basis may not exist. Symmetric matrices have real eigenvalues and an
  orthogonal eigenbasis, which is why eigendecomposition is used for covariance matrices.

## 4. Gradient and Vector Calculus

```
grad f   (vector, df/dx_i)             Jacobian J (m x n) for vector->vector
Hessian  H (n x n, symmetric)          directional derivative: grad f . u
chain rule: d/dx g(f(x)) = J_f' grad g
```

- The Jacobian's **condition number** governs how errors propagate through a layer; the
  spectral norm of `J` bounds the Lipschitz constant, which is the quantity relevant to
  adversarial robustness and to explaining why deep networks amplify perturbations.
- The Hessian gives curvature: at a critical point, `H` positive definite means a local
  minimum. Singular values of `H` predict convergence rates for Newton-type methods.
- Automatic differentiation is the chain rule applied systematically: forward mode
  differentiates a scalar through a computation (efficient for few inputs), reverse mode
  differentiates a scalar through many (efficient for few outputs — which is why backprop is
  reverse mode).

## 5. Probability Distributions

| Distribution | Form | Where it appears |
|--------------|------|------------------|
| Bernoulli | `{0,1}` | Single binary outcome |
| Binomial | `C(n,k) p^k (1-p)^(n-k)` | Counts of successes |
| Poisson | `lambda^k e^-lambda / k!` | Counts of arrivals |
| Exponential | `lambda e^-lambda t` | Wait times (memoryless) |
| Gaussian | `exp(-(x-mu)^2/(2 sigma^2))` | Nearly everything, by CLT |
| Categorical | `softmax(z)` | Every softmax layer |
| Dirichlet | over simplex | Class priors, Bayesian topic models |

- **Maximum entropy** argument for the Gaussian: it is the distribution on the reals with
  given mean and variance that assumes the least. That is why `L2` regularization and
  Gaussian priors are the defaults rather than a choice.
- **Exponential family**: `p(x) = h(x) exp(eta' T(x) - A(eta))`. Bernoulli, Gaussian,
  Poisson, and categorical all belong, and conjugate priors work because the sufficient
  statistics `T(x)` are fixed. This one structure explains most of Bayesian ML.
- **Moment matching**: matching the first two moments to a Gaussian is often sufficient and
  always cheap — the basis of the log-sum-exp trick's correctness.

## 6. Bayesian Inference

```
p(theta | D) proportional to p(D | theta) p(theta)
```

- **Conjugate prior**: Beta for Bernoulli, Gamma for Poisson, Normal for a Gaussian mean,
  Inverse-Gamma for a Gaussian variance. The posterior is in the same family and the
  hyperparameters update in closed form.
- **Beta-Binomial**: `alpha -> alpha + successes`, `beta -> beta + failures`. Concretely and
  worth memorizing.
- **MAP vs MLE**: MAP adds the prior; with a flat prior they coincide.
- **Full Bayes vs MAP**: full Bayes integrates over `theta`; MAP picks a point. Full Bayes
  is better but expensive, which is why the distinction matters in practice.
- **Variational inference**: approximate the posterior with a tractable family by minimizing
  the KL divergence. The ELBO is what you actually maximize:

```
ELBO = E_q[log p(D|theta)] - KL(q(theta) || p(theta))
```

The gap between ELBO and true log marginal likelihood is the **variational gap** — a
measurable quantity, and worth tracking.

## 7. Information Theory

```
H(X)      = -sum p log p                        entropy, in nats or bits
H(X|Y)    = conditional entropy
I(X;Y)    = H(X) - H(X|Y)                       mutual information
D_KL(p||q) = sum p log(p/q)                     KL divergence, >= 0
D_JS(p,q)  = (D_KL(p||m) + D_KL(q||m))/2, m = (p+q)/2
```

- **Chain rule** `H(X,Y) = H(X) + H(Y|X)` mirrors the chain rule of probability, which is why
  autoregressive factorization works at all.
- **KL is not a metric**: asymmetric, and `D_KL(p||p) = 0` with no triangle inequality. The
  Jensen-Shannon divergence is bounded, symmetric, and zero only at equality — which is why
  it is the right choice for monitoring distributions you cannot both fix as ground truth.
- **Cross-entropy is KL plus a constant**: `H(p, q) = H(p) + D_KL(p||q)`. Minimizing
  cross-entropy with a one-hot `p` is maximum likelihood.
- **Data processing inequality**: applying any channel cannot increase mutual information.
  This is the formal reason a lossy compression step cannot help retrieval quality.
- **Maximum entropy**: uniform is the highest-entropy distribution over a finite set.

## 8. Optimization Fundamentals

- **Convexity**: `f(ta + (1-t)b) <= t f(a) + (1-t) f(b)`. Any local minimum of a convex
  function is global. Non-convexity is why deep learning has no global guarantees.
- **Strong vs weak convexity**: strong convexity with parameter `mu > 0` gives
  `f(x*) <= f(x) - (mu/2)||x - x*||^2`, which is what guarantees an `O(1/k)` rate for
  gradient descent and turns a rate into a distance guarantee.
- **Lagrangian duality**: `L(x, lambda) = f(x) + lambda'(c(x) - b)`. Strong duality holds
  for convex problems. KKT conditions (stationarity, primal feasibility, dual feasibility,
  complementary slackness) are necessary and sufficient.
- **Saddle points**: negative semidefinite Hessian directions are why plain gradient descent
  stalls. Adding small noise (SGD) escapes them — which is part of why SGD generalizes
  better than full-batch GD on non-convex problems.
- **Ill-conditioning**: `cond(H)` bounds the convergence rate of first-order methods;
  Newton's rate depends on `lambda_min/lambda_max`.

## 9. Gradient Descent Variants

```
GD        w -= eta * mean(grad)                  full batch; slow, smooth
SGD       w -= eta * grad_i                      noisy, cheap, generalizes
Mini-batch w -= eta * mean(grad over B)           the practical default
Momentum  v = mu v + g;          w -= eta v
Nesterov  look ahead, then correct                better on ill-conditioned quadratics
AdaGrad   accum += g^2;          w -= eta g / sqrt(accum)   decays forever
RMSProp   EMA of g^2                                 forgets old gradients
Adam      m and v, bias-corrected                   the default
AdamW     Adam + decoupled decay                    correct weight decay
```

- **Noise as regularization**: SGD's gradient noise scales as `1/sqrt(B)`, so smaller batches
  are noisier and implicitly more regularized. This is the empirical reason batch size
  interacts with the learning rate rather than being independent.
- **Condition number and step size**: for `L`-smooth quadratic objectives, the stable step is
  `eta <= 2/L`. Too large does not merely slow convergence — it diverges.
- **Adam's state cost**: two extra parameter-sized arrays. At 7B parameters in FP32 that is
  56 GB of optimizer state — which is why optimizer-state sharding or 8-bit Adam exists.
- **Adaptive methods and generalization**: adaptive methods often fit training data better
  and generalize slightly worse on some tasks. Empirical, not a law, but reproducible
  enough to be worth testing.

## 10. Numerical Computing

- **IEEE 754 double**: 53 bits of mantissa, `eps = 2.2e-16`. Sums of order `1/eps ~ 4.5e15`
  terms lose all meaning.
- **Condition vs stability**: a well-conditioned problem solved with an unstable algorithm
  still produces a wrong answer. Two separate requirements.
- **Catastrophic cancellation**: `a - b` when `a ≈ b` loses digits proportional to the ratio.
  Example: `sqrt(2)^2 - 2` in double is ~`4.4e-16`, not 0.
- **The log-sum-exp trick**:

```
log sum exp(x_i) = m + log sum exp(x_i - m)     m = max(x_i)
```

  Without it, `exp(800)` overflows to infinity. This one line is what makes softmax and
  attention numerically stable, and it appears in every serious implementation.
- **Eigenvalue algorithms**: the characteristic polynomial is catastrophically
  cancellation-prone; QR iteration with shifts is stable. Never compute eigenvalues by
  expanding `det(A - lambda I)`.
- **Gram-Schmidt**: classical form loses orthogonality (`O(eps)`); modified (re-orthogonalize)
  or Householder QR is stable.

## Cross-Cutting Judgement

1. **Numerical stability is a design property, not a bug fix.** The log-sum-exp shift, QR
   over normal equations, and per-channel quantization scales all exist for the same reason.
2. **Condition number predicts everything.** If `cond(A)` is large, no algorithm will save
   you.
3. **Convexity determines what you can claim.** Never state a convergence guarantee for a
   non-convex objective without qualifying it.
4. **Automatic differentiation is the chain rule plus bookkeeping.** Understanding it makes
   every framework's behavior predictable.
