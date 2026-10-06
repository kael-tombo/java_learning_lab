# Time Series Analysis

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

## 1. The Problem This Solves

Observations arrive in order, the level drifts, and the same weekday keeps repeating. Treating that sequence as independent samples produces forecasts that are confidently wrong.

Almost every operational metric is a time series, and the difference between a forecast that works and one that fails is usually whether seasonality and autocorrelation were respected.

## 2. Learning Objectives

- Decompose a series into trend, seasonality and residual components
- Compute moving averages and exponential smoothing with a justified parameter
- Measure autocorrelation and identify a seasonal period from it
- Forecast with an interval and evaluate with a time-aware protocol
- Detect structural breaks rather than explaining them as noise
- Choose between naive, seasonal naive and smoothed forecasts honestly

## 3. Core Concepts

### 3.1 A time series is not i.i.d.

Observations in order carry information from their predecessors. Any test assuming independence on a trending series will produce spuriously small p-values, and any forecast model ignoring autocorrelation will learn the wrong relationships.

### 3.2 Trend, seasonality, residual

Classical decomposition splits the series into a slowly moving level, a repeating pattern of fixed period, and everything else. The split is a choice: additive decomposition suits stable amplitudes, multiplicative suits seasonal ones that grow with the level.

### 3.3 Smoothing choices are assumptions

A simple moving average of window k assumes k observations are equally relevant. Exponential smoothing discounts older observations geometrically, and alpha is a statement about how fast you believe the world changes.

### 3.4 Autocorrelation identifies structure

The autocorrelation function shows how strongly an observation predicts itself at lag k. A spike at the seasonal lag is the signature of a cycle; a slowly decaying function indicates momentum; a sharp cut-off indicates a moving-average process.

### 3.5 Forecast intervals must account for residual behaviour

An interval from residual standard deviation is too narrow when residuals are autocorrelated, because the effective information in a series is less than its length suggests. Wider, empirically derived intervals are more honest.

### 3.6 Evaluation must respect time

A random train/test split on a time series lets the model train on the future. Rolling-origin evaluation, with each fold training only on the past, is the only honest protocol, and the naive baseline is the one every sophisticated model must beat.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `y_t = T_t + S_t + e_t` | Additive decomposition | fixed seasonal amplitude |
| `y_t = T_t · S_t · e_t` | Multiplicative decomposition | seasonal amplitude grows with level |
| `SMA_t = (1/k)Σ_{i=0}^{k-1} y_{t-i}` | Simple moving average | equal weight over k |
| `EMA_t = α y_t + (1−γ)EMA_{t−1}` | Exponential smoothing | α is the responsiveness |
| `ACF(k) = corr(y_t, y_{t−k})` | Autocorrelation | structure at lag k |
| `seasonal naive: ŷ_{t+h} = y_{t+h−m}` | Seasonal naive | the baseline to beat |
| `MASE = MAE / MAE_naive` | Scale-free error | comparable across series |
| `forecast error = MAPE on rolling origins` | Rolling-origin evaluation | the honest protocol |

## 5. How the Pieces Fit Together

1. Plot the series, its ACF and its seasonal decomposition before modelling anything.

2. Establish baselines: naive and seasonal naive, with their errors computed.

3. Detect and test for structural breaks; a level shift is not noise.

4. Decompose into trend, seasonality and residual; choose additive or multiplicative.

5. Fit a smoothing or AR model on the training period only.

6. Evaluate with rolling-origin cross-validation and report an honest interval.

## 6. Assumptions and Invariants

- The seasonal period is known or identified from the ACF
- Decomposition is stable over the horizon being forecast
- Residuals are approximately stationary for the chosen model class
- Structural breaks are detected rather than absorbed into noise
- Evaluation uses rolling origins, never a random split
- Forecast intervals reflect residual autocorrelation, not just its spread

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| Accuracy looks excellent but live forecasts are terrible | random train/test split let the model see the future | rolling-origin evaluation only |
| A seasonal pattern ignored entirely | ACF and period not examined | plot the ACF, identify the lag, use a seasonal naive baseline |
| A level shift treated as growth | structural break not detected | run a break test and model the change explicitly |
| Forecast intervals too narrow | residuals are autocorrelated | derive intervals from rolling-origin errors |
| Alpha chosen by trying many values on the test set | test set used for tuning | tune on rolling validation folds |
| Weekly seasonality inferred when it is annual | wrong period assumed | identify the period from the ACF and business calendar |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `Deque/ring buffer for sliding windows` | moving averages without copying the series |
| `Arrays.sort on lagged pairs` | autocorrelation from sorted values rather than raw sums |
| `record SeriesPoint(Instant t, double y)` | explicit timestamps, because order carries meaning |
| `record Forecast(double point, double low, double high)` | interval attached to every forecast |
| `Breaks via cumulative sum change points` | structural break detection on the level |

## 9. Where This Sits in the Larger System

- **lab03** provides the tests, but the independence assumption must be checked first.
- **lab01** provides the summaries used for level and spread reporting.
- **lab02** provides the noise models that justify residual assumptions.
- **lab08** provides randomisation and blocking, which time series designs approximate with calendar structure.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Decompose a series into trend, seasonality and residual components
- [ ] 0 — cannot yet — Compute moving averages and exponential smoothing with a justified parameter
- [ ] 0 — cannot yet — Measure autocorrelation and identify a seasonal period from it
- [ ] 0 — cannot yet — Forecast with an interval and evaluate with a time-aware protocol
- [ ] 0 — cannot yet — Detect structural breaks rather than explaining them as noise
- [ ] 0 — cannot yet — Choose between naive, seasonal naive and smoothed forecasts honestly

## 11. Summary Checklist

- [ ] I plot the series, ACF and decomposition before modelling.
- [ ] Naive and seasonal naive baselines are computed and reported.
- [ ] Evaluation uses rolling origins, never a random split.
- [ ] Structural breaks are tested for.
- [ ] Forecast intervals come from rolling-origin errors.
- [ ] Tuning happens on validation folds, not the test period.
