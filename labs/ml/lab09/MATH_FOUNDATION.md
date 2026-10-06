# Gradient Boosting - Mathematical Foundations

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

## Notation

| Symbol | Meaning |
|---|---|
| `Fₘ(x) = Fₗ₋₁(x) + η hₘ(x)` | Boosting update - add a weak learner, scaled |
| `rᵢ = yᵢ − F(xᵢ)` | Residual (squared error) - negative gradient for least squares |
| `gᵢ = pᵢ − yᵢ (log loss)` | Negative gradient (logistic) - the analogue for classification |
| `η ∈ (0, 1]` | Learning rate - shrinkage; small η needs more rounds |
| `v(x) = Σ_{m} η Tₘ(x)` | Ensemble value - sum of tree outputs, exactly additive |
| `early stop at argmin_m val_loss(m)` | Early stopping - the standard safeguard |
| `SHAP_i ≈ γ^T E[|S ∪ {i}|]` | TreeSHAP - exact additive attribution for tree ensembles |

## Why the Math Matters

Boosting turns learning into optimisation: the loss is the objective, the residual is the gradient, and the tree is the optimiser. Once that framing lands, the loss function becomes a plug-in choice and the only real questions are regularisation and early stopping.


---

## 1. From residuals to functional gradients

```text
F_m(x) = F_{m-1}(x) + eta * h_m(x)
r_i = y_i - F(x_i)                 (least squares)
r_i = p_i - y_i               (logistic)
F_m(x) = F_{m-1}(x) + eta * h_m(x),  h_m fits r
```

The residual is the negative gradient of the squared loss with respect to F(x). Gradient boosting generalises this to any differentiable loss, which is why it fits classification as easily as regression.

**Worked example.** y = [1, 3, 5], F = [1, 1, 1]. Residuals = [0, 2, 4]; the next tree fits them and F becomes [1, 3, 5]. Squared loss drops from 20/3 to 0.


---

## 2. Shrinkage as regularisation

```text
gradient of regularised objective:
G_M(x) = sum_m eta * h_m(x) + lambda * ||h_m||^2 / 2
approximate bound: test loss <= train_loss + sum_m eta * V(h_m) + M lambda
```

A small η with many weak learners approximates the full gradient path more finely, which lowers variance at the cost of many rounds. Lambda adds explicit complexity control for leaf values.

**Worked example.** eta = 1.0 reaches train error 0 in 6 rounds but test error 0.24. eta = 0.05 needs 120 rounds and reaches test error 0.11.


---

## 3. Early stopping as a bias-variance knob

```text
m* = argmin_m validation_loss(m)
shrink the final model toward the mean by eta * m* / m_best
```

Early stopping is choosing m, a hyperparameter, by validation loss. The optional extra shrinkage replaces the overfit tail rounds with a slightly more conservative model.

**Worked example.** Validation loss by round: 50 → 0.21, 100 → 0.14, 200 → 0.13, 400 → 0.18. Best round 200; without early stopping you ship round 400 at 0.18.


---

## 4. Histogram binning cost

```text
exact: O(n log n) sort + O(n * #distinct_values) per node
binned: O(n * #bins) per node, #bins ~ 64–256
speedup on 5M x 50: roughly 10–50x
```

Binning is a lossy but nearly free approximation: it trades a tiny amount of split precision for an order of magnitude in speed, and it is what makes GPU and histogram boosting practical.

**Worked example.** 5M rows × 50 features: exact search visits ~250M candidate splits per level; histogram visits 5M × 256 = 1.28B per level but with contiguous memory and no sorting — net 10–50x faster in practice.


---

## 5. Additivity and TreeSHAP

```text
prediction = base_value + sum_i phi_i
consistency: swapping a feature's value
changes the prediction by exactly the sum of its SHAP values
```

Because the model is a sum of trees, attributions can be computed exactly rather than approximated. The efficiency property means the sum of contributions equals the prediction gap, always.

**Worked example.** For a 20-feature tree ensemble, TreeSHAP is O(TLD²) versus sampling-based methods at ~200 evaluations; the additivity identity holds to 1e-9.


---

## 6. Stochastic gradient boosting

```text
each tree sees rows I with P(i in I) = rho, rho < 1
rho → 1: standard boosting (higher variance)
rho ~ 0.8: decorrelated trees, better generalisation
```

Subsampling rows per tree is the analogue of feature randomness in random forests. Averaging decorrelated trees reduces variance, which matters most exactly where boosting is weakest — shallow, high-bias trees.

**Worked example.** On a noisy tabular dataset, rho = 0.8 with depth 3 improves test error from 0.17 to 0.14 while allowing eta = 0.1 (faster convergence than eta = 0.03).


---

## Cheat Sheet

- `Fₘ(x) = Fₗ₋₁(x) + η hₘ(x)` - Boosting update
- `rᵢ = yᵢ − F(xᵢ)` - Residual (squared error)
- `gᵢ = pᵢ − yᵢ (log loss)` - Negative gradient (logistic)
- `η ∈ (0, 1]` - Learning rate
- `v(x) = Σ_{m} η Tₘ(x)` - Ensemble value
- `early stop at argmin_m val_loss(m)` - Early stopping
- `SHAP_i ≈ γ^T E[|S ∪ {i}|]` - TreeSHAP

## Numerical Traps

- Training to the last round instead of the best round.
- Computing the initial value as 0 rather than the loss-minimising constant.
- Summing SHAP values without the baseline expectation, breaking additivity.
- Using gain-based importance as if it were attribution.
- Tuning depth and eta separately, which lands on an expensive pair.

## Self-Check Problems

1. Compute two rounds of squared-error boosting by hand on 4 points with depth-1 stumps.
2. Compute the negative gradient for squared error, absolute error and logistic loss; state which is which.
3. Plot validation loss by round from a synthetic run and pick m*.
4. Verify TreeSHAP additivity numerically on a 3-tree ensemble.
5. Measure the effect of subsampling rho in {1.0, 0.9, 0.8, 0.6} on held-out loss.
