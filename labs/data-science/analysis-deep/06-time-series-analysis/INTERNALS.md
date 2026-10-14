# Internals - Time Series Computations

## Sample ACF in O(T*K)

For lags 1..K the double loop touches T*K pairs. With T in the hundreds
and K ~ 20 this is trivial; FFT-based autocorrelation only matters for
very long series and is out of scope for this lab.

## PACF via Levinson-Durbin

Partial autocorrelations solve the Yule-Walker equations per order.
Levinson-Durbin recursion reuses order-k work for order k+1, giving
O(K^2) total instead of O(K^4) for naive repeated solves.

## Differencing and inversion

diff() is O(T); inverting a forecast needs the last level value only:
y_{T+h} = y_T + sum of forecast diffs. Keep that anchor or inversion is
impossible - a frequent bug (see DEBUGGING.md).

## Numerics

- Variance via two-pass (mean first, then deviations) avoids
  catastrophic cancellation that single-pass sums suffer.
- MAPE accumulates only over nonzero actuals; the skipped count is
  returned alongside so callers see the reduced denominator.
- RMSE uses Math.sqrt on the mean square; for huge values scale first
  to avoid overflow of the squared sum.

## Memory

All state is O(T): the series, one diff buffer, ACF arrays of size K.
No matrices larger than (p+q)^2 are ever formed here.

## Edge cases

- Constant series: variance 0 makes ACF 0/0 - return NaN with a documented
  reason instead of dividing; baselines still work (naive is exact).
- T <= K: refuse lags beyond T - 1; short series get short ACF tables.
- Single spike: variance explodes, all rho shrink - flag the spike first
  (see lab 09's fences), then re-read structure on cleaned data.

## Why two-pass variance

Single-pass sum(x^2) - T*mean^2 cancels catastrophically when values are
large with small spread (e.g. 1e9 +/- 1). Two-pass costs one extra scan
and keeps full precision - always worth it below 1e8 points.
