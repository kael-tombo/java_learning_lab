# Security Notes - Time Series

## Lookahead as integrity risk

Future data in training is not just a stats error - in regulated demand
or trading contexts it is a misrepresentation of model skill. Temporal
splits with a documented cutoff date are the audit trail.

## Data provenance

Series get revised (sales restated, sensors recalibrated). Pin the
vintage used for each backtest; silently updating history rewrites both
training and test and voids comparability.

## Forecast-driven abuse

Published forecasts move behavior (orders, prices). If forecasts are
public, separate the research series from the released numbers and log
who changed what before release.

## Privacy in granular series

Household energy or individual mobility series can re-identify people
even aggregated. Aggregate to safe grains and avoid publishing residual
series that isolate single-source patterns.

## Code-level hygiene (JDK)

No network or file I/O appears in this lab's snippets; keep it that
way in exercises. Validate array lengths before loops and reject NaN
inputs so corrupt feeds fail loudly instead of forecasting garbage.

## Model-theft via forecast API

A public forecast endpoint leaks the model: queried densely, it reveals
seasonality and trend parameters to competitors. Rate-limit, round
outputs, and log query patterns - forecasts are intellectual property.

## Backtest tampering

Re-choosing the holdout window until results shine is leakage with
intent. Freeze cutoff dates in version control before fitting; review
any commit that moves a cutoff after results exist.

## Shared-notebook leakage

Forecast notebooks shared across clients can leak one client's seasonality
through cached outputs and fitted parameters. Isolate runs per client,
clear state between them, and treat fitted coefficients as confidential.
