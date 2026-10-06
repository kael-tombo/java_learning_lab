# MINI_PROJECT — Dimensionality Reduction for a Credit Scorecard

**Track:** ml  |  **Lab:** lab08  |  **Level:** Intermediate

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

**Brief.** Reduce a correlated feature set, choose components with evidence, and ship a compression transform with a monitored spectrum.

**Timebox.** 3 hours

## 1. Why This Project Exists

Credit modelling is full of near-duplicate features (income variants, debt ratios), so collinearity is real and PCA both diagnoses and fixes it.

## 2. Requirements

- Load a lending-style dataset (or synthesise correlated features deliberately).
- Standardise, fit PCA, and print the eigenvalue spectrum with a cumulative-variance curve.
- Sweep k and compare downstream logistic-regression validation error; choose k from that curve.
- Compare PCA features against the raw correlated features and against ridge; report all three.
- Interpret the top 3 components by loading pattern and write a paragraph each.
- Ship the transform with mean, scale and components; add a drift check comparing incoming variance to the fitted spectrum.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 25m | Build the feature matrix with deliberately correlated columns; quantify VIF | A collinearity report |
| 2 | 25m | Fit PCA; print eigenvalues, ratios and cumulative curve | A spectrum table |
| 3 | 30m | Sweep k; cross-validated logistic regression per k | A validation-error-vs-k curve |
| 4 | 25m | Compare raw, PCA and ridge on the same folds | A three-row comparison table |
| 5 | 25m | Interpret the top 3 components from loadings | Three written interpretations |
| 6 | 25m | Serialise the transform; verify prediction parity after reload | A parity test |
| 7 | 20m | Add the spectrum drift check and a model card | A monitoring stub and a card |

## 4. Architecture Sketch

```text
applications.csv --> feature matrix (correlated)
                        |
        Standardiser (frozen in artifact)
                        |
   eigen-decomposition of covariance  |  SVD cross-check
                        |
   component scores --> logistic regression (k sweep)
                        |
   raw vs PCA vs ridge comparison
                        |
   serialised transform + spectrum drift check
```

## 5. Implementation Notes

- If PCA and ridge perform identically, that is a finding: say so rather than shipping PCA for its own sake.
- Correlated features make individual loadings unstable; report component patterns, not a ranking of coefficients.
- The spectrum drift check catches a change in the input distribution that would silently invalidate the transform.
- Verify parity after reload: rounding in the serialised format has bitten everyone.

## 6. Deliverables

1. One-command run producing the spectrum, k sweep and three-way comparison.
1. Top-3 component interpretations in plain language.
1. Serialised transform with a parity test.
1. Model card including the collinearity finding and a retrain trigger.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Correctness | 30% | PCA verified against SVD; scaling and centring inside the artifact |
| k selection | 25% | Downstream validation used, not the 95% convention |
| Comparison | 20% | Raw vs PCA vs ridge on identical folds |
| Interpretation | 15% | Component-level interpretation, honest about instability |
| Communication | 10% | Model card states the operational caveat |

## 8. Stretch Goals

- Add whitening and report the effect on the downstream model's coefficient stability.
- Implement incremental PCA and update the transform weekly as data accrues.
- Compare against a supervised projection on the same folds and write the recommendation.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Load a lending-style dataset (or synthesise correlated features deliberately).
- [ ] Standardise, fit PCA, and print the eigenvalue spectrum with a cumulative-variance curve.
- [ ] Sweep k and compare downstream logistic-regression validation error; choose k from that curve.
- [ ] Compare PCA features against the raw correlated features and against ridge; report all three.
- [ ] Interpret the top 3 components by loading pattern and write a paragraph each.
- [ ] Ship the transform with mean, scale and components; add a drift check comparing incoming variance to the fitted spectrum.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
