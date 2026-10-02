# Time Series Analysis — Exercises

**Prerequisites:** Python 3.x with `numpy`, `pandas`, `statsmodels`, `pmdarima`, `prophet` (optional), or Java with Apache Commons Math.

---

## Exercise 1: Generate and Analyze Synthetic Time Series

**Objective:** Create and decompose time series with known components.

**Tasks:**
1. Generate 5 years of monthly data (n=60):
   - Trend: Tₜ = 100 + 0.5×t
   - Seasonality: Sₜ = 10×sin(2πt/12) + 5×cos(2πt/12)
   - Noise: εₜ ~ N(0, 2)
   - Yₜ = Tₜ + Sₜ + εₜ
2. Plot the series, trend, seasonality, and residuals.
3. Apply classical additive decomposition (statsmodels `seasonal_decompose`).
4. Compare extracted components to true components.
5. **Challenge:** Repeat with multiplicative seasonality: Yₜ = Tₜ × (1 + Sₜ/100) × exp(εₜ). Use multiplicative decomposition.

**Expected Answer:** Decomposition should recover trend ≈ 0.5/month, seasonal amplitude ≈ 11-12, residuals ~ N(0,2).

---

## Exercise 2: Stationarity Testing and Differencing

**Objective:** Test for unit roots and apply appropriate differencing.

**Tasks:**
1. Generate three series (n=200):
   - Random walk: Yₜ = Yₜ₋₁ + εₜ
   - Random walk with drift: Yₜ = 0.1 + Yₜ₋₁ + εₜ
   - Trend-stationary: Yₜ = 0.1×t + εₜ
2. Plot each series and its ACF/PACF.
3. Run ADF test on each (statsmodels `adfuller`). Interpret p-values.
4. Run KPSS test on each (statsmodels `kpss`). Compare conclusions.
5. Apply first difference to random walk series. Re-test.
6. **Challenge:** Generate seasonal random walk (SARIMA with seasonal unit root). Test with HEGY seasonal unit root test.

**Expected Answer:** 
- Random walk: ADF fails to reject (p>0.05), KPSS rejects (p<0.05) → unit root
- With drift: similar, may need trend in ADF regression
- Trend-stationary: ADF rejects, KPSS fails to reject → trend-stationary
- First difference of RW → stationary (ADF rejects, KPSS fails to reject)

---

## Exercise 3: ARMA/ARIMA Model Identification and Estimation

**Objective:** Identify and estimate ARIMA models using ACF/PACF and information criteria.

**Tasks:**
1. Generate AR(2): Yₜ = 0.6Yₜ₋₁ − 0.3Yₜ₋₂ + εₜ
2. Generate MA(2): Yₜ = εₜ + 0.5εₜ₋₁ − 0.2εₜ₋₂
3. Generate ARMA(2,1): Yₜ = 0.5Yₜ₋₁ − 0.2Yₜ₋₂ + εₜ + 0.4εₜ₋₁
4. For each, plot theoretical and sample ACF/PACF (up to lag 20).
5. Fit ARIMA models using `auto_arima` (pmdarima) and manual specification.
6. Compare AIC/BIC across candidate models.
7. Check residuals with Ljung-Box test.
8. **Challenge:** Estimate parameters via maximum likelihood manually (Kalman filter) and compare to statsmodels.

**Expected Answer:** 
- AR(2): PACF cuts off at lag 2, ACF decays
- MA(2): ACF cuts off at lag 2, PACF decays
- ARMA: both decay
- `auto_arima` should select correct orders (may differ slightly due to sampling variability)

---

## Exercise 4: Seasonal ARIMA (SARIMA) Modeling

**Objective:** Model and forecast seasonal time series.

**Tasks:**
1. Generate monthly data with:
   - Trend: 0.2×t
   - Seasonal AR(1) at lag 12: Φ=0.7
   - Non-seasonal MA(1): θ=0.3
   - Yₜ follows SARIMA(0,1,1)×(1,0,0)₁₂
2. Plot series, ACF/PACF (note spikes at lags 12, 24...).
3. Fit SARIMA models with different (P,D,Q) combinations.
4. Use `auto_arima` with `seasonal=True, m=12`.
5. Compare in-sample fit and out-of-sample forecast (last 12 months).
6. **Challenge:** Implement grid search over (p,d,q)×(P,D,Q) with AIC. Plot AIC heatmap.

**Expected Answer:** Best model should be close to (0,1,1)×(1,0,0)₁₂. Forecast should capture seasonal pattern.

---

## Exercise 5: Exponential Smoothing (ETS) Models

**Objective:** Fit and compare ETS models.

**Tasks:**
1. Use the same data from Exercise 1 (trend + seasonality + noise).
2. Fit:
   - Simple Exponential Smoothing (SES)
   - Holt's Linear Trend
   - Holt-Winters Additive
   - Holt-Winters Multiplicative
   - Damped trend variants
3. Compare AIC, RMSE on holdout set (last 12 months).
4. Plot forecasts with prediction intervals.
5. **Challenge:** Use `ets` from `statsmodels` or `forecast` package (R) for automatic model selection.

**Expected Answer:** Holt-Winters Additive should perform best (matches data-generating process). Damped trend may improve long-horizon forecasts.

---

## Exercise 6: Forecast Evaluation and Cross-Validation

**Objective:** Properly evaluate forecast accuracy using time series CV.

**Tasks:**
1. Load a real dataset (e.g., `statsmodels` `co2`, `airpassengers`, or M4 competition data).
2. Implement expanding window CV:
   - Initial train: first 60% of data
   - Step: expand by 12 months, forecast next 12 months
   - Compute MAE, RMSE, MAPE, MASE for each fold
3. Implement rolling window CV (fixed window size = 60 months).
4. Compare SARIMA, ETS, and Prophet (if available) across folds.
5. Plot forecast errors over time.
6. **Challenge:** Implement MASE (Mean Absolute Scaled Error) using naive seasonal forecast as benchmark.

**Expected Answer:** Expanding window uses more data over time; rolling window adapts to recent patterns. MASE < 1 means better than naive seasonal forecast.

---

## Exercise 7: Multivariate Time Series — VAR and Granger Causality

**Objective:** Model multiple interacting time series.

**Tasks:**
1. Generate bivariate VAR(1):
   ```
   Y₁ₜ = 0.5Y₁ₜ₋₁ + 0.2Y₂ₜ₋₁ + ε₁ₜ
   Y₂ₜ = 0.3Y₁ₜ₋₁ + 0.4Y₂ₜ₋₁ + ε₂ₜ
   ```
2. Plot both series and cross-correlation function (CCF).
3. Fit VAR model using `statsmodels.tsa.api.VAR`.
4. Select lag order using AIC/BIC.
5. Test Granger causality: Does Y₂ Granger-cause Y₁? (Wald test on coefficients)
6. Compute impulse response functions (IRF) — effect of shock to Y₂ on Y₁ over time.
7. **Challenge:** Forecast both series jointly. Compare to univariate forecasts.

**Expected Answer:** VAR should recover coefficient matrix. Granger test: Y₂ → Y₁ significant (0.2), Y₁ → Y₂ significant (0.3). IRF shows dynamic effects decay over time.

---

## Exercise 8: Cointegration and VECM

**Objective:** Model long-run equilibrium relationships.

**Tasks:**
1. Generate two cointegrated series:
   - Y₁ₜ = Y₁ₜ₋₁ + ε₁ₜ (random walk)
   - Y₂ₜ = 0.8×Y₁ₜ + ε₂ₜ (cointegrated with Y₁, cointegrating vector β = [1, -0.8])
2. Confirm both are I(1) (ADF fails to reject unit root).
3. Test cointegration: Engle-Granger (OLS + ADF on residuals) and Johansen test.
4. Fit VECM (Vector Error Correction Model).
5. Interpret adjustment coefficients (α) — speed of return to equilibrium.
6. **Challenge:** Forecast with VECM vs differenced VAR. Compare long-horizon accuracy.

**Expected Answer:** Engle-Granger: regress Y₂ on Y₁, test residuals for stationarity. Johansen: trace/max-eigen statistics. VECM captures both short-run dynamics and long-run equilibrium.

---

## Exercise 9: State Space Models and Kalman Filter

**Objective:** Implement local level model with Kalman filter.

**Tasks:**
1. Local level model:
   - State: αₜ₊₁ = αₜ + ηₜ, ηₜ ~ N(0, σ²_η)
   - Observation: Yₜ = αₜ + εₜ, εₜ ~ N(0, σ²_ε)
2. Generate data with known σ²_η, σ²_ε.
3. Implement Kalman filter (forward pass):
   - Predict: aₜ|ₜ₋₁, Pₜ|ₜ₋₁
   - Update: aₜ|ₜ, Pₜ|ₜ
4. Implement Kalman smoother (backward pass).
5. Estimate σ²_η, σ²_ε via maximum likelihood (optimize log-likelihood from filter).
6. **Challenge:** Add seasonal component (trigonometric or dummy). Compare to ETS/Holt-Winters.

**Expected Answer:** Filter gives one-step-ahead predictions; smoother gives full-sample estimates. MLE recovers true variance parameters (with sampling error).

---

## Exercise 10: Real-World Forecasting Project

**Dataset:** Choose one: [M4 Hourly](https://github.com/Mcompetitions/M4-methods), [Electricity Load](https://archive.ics.uci.edu/ml/datasets/ElectricityLoadDiagrams20112014), [Traffic](https://archive.ics.uci.edu/ml/datasets/PEMS-SF), or [Walmart Sales](https://www.kaggle.com/c/walmart-recruiting-store-sales-forecasting).

**Tasks:**
1. Exploratory analysis: plot, decomposition, stationarity tests, ACF/PACF.
2. Split: train (all but last 20%), test (last 20%).
3. Build baseline models: Naive, Seasonal Naive, ARIMA, ETS, Prophet.
4. Hyperparameter tuning for each (cross-validation on train).
5. Evaluate on test: MAE, RMSE, MAPE, MASE, RMSSE.
6. Ensemble: simple average or weighted by CV performance.
7. Produce forecast for next 30 days with prediction intervals.
8. **Deliverable:** 3-page report: data description, methods, results table, best model, forecast plot, limitations.

**Reflection Questions:**
- How did you handle missing values/outliers?
- Did you transform the data (log, Box-Cox)?
- How sensitive are results to CV strategy?
- What would you do with more time/data?