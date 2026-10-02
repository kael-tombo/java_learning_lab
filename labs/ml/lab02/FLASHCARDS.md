# Logistic Regression — Flashcards

**Format:** Question (front) → Answer (back). Use for spaced repetition.

---

### Card 1
**Q:** What is logistic regression?
**A:** Binary classification model: P(Y=1|X) = σ(β₀ + βᵀX). Models probability directly.

---

### Card 2
**Q:** What is the sigmoid function?
**A:** σ(z) = 1/(1+e⁻ᶻ) = eᶻ/(1+eᶻ). Range: (0,1). S-shaped curve.

---

### Card 3
**Q:** What is the logit (log-odds)?
**A:** log(P/(1−P)) = β₀ + βᵀX. Linear in X. Inverse of sigmoid.

---

### Card 4
**Q:** What is the decision boundary?
**A:** β₀ + βᵀX = 0. Linear separator in feature space. P(Y=1|X) = 0.5.

---

### Card 5
**Q:** What is the binary cross-entropy loss?
**A:** L = −[y log(p) + (1−y) log(1−p)]. For dataset: J(β) = −¹/n Σ[yᵢ log(ŷᵢ) + (1−yᵢ) log(1−ŷᵢ)].

---

### Card 6
**Q:** Why cross-entropy instead of MSE?
**A:** MSE with sigmoid is non-convex (local minima). Cross-entropy is convex (global optimum guaranteed).

---

### Card 7
**Q:** What is the gradient of logistic loss?
**A:** ∇J = ¹/n Xᵀ(ŷ − y) where ŷ = σ(Xβ). Same form as linear regression!

---

### Card 8
**Q:** What is the Hessian of logistic loss?
**A:** H = ¹/n XᵀDX where D = diag(ŷᵢ(1−ŷᵢ)). Positive definite → convex.

---

### Card 9
**Q:** How to optimize logistic regression?
**A:** Gradient descent, Newton's method (IRLS), L-BFGS, coordinate descent. IRLS uses Hessian for fast convergence.

---

### Card 10
**Q:** What is IRLS (Iteratively Reweighted Least Squares)?
**A:** Newton's method for logistic regression. Update: β := β − H⁻¹∇J. Equivalent to weighted least squares at each iteration.

---

### Card 11
**Q:** Interpretation of coefficient βⱼ?
**A:** Change in log-odds per unit Xⱼ. exp(βⱼ) = odds ratio. Not probability change (non-linear).

---

### Card 12
**Q:** What is the odds ratio?
**A:** OR = exp(βⱼ). Odds(Y=1|Xⱼ+1) / Odds(Y=1|Xⱼ). OR > 1: increases odds. OR < 1: decreases odds.

---

### Card 13
**Q:** What is regularization in logistic regression?
**A:** Add λ||β||₂₂ (Ridge) or λ||β||₁ (Lasso) to cross-entropy loss. Prevents overfitting.

---

### Card 14
**Q:** What is the effect of L2 regularization?
**A:** Shrinks all coefficients toward zero. Reduces variance. Handles multicollinearity. No sparsity.

---

### Card 15
**Q:** What is the effect of L1 regularization?
**A:** Induces sparsity (some βⱼ = 0). Feature selection. Less stable with correlated features.

---

### Card 16
**Q:** What is Elastic Net?
**A:** J = CE + λ₁||β||₁ + λ₂||β||₂₂. Combines L1 sparsity + L2 grouping of correlated features.

---

### Card 17
**Q:** How to choose λ?
**A:** Cross-validation (k-fold). Grid search or random search over log-spaced λ. 1-SE rule for simpler model.

---

### Card 18
**Q:** What is multi-class logistic regression?
**A:** Softmax: P(Y=k|X) = exp(βₖᵀX) / Σⱼ exp(βⱼᵀX). K classes, K-1 parameter vectors (reference class fixed).

---

### Card 19
**Q:** What is One-vs-Rest (OvR)?
**A:** Train K binary classifiers: class k vs all others. Predict class with highest probability.

---

### Card 20
**Q:** Softmax vs OvR?
**A:** Softmax: single model, calibrated probabilities, K-1 vectors. OvR: K independent models, simpler, uncalibrated.

---

### Card 21
**Q:** What is the decision boundary for multi-class?
**A:** Set of points where P(Y=k|X) = P(Y=j|X) ⇔ βₖᵀX = βⱼᵀX. Linear boundaries between each pair.

---

### Card 22
**Q:** What is calibration in classification?
**A:** Predicted probabilities match true frequencies. If P̂=0.8, should be correct 80% of time. Logistic regression is well-calibrated.

---

### Card 23
**Q:** How to calibrate a classifier?
**A:** Platt scaling (logistic regression on scores), isotonic regression. Post-processing step.

---

### Card 24
**Q:** What is the ROC curve?
**A:** Plot of TPR (recall) vs FPR at all thresholds. TPR = TP/(TP+FN), FPR = FP/(FP+TN).

---

### Card 25
**Q:** What is AUC?
**A:** Area Under ROC Curve. Probability that random positive ranks higher than random negative. 0.5 = random, 1.0 = perfect.

---

### Card 26
**Q:** What is the Precision-Recall curve?
**A:** Precision vs Recall at all thresholds. Better for imbalanced data. AUC-PR = average precision.

---

### Card 27
**Q:** What is the confusion matrix?
**A:** [[TN, FP], [FN, TP]]. True/False × Positive/Negative. Basis for all classification metrics.

---

### Card 28
**Q:** What are Precision, Recall, F1?
**A:** Precision = TP/(TP+FP). Recall = TP/(TP+FN). F1 = 2×P×R/(P+R). Harmonic mean.

---

### Card 29
**Q:** What is the relationship between decision threshold and metrics?
**A:** Lower threshold → more positives → higher recall, lower precision. Trade-off. Default 0.5 not always optimal.

---

### Card 30
**Q:** How to choose optimal threshold?
**A:** Maximize F1, or maximize (TPR − FPR) [Youden's J], or based on business cost matrix.

---

### Card 31
**Q:** What is class imbalance?
**A:** One class much rarer (e.g., fraud 0.1%). Accuracy misleading. Use AUC, F1, PR-AUC, balanced accuracy.

---

### Card 32
**Q:** How to handle class imbalance?
**A:** Class weights (weighted loss), resampling (oversample minority / undersample majority), threshold tuning, anomaly detection.

---

### Card 33
**Q:** What is the class weight in logistic regression?
**A:** Weighted loss: J = −Σ wᵢ[yᵢ log(ŷᵢ) + (1−yᵢ) log(1−ŷᵢ)]. w₁ = n/(2×n₁), w₀ = n/(2×n₀) for balanced.

---

### Card 34
**Q:** What is separation in logistic regression?
**A:** Perfect linear separation → MLE coefficients → ±∞. Regularization (λ>0) solves this.

---

### Card 35
**Q:** What is complete vs quasi-complete separation?
**A:** Complete: perfect separation exists. Quasi: separation for some subset. Both cause infinite MLE.

---

### Card 36
**Q:** What is the connection between logistic regression and Maximum Entropy?
**A:** Logistic regression = MaxEnt model with feature expectations as constraints. Same mathematical form.

---

### Card 37
**Q:** What is the connection to Generalized Linear Models (GLM)?
**A:** Logistic regression = GLM with Bernoulli distribution, logit link function. Linear predictor = η = Xβ.

---

### Card 38
**Q:** What are the assumptions of logistic regression?
**A:** (1) Linear log-odds, (2) Independence of observations, (3) No perfect multicollinearity, (4) Large sample (for asymptotics).

---

### Card 39
**Q:** What is the likelihood ratio test?
**A:** Compare nested models: −2(log L₀ − log L₁) ~ χ²_{df}. Tests if additional coefficients are jointly zero.

---

### Card 40
**Q:** What is the Hosmer-Lemeshow test?
**A:** Goodness-of-fit test. Group by predicted probability deciles, compare observed vs expected counts. χ² test.