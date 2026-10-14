# Interview Q&A - Time Series

Q: How do you check stationarity in practice?
A: Plot rolling mean/variance, difference if trending, and use the ADF
unit-root test as one piece of evidence - never the only one.

Q: ACF tails off, PACF cuts off at lag 2. What do you try?
A: AR(2) on the (possibly differenced) series; verify residuals are
white noise before accepting it.

Q: Why is shuffling a series for cross-validation wrong?
A: It trains on the future and tests on the past - lookahead leakage
that inflates scores and hides regime changes.

Q: Your model beats the training fit but loses to seasonal-naive. Ship?
A: No. Seasonal-naive is the bar on seasonal data; investigate the
seasonal structure the model is missing.

Q: MAPE is 400%. What do you check first?
A: Actuals near zero - a handful of near-zero denominators dominate
MAPE. Switch to MAE/RMSE or exclude by stated policy.

Q: Residuals still correlate at lag 12 on monthly data. Meaning?
A: Unmodeled annual seasonality - add seasonal terms or dummies rather
than raising non-seasonal orders.

Q: Point forecast for 24 months ahead - concerns?
A: Error variance grows with horizon; present intervals that widen and
warn that far-horizon points are scenarios, not promises.

Q: Random walk - best simple forecast?
A: Naive (last value); its expected squared error equals the shock
variance, which is why it is the baseline to beat.

Q: Train RMSE 0.5, rolling RMSE 2.1, seasonal-naive 1.9. Diagnose?
A: Overfit order that memorized in-sample wiggles; it loses to the
seasonal baseline out of sample. Cut orders until rolling error clears
1.9 with white residuals.

Q: Monthly data, ACF spike at lag 12 only. Model?
A: Pure seasonal structure - seasonal-naive or a seasonal term first.
Non-seasonal ARMA orders address the wrong frequency entirely.
