# Performance - Time Series

## Complexities (this lab's scope)

- Differencing, MAE/RMSE/MAPE, naive forecasts: O(T) time, O(1) extra.
- Sample ACF to lag K: O(T*K) time, O(K) extra.
- Rolling backtest with R origins and horizon H: O(R*H) forecasts plus
  refit cost per origin for fitted models (baselines refit for free).

## Scaling guidance

- Small data (T < 10^4): everything here runs in milliseconds; clarity
  beats optimization. Prefer the two-pass variance.
- Long series (T > 10^5): compute ACF with stride sampling for
  exploration, full pass only for final numbers.
- Many series (retail catalogs): fit per-series baselines first and
  spend fitting budget only where baselines fail - most series never
  need more.

## No invented benchmarks

This lab states no timings or speedups: wall-clock numbers depend on
hardware and JVM and would mislead. Measure your own with JMH if you
need them.

## Honest cost driver

Refitting per rolling origin dominates cost for estimated models. If
that is too slow, refit every k-th origin and say so in the report.

## Cost table (this lab's programs)

| Operation | Time | Extra memory |
|---|---|---|
| diff / naive / metrics | O(T) | O(1) |
| ACF to lag K | O(T*K) | O(K) |
| PACF Levinson-Durbin | O(K^2) | O(K) |
| rolling backtest, R origins | O(R * refit) | O(H) |

## Measurement note

If you time anything, report JVM version, warmup, T, K, and R alongside
- a naked millisecond number reproduces nothing. Median of 5 timed runs
after 3 warmup runs is the minimum honest protocol.
