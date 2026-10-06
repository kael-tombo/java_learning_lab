# Gradient Boosting

**Track:** ml  |  **Lab:** lab09  |  **Level:** Advanced

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

A single shallow tree underfits. Sequentially adding many of them, each correcting the last, fits nearly as well as a deep model while keeping the pieces interpretable.

Boosting is the default for tabular prediction. Its two knobs — the learning rate and the number of rounds — are the bias-variance dial of practical machine learning.

## 2. Learning Objectives

- Derive the gradient-boosting update from the negative gradient of a loss
- Implement regression and logistic boosting with shallow trees as weak learners
- Explain the difference between gradient boosting and AdaBoost
- Use the learning rate and n_estimators as a joint regularisation pair
- Diagnose overfitting with validation curves and early stopping
- Read feature importance and SHAP-style contributions from an additive model

## 3. Core Concepts

### 3.1 Stage-wise additive fitting

Fₘ(x) = Fₗ₋₁(x) + η hₘ(x). Each new weak learner fits the negative gradient of the loss with respect to the current prediction, so the ensemble improves monotonically on the training objective. It is boosting in the functional-gradient sense, not a reweighting scheme.

### 3.2 The learning rate is the real hyperparameter

η scales every weak learner's contribution. Small η with many rounds is a fine-grained, well-regularised fit; large η with few rounds is coarse and fast. The pair (η, M) is one regularisation dial — tune it jointly, never separately, and always with early stopping as the backstop.

### 3.3 Gradient boosting versus AdaBoost

AdaBoost reweights misclassified samples and fits a classifier on the reweighted set. Gradient boosting fits residuals or gradients directly, which generalises to any differentiable loss — squared error, absolute error, logistic — with no reweighting trick. XGBoost and LightGBM add regularisation and histogram binning to the same idea.

### 3.4 Early stopping and the eval set

Boosting overfits monotonically on training loss while validation loss turns. The standard protocol reserves a validation split, tracks validation loss every round, and stops at the best round with a patience window. In production, ship the best-round count, not the last round.

### 3.5 Subsampling as stochastic regularisation

Stochastic gradient boosting samples a fraction of rows per tree. This decorrelates the trees the same way feature randomness does in a random forest, which is where a good part of its robustness comes from.

### 3.6 Additivity makes it explainable

Because the model is a sum of trees, a prediction decomposes exactly into per-feature contributions. This is the basis of treeSHAP and of the reason-code systems risk teams need — a property no other strong tabular model offers as cleanly.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `Fₘ(x) = Fₗ₋₁(x) + η hₘ(x)` | Boosting update | add a weak learner, scaled |
| `rᵢ = yᵢ − F(xᵢ)` | Residual (squared error) | negative gradient for least squares |
| `gᵢ = pᵢ − yᵢ (log loss)` | Negative gradient (logistic) | the analogue for classification |
| `η ∈ (0, 1]` | Learning rate | shrinkage; small η needs more rounds |
| `v(x) = Σ_{m} η Tₘ(x)` | Ensemble value | sum of tree outputs, exactly additive |
| `early stop at argmin_m val_loss(m)` | Early stopping | the standard safeguard |
| `SHAP_i ≈ γ^T E[|S ∪ {i}|]` | TreeSHAP | exact additive attribution for tree ensembles |

## 5. How the Pieces Fit Together

1. Split into train/validation/test; the validation split drives early stopping and is not the test set.

2. Initialise F₀ with a constant (mean target, or log-odds for logistic loss).

3. For each round m: compute negative gradients, fit a shallow tree on them, update F ← F + η hₘ.

4. Track validation loss every round; keep the best round.

5. Sweep η and depth jointly, and pick the pair with the best validation loss at a comparable round count.

6. Fit the final model with the chosen M, then extract SHAP values for explanations and importance.

## 6. Assumptions and Invariants

- The loss is differentiable and the weak learner can fit its negative gradient
- Trees are deliberately shallow (depth 1–6); depth and boosting interact strongly
- Shrinkage is used; η = 1 with many rounds overfits almost immediately
- Validation data is separate from training and from the final test set
- Features are handled the same way at train and serve time (no target leakage in splits)
- Early stopping is available; without it the model will train past its optimum

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| Train loss keeps falling, validation loss turns at round 40 | training continued past the optimum | early stop on validation loss and ship the best round |
| The model is worse than a random forest | depth too large and η too small, or no subsampling | try depth 2–3, η 0.05–0.1, subsample 0.8 |
| SHAP values sum to something other than the prediction | missing the baseline expectation term | use the tree_path_dependent method and verify the additivity identity |
| Predictions change after deploy | categorical encoding or scaling done outside the estimator | version preprocessing inside the model artifact |
| Training is slow on 5M rows | exact splits on all features | histogram binning: pre-bucket features into 64–256 bins |
| Boosting importance looks like importance | correlated features split credit arbitrarily | use SHAP values on held-out data, not gain-based importance |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `int[] binIndex per feature` | histogram binning turns split search into integer counting |
| `PriorityQueue<Double> leafValues` | SHAP value computation over tree paths |
| `Arrays.sort on per-feature histograms` | the classic boosting inner loop |
| `SplittableRandom` | per-tree row subsampling that stays reproducible |
| `double[][] featureImportance by gain` | cheap first pass before investing in SHAP |

## 9. Where This Sits in the Larger System

- **Lab 03** supplies the weak learner; here it is a shallow tree added sequentially.
- **Lab 01** supplies the residuals that squared-error boosting fits.
- **Lab 02** supplies the logistic loss whose gradient boosting also minimises.
- **Lab 10** gives the validation protocol that early stopping depends on.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Derive the gradient-boosting update from the negative gradient of a loss
- [ ] 0 — cannot yet — Implement regression and logistic boosting with shallow trees as weak learners
- [ ] 0 — cannot yet — Explain the difference between gradient boosting and AdaBoost
- [ ] 0 — cannot yet — Use the learning rate and n_estimators as a joint regularisation pair
- [ ] 0 — cannot yet — Diagnose overfitting with validation curves and early stopping
- [ ] 0 — cannot yet — Read feature importance and SHAP-style contributions from an additive model

## 11. Summary Checklist

- [ ] I can derive the boosting update as functional gradient descent
- [ ] I tune learning rate and rounds jointly, with early stopping
- [ ] I know how boosting differs from AdaBoost and from random forests
- [ ] I can compute and verify SHAP additivity
- [ ] I use histogram binning when n is large
- [ ] I never report boost importance without saying what it measures
