# classical-ml-deep — Flashcards

60 rows. Cover the answer column, recall it, then check. Last column is the module.

| # | Question | Answer | Module |
|---|----------|--------|--------|
| 1 | OLS closed form? | `w = (X'X)^-1 X'y`; in code use QR or SVD, never an explicit inverse | 01 |
| 2 | When is OLS identifiable? | Only when `X'X` is full rank — no exact collinearity | 01 |
| 3 | R^2 can what? | Rise as you add junk features | 01 |
| 4 | Adjusted R^2 penalizes what? | Parameter count, so it can fall where R^2 rises | 01 |
| 5 | Multicollinearity harms what? | Coefficient interpretability and variance, not predictions much | 01 |
| 6 | Condition number above ~1e10 means? | Coefficients are numerically meaningless | 01 |
| 7 | Logistic regression decision rule? | `p = sigmoid(w'x)`, compare `p` to 0.5 | 02 |
| 8 | Binary cross-entropy? | `-(1/n) sum[ y log p + (1-y) log(1-p) ]` | 02 |
| 9 | Why not optimize 0/1 error? | Non-differentiable; the model stalls at initialization | 02 |
| 10 | `exp(b)` for a logistic coefficient means? | The multiplicative change in odds per unit feature | 02 |
| 11 | IRLS / Newton-Raphson needs? | A Hessian inverse; converges in ~5-8 iterations on small data | 02 |
| 12 | Perfect separation causes? | MLE coefficients diverge; ridge or a prior fixes it | 02 |
| 13 | Multiclass logistic generalization? | Softmax over `w_y'x` with the same log-loss | 02 |
| 14 | SVM primal objective? | Minimize `||w||^2` subject to `y_i(w'x_i+b) >= 1` | 03 |
| 15 | The dual buys you? | The kernel trick; only support vectors get non-zero coefficients | 03 |
| 16 | Support vectors are? | Points on or inside the margin, `y_i(w'x_i+b) <= 1` | 03 |
| 17 | RBF kernel? | `exp(-gamma * ||x - x'||^2)`; `gamma` needs tuning | 03 |
| 18 | SVM weakness on `n`? | Quadratic or worse in training samples; use kernels | 03 |
| 19 | SVM probabilities? | None natively; Platt scaling is a post-hoc approximation | 03 |
| 20 | SVR tube? | Epsilon-insensitive: zero loss within `+-eps`, points inside are not support vectors | 03 |
| 21 | ID3 criterion? | Information gain | 04 |
| 22 | CART criterion? | Gini impurity for classification, variance reduction for regression | 04 |
| 23 | Gini impurity? | `1 - sum_c p_c^2` | 04 |
| 24 | C4.5's fix for cardinality bias? | Gain ratio: gain divided by `H(A)` | 04 |
| 25 | Trees are invariant to? | Feature scaling — the first such algorithms | 04 |
| 26 | Trees are high-? | Variance: one rotation of the data changes the whole tree | 04 |
| 27 | Regression trees split on? | Reduction in within-node variance | 04 |
| 28 | Missing values in trees? | Surrogate splits, or route missing to the majority branch | 04 |
| 29 | Cost-complexity pruning? | Prune leaves while `R_alpha(T) = R(T) + alpha |leaves|` does not increase | 04 |
| 30 | Bootstrap unique-sample fraction? | `1 - (1-1/n)^n -> 1 - 1/e ~ 63.2%` | 05 |
| 31 | Forest `mtry`? | `sqrt(p)` classification, `p/3` regression | 05 |
| 32 | OOB error needs? | No holdout: each tree predicts its own held-out third | 05 |
| 33 | Impurity importance's flaw? | Biased toward high-cardinality features; use permutation importance | 05 |
| 34 | Boosting form? | `F_M(x) = F_0(x) + sum_m eta * h_m(x)` fitted to negative gradients | 06 |
| 35 | XGBoost's Taylor expansion adds? | A second-order term, giving closed-form optimal leaf weights | 06 |
| 36 | Optimal leaf value? | `-G / (H + lambda)` | 06 |
| 37 | XGBoost histogram splitting? | Bin features into ~64 quantile buckets, search splits on bin boundaries | 06 |
| 38 | LightGBM GOSS? | Keep top-`A` gradient rows, subsample the rest, rescale to compensate | 06 |
| 39 | LightGBM EFB? | Bundles mutually exclusive sparse features into one | 06 |
| 40 | CatBoost ordered TS? | Category statistics from prior rows only, avoiding target leakage | 06 |
| 41 | Learning rate vs tree count? | Trade off: halve `eta`, roughly double estimators | 06 |
| 42 | PCA steps? | Center, eigendecompose the covariance, keep top `k` eigenvectors | 07 |
| 43 | PCA via SVD? | Same result, better numerics, avoids forming `X'X` | 07 |
| 44 | Explained variance ratio? | `lambda_i / sum_j lambda_j`; cumulative curve chooses `k` | 07 |
| 45 | PCA's blind spot? | It maximizes variance, not class separation | 07 |
| 46 | K-means objective? | Within-cluster sum of squares, `J = sum_k sum_{x in C_k} ||x-mu_k||^2` | 08 |
| 47 | k-means++ improves? | Initialization, which matters more than the convergence threshold | 08 |
| 48 | Silhouette measures? | Within-cluster cohesion versus nearest-other-cluster separation, per point | 08 |
| 49 | Gap statistic? | Observed within-cluster dispersion versus a uniform reference | 08 |
| 50 | K-means assumption? | Spherical, similarly sized clusters; breaks on elongated or nested shapes | 08 |
| 51 | Elkan's speedup? | Triangle inequality pruning of distance computations | 08 |
| 52 | DBSCAN parameters? | `eps` and `minPts`; choose `eps` at the knee of the k-distance plot | 09 |
| 53 | Core / border / noise? | `minPts` neighbors within `eps` / reachable from core but not core / neither | 09 |
| 54 | DBSCAN's weakness? | One global `eps` cannot serve regions of differing density | 09 |
| 55 | HDBSCAN advantage? | No `eps` at all; variable-density clusters plus stability-based extraction | 09 |
| 56 | Single-linkage pathology? | Chaining — distant points merge through a chain of neighbors | 09 |
| 57 | Agglomerative memory? | Full `n^2` distance matrix; does not scale past a few thousand rows | 09 |
| 58 | Isolation Forest principle? | Anomalies are few and lie in sparse regions, so short random paths isolate them | 10 |
| 59 | LOF detects? | Low-density points relative to their `k` neighbors, not just global outliers | 10 |
| 60 | Imbalanced detector reporting? | PR-AUC and the confusion matrix at the shipping threshold — never plain accuracy | 10 |
