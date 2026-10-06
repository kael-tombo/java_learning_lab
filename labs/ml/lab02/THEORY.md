# Logistic Regression

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

## 1. The Problem This Solves

Your target is a class, not a number, but you still want a linear decision boundary you can defend to a regulator.

It is the calibration reference for every classifier in the track, and the fastest way to learn how a loss function differs from a metric.

## 2. Learning Objectives

- Derive cross-entropy from maximum likelihood under Bernoulli outcomes
- Implement the sigmoid stably and know where it saturates
- Fit by gradient descent with feature scaling and a learning-rate schedule
- Read a confusion matrix and derive precision, recall, F1, accuracy
- Explain why the 0.5 threshold is a business decision, not a statistical one
- Diagnose complete separation and fix it with regularisation

## 3. Core Concepts

### 3.1 The sigmoid as a link function

s(z) = 1/(1+e⁻ᵣ) maps any real score to a probability. Its log-odds are linear: log(p/(1−p)) = z = β₀ + βᵀx. That is the actual model; the probability is just how we report it. Anything linear-in-log-odds is a logistic regression.

### 3.2 Cross-entropy as negative log-likelihood

J(β) = −(1/m)Σ[yᵢ log pᵢ + (1−yᵢ) log(1−pᵢ)]. Because it is the log of a Bernoulli likelihood, minimising it is maximum likelihood — no assumed error distribution, unlike squared loss on 0/1 labels.

### 3.3 Numerical stability

Never call log(sigmoid(−1000)): the sigmoid returns 0.0 and log(0) is −∞. Use the piecewise form or `log1p(exp(∑z))`, and clip probabilities before taking logs. This one detail separates a working implementation from a NaN at iteration 3.

### 3.4 The decision threshold

Predict 1 when p > 0.5 by default, but the threshold is a cost decision. A missed fraud (recall cost) is not the same as a false alarm. Sweep the threshold against your cost matrix and put the chosen value in the config.

### 3.5 Separation and regularisation

If a feature perfectly separates the classes, β diverges: log-loss keeps falling while accuracy is already 1. The fix is a small L2 penalty (or bounded iterations). Perfect accuracy plus enormous coefficients is the signature, and it will fail the moment the boundary moves.

### 3.6 Calibration vs discrimination

Discrimination is ranking positives above negatives (AUC); calibration is predicted probability matching observed frequency. Logistic regression is naturally calibrated; boosted trees and KNN often are not. If you report a probability to a risk team, check calibration, not just AUC.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `p = σ(z) = 1/(1+e⁻ᵣ)` | Sigmoid | score → probability |
| `z = β₀ + βᵀx` | Log-odds (logit) | the linear part of the model |
| `J(β) = −(1/m)Σ[y log p + (1−y)log(1−p)]` | Cross-entropy | mean negative log-likelihood |
| `∂J/∂βⱼ = (1/m)(pᵢ − yᵢ)xᵢ` | Gradient | convex, so descent converges |
| `Precision = TP/(TP+FP)` | Precision | of flagged cases, how many were right |
| `Recall = TP/(TP+FN)` | Recall / TPR | of true cases, how many we caught |
| `F1 = 2PR/(P+R)` | F1 | harmonic mean; punishes imbalance |
| `AUC = P(score(X₁) > score(X₀))` | ROC AUC | ranking quality, threshold-free |

## 5. How the Pieces Fit Together

1. Encode labels as 0/1 and split with stratification so both folds keep the class ratio.

2. Scale features (logistic regression has no scale invariance because of the penalty).

3. Initialise β = 0, so the initial loss is log 2 ≈ 0.693 — a useful sanity check.

4. Iterate β ← β − α·Xᵀ(p − y)/m until the loss change is below tolerance.

5. Compute the decision threshold from your cost matrix rather than accepting 0.5.

6. Report the confusion matrix, the PR curve and calibration — AUC alone hides threshold failures.

## 6. Assumptions and Invariants

- Correct model form: log-odds are linear in the features
- Observations are conditionally independent given the features
- No perfect separation, or a penalty is applied
- Features are measured without error (measurement error attenuates β)
- Sample is representative of the population you will score
- If regularising, features were standardised so the penalty is uniform

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| log(0) or NaN during the first iterations | computing log(sigmoid(z)) naively for large negative z | use the piecewise stable form or log1p(exp(z)) |
| Accuracy 100%, coefficients in the thousands | complete separation, no penalty | add L2 regularisation and report bounded coefficients |
| A great AUC and a useless model in practice | threshold set to 0.5 on an uncalibrated score | choose the threshold from the cost matrix; check calibration |
| Test F1 collapses while accuracy looks fine | class imbalance makes accuracy meaningless | always read the confusion matrix; optimise the metric that is priced |
| Predictions flip after deploy | scaler refit outside the estimator | ship the fitted scaler with β |
| Training loss decreases but probabilities are absurd | loss computed with unnormalised scores | verify the loss is averaged over samples, not summed inconsistently |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `Math.exp / Math.log1p` | stable sigmoid and log-loss without overflowing |
| `DoubleSummaryStatistics` | streaming class counts and score statistics |
| `Arrays.stream(...).parallel()` | the Xᵀ(p−y) accumulation parallelises cleanly over rows |
| `record BinaryRow(double[] x, int y)` | keeps the label alongside features so folds cannot drift apart |
| `SplittableRandom` | reproducible stratified shuffling for splits |
| `Math.min / Math.max clamping` | guard p into [ε, 1−ε] before taking logs |

## 9. Where This Sits in the Larger System

- **Lab 10** turns the confusion matrix into cross-validation and PR/ROC analysis.
- **Lab 03** trades the smooth boundary for axis-aligned splits and gains nonlinearity.
- **Lab 09** shows how boosting fixes logistic regression's linearity by adding weak trees.
- **mlops/lab10** applies these metrics to a real A/B decision on production traffic.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Derive cross-entropy from maximum likelihood under Bernoulli outcomes
- [ ] 0 — cannot yet — Implement the sigmoid stably and know where it saturates
- [ ] 0 — cannot yet — Fit by gradient descent with feature scaling and a learning-rate schedule
- [ ] 0 — cannot yet — Read a confusion matrix and derive precision, recall, F1, accuracy
- [ ] 0 — cannot yet — Explain why the 0.5 threshold is a business decision, not a statistical one
- [ ] 0 — cannot yet — Diagnose complete separation and fix it with regularisation

## 11. Summary Checklist

- [ ] I can derive cross-entropy from a Bernoulli likelihood in four lines
- [ ] I never call log(sigmoid(z)) without a stability guard
- [ ] I choose the threshold from costs, and can defend the choice
- [ ] I can spot separation from the coefficient magnitudes
- [ ] I can explain the PR curve's advantage over ROC under imbalance
- [ ] I know what calibration means and how to test it
