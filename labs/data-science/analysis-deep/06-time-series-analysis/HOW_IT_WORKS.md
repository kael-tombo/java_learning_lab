# How Time Series Forecasting Works

## 1. Plot first

Plot y_t against time plus rolling mean and rolling variance. A rising
rolling mean means trend; a widening band means non-constant variance
(consider a log transform for multiplicative growth).

## 2. Test stationarity

Run the ADF concept: null = unit root. Rejection plus a flat rolling
mean suggests stationarity. If trending, difference once (d = 1) and
re-check before fitting ARMA terms.

## 3. Identify structure

Compute ACF/PACF of the (possibly differenced) series. PACF cutoff at
lag p suggests AR(p); ACF cutoff at lag q suggests MA(q). Mixed slow
decay on both suggests ARMA or higher orders - start small.

## 4. Fit and diagnose residuals

Fit candidate ARIMA(p,d,q) orders and inspect residuals: they should
look like white noise (ACF inside the +/-1.96/sqrt(T) band, no trend).
Leftover structure means the order is wrong, not that more data fixes it.

## 5. Validate forward in time

Use rolling-origin backtests: train on [1..t], forecast t+1..t+h, roll
t forward. Average the error across origins. Never shuffle folds.

## 6. Compare to baselines

Report naive, seasonal-naive, mean, and drift errors next to the model.
A model that cannot beat seasonal-naive on seasonal data adds nothing.

## 7. Forecast with intervals

Point forecasts degrade with horizon h (error variance grows). Quote
intervals from residual variance; widen them as h increases rather than
presenting a single confident line far into the future.

## Worked trace on toy data

Series {3, 5, 4, 6, 5, 7, 6, 8}: naive forecasts the last point as 6
(error 2); seasonal-naive with m = 2 predicts 6 as well here (error 2).
TsAcf's lag-2 0.4722 explains why: the even-lag echo dominates, so a
lag-2-based rule beats lag-1 on this shape - structure dictates method.

## When to stop

Stop adding orders when residuals whiten and rolling error flattens.
A third AR term that trims in-sample fit but not rolling error is
complexity without evidence - cut it and say so in the report.
