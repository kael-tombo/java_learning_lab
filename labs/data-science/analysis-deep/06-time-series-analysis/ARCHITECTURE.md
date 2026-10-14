# Architecture - Time Series Mini-Toolkit

JDK-only layout used by this lab's programs (package com.tslab):

```
TsSeries   - wraps double[] + period m; guards ragged/empty input
Differencer- first/second differences; inverse (cumsum) for forecasts
AcfPacf    - sample ACF lags, PACF via Levinson-Durbin recursion
Baselines  - naive, seasonal-naive, mean, drift forecast functions
Metrics    - MAE/RMSE/MAPE with explicit zero-actual policy
Backtest   - rolling-origin loop returning per-origin errors
```

## Data flow

Raw series -> Differencer (d chosen by ADF-style reasoning) ->
AcfPacf (order hints) -> model fit -> Backtest -> Metrics vs Baselines.

## Design choices

- double[] throughout; no boxed collections on hot paths.
- Missing values are a separate boolean mask, never silent NaN fill.
- Metrics take the zero-actual policy as a parameter (SKIP vs FAIL)
  so MAPE's trap is a compile-time-visible decision.
- Backtest owns the temporal split so callers cannot shuffle by mistake.

## Boundaries

Fitting (least squares / MLE) lives behind a `Fitter` interface so the
validation and metric layers stay independent of the optimizer.

## Record sketches

```java
record Split(double[] train, double[] test, int origin) {}
record Score(double mae, double rmse, double mape, int mapeN) {}
record Verdict(String order, Score rolling, Score baseline) {}
```

Score carries mapeN (points actually averaged) so MAPE exclusions stay
visible; Verdict pairs every model with its baseline so no number
travels alone.

## Failure routing

Empty series, single-point input, and constant series (zero variance)
throw IllegalArgumentException naming the violated precondition.
NaN inputs fail at the TsSeries boundary - never inside Metrics.
