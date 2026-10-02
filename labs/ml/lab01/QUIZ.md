# Linear Regression — Quiz (10 Questions)

**Instructions:** Answer each question. Correct answers and explanations follow.

---

### Q1: What is the Ordinary Least Squares (OLS) estimator minimizing?
A) Sum of absolute residuals
B) Sum of squared residuals
C) Maximum likelihood
D) Sum of residuals

**Answer: B** — OLS minimizes Σ(yᵢ − ŷᵢ)² = Σ(yᵢ − xᵢᵀβ)². The solution is β̂ = (XᵀX)⁻¹Xᵀy.

---

### Q2: What are the Gauss-Markov assumptions for OLS to be BLUE?
A) Linearity, random sampling, no perfect multicollinearity, zero conditional mean, homoscedasticity
B) Normality, independence, equal variance
C) Large sample size, no outliers
D) Only linearity and independence

**Answer: A** — BLUE = Best Linear Unbiased Estimator. Assumptions: (1) Linear in parameters, (2) Random sampling, (3) No perfect multicollinearity (XᵀX invertible), (4) E[ε|X] = 0 (exogeneity), (5) Var(ε|X) = σ² (homoscedasticity). Normality not required for BLUE.

---

### Q3: What does R² (coefficient of determination) measure?
A) Correlation between X and Y
B) Proportion of variance in Y explained by the model
C) Average prediction error
D) Statistical significance of coefficients

**Answer: B** — R² = 1 − SSR/SST = 1 − Σ(yᵢ−ŷᵢ)² / Σ(yᵢ−ȳ)². Ranges [0,1] for OLS with intercept. Higher = more variance explained.

---

### Q4: What is the difference between R² and adjusted R²?
A) Adjusted R² penalizes for number of predictors
B) Adjusted R² is always higher
C) Adjusted R² uses different formula for SST
D) They are the same

**Answer: A** — Adjusted R² = 1 − (1−R²)(n−1)/(n−p−1). Penalizes adding predictors that don't improve fit enough. Can decrease when adding useless variables.

---

### Q5: In gradient descent for linear regression, what is the update rule for weights?
A) w := w + α × ∇J(w)
B) w := w − α × ∇J(w)
C) w := w / α × ∇J(w)
D) w := α × w − ∇J(w)

**Answer: B** — Gradient descent moves opposite to gradient: w := w − α∇J(w). For MSE, ∇J(w) = (2/n)Xᵀ(Xw − y). α = learning rate.

---

### Q6: What is the effect of feature scaling on gradient descent?
A) No effect
B) Slows convergence
C) Speeds up convergence by making contours more circular
D) Changes the optimal solution

**Answer: C** — Without scaling, elongated contours cause zigzagging. Scaling (standardization/normalization) makes contours more spherical, allowing faster convergence. Does not change optimal solution for linear regression.

---

### Q7: What is the normal equation solution for linear regression?
A) β̂ = Xᵀy
B) β̂ = (XᵀX)⁻¹Xᵀy
C) β̂ = X(XᵀX)⁻¹y
D) β̂ = (XXᵀ)⁻¹Xy

**Answer: B** — Derived by setting ∇J(β) = 0: XᵀXβ = Xᵀy → β̂ = (XᵀX)⁻¹Xᵀy. Requires XᵀX invertible (no perfect multicollinearity). Computational cost O(p³) vs O(np²) for gradient descent.

---

### Q8: What is multicollinearity and its effect on OLS?
A) Correlated features; increases variance of coefficient estimates
B) Correlated features; biases coefficient estimates
C) Correlated errors; increases variance
D) Correlated errors; biases coefficient estimates

**Answer: A** — Multicollinearity = high correlation among predictors. OLS remains unbiased but variance of β̂ inflates (Var(β̂) = σ²(XᵀX)⁻¹). Large standard errors, unstable estimates. VIF > 10 indicates problematic multicollinearity.

---

### Q9: What is the difference between MSE, RMSE, and MAE?
A) MSE = mean squared error; RMSE = sqrt(MSE); MAE = mean absolute error
B) MSE = median squared error; RMSE = root mean squared error; MAE = median absolute error
C) They are all the same
D) MSE is for classification; RMSE/MAE for regression

**Answer: A** — MSE = ¹/n Σ(yᵢ−ŷᵢ)² (penalizes large errors quadratically). RMSE = √MSE (same units as Y). MAE = ¹/n Σ|yᵢ−ŷᵢ| (linear penalty, more robust to outliers).

---

### Q10: When would you use gradient descent instead of normal equations?
A) When n is small and p is large
B) When n is very large (millions) or p is very large
C) When you need exact solution
D) When features are not scaled

**Answer: B** — Normal equations: O(p³) for inversion + O(np²) for XᵀX. Gradient descent: O(np) per iteration. For very large n or p, iterative methods (SGD, mini-batch) are more scalable. Also works for non-linear models where no closed form exists.