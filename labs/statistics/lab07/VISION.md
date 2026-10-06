# Time Series Analysis - Vision & Where This Is Going

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

## 1. The Future State

Time series practice converges on hierarchical forecasting (reconciling forecasts across levels), probabilistic forecasts with calibrated intervals, and change-point detection as a first-class component. Honest evaluation remains the differentiator.

The test of that future state is boring: a new engineer ships a change to time series analysis on day two without asking anyone where the magic lives.

## 2. What "Good" Looks Like in Practice

- Naive and seasonal naive baselines are computed and published.
- Evaluation uses rolling origins and reports error by horizon.
- Change points are detected and modelled explicitly.
- Forecast intervals come from realised errors.

## 3. Capability Ladder

| Level | Capability | You can... |
|---|---|---|
| L1 | Visualise | Plot the series, ACF and decomposition. |
| L2 | Baseline | Naive and seasonal naive with rolling-origin errors. |
| L3 | Model | Smoothing, differencing and AR models chosen from diagnostics. |
| L4 | Honest | Empirical intervals, change-point handling, horizon-aware reporting. |

## 4. Behaviours to Build

Establish the baseline before the model. Evaluate the way you forecast. Report error by horizon, because that is what tells a business when to stop trusting the forecast.

## 5. Anti-Vision (the failure mode we are avoiding)

- A random split on a time series.
- A forecast with no interval.
- A model tuned on the test period.
- A level shift described as a growth trend.

## 6. Technology Shifts That Change the Work

1. Hierarchical forecasting with coherent reconciliation across levels.
1. Calibrated probabilistic forecasts with quantile or distribution outputs.
1. Change-point detection integrated into forecast models.
1. Foundation-model forecasting approaches with careful benchmark baselines.

## 7. Your 30/60/90 Commitment

- **30 days.** Plot the series, ACF and decomposition; compute both naive baselines.
- **60 days.** Implement rolling-origin evaluation and compare three forecasters.
- **90 days.** Add change-point detection and empirical forecast intervals with measured coverage.

## 8. How To Tell You Are Actually Getting Better

- My evaluation never lets the model see the future.
- I report error by horizon.
- I beat the seasonal naive baseline or explain why not.
- My intervals come from realised errors.

## 9. Principles That Should Not Change

- **Decompose a series into trend, seasonality** Decompose a series into trend, seasonality and residual components
- **Compute moving averages** Compute moving averages and exponential smoothing with a justified parameter
- **Measure autocorrelation** Measure autocorrelation and identify a seasonal period from it

> A time-series forecast without a baseline and a time-aware evaluation is an opinion with decimals.
