# Linear Regression — Flashcards

**Format:** Question (front) → Answer (back). Use for spaced repetition.

---

### Card 1
**Q:** What is linear regression?
**A:** Model: Y = Xβ + ε. Goal: estimate β to minimize prediction error.

---

### Card 2
**Q:** What is the OLS objective function?
**A:** Minimize SSR = Σ(yᵢ − xᵢᵀβ)² = ||y − Xβ||²₂.

---

### Card 3
**Q:** What is the closed-form OLS solution (normal equation)?
**A:** β̂ = (XᵀX)⁻¹Xᵀy. Requires XᵀX invertible.

---

### Card 4
**Q:** What are the Gauss-Markov assumptions?
**A:** (1) Linear in parameters, (2) Random sampling, (3) No perfect multicollinearity, (4) E[ε|X]=0, (5) Var(ε|X)=σ².

---

### Card 5
**Q:** What does BLUE mean?
**A:** Best Linear Unbiased Estimator. OLS is BLUE under Gauss-Markov assumptions.

---

### Card 6
**Q:** What is R²?
**A:** R² = 1 − SSR/SST = proportion of variance in Y explained by model. Range [0,1] with intercept.

---

### Card 7
**Q:** What is adjusted R²?
**A:** R²_adj = 1 − (1−R²)(n−1)/(n−p−1). Penalizes extra predictors. Can be negative.

---

### Card 8
**Q:** What is the gradient of MSE w.r.t β?
**A:** ∇J(β) = (2/n) Xᵀ(Xβ − y).

---

### Card 9
**Q:** What is the gradient descent update rule?
**A:** β := β − α × ∇J(β). α = learning rate.

---

### Card 10
**Q:** What is the difference between batch, mini-batch, and SGD?
**A:** Batch: all n samples. Mini-batch: small subset. SGD: 1 sample per update. Trade-off: noise vs speed.

---

### Card 11
**Q:** Why scale features for gradient descent?
**A:** Makes loss contours spherical → faster convergence. Doesn't change OLS solution.

---

### Card 12
**Q:** What is the learning rate schedule?
**A:** Decay α over time (e.g., αₜ = α₀/√t or α₀/t). Helps converge to minimum.

---

### Card 13
**Q:** What is MSE?
**A:** MSE = ¹/n Σ(yᵢ − ŷᵢ)². Penalizes large errors more.

---

### Card 14
**Q:** What is RMSE?
**A:** RMSE = √MSE. Same units as target variable.

---

### Card 15
**Q:** What is MAE?
**A:** MAE = ¹/n Σ|yᵢ − ŷᵢ|. Linear penalty, more robust to outliers.

---

### Card 16
**Q:** What is multicollinearity?
**A:** High correlation among predictors. Inflates Var(β̂) = σ²(XᵀX)⁻¹. Large SEs, unstable estimates.

---

### Card 17
**Q:** How to detect multicollinearity?
**A:** VIF (Variance Inflation Factor) = 1/(1−R²ⱼ) where R²ⱼ from regressing Xⱼ on other X's. VIF > 10 problematic.

---

### Card 18
**Q:** What is the bias-variance tradeoff in linear regression?
**A:** More complex model (more features) → lower bias, higher variance. Regularization balances this.

---

### Card 19
**Q:** What is Ridge Regression (L2)?
**A:** Minimize ||y − Xβ||²₂ + λ||β||²₂. Shrinks coefficients toward zero. Keeps all features.

---

### Card 20
**Q:** What is Lasso Regression (L1)?
**A:** Minimize ||y − Xβ||²₂ + λ||β||₁. Shrinks some coefficients exactly to zero → feature selection.

---

### Card 21
**Q:** What is Elastic Net?
**A:** Combination: λ₁||β||₁ + λ₂||β||₂. Best of both: handles correlated features better than Lasso alone.

---

### Card 22
**Q:** What is the hat matrix?
**A:** H = X(XᵀX)⁻¹Xᵀ. ŷ = Hy. Diagonal hᵢᵢ = leverage. Trace(H) = p (degrees of freedom).

---

### Card 23
**Q:** What are residuals vs errors?
**A:** Errors εᵢ = yᵢ − xᵢᵀβ (unobserved). Residuals eᵢ = yᵢ − ŷᵢ (observed). Σeᵢ = 0 if intercept included.

---

### Card 24
**Q:** What are the OLS residual properties?
**A:** (1) Σeᵢ = 0 (with intercept), (2) Xᵀe = 0 (orthogonal to predictors), (3) ŷᵀe = 0.

---

### Card 25
**Q:** What is heteroscedasticity?
**A:** Var(ε|X) not constant. OLS still unbiased but not efficient. Standard errors wrong. Use robust (White) SEs.

---

### Card 26
**Q:** What is the Breusch-Pagan test?
**A:** Tests for heteroscedasticity. Regress e² on X. LM statistic = n×R² ~ χ²ₚ.

---

### Card 27
**Q:** What is the Durbin-Watson test?
**A:** Tests for autocorrelation in residuals. DW ≈ 2(1−ρ̂). DW ≈ 2 → no autocorrelation.

---

### Card 28
**Q:** What is the leverage of a point?
**A:** hᵢᵢ = diagonal of hat matrix. High leverage = unusual X values. hᵢᵢ > 2p/n flagged.

---

### Card 29
**Q:** What is Cook's distance?
**A:** Measures influence of each observation on all fitted values. Dᵢ > 4/n flagged.

---

### Card 30
**Q:** What is polynomial regression?
**A:** Linear in parameters but non-linear in X: Y = β₀ + β₁X + β₂X² + ... Still OLS!

---

### Card 31
**Q:** What is the interpretation of βⱼ in multiple regression?
**A:** Expected change in Y per unit change in Xⱼ, holding all other predictors constant.

---

### Card 32
**Q:** What is omitted variable bias?
**A:** Excluding relevant variable correlated with included X biases β̂. Direction = sign(corr) × sign(true β).

---

### Card 33
**Q:** What is the variance of OLS estimator?
**A:** Var(β̂) = σ²(XᵀX)⁻¹. Estimated by s²(XᵀX)⁻¹ where s² = SSR/(n−p−1).

---

### Card 34
**Q:** What is a confidence interval for βⱼ?
**A:** β̂ⱼ ± t_{α/2,n−p−1} × SE(β̂ⱼ). SE = √[σ̂²(XᵀX)⁻¹ⱼⱼ].

---

### Card 35
**Q:** What is the F-test for overall significance?
**A:** H₀: β₁=...=βₚ=0. F = (R²/p) / ((1−R²)/(n−p−1)) ~ F_{p, n−p−1}.

---

### Card 36
**Q:** What is the prediction interval vs confidence interval for mean?
**A:** CI for E[Y|X]: narrower. PI for individual Y: wider by factor √(1 + 1/n + ...).

---

### Card 37
**Q:** What is regularization path?
**A:** Plot of coefficient values vs λ. Ridge: smooth shrink to 0. Lasso: hit 0 at different λ.

---

### Card 38
**Q:** How to choose λ for Ridge/Lasso?
**A:** Cross-validation (typically k-fold). Select λ minimizing CV error. 1-SE rule for simpler model.

---

### Card 39
**Q:** What is the difference between standardization and normalization?
**A:** Standardization: (x − μ)/σ (mean 0, SD 1). Normalization: (x − min)/(max − min) → [0,1].

---

### Card 40
**Q:** When to use normal equations vs gradient descent?
**A:** Normal eq: small/medium p (p < 10k), exact solution. GD: large p, large n, or non-linear models.