# Correlation & Regression - Vision & Where This Is Going

**Track:** statistics  |  **Lab:** lab05  |  **Level:** Intermediate

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

Regression gives way to regularised and distributional models for prediction, and to explicit causal designs for explanation. The persisting skill is reading residual and influence diagnostics honestly rather than accepting a coefficient.

The test of that future state is boring: a new engineer ships a change to correlation & regression on day two without asking anyone where the magic lives.

## 2. What "Good" Looks Like in Practice

- Data is plotted and both correlations computed before any fit.
- Coefficients carry standard errors and intervals.
- Residual and influence diagnostics are part of every fit, not an optional extra.
- Language distinguishes association from causation.

## 3. Capability Ladder

| Level | Capability | You can... |
|---|---|---|
| L1 | Fit | Simple and multiple regression with a coefficient table. |
| L2 | Diagnose | Residuals, leverage, influence, VIF and curvature. |
| L3 | Repair | Transforms, robust fitting and regularisation with validation. |
| L4 | Claim | Causal language only when a design supports it. |

## 4. Behaviours to Build

Plot first, fit second, diagnose third. Report uncertainty with every estimate. Never call an observational coefficient an effect.

## 5. Anti-Vision (the failure mode we are avoiding)

- R² quoted as accuracy with no validated error.
- A causal claim from a dashboard regression.
- A confident prediction outside the observed range of x.
- A model with high VIF presented as interpretable.

## 6. Technology Shifts That Change the Work

1. Regularisation and sparse models where prediction is the goal.
1. Heteroscedasticity-robust and Bayesian inference for coefficient uncertainty.
1. Causal inference frameworks making the identifying assumption explicit.
1. Distributional regression for heteroscedastic and heavy-tailed outcomes.

## 7. Your 30/60/90 Commitment

- **30 days.** Implement Pearson and Spearman and explain any gap between them.
- **60 days.** Implement multiple regression with intervals and full residual diagnostics.
- **90 days.** Handle collinearity and nonlinearity, validate on held-out data, and write causal limitations.

## 8. How To Tell You Are Actually Getting Better

- I plot before I fit.
- My coefficients carry intervals.
- I inspect residuals and influence on every fit.
- I never describe an observational coefficient as an effect.

## 9. Principles That Should Not Change

- **Compute Pearson** Compute Pearson and Spearman correlation and explain the difference
- **Build simple** Build simple and multiple linear regression by least squares
- **Interpret slope, intercept, R²** Interpret slope, intercept, R² and coefficient uncertainty correctly

> The coefficient is the smallest part of a regression; the diagnostics and the design are the analysis.
