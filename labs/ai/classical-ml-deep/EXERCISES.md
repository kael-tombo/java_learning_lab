# classical-ml-deep — Exercises

Difficulty: **E** easy, **M** medium, **H** hard. All Java 21, no external dependencies.
`double[][]` matrices, hand-written loops, deterministic seeds.

## Module 01 — Linear Regression

- [ ] **E1.1** OLS by normal equations on a 3x2 design matrix. Compare against a
      QR-based solve. Assert the two agree to 1e-9.
- [ ] **E1.2** Compute R^2 and adjusted R^2 on a held-out split. Show adjusted R^2
      *dropping* while R^2 rises when you add a junk feature.
- [ ] **E1.3** Gradient descent on the same problem with 3 learning rates. Log the loss
      per epoch; mark the divergence case.
- [ ] **M1.4** Add two perfectly collinear columns. Report the condition number and the
      coefficient magnitudes. Explain why predictions are fine and coefficients are not.
- [ ] **M1.5** Ridge regression with a feature-standardization step. Sweep lambda and
      plot coefficient norm versus lambda.
- [ ] **H1.6** Diagnose heteroscedasticity: generate errors with variance proportional
      to `x`, fit OLS, and show the residual funnel. Then fit on log(y) and compare.

## Module 02 — Logistic Regression

- [ ] **E2.1** Sigmoid with numerically stable branches for `x < -35` and `x > 35`.
- [ ] **E2.2** Gradient descent on binary cross-entropy. Show that optimizing 0/1 error
      stalls while log-loss converges.
- [ ] **E2.3** IRLS / Newton-Raphson to convergence. Report iteration count and compare
      the objective against gradient descent at equal wall time.
- [ ] **M2.4** Softmax multiclass with a numerically stable log-sum-exp. Verify rows of
      the probability matrix sum to 1.
- [ ] **M2.5** Interpret coefficients as log-odds; convert to odds ratios. Sanity-check
      one coefficient against a manual two-row computation.
- [ ] **H2.6** Simulate perfect separation. Show MLE coefficients diverge, then add
      ridge and report the recovery.

## Module 03 — SVM

- [ ] **E3.1** Hard-margin linear SVM by subgradient descent on a separable toy set.
- [ ] **E3.2** Count support vectors; verify points strictly outside the margin have zero
      dual coefficients.
- [ ] **E3.3** KERNEL evaluation for linear, polynomial, and RBF. Prove the RBF kernel
      matrix is symmetric positive semi-definite for 50 random points via eigenvalues.
- [ ] **M3.4** Soft-margin with slack, sweep `C`, plot the margin width and error rate.
- [ ] **M3.5** SMO by hand: one pair selection, two-variable analytic update, KKT check.
- [ ] **H3.6** SVR with the epsilon tube. Count support vectors inside versus outside and
      verify the dual coefficients are zero on interior points.

## Module 04 — Decision Trees

- [ ] **E4.1** ID3 with information gain on a 14-row contact-liveness style dataset.
- [ ] **E4.2** CART with Gini. Show the two criteria pick different splits on the same
      data.
- [ ] **E4.3** Gain ratio; demonstrate that C4.5 prefers a low-cardinality feature where
      information gain does not.
- [ ] **M4.4** Pre-pruning with `min_samples_split` and `max_depth`. Plot train and
      validation error versus depth.
- [ ] **M4.5** Regression tree splitting on variance reduction; predict and compare
      against OLS on a linear target.
- [ ] **M4.6** Missing values via surrogate splits. Remove 10% at random and compare
      against mean-imputation.
- [ ] **H4.7** Cost complexity pruning: enumerate the pruning path and pick the alpha by
      cross-validation.

## Module 05 — Random Forest

- [ ] **E5.1** Bootstrap sampling with replacement; verify ~63.2% of rows appear in a
      given bootstrap (unique fraction).
- [ ] **E5.2** Train 50 trees, compute OOB error directly from held-out predictions.
      Compare with a 70/30 split estimate.
- [ ] **M5.3** Permutation importance on OOB data. Contrast with impurity importance on
      a dataset with one high-cardinality noise feature.
- [ ] **M5.4** Vary `mtry` from 1 to `p`; plot OOB error. Explain the U-shape.
- [ ] **H5.5** Proximity matrix: fraction of trees where two samples land in the same
      leaf. Find the two most similar outliers.
- [ ] **H5.6** Quantify the correlation effect: prediction interval width from the tree
      vote distribution versus the true error rate.

## Module 06 — Gradient Boosting

- [ ] **E6.1** Forward stagewise boosting with squared error: each stage fits a residual.
      Verify residuals are orthogonal to the previous stage's fit.
- [ ] **E6.2** Gradient boosting with logistic loss on a binary task; compare AUC
      against the single tree.
- [ ] **M6.3** Second-order Taylor expansion with `lambda` leaf penalty; derive the
      optimal leaf value `-G / (H + lambda)`.
- [ ] **M6.4** Histogram binning: 64 quantile bins on a 10,000-row feature. Verify
      split finding over bins matches exact search on a small dataset.
- [ ] **M6.5** Early stopping on a validation metric. Sweep `n_estimators` and find the
      best round.
- [ ] **H6.6** Implement GOSS-style sampling: keep all `A` highest-gradient rows, sample
      `B` from the rest, rescale. Match full-data performance within 0.5% AUC.
- [ ] **H6.7** Learning-rate/tree-count equivalence experiment on one dataset. Find two
      pairs with similar error.

## Module 07 — PCA

- [ ] **E7.1** PCA by eigendecomposition of the covariance matrix on 2D data. Verify
      the first principal axis is the direction of maximum variance.
- [ ] **E7.2** PCA by SVD of the centered matrix. Show the singular values equal the
      square roots of the covariance eigenvalues.
- [ ] **M7.3** Explained variance ratio and a cumulative plot. Choose `k` for 95%.
- [ ] **M7.4** Reconstruct at `k=1..5`; report reconstruction error per dimension.
- [ ] **M7.5** Projection of a 3D dataset into 2D; verify the projection maximizes
      variance subject to orthogonality.
- [ ] **H7.6** Build a dataset where the top variance direction is pure nuisance. Show
      PCA destroys the label signal and LDA does not.
- [ ] **H7.7** Kernel PCA with an RBF kernel and centered kernel matrix. Reconstruct and
      compare to linear PCA on a two-moons dataset.

## Module 08 — K-Means

- [ ] **E8.1** Lloyd's algorithm; verify objective `J` decreases monotonically.
- [ ] **E8.2** `k-means++` seeding versus random seeding over 50 runs. Report mean and
      worst final `J`.
- [ ] **M8.3** Elbow, silhouette, and gap statistic for `k = 1..10`. Report all three
      and defend the `k` you choose.
- [ ] **M8.4** Elkan's triangle-inequality acceleration; count distance computations
      versus Lloyd's on a 10,000-row dataset.
- [ ] **M8.5** k-means on two anisotropic Gaussians. Show the failure and explain why
      the spherical-cluster assumption breaks.
- [ ] **H8.6** Mini-batch k-means: 50 epochs of sampled updates. Compare inertia and
      wall time against full Lloyd's.

## Module 09 — DBSCAN and Hierarchical

- [ ] **E9.1** DBSCAN with a hand-computed `eps`/`minPts`; classify every point core,
      border, or noise.
- [ ] **E9.2** Sweep `eps` on the k-distance plot and pick the knee. Show the resulting
      cluster count is stable across a knee neighbourhood.
- [ ] **M9.3** DBSCAN on two-moons (works) versus k-means (fails). Report both.
- [ ] **M9.4** Dataset with two densities. Show one `eps` cannot serve both and report
      the misassignment count.
- [ ] **M9.5** Agglomerative clustering with single, complete, average, and Ward linkage
      on the same data. Show single linkage chaining.
- [ ] **H9.6** Dendrogram: cut at each merge height, compute silhouette, pick the cut.
- [ ] **H9.7** OPTICS-style ordering: compute the reachability plot and extract
      clusters as steep drops.

## Module 10 — Anomaly Detection

- [ ] **E10.1** Z-score and IQR thresholds on a Gaussian mixture; report the false
      positive rate.
- [ ] **E10.2** At a 1% contamination rate, report accuracy and PR-AUC side by side.
      Explain the accuracy number.
- [ ] **M10.3** Isolation Forest with 100 trees; score held-out anomalies. Compare to
      the z-score baseline.
- [ ] **M10.4** LOF with `k=20`. Show that LOF detects a low-density anomaly that
      Isolation Forest misses.
- [ ] **M10.5** Autoencoder reconstruction-error detector; plot the error histogram with
      a threshold chosen for a target FPR.
- [ ] **H10.6** One-class SVM with an RBF kernel. Compare PR-AUC against Isolation
      Forest on three datasets.
- [ ] **H10.7** Cost-sensitive thresholding: with `C_FN = 100 * C_FP`, find the
      threshold and report the confusion matrix at that operating point.

## Cross-Module

- [ ] **X1** Full tabular pipeline: impute, encode categoricals, fit gradient boosting,
      calibrate probabilities, tune the threshold on the PR curve. Report the model card.
- [ ] **X2** Baseline ladder: mean, logistic, random forest, gradient boosting. Report
      the metric at each rung and the incremental value of the last one.
- [ ] **X3** Leakage hunt: add a feature derived from the label, measure the inflated
      score, then remove it and record the drop.
- [ ] **X4** Reproducibility: run a pipeline twice with the same seed and diff the
      predictions. Make it pass by threading one `Random` through everything.
