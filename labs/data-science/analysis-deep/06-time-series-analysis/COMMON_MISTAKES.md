# Common Mistakes - Time Series

1. Shuffling folds. Temporal order is information; shuffling fabricates
   foresight. Always split past-vs-future.
2. Fitting scalers on the full series. Leakage by another name - fit on
   train prefix, apply to the tail.
3. Skipping baselines. Without naive/seasonal-naive numbers, no error
   value is interpretable.
4. Over-differencing. d = 1 fixes linear trend; differencing again adds
   MA noise and variance. Stop when stable.
5. Reading raw ACF as direct effects. ACF mixes direct and carried-over
   links; confirm order hints with PACF.
6. Trusting MAPE with zeros. One zero actual voids MAPE; set an explicit
   exclusion policy and report n.
7. Judging by in-sample fit. Bigger models always fit better; judge by
   rolling-origin out-of-sample error.
8. Ignoring residual seasonality. A lag-m ACF spike means the seasonal
   structure is unmodeled, not that p must grow.
9. Quoting far-horizon points without intervals. Uncertainty compounds;
   far points without widening bands mislead.
10. Confusing correlation with regime. A strong ACF in a trending level
    usually just re-describes the trend - difference first, then read.

11. Differencing dates, not values. Timestamps order rows; only values
    get differenced - a surprisingly common off-by-confusion in logs.
12. Averaging MAPEs across series. Percentages over different scales do
    not average; aggregate errors in native units or use per-series ranks.

Rule of thumb: if the analysis cannot be drawn as the checkpoint table
in STEP_BY_STEP.md, it was not finished - it was abandoned.

13. Logging levels instead of diffs. Plotting raw trending levels and
    calling the slope "momentum" re-describes the trend as a finding.
14. One backtest origin. A single tail split is one draw - roll several
    origins before claiming generality.
