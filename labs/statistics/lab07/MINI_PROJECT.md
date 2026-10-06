# MINI_PROJECT — Weekly Demand Forecast with Honest Intervals

**Track:** statistics  |  **Lab:** lab07  |  **Level:** Advanced

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

**Brief.** Forecast a seasonal series, beat the naive baselines with rolling-origin evaluation, and publish intervals.

**Timebox.** 3–4 hours

## 1. Why This Project Exists

Forecasting is where statistical shortcuts hide best, because random splits and narrow intervals both look like success.

## 2. Requirements

- Decomposition with an argued additive or multiplicative choice.
- SMA and EMA with a responsiveness argument for the chosen parameter.
- ACF analysis identifying the seasonal period and any momentum.
- Naive and seasonal naive baselines computed on identical folds.
- Rolling-origin evaluation as the only protocol, reporting error by horizon.
- Structural break detection with explicit modelling of a shift.
- Empirical forecast intervals with measured coverage.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 30m | Plot series, ACF and decomposition | A diagnostic panel |
| 2 | 25m | Naive and seasonal naive baselines | Baseline errors by horizon |
| 3 | 30m | SMA/EMA with a responsiveness argument | A smoothing choice with reasons |
| 4 | 35m | Rolling-origin evaluation across three forecasters | A comparison by horizon |
| 5 | 25m | Change-point detection and modelling | A break demonstration |
| 6 | 30m | Empirical intervals with measured coverage | An interval comparison |
| 7 | 25m | Forecast with caveats and a recommended horizon | A handover report |

## 4. Architecture Sketch

```text
 series plot --> ACF --> seasonal period identified
     |
 decomposition: trend + seasonal + residual (additive or multiplicative)
     |
 baselines: naive | seasonal naive        (same folds as everything else)
     |
 models: SMA / EMA with declared responsiveness
     |
 rolling-origin evaluation --> error by horizon (the only protocol)
     |
 change points detected --> level shift modelled explicitly
     |
 empirical intervals --> coverage measured
     |
 report: forecast + interval + recommended horizon + failure modes
```

## 5. Implementation Notes

- Establish the baselines first; a sophisticated model that loses to seasonal naive is the honest outcome.
- Report error by horizon so the report can state where the forecast stops being useful.
- Inject a known level shift to prove your break detection works.
- Intervals from realised errors beat residual-standard-deviation intervals; measure the coverage.

## 6. Deliverables

1. Diagnostic panel with series, ACF and decomposition.
1. Rolling-origin comparison of three forecasters against both baselines.
1. Change-point demonstration and empirical interval coverage.
1. Forecast with interval, recommended horizon and stated failure modes.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Diagnostics | 25% | ACF read correctly; decomposition choice justified |
| Evaluation | 30% | Rolling origins only; baselines on identical folds; error by horizon |
| Uncertainty | 25% | Empirical intervals with measured coverage |
| Structure | 20% | Break detection and explicit modelling of level shifts |

## 8. Stretch Goals

- Add autoregressive modelling with differencing.
- Add hierarchical reconciliation if the series aggregates.
- Add quantile forecasts with calibration checks.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Decomposition with an argued additive or multiplicative choice.
- [ ] SMA and EMA with a responsiveness argument for the chosen parameter.
- [ ] ACF analysis identifying the seasonal period and any momentum.
- [ ] Naive and seasonal naive baselines computed on identical folds.
- [ ] Rolling-origin evaluation as the only protocol, reporting error by horizon.
- [ ] Structural break detection with explicit modelling of a shift.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
