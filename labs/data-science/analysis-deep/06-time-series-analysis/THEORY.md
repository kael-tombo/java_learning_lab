# Time Series Theory

## 1. What makes a series special

A time series keeps its order. y_t may depend on y_{t-1}, y_{t-2},
and on a seasonal lag y_{t-m}. Methods that assume independent rows
(such as plain cross-validation with shuffling) are invalid here.

## 2. Stationarity

A (weakly) stationary series has constant mean, constant variance,
and autocovariance Cov(y_t, y_{t-k}) that depends only on the lag k,
never on t. Trends and growing variance violate stationarity.

The Augmented Dickey-Fuller (ADF) test formalizes one check: its null
hypothesis is a unit root (non-stationary); rejecting it is evidence
the series may be stationary. A test never proves stationarity alone,
so plots of rolling mean/variance accompany it.

## 3. Autocorrelation: ACF and PACF

- ACF(k) = Corr(y_t, y_{t-k}). Shows direct plus carried-over dependence.
- PACF(k) = correlation of y_t and y_{t-k} after removing the linear
  effect of the lags between them. Isolates the direct link at lag k.

Reading rules used in Box-Jenkins identification:

- AR(p): PACF cuts off after lag p; ACF tails off gradually.
- MA(q): ACF cuts off after lag q; PACF tails off gradually.

## 4. AR, MA, ARIMA

AR(1): y_t = c + phi_1 * y_{t-1} + e_t, with |phi_1| < 1 for stationarity.
MA(1): y_t = mu + e_t + theta_1 * e_{t-1}; finite MA orders are always
stationary but need invertibility (|theta_1| < 1) for unique estimation.
ARIMA(p,d,q): apply d rounds of differencing (d=1: w_t = y_t - y_{t-1})
until the series looks stationary, then fit ARMA(p,q) to w_t.

## 5. Temporal validation

Train on the past, test on the future. Rolling (walk-forward) and
expanding windows are standard. Shuffling leaks future into training
(lookahead leakage) and overstates accuracy.

## 6. Decomposition and baselines

Additive: y_t = Trend_t + Seasonal_t + Residual_t (multiplicative form
exists for growing seasonal swings). Always compare against naive
(next = last value) and seasonal-naive (next = value m steps back),
plus mean and drift baselines, before trusting a fitted model.

## 7. Error metrics

MAE = mean|y - f|, RMSE = sqrt(mean((y - f)^2)) which punishes large
misses, MAPE = 100 * mean(|(y - f)/y|). MAPE is undefined at y = 0 and
explodes near zero, so skip or replace zero-actual points explicitly.
