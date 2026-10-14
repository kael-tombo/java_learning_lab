# Step by Step - First Forecast

## Step 1. Assemble the series

Collect evenly spaced observations (daily sales, monthly demand).
Fill or flag gaps explicitly; hidden interpolation invents history.

## Step 2. Hold out the tail

Reserve the last H points (e.g. last 12 of monthly data) as the test
set. Everything - including scaling and differencing choices - is
decided on the training prefix only.

## Step 3. Difference if trending

Compute w_t = y_t - y_{t-1}. Check the diffed mean/variance across
halves of the training data; stability here is the practical face of
stationarity (see TsDiff output in CODE_DEEP_DIVE.md).

## Step 4. Read ACF/PACF

Compute sample ACF lags 1..12 on the training data. A sharp cutoff
suggests MA order; a PACF cutoff suggests AR order. Write down two or
three candidate (p,d,q) triples, smallest first.

## Step 5. Score baselines

Forecast the test tail with naive and seasonal-naive rules and record
MAE/RMSE/MAPE. These numbers are the bar every model must clear.

## Step 6. Fit, roll forward, compare

Fit each candidate, run rolling-origin forecasts over the test tail,
and keep the order with the lowest mean rolling error - not the lowest
in-sample fit (in-sample fit always favors bigger models).

## Step 7. Report

Report the winning model's test-tail errors next to the baselines,
state the horizon H, and note MAPE exclusions if any actual was zero.

## Checkpoint table

| Step | Artifact | Check |
|---|---|---|
| 1 assemble | dated series, gaps flagged | no hidden interpolation |
| 2 hold out | tail of length H | transforms fitted on prefix only |
| 3 difference | diffed training series | rolling mean flat |
| 4 ACF/PACF | lags 1..12 table | rho_0 == 1.0 sanity |
| 5 baselines | naive/seasonal errors | bar every model must clear |
| 6 roll forward | per-origin errors | average, not best origin |
| 7 report | errors + horizon + MAPE n | exclusions stated |

Fill one row per analysis; an empty cell means the step was skipped.
