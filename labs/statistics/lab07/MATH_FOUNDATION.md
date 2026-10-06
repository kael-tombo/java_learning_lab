# Time Series Analysis - Mathematical Foundations

**Track:** statistics  |  **Lab:** lab07  |  **Level:** Advanced

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

## Notation

| Symbol | Meaning |
|---|---|
| `y_t = T_t + S_t + e_t` | Additive decomposition - fixed seasonal amplitude |
| `y_t = T_t · S_t · e_t` | Multiplicative decomposition - seasonal amplitude grows with level |
| `SMA_t = (1/k)Σ_{i=0}^{k-1} y_{t-i}` | Simple moving average - equal weight over k |
| `EMA_t = α y_t + (1−γ)EMA_{t−1}` | Exponential smoothing - α is the responsiveness |
| `ACF(k) = corr(y_t, y_{t−k})` | Autocorrelation - structure at lag k |
| `seasonal naive: ŷ_{t+h} = y_{t+h−m}` | Seasonal naive - the baseline to beat |
| `MASE = MAE / MAE_naive` | Scale-free error - comparable across series |
| `forecast error = MAPE on rolling origins` | Rolling-origin evaluation - the honest protocol |

## Why the Math Matters

The formulas below are not decoration: each one is the place where a wrong assumption silently produces a plausible number. Knowing which formula applies, and when it stops applying, is the skill this lab builds.


---

## 1. Decomposition and the choice of additive versus multiplicative

```text
additive: y_t = T_t + S_t + e_t, requires constant seasonal amplitude
multiplicative: y_t = T_t S_t e_t, amplitude proportional to the level
seasonal strength: F_S = max(0, 1 - Var(e)/Var(S + e))
```

The decomposition choice is an assumption about whether seasonal swings grow with the level. Choosing multiplicatively on additive data and vice versa distorts both the trend and the seasonal indices.

**Worked example.** Sales rising from 100 to 400 with seasonal amplitude 10 early and 40 late: multiplicative, since the amplitude tracks the level. The same absolute swings on a flat series would be additive.


---

## 2. Smoothing as a statement about responsiveness

```text
SMA_k: weights 1/k over k lags
EMA: alpha on the newest, (1-alpha) decaying thereafter
effective memory of EMA ~ 1/alpha observations
```

The smoothing window and parameter are statements about how quickly the level changes. Too slow and you lag a turning point; too fast and you chase noise. Both are errors that compound through a forecast horizon.

**Worked example.** Alpha = 0.1 gives effective memory about 10 observations, so a level shift takes roughly 20–30 observations to be absorbed. Alpha = 0.5 halves that, tracking turns faster while amplifying noise by roughly sqrt(2).


---

## 3. Autocorrelation and structure identification

```text
ACF(k) = sum_t (y_t - ybar)(y_{t-k} - ybar) / sum_t (y_t - ybar)^2
spikes at lag k indicate a k-periodic component
decaying ACF indicates an autoregressive process
ACF truncated after a sharp cut-off indicates moving average
```

The ACF is the tool for identifying period and process order, and reading it before fitting prevents choosing a model that cannot represent the structure that is present.

**Worked example.** Retail weekly data with ACF(7) = 0.62 and ACF(14) = 0.55, near zero elsewhere: a 7-periodic seasonal component. ACF(1) = 0.3 decaying smoothly instead indicates momentum, needing an AR term rather than a seasonal index.


---

## 4. Rolling-origin evaluation

```text
for each origin t: train on y[0..t], forecast y[t+1..t+h]
error accumulated across origins
random split is invalid: it trains on future values
```

Rolling origins reproduce the actual forecasting task: everything available at time t, predicting the future. It also reveals how error grows with horizon, which a single split cannot.

**Worked example.** Daily series, 7-day horizon, 30 origins: MAE 12 at h=1 rising to 26 at h=7. A random split reports MAE 9 because the model effectively interpolates between points it has already seen.


---

## 5. Forecast intervals from realised errors

```text
interval width from empirical quantiles of rolling-origin errors
scale by horizon: errors grow with sqrt(h) or h
account for residual autocorrelation when choosing the distribution
```

Empirically derived intervals from rolling-origin errors are honest about how wrong the model actually is. Parametric intervals from residual variance ignore that errors at longer horizons are larger and often correlated.

**Worked example.** Empirical 90% interval at h=7 is [−41, +52] around the point forecast. A residual-standard-deviation interval gives roughly [∑22, +22], which would have covered fewer than half the realised errors.


---

## Cheat Sheet

- `y_t = T_t + S_t + e_t` - Additive decomposition
- `y_t = T_t · S_t · e_t` - Multiplicative decomposition
- `SMA_t = (1/k)Σ_{i=0}^{k-1} y_{t-i}` - Simple moving average
- `EMA_t = α y_t + (1−γ)EMA_{t−1}` - Exponential smoothing
- `ACF(k) = corr(y_t, y_{t−k})` - Autocorrelation
- `seasonal naive: ŷ_{t+h} = y_{t+h−m}` - Seasonal naive
- `MASE = MAE / MAE_naive` - Scale-free error
- `forecast error = MAPE on rolling origins` - Rolling-origin evaluation

## Numerical Traps

- Randomly splitting a time series for train and test.
- Decomposing multiplicatively when the seasonal amplitude is constant.
- Tuning smoothing parameters on the test period.
- Deriving intervals from residual variance while ignoring horizon growth.
- Treating a structural break as exponential growth.

## Self-Check Problems

1. Decompose a series with growing seasonal amplitude and justify additive versus multiplicative.
2. Compute SMA and EMA for a series with a level shift and compare responsiveness.
3. Compute an ACF and identify the seasonal period; distinguish momentum from a cycle.
4. Run rolling-origin evaluation and compare with a random split, quantifying the optimism.
5. Derive empirical forecast intervals and compare coverage against a parametric interval.
