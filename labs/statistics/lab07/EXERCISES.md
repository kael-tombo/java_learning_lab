# Time Series Analysis - Exercises

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

## How To Work These

Work in order. Each exercise builds the next; do not skip ahead.
Every exercise ends with a *deliverable* you can show someone - code that compiles, a number you can defend, or a table you can regenerate.

Run the lab as you go:

```bash
cd lab07
javac -d out $(Get-ChildItem -Recurse -Filter *.java src | ForEach-Object { $_.FullName })
java -cp out com.statistics.lab07.TimeSeriesAnalysis
```

## Exercise 1: Decomposition

**Task.** Trend, seasonality, residual.

**Steps**
- Compute a trend by centred moving average.
- Extract seasonal indices for a declared period.
- Choose additive or multiplicative with a reason.
- Plot the residual component.

**Deliverable.** A decomposition with a justified choice.

## Exercise 2: Smoothing and responsiveness

**Task.** Know what alpha means.

**Steps**
- Implement SMA and EMA.
- Apply a level shift and compare responsiveness.
- Sweep alpha and record bias versus variance.
- Choose alpha for a stated operational cost.

**Deliverable.** A smoothing comparison with a chosen parameter.

## Exercise 3: Autocorrelation analysis

**Task.** Identify structure before modelling.

**Steps**
- Compute ACF to a maximum lag with confidence bounds.
- Identify the seasonal lag and any momentum.
- Distinguish seasonality from autocorrelation.
- Justify the model class you chose.

**Deliverable.** An ACF analysis with a model justification.

## Exercise 4: Rolling-origin evaluation

**Task.** The honest protocol.

**Steps**
- Implement rolling-origin folds.
- Evaluate naive, seasonal naive and a smoothed forecaster.
- Report error by horizon.
- Show what a random split would have claimed.

**Deliverable.** An evaluation report with the optimism quantified.

## Exercise 5: Structural breaks

**Task.** Separate change from noise.

**Steps**
- Detect change points on a series with a known shift.
- Compare with the same shift absent.
- Model the break explicitly.
- Show the effect on forecast accuracy.

**Deliverable.** A break detection and modelling demonstration.

## Exercise 6: Forecast intervals

**Task.** Be honestly uncertain.

**Steps**
- Derive intervals from rolling-origin errors.
- Compare against residual-standard-deviation intervals.
- Measure empirical coverage.
- Report the width at each horizon.

**Deliverable.** An interval comparison with measured coverage.

## Exercise 7: Weekly and seasonal forecasting

**Task.** The operational case.

**Steps**
- Build a weekly series with holidays and a trend.
- Compare seasonal naive with a smoothed seasonal model.
- Tune on validation folds only.
- Write the forecast with an interval and caveats.

**Deliverable.** A seasonal forecast with an honest interval.

## Exercise 8: Full forecasting report

**Task.** Something you would hand over.

**Steps**
- Plot series, ACF and decomposition.
- Establish baselines and report their errors.
- Fit a model chosen from the diagnostics.
- Report rolling-origin error by horizon with intervals and limitations.

**Deliverable.** A handover-ready forecast report.


---

## Self-Check Before You Move On

- [ ] My evaluation never lets the model see the future.
- [ ] I report error by horizon, not one aggregate.
- [ ] I beat the seasonal naive baseline or I explain why not.
- [ ] My forecast intervals come from realised errors.
