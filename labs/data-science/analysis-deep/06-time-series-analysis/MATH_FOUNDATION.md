# Math Foundation - Time Series

## 1. Autocovariance and autocorrelation

Let mu = E[y_t]. Lag-k autocovariance:

  gamma_k = E[(y_t - mu)(y_{t-k} - mu)]

Autocorrelation rho_k = gamma_k / gamma_0, so rho_0 = 1 always.
Sample estimate on T points with sample mean m:

  rho_k = sum_{t=k+1..T} (y_t - m)(y_{t-k} - m) / sum_t (y_t - m)^2

For a white-noise series, sample ACF values beyond lag 0 scatter
inside roughly +/- 1.96/sqrt(T) (an approximate 95% band).

## 2. AR(1) stationarity derivation

y_t = c + phi * y_{t-1} + e_t, e_t white noise with variance s^2.
Repeated substitution gives y_t as a weighted sum of past shocks with
weights 1, phi, phi^2, ... This sum has finite variance only when the
geometric weights decay, i.e. |phi| < 1. Then E[y_t] = c / (1 - phi)
and Var(y_t) = s^2 / (1 - phi^2).

## 3. Why differencing removes a linear trend

If y_t = a + b*t + stationary noise, first differences give
w_t = y_t - y_{t-1} = b + (noise_t - noise_{t-1}), whose mean b is
constant and whose noise part is stationary (an MA(1) structure).
Hence ARIMA sets d = 1 for a linear trend, d = 2 for quadratic.

## 4. MA(1) autocorrelation

y_t = mu + e_t + theta * e_{t-1}. Then gamma_0 = s^2(1 + theta^2),
gamma_1 = s^2 * theta, gamma_k = 0 for k >= 2. So the ACF cuts off
after lag 1: the signature of an MA(1) process.

## 5. Error metric relationships

RMSE >= MAE always (square-then-root penalizes spread; equality only
when all absolute errors are identical). MAPE is scale-free (percent)
but asymmetric: it punishes positive errors more than negative ones
and is undefined at actual = 0.

## 6. Naive forecast error identity

For a random walk y_t = y_{t-1} + e_t, the naive forecast (predict the
last value) has expected squared error exactly s^2 per step, which is
why naive is the baseline to beat rather than a straw man.
