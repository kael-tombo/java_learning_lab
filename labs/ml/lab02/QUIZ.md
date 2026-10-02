# Logistic Regression — Quiz (10 Questions)

**Instructions:** Answer each question. Correct answers and explanations follow.

---

### Q1: What is the sigmoid function and its range?
A) σ(z) = 1 / (1 + e⁻ᶻ), range (0, 1)
B) σ(z) = eᶻ / (1 + eᶻ), range (0, 1)
C) σ(z) = 1 / (1 + eᶻ), range (0, 1)
D) Both A and B are correct

**Answer: D** — Both forms are equivalent: 1/(1+e⁻ᶻ) = eᶻ/(1+eᶻ). Maps any real number to (0,1), interpretable as probability.

---

### Q2: In logistic regression, what does the linear predictor z = β₀ + βᵀx represent?
A) The predicted probability
B) The log-odds (logit) of the positive class
C) The decision boundary
D) The loss function

**Answer: B** — z = log(P(Y=1|X)/P(Y=0|X)) = log-odds. P(Y=1|X) = σ(z) = eᶻ/(1+eᶻ).

---

### Q3: What is the decision boundary for binary logistic regression?
A) β₀ + βᵀx = 0
B) β₀ + βᵀx = 0.5
C) σ(β₀ + βᵀx) = 0
D) σ(β₀ + βᵀx) = 1

**Answer: A** — Decision boundary: P(Y=1|X) = 0.5 ⇔ σ(z) = 0.5 ⇔ z = 0 ⇔ β₀ + βᵀx = 0. Linear in feature space.

---

### Q4: What is the loss function for logistic regression (binary cross-entropy)?
A) J(β) = −Σ[yᵢ log(ŷᵢ) + (1−yᵢ) log(1−ŷᵢ)]
B) J(β) = Σ(yᵢ − ŷᵢ)²
C) J(β) = Σ|yᵢ − ŷᵢ|
D) J(β) = −Σ[yᵢ log(1−ŷᵢ) + (1−yᵢ) log(ŷᵢ)]

**Answer: A** — Binary cross-entropy (log loss). For one sample: L = −[y log(p) + (1−y) log(1−p)]. Convex in β. MLE under Bernoulli assumption.

---

### Q5: What is the gradient of the logistic regression loss?
A) ∇J = Xᵀ(ŷ − y)
B) ∇J = Xᵀ(y − ŷ)
C) ∇J = (ŷ − y)X
D) ∇J = X(ŷ − y)

**Answer: A** — ∇J = ¹/n Xᵀ(σ(Xβ) − y) = ¹/n Xᵀ(ŷ − y). Same form as linear regression but ŷ = σ(Xβ). Enables efficient gradient descent.

---

### Q6: Why can't we use MSE (squared error) for logistic regression?
A) MSE is not convex for logistic regression
B) MSE doesn't work with probabilities
C) MSE is only for regression
D) MSE is computationally expensive

**Answer: A** — MSE with sigmoid creates non-convex loss surface with local minima. Cross-entropy is convex (assuming linear predictor), guaranteeing global optimum.

---

### Q7: What is the interpretation of coefficient βⱼ in logistic regression?
A) Change in probability per unit change in Xⱼ
B) Change in log-odds per unit change in Xⱼ, holding others constant
C) Change in odds per unit change in Xⱼ
D) Correlation between Xⱼ and Y

**Answer: B** — βⱼ = Δ log-odds for 1-unit increase in Xⱼ. exp(βⱼ) = odds ratio (multiplicative change in odds). Probability change depends on current probability (non-linear).

---

### Q8: What is regularization in logistic regression?
A) Adding λ||β||²₂ (L2) or λ||β||₁ (L1) to the loss
B) Scaling features
C) Removing outliers
D) Using different optimization algorithm

**Answer: A** — Regularized loss: J(β) = CE(β) + λ||β||₂₂ (Ridge) or λ||β||₁ (Lasso). Prevents overfitting, handles multicollinearity. L1 induces sparsity.

---

### Q9: How do you handle multi-class classification with logistic regression?
A) Train K binary classifiers (One-vs-Rest)
B) Use softmax: P(Y=k|X) = e^{βₖᵀX} / Σⱼ e^{βⱼᵀX} (Multinomial)
C) Both A and B are valid approaches
D) Neither works

**Answer: C** — OvR: K binary classifiers. Multinomial (softmax): single model with K-1 parameter vectors (one class as reference). Softmax is more statistically efficient.

---

### Q10: What is the relationship between logistic regression and Naive Bayes?
A) They are the same model
B) Generative (NB) vs Discriminative (LogReg). LogReg lower asymptotic error if model correct; NB better with small data
C) Naive Bayes is always better
D) Logistic regression is a special case of Naive Bayes

**Answer: B** — NB models P(X|Y)P(Y) (generative). LogReg models P(Y|X) directly (discriminative). NB converges faster with less data but has higher asymptotic error if independence assumption violated. LogReg makes no independence assumption.