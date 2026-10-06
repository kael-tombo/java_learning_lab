# classical-ml-deep — Mini Project

## Project: A Tabular ML Workbench in Java 21

Build an end-to-end tabular machine learning workbench from scratch: a matrix library, five
model families, four clustering algorithms, three dimensionality-reduction methods, three
anomaly detectors, a full evaluation suite, and a model card generator. No external
dependencies.

## Goal

`Main` loads a CSV, runs a baseline ladder, reports metrics per model, tunes thresholds on
the PR curve, hunts for leakage, and writes `REPORT.md` containing a defensible model
card.

## Requirements

### Phase 1: Linear Algebra Core
- [ ] Matrix multiply, transpose, matrix-vector, norm, mean, variance.
- [ ] QR solve (Householder) and Cholesky solve; assert they agree.
- [ ] Eigen-decomposition of a symmetric matrix (Jacobi); all eigenvalues positive.
- [ ] SVD (one-sided Jacobi); singular values match eigenvalues of `A'A`.
- [ ] Assert `cond(X'X) = cond(X)^2` on a matrix with a known condition number.

### Phase 2: Data Frame and Preprocessing
- [ ] CSV reader with a typed schema; missing values as `Double.NaN`.
- [ ] Mean/median imputation with an indicator column; fit on train only.
- [ ] Standardization; inverse transform to verify round-trip error < 1e-12.
- [ ] Categorical encoding: one-hot and ordered target statistics (with the ordering
      derived from train rows only — this is where leakage happens).
- [ ] Train/validation/test split with a single seed; assert no row overlap.

### Phase 3: Regression Models
- [ ] OLS via QR; R^2, adjusted R^2, RMSE, MAE.
- [ ] Ridge and Lasso (coordinate descent); sparsity curve for Lasso.
- [ ] Regression trees with variance-reduction splits; pruning path.
- [ ] Gradient boosting for regression with learning-rate sweep.

### Phase 4: Classification Models
- [ ] Logistic regression by gradient descent **and** IRLS; compare iterations and loss.
- [ ] Softmax multiclass.
- [ ] Random forest with OOB error and permutation importance.
- [ ] Gradient boosting with logistic loss; probability calibration (isotonic) and a
      reliability diagram.

### Phase 5: Kernel Models
- [ ] Linear SVM by subgradient descent.
- [ ] Soft-margin SVM via SMO (pair selection, two-variable analytic update, KKT).
- [ ] RBF and polynomial kernels; PSD check on a 50-point kernel matrix.
- [ ] SVR with the epsilon tube; count support vectors inside and outside.

### Phase 6: Unsupervised
- [ ] k-means with `k-means++`; assert monotone `J`; Elbow, silhouette, gap statistic.
- [ ] DBSCAN with knee-selected `eps`; core/border/noise classification.
- [ ] Agglomerative clustering, four linkage methods; dendrogram cut by silhouette.
- [ ] PCA by SVD; explained variance; reconstruction error; a 2D scatter plot in text.
- [ ] Kernel PCA with an RBF kernel on two-moons; compare to linear PCA.

### Phase 7: Anomaly Detection
- [ ] Z-score, IQR, Isolation Forest, LOF, autoencoder reconstruction error.
- [ ] PR-AUC for each at contamination rates 0.5%, 1%, 5%.
- [ ] Cost-optimal threshold with `C_FN = 100 * C_FP` and the confusion matrix at it.
- [ ] A demonstration that plain accuracy is uninformative at these rates.

### Phase 8: Evaluation and Diagnostics
- [ ] Full metric suite: accuracy, precision, recall, F1, ROC-AUC, PR-AUC, MCC,
      confusion matrix at a chosen threshold.
- [ ] Learning curves (train vs validation) to diagnose bias vs variance.
- [ ] Residual plots as ASCII histograms; a funnel shape must be detectable.
- [ ] Feature importance from permutation, with the impurity-importance contrast.
- [ ] Calibration curve and expected calibration error.

### Phase 9: Leakage Hunt
- [ ] Deliberately add a label-derived feature; record the inflated score.
- [ ] Remove it; record the drop.
- [ ] Also test: fitting a scaler on all data, and a target encoder built on all rows.
- [ ] A CI-style check that fails when any preprocessing touches validation data.

### Phase 10: Model Card
- [ ] Dataset description, target, class balance, preprocessing steps with parameters.
- [ ] Metrics for the baseline ladder, one line per rung.
- [ ] Chosen model, hyperparameters, and the tuning protocol.
- [ ] Threshold and the operating-point confusion matrix.
- [ ] Known failure modes and slice metrics (performance by group).

## Directory Layout

```
classical-ml-deep/
  src/com/ailab/classical/
    linalg/{Mat,Eigen,Svd,Dist}.java
    data/{DataFrame,CsvReader,Preprocess}.java
    linear/{Ols,Ridge,Lasso,Logistic,Softmax,SgdClassifier}.java
    svm/{LinearSvm,Smo,Kernel,Svr}.java
    tree/{DecisionTree,RandomForest,Boosting,Histogram}.java
    unsup/{KMeans,Dbscan,Agglomerative,Pca,KernelPca}.java
    anomaly/{ZScore,Iqr,IsolationForest,Lof,Autoencoder}.java
    eval/{Metrics,Calibration,LearningCurve,Leakage}.java
    report/ModelCard.java
  Main.java
  REPORT.md
```

## Milestones

1. **M1** — matrix core; QR and Cholesky agree to 1e-10.
2. **M2** — eigen and SVD; singular values verified against `A'A` eigenvalues.
3. **M3** — DataFrame, split, preprocessing with a leakage-proof fit discipline.
4. **M4** — OLS, ridge, Lasso; sparsity curve plotted.
5. **M5** — logistic by GD and IRLS; convergence comparison in the report.
6. **M6** — trees, random forest with OOB, permutation importance.
7. **M7** — gradient boosting with lambda leaf penalty and early stopping.
8. **M8** — SMO and kernels; PSD check green.
9. **M9** — k-means, DBSCAN, agglomerative, PCA, kernel PCA.
10. **M10** — anomaly suite; PR-AUC table at three contamination rates.
11. **M11** — calibration and learning curves.
12. **M12** — leakage hunt completed and documented.
13. **M13** — baseline ladder with incremental value per rung.
14. **M14** — model card written.

## Acceptance Criteria

- [ ] QR and Cholesky solves agree to 1e-10 on a well-conditioned system.
- [ ] SVD singular values equal `sqrt(eigenvalues(A'A))` to 1e-9.
- [ ] Ridge leaves no exact zeros; Lasso produces at least one exact zero.
- [ ] Logistic regression reaches the same loss via GD and IRLS.
- [ ] k-means `J` is monotonically non-increasing on every iteration.
- [ ] DBSCAN classifies border and noise points correctly on a hand-checked example.
- [ ] PCA reconstruction error at `k` equals the tail sum of squared singular values.
- [ ] Isolation Forest beats the z-score baseline on PR-AUC at all three rates.
- [ ] Model card reports PR-AUC, not accuracy, for the imbalanced task.
- [ ] Leakage check fails when a scaler is fit on validation data.
- [ ] Every metric is reproducible from a fixed seed.
- [ ] Slice metrics reported for at least three groups.
- [ ] Runtime reported for fit and predict separately.

## Stretch Goals

- [ ] LightGBM-style histogram binning with quantile sketches; match exact split search.
- [ ] GOSS sampling: match full-data AUC within 0.5%.
- [ ] Elkan's k-means acceleration with an operation count.
- [ ] HDBSCAN-style density-based clustering without `eps`.
- [ ] One-class SVM as a fifth anomaly detector.
- [ ] Gradient boosting with early stopping driven by a PR-AUC plateau.
- [ ] A textual confusion-matrix heatmap renderer.
- [ ] Autoencoder with two hidden layers trained by hand-written backprop.

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| Coefficients in the thousands | Perfect separation; add ridge |
| Logistic model stuck at chance | Optimizing 0/1 error, or a non-standardized feature |
| Tree identical to a stump | `min_samples_leaf` too high, or max_depth too low |
| Forest no better than one tree | Correlated trees: too few trees, or `mtry` at its extreme |
| Boosting overfits after 20 rounds | Learning rate too high, or no validation-based early stop |
| `J` increases in k-means | Wrong assignment or update ordering |
| DBSCAN returns one giant cluster | `eps` too large; check the k-distance plot |
| DBSCAN returns all noise | `eps` too small or `minPts` too high |
| PCA component points the wrong way | Sign convention ambiguity; eigenvectors are defined up to sign |
| Anomaly precision near 0.1 | Imbalance; tune the threshold, do not blame the model |
| Perfect test score | Leakage; run the leakage hunt |

## Definition of Done

`REPORT.md` contains: the matrix core verification results (QR vs Cholesky, SVD vs
eigenvalues, the condition-number demonstration), the dataset summary with class balance,
the preprocessing pipeline with every parameter, the baseline ladder with per-rung
metrics and incremental value, the final model with hyperparameters and the tuning
protocol, calibration curve and expected calibration error, learning curves diagnosing
bias vs variance, the leakage-hunt results including the inflated score and the corrected
score, the anomaly detection PR-AUC table at three contamination rates with
cost-optimal thresholds, clustering results with elbow/silhouette/gap for k-means and the
knee-selected `eps` for DBSCAN, PCA explained variance and a 2D projection description,
feature importance with the impurity-vs-permutation contrast, slice metrics for three
groups, fit and predict runtimes, and a list of known failure modes with a mitigation for
each.
