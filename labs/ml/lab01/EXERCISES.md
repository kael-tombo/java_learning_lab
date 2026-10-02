# Linear Regression — Exercises

**Prerequisites:** Java 21+ with Apache Commons Math, or Python with `numpy`, `scikit-learn`, `pandas`.

---

## Exercise 1: OLS from Scratch (Normal Equations)

**Objective:** Implement OLS using the normal equation.

**Tasks:**
1. Generate synthetic data: n=1000, p=5
   - X ~ N(0, I₅)
   - β_true = [2.0, -1.5, 0.8, 0.0, 3.2]
   - y = Xβ_true + ε, ε ~ N(0, 1)
2. Implement `OLS.fit(X, y)` computing β̂ = (XᵀX)⁻¹Xᵀy
   - Add intercept column of 1s
   - Handle potential singular matrix (add small ridge λI)
3. Compute predictions, residuals, R², adjusted R²
4. Compare estimated β̂ to β_true. Compute estimation error ||β̂ − β_true||₂
5. **Challenge:** Implement using SVD (X = UΣVᵀ) for numerical stability: β̂ = VΣ⁻¹Uᵀy

**Expected Answer:** β̂ close to β_true. R² ≈ 0.9+. SVD handles near-singular XᵀX better.

---

## Exercise 2: Gradient Descent for Linear Regression

**Objective:** Implement batch, mini-batch, and stochastic gradient descent.

**Tasks:**
1. Implement MSE loss: J(β) = ¹/(2n) ||y − Xβ||²₂
2. Implement gradient: ∇J(β) = −¹/n Xᵀ(y − Xβ)
3. **Batch GD:** Update β using full gradient. Try learning rates: 0.001, 0.01, 0.1, 1.0. Plot loss vs iterations.
4. **Mini-batch GD:** Batch size = 32. Shuffle data each epoch. Compare convergence speed to batch GD.
5. **SGD:** Batch size = 1. Plot loss (noisier). Try learning rate decay: αₜ = α₀ / (1 + t/τ)
6. Compare final β from all three methods to normal equation solution.
7. **Challenge:** Implement momentum (β := β − α∇J + γ(βₜ − βₜ₋₁)) and Adam optimizer.

**Expected Answer:** Batch GD: smooth convergence. Mini-batch: faster per epoch. SGD: noisy but escapes local minima (not relevant for convex MSE). All should converge to similar solution.

---

## Exercise 3: Feature Scaling Impact

**Objective:** Demonstrate why feature scaling matters for gradient descent.

**Tasks:**
1. Create dataset with features on different scales:
   - X₁ ~ N(0, 1)
   - X₂ ~ N(0, 10000) (scale 100x)
   - X₃ ~ N(0, 0.0001) (scale 0.01x)
   - y = 2X₁ − 3X₂ + 1.5X₃ + ε
2. Run gradient descent WITHOUT scaling. Plot loss contours (2D slice: β₁ vs β₂).
3. Run gradient descent WITH standardization (zero mean, unit variance).
4. Compare iterations to convergence (loss < 1e-4).
5. **Challenge:** Implement automatic feature scaling in your LinearRegression class (fit scaler on train, transform test).

**Expected Answer:** Without scaling: elongated contours, very slow convergence (thousands of iterations). With scaling: fast convergence (< 100 iterations). Normal equation unaffected.

---

## Exercise 4: Regularization (Ridge, Lasso, Elastic Net)

**Objective:** Implement regularized linear regression.

**Tasks:**
1. **Ridge (L2):** Minimize J(β) = MSE + λ||β||²₂
   - Closed form: β̂_ridge = (XᵀX + λI)⁻¹Xᵀy (don't regularize intercept!)
   - Gradient: ∇J = −¹/n Xᵀ(y−Xβ) + 2λβ
2. **Lasso (L1):** Minimize J(β) = MSE + λ||β||₁
   - No closed form. Use coordinate descent or proximal gradient.
   - Proximal operator: prox_{λα}(z) = sign(z) × max(|z| − λα, 0)
3. **Elastic Net:** J(β) = MSE + λ₁||β||₁ + λ₂||β||₂₂
3. Generate data with correlated features (multicollinearity).
4. Plot regularization paths: coefficient values vs λ (log scale).
5. Use cross-validation to select optimal λ.
6. **Challenge:** Implement coordinate descent for Lasso (cycling through coordinates).

**Expected Answer:** Ridge: shrinks all coefficients smoothly. Lasso: sparse solution (some exactly 0). Elastic Net: groups correlated features together.

---

## Exercise 5: Model Evaluation and Diagnostics

**Objective:** Implement comprehensive regression diagnostics.

**Tasks:**
1. Fit OLS on a dataset (use Boston Housing, California Housing, or synthetic).
2. Compute:
   - Residuals, standardized residuals, studentized residuals
   - Leverage (hat matrix diagonal)
   - Cook's distance
   - DFFITS, DFBETAS
3. Plot:
   - Residuals vs Fitted (check homoscedasticity)
   - Q-Q plot of residuals (check normality)
   - Scale-Location plot (√|standardized residuals| vs fitted)
   - Residuals vs Leverage (identify influential points)
4. Statistical tests:
   - Breusch-Pagan for heteroscedasticity
   - Durbin-Watson for autocorrelation
   - Shapiro-Wilk for normality
   - Rainbow test for linearity
5. **Challenge:** Implement automated outlier/influential point detection and refit after removal.

**Expected Answer:** Diagnostic plots reveal assumption violations. Influential points (high leverage + large residual) can distort model. Statistical tests give p-values for formal inference.

---

## Exercise 6: Polynomial Regression and Overfitting

**Objective:** Explore polynomial features and regularization to prevent overfitting.

**Tasks:**
1. Generate 1D data: y = sin(2πx) + ε, x ∈ [0,1], n=50
2. Fit polynomial regression of degrees 1, 3, 5, 10, 15
   - Create polynomial features: [1, x, x², ..., x^d]
   - Use OLS (normal equations)
3. Plot fits on dense grid. Compute train/test MSE (split 80/20).
4. Observe overfitting at high degrees (train error → 0, test error ↑).
5. Apply Ridge regularization to degree 15 model. Plot test MSE vs λ.
6. **Challenge:** Use cross-validation to select optimal degree AND λ jointly.

**Expected Answer:** Degree 1: underfit. Degree 3-5: good fit. Degree 10+: severe overfitting (wild oscillations). Ridge controls overfitting by shrinking high-degree coefficients.

---

## Exercise 7: Multicollinearity and VIF

**Objective:** Diagnose and address multicollinearity.

**Tasks:**
1. Generate correlated features:
   - X₁ ~ N(0,1)
   - X₂ = 0.9X₁ + 0.1×N(0,1) (highly correlated)
   - X₃ ~ N(0,1) independent
   - y = 2X₁ + 1.5X₃ + ε
2. Fit OLS. Examine coefficient estimates and standard errors.
3. Compute VIF for each feature: VIFⱼ = 1/(1 − R²ⱼ) where R²ⱼ from regressing Xⱼ on others.
4. Apply Ridge regression. Observe coefficient stability.
5. **Challenge:** Use PCA regression (PCR): project X to principal components, regress on top k PCs.

**Expected Answer:** OLS: large SEs for X₁, X₂, unstable signs. VIF for X₁, X₂ > 10. Ridge: stable estimates. PCR: removes noise dimensions.

---

## Exercise 8: Cross-Validation for Model Selection

**Objective:** Implement k-fold CV for hyperparameter tuning.

**Tasks:**
1. Implement k-fold CV from scratch (no sklearn):
   - Split indices into k folds
   - For each fold: train on k−1, validate on 1
   - Average validation scores
2. Use CV to select:
   - Optimal polynomial degree (Exercise 6)
   - Optimal λ for Ridge/Lasso (Exercise 4)
3. Implement nested CV: outer loop for performance estimation, inner loop for hyperparameter selection.
4. Compare: single train/test split vs CV vs nested CV estimates.
5. **Challenge:** Implement stratified k-fold for regression (bin target into quantiles).

**Expected Answer:** Single split: high variance estimate. CV: lower variance. Nested CV: unbiased estimate of generalization error (no leakage from hyperparameter tuning).

---

## Exercise 9: Real-World Dataset — California Housing

**Dataset:** California Housing (sklearn.datasets.fetch_california_housing)

**Tasks:**
1. Load data. Explore: describe, correlations, missing values.
2. Split: train 80%, test 20%.
3. Baseline: OLS with all features. Compute train/test RMSE, R².
4. Feature engineering:
   - Log transform skewed features
   - Create interaction features (e.g., MedInc × AveRooms)
   - Polynomial features (degree 2) for top 3 features
5. Models to compare:
   - OLS
   - Ridge (CV for λ)
   - Lasso (CV for λ)
   - Elastic Net (CV for λ₁, λ₂)
   - Random Forest (for comparison)
6. Feature importance: coefficients (linear), permutation importance (RF).
7. Residual analysis on best model.
8. **Deliverable:** 2-page report: best model, RMSE, key features, residual diagnostics, limitations.

---

## Exercise 10: End-to-End Linear Regression Library

**Objective:** Build a production-ready LinearRegression class.

**Requirements:** Java class `LinearRegression` with:
- `fit(double[][] X, double[] y)` — normal equations with SVD fallback
- `fitGD(double[][] X, double[] y, GDConfig config)` — batch/mini-batch/SGD
- `predict(double[][] X)` — predictions
- `score(double[][] X, double[] y)` — R²
- `getCoefficients()` — β̂
- `getStandardErrors()` — SE(β̂)
- `getConfidenceIntervals(double alpha)` — CI for coefficients
- `diagnose(double[][] X, double[] y)` — returns DiagnosticResult with:
  - Residuals, leverage, Cook's distance
  - Breusch-Pagan p-value
  - Durbin-Watson statistic
  - VIF for each feature
- `save(ModelPath)` / `load(ModelPath)` — serialization

**Config classes:** `GDConfig` (learningRate, batchSize, maxIter, tolerance, momentum, lrSchedule), `RegularizationConfig` (type: NONE/RIDGE/LASSO/ELASTIC_NET, lambda1, lambda2).

**Tests:** Unit tests for each method. Integration test on California Housing.

**Bonus:** Add `crossValidate(k, metric)` returning CV scores and optimal hyperparameters.