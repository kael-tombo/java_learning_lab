# Linear Regression - Vision & Where This Is Going

**Track:** ml  |  **Lab:** lab01  |  **Level:** Foundational

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

## 1. The Future State

Linear regression survives as the transparent baseline every ML system is measured against, and as the interpretable tier inside regulated decisions. The direction of travel is not fancier β — it is β that carries its own uncertainty, updates when the data drifts, and can be explained to a regulator in one sentence.

The test of that future state is boring: a new engineer ships a change to linear regression on day two without asking anyone where the magic lives.

## 2. What "Good" Looks Like in Practice

- Every service ships a mean/baseline predictor next to the real model, and its test error is on the same dashboard.
- Coefficients are published with confidence intervals and a direction sanity check, not as bare numbers.
- Preprocessing lives inside the model artifact so train/serve skew is structurally impossible.
- Regularisation strength (λ, or the feature scaling contract) is a versioned config value, not a hard-coded constant.

## 3. Capability Ladder

| Level | Capability | You can... |
|---|---|---|
| L1 | Fit and explain | Read a residual plot and name the assumption you violated. |
| L2 | Debug the fit | Trace a coefficient change back to collinearity, scaling or leakage. |
| L3 | Engineer the estimator | Add ridge/lasso, pick λ from a held-out curve, justify it in writing. |
| L4 | Own it in production | Alert on feature drift, retrain on a schedule, publish intervals with every prediction batch. |

## 4. Behaviours to Build

Write the residual plot before the metric. State assumptions out loud and test them. Prefer the model you can explain to a non-technical stakeholder unless you have measured evidence that a complex one beats it in a way that matters.

## 5. Anti-Vision (the failure mode we are avoiding)

- Quoting training R² in a slide deck as 'accuracy'.
- Throwing features at a model until the metric improves, with no held-out set to catch it.
- Hand-editing coefficients in a spreadsheet because the fit 'looked wrong'.
- Scaling outside the estimator, then wondering why production predictions drift.

## 6. Technology Shifts That Change the Work

1. Interpretable-by-default models (GAMs, monotonic constraints, sparse scoring) as a regulated baseline tier.
1. Uncertainty-aware reporting: prediction intervals and heteroscedastic noise models on every forecast.
1. Streaming/online variants of linear models that track distribution shift without full retraining.
1. Conformal prediction wrapping any regressor to guarantee marginal coverage.

## 7. Your 30/60/90 Commitment

- **30 days.** Implement OLS via QR, add the metric suite, and reproduce a coefficient vector by hand on a small dataset.
- **60 days.** Build the k-fold harness with in-fold preprocessing and quantify the optimism a leaked scaler introduces.
- **90 days.** Ship a prediction endpoint with a baked-in scaler, a baseline comparison on the same dashboard, and a drift alert on feature means.

## 8. How To Tell You Are Actually Getting Better

- I can state my model's test MAE and the baseline's, side by side, without looking anything up.
- Given a residual plot I can name the violated assumption in under 30 seconds.
- I can justify a regularisation strength from a curve rather than a preference.
- A colleague can reproduce my exact test score from the repo with one command.

## 9. Principles That Should Not Change

- **Derive** Derive and implement the normal-equation solution for OLS
- **Implement batch gradient descent** Implement batch gradient descent and explain why closed form usually wins
- **Compute MSE, MAE, RMSE** Compute MSE, MAE, RMSE and R² and know which one to quote

> Regression literacy is not a stepping stone to something better — it is the part that tells you whether anything you built is real.
