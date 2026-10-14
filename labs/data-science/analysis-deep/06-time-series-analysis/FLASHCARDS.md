# Flashcards - Time Series

Q: What is weak stationarity?
A: Constant mean, constant variance, autocovariance depending only on lag.

Q: What is the ADF null hypothesis?
A: A unit root is present (the series is non-stationary in that sense).

Q: AR(p) signature on ACF/PACF?
A: PACF cuts off after lag p; ACF tails off gradually.

Q: MA(q) signature on ACF/PACF?
A: ACF cuts off after lag q; PACF tails off gradually.

Q: What do p, d, q in ARIMA mean?
A: AR order p, differencing rounds d, MA order q.

Q: Why never shuffle a series for validation?
A: Shuffling leaks future observations into training (lookahead leakage).

Q: What is a rolling-origin backtest?
A: Train on [1..t], forecast ahead, roll t forward, average errors.

Q: Naive vs seasonal-naive forecast?
A: Next = last value vs next = value m periods back.

Q: Write MAE, RMSE, MAPE.
A: mean|y-f|, sqrt(mean((y-f)^2)), 100*mean(|(y-f)/y|).

Q: MAPE trap?
A: Undefined at actual = 0; explodes near zero - exclude such points.

Q: Additive decomposition?
A: y = trend + seasonal + residual.

Q: Stationarity condition for AR(1)?
A: |phi_1| < 1.

Q: First difference of a linear trend gives what?
A: A constant mean plus MA(1)-type noise - stationary.

Q: Why report baselines?
A: A model that cannot beat seasonal-naive adds nothing.

Q: Do forecast intervals widen with horizon?
A: Yes - error variance grows with each step ahead.
