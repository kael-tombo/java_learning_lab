# MINI_PROJECT — Demand Forecaster with an Honest Evaluation Harness

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

**Brief.** Build a small regression service that predicts daily demand per store and SKU, with the preprocessing, the baseline, and the evaluation protocol all inside the same artifact.

**Timebox.** 3–4 hours

## 1. Why This Project Exists

The interesting part of a forecasting model is not the fit — it is the baseline it must beat, the split that respects time, and the fact that the scaler must ship with the coefficients. This project forces all three.

## 2. Requirements

- Load a CSV of date, store_id, sku, promo_flag, price, units_sold (synthesise 2 years of data if you have none).
- Engineer features: day-of-week one-hot, month, rolling 7-day mean of *past* units only, and a promo interaction.
- Implement OLS (closed form) plus a ridge variant with a λ you select from a held-out curve.
- Ship a mean-of-last-28-days baseline and beat it, or explain why you cannot.
- Split by time (train on the past, test on the last 30 days), never randomly.
- Report MSE, MAE, R² and a per-SKU breakdown; write a 10-line model card.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 20m | Synthesise or load the dataset; assert no future leakage in feature construction | A CSV plus a leakage checklist you can defend |
| 2 | 25m | Implement `features(row, asOfDate)` so a row's features only use history | Refusing any feature that would need future data |
| 3 | 30m | Implement OLS and ridge with in-estimator scaling | Coefficients reproduce to 1e-8 and ridge shrinks them |
| 4 | 25m | Build the time-based split and the 28-day-mean baseline | Baseline MAE computed and printed first |
| 5 | 30m | Sweep λ on the validation window, plot test error, choose λ | A defensible λ plus the curve that justifies it |
| 6 | 25m | Per-SKU error breakdown and a residual diagnostic pass | Worst 5 SKUs explained in one line each |
| 7 | 20m | Write the model card and a README with the exact run command | A stranger reproduces your numbers in one command |

## 4. Architecture Sketch

```text
CSV rows --> FeatureBuilder (uses history only)
                    |
                    v
             [time split: train / valid / test-30d]
                    |
        +-----------+-----------+
        |                       |
   Standardizer            Baseline (28-day mean)
   (inside estimator)             |
        |                       |
     OLS / ridge                 |
        |                       |
        +-----------+-----------+
                    v
        Metrics + per-SKU report + model card
```

## 5. Implementation Notes

- Rolling means must use `shift(1)` semantics: today's feature cannot include today's sales.
- Promo interactions are where ridge earns its keep — promo and price are strongly correlated.
- Store a `featureVersion` string with the artifact so a schema change is detectable.
- Print the baseline metric before your model metric; it disciplines every claim that follows.

## 6. Deliverables

1. Runnable Maven/Gradle project with one command to reproduce the reported numbers.
1. Metrics table: baseline vs OLS vs ridgeλ*, train/valid/test, MAE and MSE.
1. ASCII plots of validation error vs λ and of residuals vs fitted.
1. 10-line model card: data, features, metrics, known limitations, retrain trigger.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Correctness | 30% | Coefficients verified by hand; no leakage; time-based split respected |
| Evaluation honesty | 25% | Baseline reported, λ chosen from a curve, test set touched once |
| Engineering | 20% | Estimator owns its preprocessing; artifacts are versioned; tests pass |
| Communication | 15% | Model card explains limitations and a retrain trigger |
| Insight | 10% | At least one non-obvious finding about the data, quantified |

## 8. Stretch Goals

- Add a seasonal naive baseline (same weekday, previous week) and show which model wins where.
- Compute prediction intervals with residual quantiles and report coverage.
- Add a drift check that alerts when live rolling-mean features diverge from training.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Load a CSV of date, store_id, sku, promo_flag, price, units_sold (synthesise 2 years of data if you have none).
- [ ] Engineer features: day-of-week one-hot, month, rolling 7-day mean of *past* units only, and a promo interaction.
- [ ] Implement OLS (closed form) plus a ridge variant with a λ you select from a held-out curve.
- [ ] Ship a mean-of-last-28-days baseline and beat it, or explain why you cannot.
- [ ] Split by time (train on the past, test on the last 30 days), never randomly.
- [ ] Report MSE, MAE, R² and a per-SKU breakdown; write a 10-line model card.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
