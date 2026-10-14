# Debugging - Time Series

## 1. ACF values outside [-1, 1]

Cause: dividing by the wrong denominator (e.g. lag-truncated variance)
or integer division. Fix: single full-sample variance as denominator;
verify rho_0 == 1.0 exactly in a unit check.

## 2. Forecast shifted by one period

Cause: off-by-one aligning differenced forecasts back to levels.
Fix: anchor inversion at the last training level and assert the first
forecast sits at T+1 on a toy series by hand.

## 3. MAPE = Infinity or absurd percent

Cause: zero or near-zero actuals in the denominator. Fix: apply the
SKIP-zero policy and report the reduced n (see TsErrors); cross-check
with MAE/RMSE which have no denominator.

## 4. Suspiciously perfect validation scores

Cause: shuffled split or scaling/differencing fitted on the full
series. Fix: re-split strictly temporal, fit every transform inside
the training prefix, re-run.

## 5. Residuals still seasonal

Symptom: ACF spike at lag m (12 for monthly). Cause: non-seasonal
model on seasonal data. Fix: seasonal differencing or seasonal terms;
do not just raise p and q.

## 6. Differenced forecast drifts forever

Cause: forecasting the diff mean far ahead cumulates bias each step.
Fix: damp the trend (drift with shrinkage) and widen intervals with
horizon instead of extending the point line.

## 7. Non-reproducible numbers

Cause: hidden randomness or unordered map iteration in aggregation.
Fix: seed any RNG, use LinkedHashMap/ordered arrays, print inputs with
the outputs in failing cases.

## 8. Constant-series NaN cascade

Symptom: ACF prints NaN and every downstream number follows. Cause: zero
variance (flat sensor, dead feed). Fix: detect constant input at the
boundary, report "no variance - check the sensor," skip structure reads.
