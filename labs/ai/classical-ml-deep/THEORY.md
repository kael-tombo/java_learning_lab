# classical-ml-deep — Theory

Track-level theory for the ten classical ML modules. Each section states the mechanism,
the assumption, and the failure mode — because the third one is what interviews and
incidents actually test.

## 1. Linear Regression

`y = Xw + b`. The OLS solution `w = (X'X)^-1 X'y` is optimal only when `X'X` is
invertible. Practitioners use QR or SVD instead of an explicit inverse, because the
inverse exists only in exact arithmetic.

- **Assumption**: linearity in parameters, independent homoscedastic errors.
- **Diagnosis**: residual plots show curvature you have not modeled; heteroscedasticity
  shows as a funnel.
- **Failure mode**: multicollinearity inflates coefficient variance without changing
  predictions. Condition number above ~1e10 makes the coefficients meaningless.
- Fixes: standardize, drop or combine collinear features, ridge regardless.

## 2. Logistic Regression

`sigmoid(w'x)` with log-odds linear in parameters. **Optimize log-loss, never raw
0/1 error** — 0/1 is non-differentiable and will silently give you a model at init.

- `logloss = -(1/n) * sum[ y*log(p) + (1-y)*log(1-p) ]`
- Newton-Raphson / IRLS converges in ~5-8 iterations; use it when `n` is small and
  `p` is small.
- Coefficients are log-odds ratios; `exp(b)` is the odds ratio.
- Multiclass: softmax with the same loss, mutually exclusive classes.

## 3. SVM

Maximize the margin: `min ||w||^2` subject to `y_i(w'x_i + b) >= 1`. The dual form
exposes the kernel trick and shows only support vectors matter.

- **SVM**: strong with small `n`, high dimension, hard margins; scales badly in `n`.
- **SVR**: epsilon-insensitive tube; the loss is zero inside the tube.
- **RBF kernel**: `exp(-gamma * ||x - x'||^2)`. `gamma` must be tuned — the default
  (`1/(p * var)`) is usually wrong.
- Failure: no native probabilities (Platt scaling is a post-hoc approximation),
  sensitive to feature scale, and memory-hungry in kernel mode.

## 4. Decision Trees

Split selection: ID3 uses information gain, C4.5 uses gain ratio (fixes the bias toward
high-cardinality features), CART uses Gini for classification and variance reduction for
regression.

```
gain(S, A) = H(S) - sum_v (|S_v|/|S|) * H(S_v)
gini(S)    = 1 - sum_c p_c^2
```

- Trees are invariant to feature scaling — the first algorithm where that is true.
- They are high-variance: a single rotation of the data changes the whole tree.
- Missing values: surrogate splits, or route missing to the majority branch.

## 5. Random Forest

Bootstrap aggregation plus random subspace at each split. Two independent sources of
randomness decorrelate the trees, which is the entire point.

- **OOB error**: each tree's held-out third gives a free validation estimate — no
  separate split needed.
- Feature importance from permutation on OOB data, not from impurity decrease. Impurity
  importance is biased toward high-cardinality features.
- `mtry = sqrt(p)` for classification, `p/3` for regression.
- Probability = mean of tree votes. Correlated trees make this narrower than it looks.

## 6. Gradient Boosting

Forward stagewise additive model, each stage fitting the negative gradient of the loss.

```
F_M(x) = F_0(x) + sum_m eta * h_m(x)
```

- **XGBoost**: second-order Taylor expansion, explicit `lambda` on leaf weights,
  histogram binning with quantile sketching, exact and approximate split finding.
- **LightGBM**: GOSS (sample high-gradient rows, subsample the rest) and EFB (bundle
  mutually exclusive sparse features).
- **CatBoost**: ordered target statistics, which removes the target-leakage-in-CV problem
  that naive category encoding creates.
- Learning rate and tree count trade off against each other — halve one, double the other.

## 7. PCA

Center, compute the covariance matrix, eigendecompose, keep the top `k` eigenvectors.
Equivalently: SVD of the centered data matrix. SVD is numerically better and skips
forming `X'X`.

- Explained variance ratio `lambda_i / sum(lambda)`.
- **PCA is unsupervised**: it maximizes variance, not class separation. On data where the
  top variance direction is nuisance, PCA destroys the signal.
- Fit on train only. Fitting on train+test leaks test variance into the projection.

## 8. K-Means

Minimize within-cluster sum of squares (WCSS). Lloyd's algorithm: assign, then recompute.

```
J = sum_k sum_{x in C_k} ||x - mu_k||^2
```

- `k-means++` initialization matters far more than the convergence criterion.
- Elbow, silhouette, and gap statistic answer different questions; report all three.
- Elkan for large `k`, Hartigan-Wong when clusters are wildly unequal in size.
- Assumption: spherical, similarly-sized clusters. Fails on elongated or nested shapes.

## 9. DBSCAN and Hierarchical Clustering

DBSCAN: two parameters, `eps` and `minPts`. Density-reachable from a core point.
Classifies points as core, border, or noise.

- **Knee point of the k-distance plot**, not a guessed `eps`.
- It finds arbitrary shapes and identifies noise — the reason to prefer it over k-means.
- HDBSCAN removes `eps` entirely; OPTICS gives an ordering over a family of `eps`.
- Failure: varying density (one global `eps` cannot serve both) and high `p`.

Hierarchical clustering: agglomerative with linkage (single, complete, average, Ward).
`n^2` memory for the full distance matrix — it does not scale past a few thousand rows.

## 10. Anomaly Detection

| Method | Assumption | Cost |
|--------|-----------|------|
| z-score | Gaussian | O(n) |
| IQR | Quartile spread | O(n log n) |
| Isolation Forest | Anomalies are few and different | O(n log n) |
| LOF | Density relative to k neighbors | O(n^2) brute force |
| One-class SVM | Boundary in feature space | O(n^2)-O(n^3) |
| Autoencoder | Anomalies reconstruct poorly | one training run |

- Precision collapses when the anomaly rate is below ~1%. Report PR-AUC, never
  accuracy on an imbalanced detector.
- **Supervised** anomaly detection (labels of known anomalies) beats all of the above
  whenever the labels exist.
- Threshold selection is a business decision: the cost of a missed fraud vs a blocked
  legitimate transaction.

## Cross-Cutting Judgement

1. **Start with a linear or tree baseline.** Gradient boosting on tabular data is the
   default ceiling-setter, but a logistic baseline tells you how much of the problem is
   actually signal.
2. **Scaling matters only to linear and kernel models.** Trees and forests ignore it.
3. **Imbalance is not solved by class weights alone.** Measure PR-AUC, tune the threshold
   on the PR curve, and check the confusion matrix at the operating point you ship.
4. **Every one of these models can be wrong in a new way.** Write the failure mode down
   next to the metric; it survives longer than the notebook does.
