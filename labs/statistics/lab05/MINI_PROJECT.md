# MINI_PROJECT — Regression with Diagnostics and Honest Claims

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

**Brief.** Fit a real relationship, diagnose it thoroughly, and write claims that match what the design supports.

**Timebox.** 3–4 hours

## 1. Why This Project Exists

Regression is where statistical care pays for itself most visibly: the diagnostics find problems no coefficient can.

## 2. Requirements

- Pearson and Spearman with an explanation of any gap.
- Simple and multiple regression with standard errors and intervals.
- Residual diagnostics: against fitted, against predictors, leverage against squared residual.
- Collinearity demonstration with VIF and a remedy.
- Nonlinearity repair with a quadratic term or transform, validated on held-out data.
- A confounding demonstration showing what adjustment does.
- A report with an explicit limitations section.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 30m | Correlations and a scatter plot; explain the gap | A correlation report |
| 2 | 35m | Simple regression with hand verification | A verified coefficient table |
| 3 | 35m | Multiple regression with intervals | A complete table |
| 4 | 30m | Residual, leverage and influence diagnostics | A diagnostics report |
| 5 | 30m | Collinearity with VIF and a remedy | A remedy demonstration |
| 6 | 30m | Nonlinearity repair plus held-out validation | A form-selection report |
| 7 | 30m | Confounding demonstration and limitations section | An honest report |

## 4. Architecture Sketch

```text
 data --> scatter plot (first, always)
     |
 Pearson + Spearman --> gap explained (curvature, outliers, ties)
     |
 least squares (simple -> multiple) with SE and intervals
     |
 diagnostics: e vs fitted | e vs each predictor | leverage vs e^2 | Cook's D
     |
 repair: VIF -> ridge/drop | curvature -> quadratic/transform | outliers -> robust fit
     |
 validate on held-out data (not R^2)
     |
 confounding analysis + limitations: extrapolation, unmeasured confounders
```

## 5. Implementation Notes

- Plot before fitting; curvature and clusters are obvious in a scatter and invisible in a coefficient.
- Compute the slope standard error by hand for the simple case so the machinery is understood.
- Influence needs both high leverage and a large residual; neither alone is enough.
- The limitations section is the deliverable most reviewers read first.

## 6. Deliverables

1. Correlation report with a scatter plot and explained gaps.
1. Regression with complete coefficient tables and diagnostics.
1. Collinearity and nonlinearity remedies with validated error.
1. Confounding analysis and an honest limitations section.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Correctness | 30% | Coefficients, standard errors and diagnostics verified |
| Diagnostics | 25% | Residual and influence plots interpreted correctly |
| Remediation | 20% | Collinearity and nonlinearity addressed with evidence |
| Validation | 15% | Held-out error reported alongside R² |
| Honesty | 10% | Limitations and causal caveats explicit |

## 8. Stretch Goals

- Add weighted least squares and compare intervals.
- Add robust regression and show the slope difference.
- Add a causal-inference framing with explicit exchangeability assumptions.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Pearson and Spearman with an explanation of any gap.
- [ ] Simple and multiple regression with standard errors and intervals.
- [ ] Residual diagnostics: against fitted, against predictors, leverage against squared residual.
- [ ] Collinearity demonstration with VIF and a remedy.
- [ ] Nonlinearity repair with a quadratic term or transform, validated on held-out data.
- [ ] A confounding demonstration showing what adjustment does.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
