# Time Series Analysis — Flashcards

**Format:** Question (front) → Answer (back). Use for spaced repetition.

---

### Card 1
**Q:** What is a time series?
**A:** Sequence of observations indexed by time: {Y₁, Y₂, ..., Yₜ}. Natural temporal ordering.

---

### Card 2
**Q:** What is stationarity?
**A:** Statistical properties (mean, variance, autocovariance) do not change over time. Weak stationarity: constant mean, constant variance, autocovariance depends only on lag.

---

### Card 3
**Q:** What is strict stationarity?
**A:** Joint distribution of (Yₜ₁,...,Yₜₖ) same as (Yₜ₁₊ₕ,...,Yₜₖ₊ₕ) for all h. Implies weak stationarity if moments exist.

---

### Card 4
**Q:** What is a unit root?
**A:** Characteristic root = 1 in AR polynomial. Causes non-stationarity. Random walk: Yₜ = Yₜ₋₁ + εₜ has unit root.

---

### Card 5
**Q:** What is the Augmented Dickey-Fuller (ADF) test?
**A:** Test for unit root. H₀: unit root (non-stationary). H₁: stationary (or trend-stationary). Regress ΔYₜ on Yₜ₋₁ + lags.

---

### Card 6
**Q:** What is the KPSS test?
**A:** H₀: trend-stationary. H₁: unit root. Complementary to ADF. Use both for robust inference.

---

### Card 7
**Q:** What is differencing?
**A:** ∇Yₜ = Yₜ − Yₜ₋₁. Removes trend/unit root. d-th difference: ∇ᵈYₜ. ARIMA "I" = integrated = differenced.

---

### Card 8
**Q:** What is seasonal differencing?
**A:** ∇ₛYₜ = Yₜ − Yₜ₋ₛ (e.g., s=12 for monthly). Removes seasonal unit root.

---

### Card 9
**Q:** What is trend?
**A:** Long-term direction (upward/downward). Deterministic (function of t) or stochastic (random walk with drift).

---

### Card 10
**Q:** What is seasonality?
**A:** Regular repeating pattern at fixed frequency (daily, weekly, monthly, yearly). Period s known.

---

### Card 11
**Q:** What is cyclical component?
**A:** Fluctuations at non-fixed frequency (business cycles). Longer than seasonality, not periodic.

---

### Card 12
**Q:** Additive vs multiplicative decomposition?
**A:** Additive: Yₜ = Tₜ + Sₜ + Rₜ. Multiplicative: Yₜ = Tₜ × Sₜ × Rₜ. Use multiplicative when seasonal amplitude grows with level.

---

### Card 13
**Q:** What is an AR(p) model?
**A:** Autoregressive: Yₜ = c + φ₁Yₜ₋₁ + ... + φₚYₜ₋ₚ + εₜ. Depends on past p values. εₜ ~ WN(0,σ²).

---

### Card 14
**Q:** What is an MA(q) model?
**A:** Moving Average: Yₜ = c + εₜ + θ₁εₜ₋₁ + ... + θₚεₜ₋ₚ. Depends on past q errors. Always stationary.

---

### Card 15
**Q:** What is an ARMA(p,q) model?
**A:** Combined: Yₜ = c + ΣφᵢYₜ₋ᵢ + εₜ + Σθⱼεₜ₋ⱼ. Stationary if AR roots outside unit circle.

---

### Card 16
**Q:** What is an ARIMA(p,d,q) model?
**A:** ARMA(p,q) applied to d-th differenced series: ∇ᵈYₜ ~ ARMA(p,q).

---

### Card 17
**Q:** What is SARIMA?
**A:** Seasonal ARIMA: (p,d,q)×(P,D,Q)ₛ. Non-seasonal × seasonal components. e.g., SARIMA(1,1,1)(1,1,1)₁₂.

---

### Card 18
**Q:** ACF of AR(1): Yₜ = φYₜ₋₁ + εₜ?
**A:** ρₖ = φᵏ. Exponential decay. |φ| < 1 for stationarity.

---

### Card 19
**Q:** PACF of AR(p)?
**A:** Cuts off after lag p. φₖₖ = 0 for k > p. Identifies AR order.

---

### Card 20
**Q:** ACF of MA(q)?
**A:** Cuts off after lag q. ρₖ = 0 for k > q. Identifies MA order.

---

### Card 21
**Q:** PACF of MA(q)?
**A:** Exponential/sinusoidal decay. Does not cut off.

---

### Card 22
**Q:** How to identify ARMA orders from ACF/PACF?
**A:** AR(p): PACF cuts off at p, ACF decays. MA(q): ACF cuts off at q, PACF decays. ARMA: both decay.

---

### Card 23
**Q:** What is AIC/BIC for model selection?
**A:** AIC = −2logL + 2k. BIC = −2logL + k log(n). Lower = better. Penalize complexity.

---

### Card 24
**Q:** What is Ljung-Box test?
**A:** Tests if residuals are white noise. H₀: all autocorrelations up to lag h are zero. Q-statistic ~ χ²ₕ.

---

### Card 25
**Q:** What is forecast horizon?
**A:** Number of steps ahead to predict. h=1 is one-step-ahead; h>1 is multi-step.

---

### Card 26
**Q:** How to compute multi-step forecasts from ARMA?
**A:** Iterative: forecast Ŷₜ₊₁, plug in to forecast Ŷₜ₊₂, etc. Uncertainty grows with horizon.

---

### Card 27
**Q:** What is prediction interval vs confidence interval?
**A:** CI: uncertainty in estimated mean. PI: uncertainty in individual prediction = CI + irreducible error σ².

---

### Card 28
**Q:** What is exponential smoothing (ETS)?
**A:** Weighted average of past obs with exponentially decaying weights. Simple (no trend/seasonal), Holt (trend), Holt-Winters (trend+seasonal).

---

### Card 29
**Q:** ETS state space formulation?
**A:** Allows likelihood-based estimation, prediction intervals, model selection via AIC. Equivalent to ARIMA for many cases.

---

### Card 30
**Q:** What is GARCH(p,q)?
**A:** Generalized ARCH: σ²ₜ = ω + Σαᵢε²ₜ₋ᵢ + Σβⱼσ²ₜ₋ⱼ. Models volatility clustering. εₜ = σₜzₜ, zₜ ~ N(0,1).

---

### Card 31
**Q:** What is volatility clustering?
**A:** Large changes tend to be followed by large changes (high volatility periods). ARCH/GARCH captures this.

---

### Card 32
**Q:** What is VAR (Vector Autoregression)?
**A:** Multivariate TS: Yₜ = c + A₁Yₜ₋₁ + ... + AₚYₜ₋ₚ + εₜ. Models dynamic interactions between multiple series.

---

### Card 33
**Q:** What is Granger causality?
**A:** X Granger-causes Y if past X improves prediction of Y beyond past Y alone. Not true causality — predictive causality.

---

### Card 34
**Q:** What is cointegration?
**A:** Non-stationary series with stationary linear combination. Long-run equilibrium relationship. Engle-Granger / Johansen tests.

---

### Card 35
**Q:** What is VECM?
**A:** Vector Error Correction Model. VAR for cointegrated series: ΔYₜ = αβ'Yₜ₋₁ + ΣΓᵢΔYₜ₋ᵢ + εₜ. β'Y = cointegrating relations.

---

### Card 36
**Q:** What is state space model / Kalman filter?
**A:** Latent state evolves linearly, observed with noise. Recursive filtering/smoothing. Handles missing data, irregular intervals.

---

### Card 37
**Q:** What is Prophet (Facebook)?
**A:** Decomposable additive model: trend + seasonality + holidays. Handles missing data, outliers, changepoints. Good for business TS.

---

### Card 38
**Q:** What is cross-validation for time series?
**A:** Expanding window (train 1:t, validate t+1:t+h) or rolling window (train t−w:t, validate t+1:t+h). No random shuffling!

---

### Card 39
**Q:** What is data leakage in TS CV?
**A:** Using future info to predict past. Random k-fold CV leaks future into training. Always respect temporal order.

---

### Card 40
**Q:** What are common TS forecast evaluation metrics?
**A:** MAE, RMSE, MAPE, sMAPE, MASE. MASE (Mean Absolute Scaled Error) preferred — scale-free, handles zeros.