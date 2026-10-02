# Time Series Analysis — Quiz (10 Questions)

**Instructions:** Answer each question. Correct answers and explanations follow.

---

### Q1: What is the key difference between time series and cross-sectional data?
A) Time series has more observations
B) Time series observations are temporally ordered and typically dependent
C) Time series only has one variable
D) Time series cannot have missing values

**Answer: B** — Time series data has a natural temporal ordering where observations at nearby times are typically correlated (autocorrelation). This violates the i.i.d. assumption of standard cross-sectional methods.

---

### Q2: What are the three main components of a time series decomposition?
A) Mean, variance, skewness
B) Trend, seasonality, residuals (irregular)
C) AR, MA, ARMA
D) Level, slope, curvature

**Answer: B** — Classical decomposition: Yₜ = Tₜ (trend) + Sₜ (seasonality) + Rₜ (residuals). Can be additive or multiplicative: Yₜ = Tₜ × Sₜ × Rₜ.

---

### Q3: What does it mean for a time series to be (weakly) stationary?
A) Mean and variance are constant over time; autocovariance depends only on lag
B) The series has no trend
C) The series has no seasonality
D) The series follows a normal distribution

**Answer: A** — Weak stationarity: (1) E[Yₜ] = μ (constant), (2) Var(Yₜ) = σ² (constant), (3) Cov(Yₜ, Yₜ₋ₖ) = γₖ (depends only on lag k, not time t). Required for many TS models.

---

### Q4: What is the autocorrelation function (ACF)?
A) Correlation between Yₜ and Yₜ₋ₖ as function of lag k
B) Correlation between Yₜ and Xₜ
C) Partial correlation controlling for intermediate lags
D) Correlation of residuals

**Answer: A** — ACF(k) = Corr(Yₜ, Yₜ₋ₖ) = γₖ/γ₀. Shows linear dependence at different lags. For AR(p), ACF decays exponentially/sinusoidally. For MA(q), ACF cuts off after lag q.

---

### Q5: What is the partial autocorrelation function (PACF)?
A) Same as ACF
B) Correlation between Yₜ and Yₜ₋ₖ controlling for Yₜ₋₁,...,Yₜ₋ₖ₊₁
C) Correlation of residuals from AR model
D) Autocorrelation of differenced series

**Answer: B** — PACF(k) = Corr(Yₜ, Yₜ₋ₖ | Yₜ₋₁,...,Yₜ₋ₖ₊₁). For AR(p), PACF cuts off after lag p. For MA(q), PACF decays exponentially. Used to identify AR order.

---

### Q6: What is the difference between AR(p) and MA(q) models?
A) AR uses past values; MA uses past errors
B) AR uses past errors; MA uses past values
C) AR is for stationary series; MA is for non-stationary
D) AR has infinite memory; MA has finite memory

**Answer: A** — AR(p): Yₜ = c + Σ φᵢYₜ₋ᵢ + εₜ (autoregressive — depends on past values). MA(q): Yₜ = c + εₜ + Σ θⱼεₜ₋ⱼ (moving average — depends on past errors/shocks).

---

### Q7: What is an ARIMA(p,d,q) model?
A) AR(p) + MA(q) on d-th differenced series
B) AR(p) with d exogenous variables
C) MA(q) with d seasonal periods
D) Automatic ARIMA selection

**Answer: A** — ARIMA = AutoRegressive Integrated Moving Average. "Integrated" (I) = differencing d times to achieve stationarity. ARIMA(p,d,q) applies ARMA(p,q) to ∇ᵈYₜ.

---

### Q8: How do you test for a unit root (non-stationarity)?
A) t-test on mean
B) Augmented Dickey-Fuller (ADF) test
C) F-test on variance
D) Chi-squared test on ACF

**Answer: B** — ADF test: H₀: unit root exists (non-stationary). H₁: stationary (or trend-stationary). Regress ΔYₜ on Yₜ₋₁ + lags of ΔY. Test coefficient of Yₜ₋₁ < 0. KPSS test has opposite null (stationarity).

---

### Q9: What is the difference between conditional mean models (ARIMA) and conditional variance models (GARCH)?
A) ARIMA models the mean; GARCH models the volatility/clustering
B) ARIMA is for stationary; GARCH for non-stationary
C) They are the same model
D) GARCH is a special case of ARIMA

**Answer: A** — ARIMA models E[Yₜ|past]. GARCH models Var(Yₜ|past) — captures volatility clustering (large changes followed by large changes). Often combined: ARIMA-GARCH.

---

### Q10: What is the purpose of cross-validation for time series?
A) Standard k-fold CV works fine
B) Use expanding/rolling window to respect temporal order
C) Randomly shuffle time indices
D) Only use the last 20% as test

**Answer: B** — Standard k-fold CV leaks future information into past. Time series CV: expanding window (train on 1:t, test on t+1:h) or rolling window (train on t-w:t, test on t+1:t+h). Respects temporal causality.