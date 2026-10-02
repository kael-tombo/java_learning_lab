# Logistic Regression — Exercises

**Prerequisites:** Java 21+ with Apache Commons Math, or Python with `numpy`, `scikit-learn`, `scipy`.

---

## Exercise 1: Sigmoid and Log-Odds

**Objective:** Implement and visualize the sigmoid function and its properties.

**Tasks:**
1. Implement `sigmoid(z)` and `logit(p)` functions.
2. Verify they are inverses: `sigmoid(logit(p)) ≈ p` for p ∈ (0,1).
3. Plot sigmoid for z ∈ [−10, 10]. Mark inflection point (z=0, σ=0.5).
4. Plot derivative: σ'(z) = σ(z)(1−σ(z)). Maximum at z=0 (0.25).
5. **Challenge:** Implement numerically stable versions for extreme z:
   - σ(z) = 1/(1+exp(−z)) for z ≥ 0
   - σ(z) = exp(z)/(1+exp(z)) for z < 0 (avoids overflow)

**Expected Answer:** Sigmoid maps ℝ → (0,1). Derivative bell-shaped, max 0.25 at 0. Stable implementation handles z = ±1000.

---

## Exercise 2: Binary Cross-Entropy Loss and Gradient

**Objective:** Implement logistic loss and its gradient; verify with automatic differentiation.

**Tasks:**
1. Implement `logistic_loss(y, y_hat)` with clipping (ε=1e-15) to avoid log(0).
2. Implement gradient: `grad = X.T @ (y_hat - y) / n`
3. Generate synthetic data: n=500, p=3, binary y from logistic model with known β.
4. Compare numerical gradient (finite differences) to analytical gradient.
5. Plot loss surface for 2D slice (β₁ vs β₂, others fixed). Verify convexity.
6. **Challenge:** Implement Hessian-vector product for Newton's method: Hv = X.T @ (D @ (X @ v)) where D = diag(y_hat*(1-y_hat)).

**Expected Answer:** Numerical ≈ analytical gradient (relative error < 1e-6). Loss surface bowl-shaped (convex). Hessian positive definite.

---

## Exercise 3: Gradient Descent Optimization

**Objective:** Train logistic regression using gradient descent variants.

**Tasks:**
1. Implement batch GD with learning rate α. Track loss per iteration.
2. Implement mini-batch GD (batch_size=32). Shuffle each epoch.
3. Implement SGD (batch_size=1).
4. Add learning rate schedules: constant, 1/√t, 1/t, exponential decay.
5. Compare convergence speed (iterations to loss < 1e-4) and final loss.
6. Plot loss curves (log scale) for all methods.
7. **Challenge:** Implement momentum (γ=0.9) and Adam optimizer (β₁=0.9, β₂=0.999, ε=1e-8).

**Expected Answer:** Batch GD: smooth but slow per epoch. Mini-batch: best trade-off. SGD: noisy. Adam: fastest convergence. All reach similar minimum.

---

## Exercise 4: Newton's Method / IRLS

**Objective:** Implement Iteratively Reweighted Least Squares for fast convergence.

**Tasks:**
1. IRLS update: β := β + (XᵀWX)⁻¹Xᵀ(y − ŷ)
   - W = diag(ŷᵢ(1−ŷᵢ)) (weights)
   - z = Xβ + W⁻¹(y − ŷ) (working response)
   - Equivalent to weighted least squares on z
2. Implement with regularization: (XᵀWX + λI)⁻¹
3. Compare iterations to convergence vs gradient descent (should be ~5-10 vs 100s).
4. Monitor condition number of XᵀWX. Add ridge if ill-conditioned.
5. **Challenge:** Implement damped Newton (line search on step size) for global convergence.

**Expected Answer:** IRLS converges in ~6-8 iterations (quadratic near optimum). Much faster than GD. Need damping for first few iterations far from optimum.

---

## Exercise 5: Regularization Paths

**Objective:** Visualize effect of L1 and L2 regularization on coefficients.

**Tasks:**
1. Generate data with correlated features (some informative, some noise).
2. Fit L2-regularized (Ridge) logistic regression for λ ∈ [10⁻⁴, 10⁴] (log-spaced, 50 values).
3. Plot coefficient paths: βⱼ vs log(λ). All shrink smoothly to 0.
4. Fit L1-regularized (Lasso) using coordinate descent. Plot paths.
4. Observe: some coefficients hit exactly 0 (sparsity).
5. Fit Elastic Net (α=0.5). Compare paths.
6. **Challenge:** Implement coordinate descent for Lasso logistic regression:
   - Cyclic coordinate updates with soft-thresholding
   - Use quadratic approximation of loss at each coordinate

**Expected Answer:** Ridge: smooth shrinkage, no zeros. Lasso: sparse (many exactly 0). Elastic Net: groups correlated features together (both in or both out).

---

## Exercise 6: Cross-Validation for Hyperparameter Selection

**Objective:** Select optimal λ using k-fold CV.

**Tasks:**
1. Implement k-fold CV (k=5) for logistic regression with L2 regularization.
2. Grid search over λ ∈ logspace(-4, 4, 20).
3. Metrics: CV log-loss, CV accuracy, CV AUC.
4. Plot CV metric vs log(λ). Select λ minimizing log-loss.
5. Apply 1-SE rule: largest λ within 1 SE of minimum.
6. Compare test performance of: λ_min, λ_1se, no regularization.
7. **Challenge:** Implement nested CV (outer: performance estimate, inner: λ selection).

**Expected Answer:** U-shaped CV curve. λ_min: best CV score but may overfit. λ_1se: simpler model, similar test performance. No regularization: overfits if p large or correlated features.

---

## Exercise 7: Multi-Class Classification (Softmax)

**Objective:** Implement multinomial logistic regression.

**Tasks:**
1. Generate 3-class data: 3 Gaussian clusters in 2D (n=300 per class).
2. Implement softmax: P(Y=k|X) = exp(βₖᵀX) / Σⱼ exp(βⱼᵀX).
   - Fix β_K = 0 for identifiability (K classes → K-1 vectors)
3. Cross-entropy loss: L = −Σᵢ Σₖ 1{yᵢ=k} log P(Y=k|Xᵢ)
4. Gradient: ∇βₖ = Xᵀ(ŷₖ − yₖ) where yₖ is one-hot.
5. Train with gradient descent. Plot decision boundaries.
6. Compare to One-vs-Rest (3 binary classifiers).
7. **Challenge:** Implement multi-class IRLS (block Newton method).

**Expected Answer:** Softmax: calibrated probabilities, single model. OvR: simpler but uncalibrated. Decision boundaries: linear between each pair. IRLS: block Hessian of size (K-1)p × (K-1)p.

---

## Exercise 8: Model Evaluation and Threshold Tuning

**Objective:** Evaluate classifier with various metrics and find optimal threshold.

**Tasks:**
1. Train logistic regression on imbalanced dataset (e.g., 95% class 0, 5% class 1).
2. Compute at default threshold 0.5:
   - Accuracy, Precision, Recall, F1, AUC-ROC, AUC-PR
3. Plot ROC curve and Precision-Recall curve.
4. Find threshold maximizing F1 score.
5. Find threshold maximizing Youden's J = TPR − FPR.
6. Implement cost-sensitive threshold: cost(FP)=$10, cost(FN)=$1000.
7. **Challenge:** Plot calibration curve (reliability diagram): bin predictions, plot avg predicted vs actual.

**Expected Answer:** Accuracy misleading (95% by always predicting 0). AUC-ROC/AUC-PR better. Optimal threshold typically < 0.5 for rare class. Calibration: logistic regression usually well-calibrated.

---

## Exercise 9: Feature Engineering and Interactions

**Objective:** Explore non-linear decision boundaries via feature engineering.

**Tasks:**
1. Generate 2D data with non-linear boundary (e.g., XOR, circles, moons).
2. Fit standard logistic regression (linear). Observe poor performance.
3. Add polynomial features (degree 2, 3). Refit. Observe improved fit.
4. Add interaction terms: x₁×x₂, x₁², x₂².
5. Use regularization to prevent overfitting with high-degree polynomials.
6. Compare to kernel SVM (RBF) as baseline.
7. **Challenge:** Implement automatic feature interaction detection (e.g., using tree-based feature importance).

**Expected Answer:** Linear logistic regression fails on non-linear boundaries. Polynomial features enable non-linear decision boundaries in original space. Regularization crucial to avoid overfitting.

---

## Exercise 10: End-to-End Logistic Regression Library

**Objective:** Build production-ready `LogisticRegression` class.

**Requirements:** Java class with:
- `fit(double[][] X, int[] y)` — supports binary and multi-class
- `fitGD(...)` / `fitIRLS(...)` — optimization algorithms
- `predict(double[][] X)` — class predictions
- `predictProba(double[][] X)` — probabilities
- `predictLogProba(double[][] X)` — log probabilities
- `score(double[][] X, int[] y)` — accuracy
- `getCoefficients()` — β̂ (binary: 1D, multi-class: 2D)
- `crossValidate(k, metric, paramGrid)` — CV with grid search
- `getFeatureImportance()` — |βⱼ| for binary, avg |βₖⱼ| for multi-class
- Regularization: `setRegularization(type, lambda1, lambda2)`
- Class weights: `setClassWeights(double[] weights)`
- Serialization: `save/load`

**Diagnostics:**
- `getConvergenceHistory()` — loss per iteration
- `getGradientNorm()` — final gradient norm
- `getHessianConditionNumber()` — for IRLS

**Tests:**
- Synthetic separable/non-separable data
- Multi-class (Iris, Wine datasets)
- Imbalanced data (fraud detection simulation)
- Comparison with sklearn (if Python bridge) or known values

**Bonus:** Add `calibrate(CalibrationMethod method)` — Platt scaling / isotonic regression.