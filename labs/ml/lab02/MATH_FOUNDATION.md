# Logistic Regression - Mathematical Foundations

**Track:** ml  |  **Lab:** lab02  |  **Level:** Foundational

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

## Notation

| Symbol | Meaning |
|---|---|
| `p = σ(z) = 1/(1+e⁻ᵣ)` | Sigmoid - score → probability |
| `z = β₀ + βᵀx` | Log-odds (logit) - the linear part of the model |
| `J(β) = −(1/m)Σ[y log p + (1−y)log(1−p)]` | Cross-entropy - mean negative log-likelihood |
| `∂J/∂βⱼ = (1/m)(pᵢ − yᵢ)xᵢ` | Gradient - convex, so descent converges |
| `Precision = TP/(TP+FP)` | Precision - of flagged cases, how many were right |
| `Recall = TP/(TP+FN)` | Recall / TPR - of true cases, how many we caught |
| `F1 = 2PR/(P+R)` | F1 - harmonic mean; punishes imbalance |
| `AUC = P(score(X₁) > score(X₀))` | ROC AUC - ranking quality, threshold-free |

## Why the Math Matters

Everything in this lab falls out of one decision: model the outcome as Bernoulli and pick the link. The cost of that choice is a linear boundary; the benefit is a calibrated probability you can threshold on business grounds.


---

## 1. Sigmoid and its derivatives

```text
sigma(z) = 1/(1+e^-z)
d sigma/dz = sigma(z) * (1 - sigma(z))
max derivative = 0.25 at z = 0
```

The derivative's maximum of 1/4 means gradients vanish for extreme scores — the vanishing-gradient problem in its mildest form, and the reason we standardise and use a sensible learning rate.

**Worked example.** z = −20: p = 2.06e-10, p·(1−p) ≈ 2e-10. The gradient contribution is effectively zero, so that row stops learning even if it is misclassified.


---

## 2. Cross-entropy from maximum likelihood

```text
P(y) = prod_i p_i^y_i (1-p_i)^(1-y_i)
log P(y) = sum_i [y_i log p_i + (1-y_i) log(1-p_i)]
J = -log P(y)/m
```

The likelihood of a set of Bernoulli labels factorises exactly because observations are conditionally independent. Taking logs turns products into sums, which is what makes the optimisation tractable.

**Worked example.** Two rows, one y=1 with p=0.9 and one y=0 with p=0.1: log-likelihood = log 0.9 + log 0.9 = -0.21, so J = 0.105. Confident and correct is cheap.


---

## 3. Stable log-loss

```text
log(1 - sigma(z)) for z >= 0:  = log(1 + e^-z) = log1p(e^-z)
log(sigma(z)) for z < 0:   = -z + log1p(e^z)
loss = -[y*logp + (1-y)*log1p_mp]
```

The two branches avoid evaluating e^(+large), which overflows a double at about 709. This is the difference between a fit that converges and one that returns NaN on row 50.

**Worked example.** z = −1000, y = 1: naive code computes log(0.0) = -Infinity, J becomes NaN and the loop dies. Stable form gives -y·z + log1p(e^z) = 0.0 exactly.


---

## 4. Gradient and convexity

```text
dJ/d beta_j = (1/m) sum_i (p_i - y_i) x_ij
J is convex in beta => gradient descent reaches the global optimum
```

Cross-entropy is convex, so there is a single global minimum and no restarts or learning-rate drama beyond step size. Regularisation keeps it strictly convex and makes the solution unique.

**Worked example.** On separable data the minimum is at infinity, so J decreases monotonically and β grows without bound — convexity, not convergence, is the issue.


---

## 5. Threshold and expected cost

```text
Cost(t) = FP(t) * cFP + FN(t) * cFN
optimal t* = argmin_t Cost(t)
for calibrated p: classify 1 iff p > cFP/(cFP+cFN)
```

The optimal threshold is a function of the cost ratio, not of the data. A missed case costing 10x a false alarm moves the threshold to about 0.09.

**Worked example.** cFP = 5, cFN = 50: threshold ≈ 0.09. At that point recall rises sharply and precision falls — the right trade when a missed case is a missed fraud.


---

## 6. Gradient descent step size

```text
Hessian of J = (1/m) X^T W X, W = diag(p(1-p))
alpha < 2 / lambda_max(H)
```

Because W ∈ (0, 0.25], the curvature is bounded, which gives a principled step-size ceiling. Too large and the iterates oscillate; too small and 1000 iterations is not enough.

**Worked example.** With standardised features and n=1000, p=10, lambda_max ≈ 2.5, so alpha = 0.1 is safely stable; alpha = 0.9 diverges and the loss becomes NaN.


---

## Cheat Sheet

- `p = σ(z) = 1/(1+e⁻ᵣ)` - Sigmoid
- `z = β₀ + βᵀx` - Log-odds (logit)
- `J(β) = −(1/m)Σ[y log p + (1−y)log(1−p)]` - Cross-entropy
- `∂J/∂βⱼ = (1/m)(pᵢ − yᵢ)xᵢ` - Gradient
- `Precision = TP/(TP+FP)` - Precision
- `Recall = TP/(TP+FN)` - Recall / TPR
- `F1 = 2PR/(P+R)` - F1
- `AUC = P(score(X₁) > score(X₀))` - ROC AUC

## Numerical Traps

- log(0), log(1) and overflow in e^z — use the two-branch stable form.
- Averaging the loss over rows while leaving the gradient un-normalised — inconsistent by a factor of m.
- Comparing AUC across datasets with different base rates; AUC is base-rate invariant but the operating point is not.
- Reporting accuracy on a 1% positive class and concluding the model works.

## Self-Check Problems

1. Derive dJ/dβⱼ from the likelihood and verify against finite differences on a 4-row example.
2. Compute the loss for p = [0.9, 0.1] with y = [1, 0] and again with y = [0, 1]; explain the difference in three sentences.
3. Show that log(sigmoid(-800)) is NaN in double precision but the stable form returns a finite number.
4. For cFP = 5 and cFN = 50, compute the cost-optimal threshold and the resulting precision/recall on a small labelled set.
5. Plot the loss surface for two collinear features and show the long valley that scaling fixes.
