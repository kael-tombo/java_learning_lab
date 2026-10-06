# classical-ml-deep — Math Foundation

## 1. Normal Equations and Why You Should Not Invert

OLS minimizes `||y - Xw||^2`:

```
w* = argmin  (y - Xw)'(y - Xw) = argmin  y'y - 2w'X'y + w'X'Xw
d/dw: -2X'y + 2X'Xw = 0   =>   X'Xw = X'y
w* = (X'X)^-1 X'y
```

Two problems with the literal formula:

1. It requires `X'X` invertible. With an intercept, `X'X` is singular iff `X` has a
   linearly dependent column (including the column of ones).
2. Forming `X'X` squares the condition number: `cond(X'X) = cond(X)^2`. Working with
   `X` directly (QR or SVD) is numerically far better.

**Condition number demo**: `X` with `cond(X) = 1e6` gives `cond(X'X) = 1e12`, which in
double precision (~16 digits) leaves ~4 digits of signal. That is why standardization and
QR are not pedantry.

## 2. Ridge and the Geometry of Shrinkage

```
min_w  ||y - Xw||^2 + lambda * ||w||^2
=>  w*_ridge = (X'X + lambda I)^-1 X'y
```

Ridge shrinks toward zero, always (no coefficient becomes exactly zero for `lambda > 0`),
and is equivalent to adding `sigma^2/lambda` to the noise variance — a Bayesian prior
`w ~ N(0, tau^2 I)` with `lambda = sigma^2/tau^2`.

Lasso adds an `L1` penalty, which is non-differentiable at zero and yields **exact**
zeros: the constraint region has corners, and the optimum sits at a corner.

**Ridge trace**: with standardized features and `lambda` from `0` to `100`, the L2 norm
of `w` decays smoothly toward zero. With L1, the norm decays and then plateaus at the
sparsity level chosen by `lambda`. That shape is the practical difference.

## 3. Logistic Regression: The Odds Form

```
p = sigmoid(z), z = w'x
odds = p/(1-p) = e^z        =>   log-odds = z = w'x
```

So the model is linear in log-odds. `exp(b_j)` is the odds multiplier for feature `j`
per unit. With feature scaling, interpret per standard deviation.

Cross-entropy gradient is remarkably clean:

```
dL/dz = p - y
```

which is why logistic regression trains stably under plain gradient descent — no
saturation, no vanishing gradient, regardless of how large `z` gets.

## 4. Separation and Divergence

If the classes are perfectly separable, the likelihood is maximized by sending `|w| ->
infinity`, and the loss approaches 0 without ever reaching a finite optimum. Symptoms:
coefficients in the thousands, probabilities at exactly 0 and 1, enormous standard
errors.

Fixes: ridge (`lambda > 0`), a bounded-link reparameterization, or Bayesian priors.
Detection: check for `|z| > 10` on training rows.

## 5. Information Gain, Gini, and Gain Ratio

Entropy and Gini for a split `S -> {S_v}` with class probabilities `p_c`:

```
H(S)   = -sum_c p_c log2 p_c
Gini(S) = 1 - sum_c p_c^2

gain(S,A)     = H(S) - sum_v |S_v|/|S| * H(S_v)
gainRatio(A)  = gain(S,A) / H(A)          H(A) = entropy of the split values
```

Note `gainRatio <= 1` always, with equality only when the partition is pure in `A`. The
normalization is exactly the fix for ID3's bias: an ID with 1,000 values can drive
weighted-conditional entropy near zero while carrying no information.

Gini is a special case of entropy in the limit: with `alpha -> 0`, `H_alpha` differs
from Gini only by a constant factor, so they rank splits nearly identically. Which is why
ID3 and CART give similar trees on clean data.

## 6. Boosting: Second-Order Expansion

Expand the loss to second order around the current prediction `F(x)`:

```
L(y, F+f) ~ L(y,F) + g*f + 0.5*h*f^2
g = dL/dF,   h = d2L/dF2
```

Under squared error, `g = y - F` (the residual) and `h = 1` — plain residual fitting.
Under logistic loss, `g = p - y` and `h = p(1-p)`, so **observations the model is already
confident about get down-weighted automatically**. That is boosting's built-in sample
weighting.

Optimal constant `f` for a leaf `L`: minimize `sum_{i in L} g_i f + 0.5 h_i f^2 + lambda f^2`:

```
f* = -sum g_i / (sum h_i + lambda) = -G / (H + lambda)
```

`lambda` penalizes leaves with few, high-curvature samples; without it, a leaf with
`H = 0` (every `p` at 0 or 1) gives an unbounded optimum.

## 7. Learning Rate and Tree Count

For a convex-approximation model, generalization error behaves like

```
err(n) ~ err_infinity + c / (eta * n)
```

Halving `eta` requires roughly doubling `n` for the same fit, but produces a **smoother
approximation** and usually generalizes better. The practical consequence: `eta = 0.03`
with early stopping is safer than `eta = 0.3` with a fixed budget, and it is
indistinguishable in final error.

## 8. PCA From Eigenvalues and From SVD

Center `X` so each column has mean 0. Then `X'X / (n-1)` is the covariance matrix `S`.
Eigendecompose `S = U D U'`. The eigenvectors in `U` are the principal directions.

The SVD route: `X = P D Q'` with centered `X`. Then `X'X = Q D^2 Q'`, so

```
eigenvalues(S) = d_i^2 / (n-1),   eigenvectors = columns of Q
```

SVD is preferred because it never forms `X'X` (avoiding the squared condition number)
and gives singular values directly. Reconstruction with `k` components:

```
X_hat = sum_{i<=k} d_i * u_i * v_i'
reconstruction error = sum_{i>k} d_i^2
```

## 9. K-Means Objective and Convergence

```
J(C) = sum_k sum_{i in C_k} ||x_i - mu_k||^2
```

Lloyd's algorithm monotonically decreases `J`: the assign step sets each point to the
nearest current center (which can only lower `J`), and the update step is the exact mean,
the minimizer for a fixed partition. So `J` is monotone decreasing and `J` decreases by
at most a constant factor per iteration, giving finite convergence.

Weakness: the objective has `k`-local-minima structure. `k-means++` seeding samples
`O(log k)` centers with `D^2` weighting, giving `O(log k)` approximation to the optimum
in expectation — which is why it beats random seeding so consistently.

## 10. DBSCAN Reachability

- **Core point**: at least `minPts` points within distance `eps`, including itself.
- **Density-reachable**: a path `p = p_1, ..., p_m = q` where each step is within `eps`.
- **Border**: not core, but density-reachable from a core point.
- **Noise**: neither.

Cluster = all points density-reachable from a core point, plus the border points. Because
core points are linked transitively, clusters can be any shape. Density-reachability is
not symmetric, which is exactly why border points need a separate label.

## 11. Anomaly Score Distributions and Why Precision Collapses

If `pi` is the anomaly rate, `TPR` the recall, `FPR` the false-positive rate:

```
precision = TPR*pi / (TPR*pi + FPR*(1-pi))
```

With `TPR = 0.95`, `FPR = 0.01`: `pi = 0.01 -> 0.49`; `pi = 0.001 -> 0.087`. The same
detector that looks excellent on a balanced benchmark becomes a coin flip in production.

**Threshold choice**: if `C_FN` is the cost of a missed anomaly and `C_FP` the cost of a
false alarm, the threshold `t*` minimizes expected cost when

```
C_FN * P(anomaly | score = t*) = C_FP * P(normal | score = t*)
```

i.e. at a specific posterior odds. That posterior odds is a business number, not a
modelling one.

## 12. Bias-Variance Decomposition

For squared error at a point `x`:

```
E[(Y - f_hat(x))^2] = bias^2 + variance + sigma^2 (irreducible)
```

- **Linear/logistic models**: high bias, low variance. Underfit on complex structure.
- **Single deep tree**: low bias, high variance. Overfits noise.
- **Random forest**: reduces variance by averaging decorrelated trees; bias rises
  slightly because each tree sees less data and fewer features.
- **Boosting**: reduces bias by fitting residuals stage by stage; the trees themselves stay
  high-variance and heavily regularized.

**Bagging vs boosting** in one line: bagging lowers variance at constant bias; boosting
lowers bias at roughly constant variance.

## 13. L2 Norm Equivalences

```
||w||_2^2 = sum w_j^2        = ||A||_F^2 when A is a 1 x p row of weights
||w||_1   = sum |w_j|        (sparse-inducing)
||w||_p   = (sum |w_j|^p)^(1/p)
```

These are interchangeable regularizers with different geometry: `L2` balls are spheres
(smooth, dense solutions), `L1` balls are diamonds (corners on axes, exact zeros). From
a Bayesian view: `L2` is a Gaussian prior, `L1` a Laplace prior.

## Worked Numbers

Dataset: `n = 500`, `p = 5` standardized features, `y` with `sigma = 1`, true model
linear with `R^2 = 0.6`.

- **Ridge sweep**: at `lambda = 0`, condition number of `X'X` ~ 1.2 (well conditioned).
  At `lambda = 10`, effective `||w||_2` drops ~35%, train RMSE rises from 0.63 to 0.66,
  test RMSE falls from 0.79 to 0.73. Report both numbers.
- **Gain ratio**: feature A splits 100 ways with gain 0.95; feature B splits 2 ways with
  gain 0.30. `H(A_A) ~ 6.6`, so gain ratio A = 0.14; `H(A_B) = 1.0`, gain ratio B = 0.30.
  ID3 picks A, C4.5 picks B.
- **Boosting leaf weight**: leaf with 8 samples, `G = 1.6`, `H = 4.0`.
  `lambda = 1` -> `f* = -1.6/5.0 = -0.32`.
  `lambda = 0` -> `-1.6/4.0 = -0.40`, and with `H = 0.1` -> `-16.0`, which is the
  overfitting failure mode `lambda` exists to prevent.
- **PCA**: first component explains 0.41 of the variance, the first two 0.62, first three
  0.74. For 95% you need `k = 5` (all of them) — which is the honest answer for this data.
- **k-means**: `J` at `k=2..8` = 412, 288, 241, 224, 218, 214, 213. The elbow is at 4;
  silhouette peaks at 3; the gap statistic flattens after 4. Report the disagreement
  rather than picking silently.
- **DBSCAN**: `k=5` distance plot elbow at `eps = 0.42`. At `eps = 0.30` all 60 points
  are noise; at `eps = 0.55` two true clusters merge into one. The usable band is
  `eps in [0.40, 0.46]` — a 15% band, which is why `eps` is a knee, not a dial.
- **Anomaly**: `pi = 0.005`, `TPR = 0.92`, `FPR = 0.008`. In 100,000 transactions:
  true anomalies 500, caught 460, false alarms 800. Precision = 460/1260 = **0.365**.
  Accuracy = 99.3% — a number that describes nothing.

## Self-Check Questions

1. Explain why `cond(X'X) = cond(X)^2` matters numerically.
2. Derive `-G/(H+lambda)` from the second-order expansion.
3. Compute the precision at `pi = 0.02`, `TPR = 0.95`, `FPR = 0.01`.
4. Show that L1 yields exact zeros while L2 does not, using the geometry of the penalty
   ball.
5. Prove Lloyd's algorithm monotonically decreases `J`.
6. Compute the effective leaf weight for `G = -2.2`, `H = 3.5`, `lambda = 0.5`.
7. Explain why a single `eps` fails on a two-density dataset, referencing reachability.
8. Given a two-moons dataset, say which of k-means and DBSCAN fails and why.
