# History - Time Series

Only widely documented facts are stated here; uncertain details are
omitted rather than guessed.

## Foundations

- Yule (1927) introduced autoregressive modeling studying sunspot
  numbers; Slutsky (also 1927) showed moving averages of random shocks
  can mimic cycles. Both predate modern computation.
- Wold's decomposition (1938) showed a stationary series splits into a
  deterministic plus a stochastic MA part - the basis for ARMA theory.

## Box and Jenkins

- Box and Jenkins published "Time Series Analysis: Forecasting and
  Control" (first edition 1970), systematizing identification,
  estimation, and checking of ARIMA models. Later editions with Reinsel
  and Ljung extend the same program.
- Their iterative loop (identify, estimate, diagnose) is still the
  recommended workflow in this lab's HOW_IT_WORKS.md.

## Forecasting practice

- Exponential smoothing (Holt, Winters, late 1950s-60s) gave business
  forecasting simple recursive methods for level, trend, and seasonality.
- The M-competitions (starting with Makridakis, early 1980s) compared
  methods empirically and pushed the field toward out-of-sample testing.
- Hyndman and Athanasopoulos's "Forecasting: Principles and Practice"
  continues as a standard freely available textbook (see REFERENCES.md).

## What this lineage teaches

Every generation re-learned the same lesson: difference to stationarity,
check residuals, validate on the future, and keep a naive baseline.

## Reading the lineage

Notice the pattern: Yule/Slutsky (structure from noise), Wold (formal
license), Box-Jenkins (working loop), M-competitions (empirical
scoreboard). Theory, method, then measurement - in that order, and the
order matters: scoreboards without theory overfit to contests.

## State-space epilogue

Kalman filtering (1960s, control engineering) reframed ARIMA in
state-space form, unifying forecasting with signal processing. Modern
tooling descends from both lines; the Box-Jenkins loop still governs
how either is validated.
