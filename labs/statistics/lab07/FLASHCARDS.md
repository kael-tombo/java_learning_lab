# Time Series Analysis - Flashcards (60 cards)

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

**Format.** Question (front) -> answer (back). Use for spaced repetition: day 0, day 1, day 3, day 7, day 21. Do not read the answer first.

| # | Front | Back |
|---|---|---|
| 1 | Why can't you treat a time series as i.i.d. samples? | Order carries information, so ignoring it inflates apparent significance and misleads the model. |
| 2 | What is seasonal naive? | Forecast equals the value from one full season ago; it is the baseline sophisticated models must beat. |
| 3 | What does a spike in the ACF at lag 7 indicate? | A 7-period seasonal component: a spike at a fixed lag is the signature of a repeating cycle. |
| 4 | When is multiplicative decomposition right? | When the seasonal amplitude grows or shrinks with the level. |
| 5 | What does alpha in exponential smoothing control? | How much weight recent observations get, i.e. how fast you believe the level changes. |
| 6 | Why are random splits invalid for time series? | They let the model train on future values, which inflates the reported accuracy. |
| 7 | What is MASE for? | Scaling forecast error by a naive benchmark so series with different scales can be compared. |
| 8 | How do you tell a structural break from noise? | With a change-point test and a look at whether the level shift persists. |
| 9 | What is A time series is not i.i.d.? | Observations in order carry information from their predecessors. |
| 10 | What is Trend, seasonality, residual? | Classical decomposition splits the series into a slowly moving level, a repeating pattern of fixed period, and everything else. |
| 11 | What is Smoothing choices are assumptions? | A simple moving average of window k assumes k observations are equally relevant. |
| 12 | What is Autocorrelation identifies structure? | The autocorrelation function shows how strongly an observation predicts itself at lag k. |
| 13 | What is Forecast intervals must account for residual behaviour? | An interval from residual standard deviation is too narrow when residuals are autocorrelated, because the effective information in a series is less than its length suggests. |
| 14 | What is Evaluation must respect time? | A random train/test split on a time series lets the model train on the future. |
| 15 | In this lab, what does `y_t = T_t + S_t + e_t` mean? | Additive decomposition: fixed seasonal amplitude |
| 16 | In this lab, what does `y_t = T_t · S_t · e_t` mean? | Multiplicative decomposition: seasonal amplitude grows with level |
| 17 | In this lab, what does `SMA_t = (1/k)Σ_{i=0}^{k-1} y_{t-i}` mean? | Simple moving average: equal weight over k |
| 18 | In this lab, what does `EMA_t = α y_t + (1−γ)EMA_{t−1}` mean? | Exponential smoothing: α is the responsiveness |
| 19 | In this lab, what does `ACF(k) = corr(y_t, y_{t−k})` mean? | Autocorrelation: structure at lag k |
| 20 | In this lab, what does `seasonal naive: ŷ_{t+h} = y_{t+h−m}` mean? | Seasonal naive: the baseline to beat |
| 21 | In this lab, what does `MASE = MAE / MAE_naive` mean? | Scale-free error: comparable across series |
| 22 | In this lab, what does `forecast error = MAPE on rolling origins` mean? | Rolling-origin evaluation: the honest protocol |
| 23 | You see 'Accuracy looks excellent but live forecasts are terrible' in production. What is the cause and the fix? | random train/test split let the model see the future Fix: rolling-origin evaluation only |
| 24 | You see 'A seasonal pattern ignored entirely' in production. What is the cause and the fix? | ACF and period not examined Fix: plot the ACF, identify the lag, use a seasonal naive baseline |
| 25 | You see 'A level shift treated as growth' in production. What is the cause and the fix? | structural break not detected Fix: run a break test and model the change explicitly |
| 26 | You see 'Forecast intervals too narrow' in production. What is the cause and the fix? | residuals are autocorrelated Fix: derive intervals from rolling-origin errors |
| 27 | You see 'Alpha chosen by trying many values on the test set' in production. What is the cause and the fix? | test set used for tuning Fix: tune on rolling validation folds |
| 28 | You see 'Weekly seasonality inferred when it is annual' in production. What is the cause and the fix? | wrong period assumed Fix: identify the period from the ACF and business calendar |
| 29 | Which Java API is the backbone of: moving averages without copying the series | `Deque/ring buffer for sliding windows` |
| 30 | Which Java API is the backbone of: autocorrelation from sorted values rather than raw sums | `Arrays.sort on lagged pairs` |
| 31 | Which Java API is the backbone of: explicit timestamps, because order carries meaning | `record SeriesPoint(Instant t, double y)` |
| 32 | Which Java API is the backbone of: interval attached to every forecast | `record Forecast(double point, double low, double high)` |
| 33 | Which Java API is the backbone of: structural break detection on the level | `Breaks via cumulative sum change points` |
| 34 | Why does A time series is not i.i.d. matter operationally? | Observations in order carry information from their predecessors. |
| 35 | Why does Trend, seasonality, residual matter operationally? | Classical decomposition splits the series into a slowly moving level, a repeating pattern of fixed period, and everything else. |
| 36 | Why does Smoothing choices are assumptions matter operationally? | A simple moving average of window k assumes k observations are equally relevant. |
| 37 | Why does Autocorrelation identifies structure matter operationally? | The autocorrelation function shows how strongly an observation predicts itself at lag k. |
| 38 | Why does Forecast intervals must account for residual behaviour matter operationally? | An interval from residual standard deviation is too narrow when residuals are autocorrelated, because the effective information in a series is less than its length suggests. |
| 39 | Why does Evaluation must respect time matter operationally? | A random train/test split on a time series lets the model train on the future. |
| 40 | In the Time Series Analysis pipeline, what happens next? Plot the series, its ACF and its seasonal decomposition befo... | Plot the series, its ACF and its seasonal decomposition before modelling anything. |
| 41 | In the Time Series Analysis pipeline, what happens next? Establish baselines: naive and seasonal naive, with their er... | Establish baselines: naive and seasonal naive, with their errors computed. |
| 42 | In the Time Series Analysis pipeline, what happens next? Detect and test for structural breaks; a level shift is not ... | Detect and test for structural breaks; a level shift is not noise. |
| 43 | In the Time Series Analysis pipeline, what happens next? Decompose into trend, seasonality and residual; choose addit... | Decompose into trend, seasonality and residual; choose additive or multiplicative. |
| 44 | In the Time Series Analysis pipeline, what happens next? Fit a smoothing or AR model on the training period only.... | Fit a smoothing or AR model on the training period only. |
| 45 | In the Time Series Analysis pipeline, what happens next? Evaluate with rolling-origin cross-validation and report an ... | Evaluate with rolling-origin cross-validation and report an honest interval. |
| 46 | Exercise focus: Decomposition | Trend, seasonality, residual. |
| 47 | Exercise focus: Smoothing and responsiveness | Know what alpha means. |
| 48 | Exercise focus: Autocorrelation analysis | Identify structure before modelling. |
| 49 | Exercise focus: Rolling-origin evaluation | The honest protocol. |
| 50 | Exercise focus: Structural breaks | Separate change from noise. |
| 51 | Exercise focus: Forecast intervals | Be honestly uncertain. |
| 52 | State the Decomposition and the choice of additive versus multiplicative result for Time Series Analysis. | Sales rising from 100 to 400 with seasonal amplitude 10 early and 40 late: multiplicative, since the amplitude tracks the level. The same absolute swings on a flat series would be additive. |
| 53 | State the Smoothing as a statement about responsiveness result for Time Series Analysis. | Alpha = 0.1 gives effective memory about 10 observations, so a level shift takes roughly 20–30 observations to be absorbed. Alpha = 0.5 halves that, tracking turns faster while amplifying noise by roughly sqrt(2). |
| 54 | State the Autocorrelation and structure identification result for Time Series Analysis. | Retail weekly data with ACF(7) = 0.62 and ACF(14) = 0.55, near zero elsewhere: a 7-periodic seasonal component. ACF(1) = 0.3 decaying smoothly instead indicates momentum, needing an AR term rather than a seasonal index. |
| 55 | State the Rolling-origin evaluation result for Time Series Analysis. | Daily series, 7-day horizon, 30 origins: MAE 12 at h=1 rising to 26 at h=7. A random split reports MAE 9 because the model effectively interpolates between points it has already seen. |
| 56 | State the Forecast intervals from realised errors result for Time Series Analysis. | Empirical 90% interval at h=7 is [−41, +52] around the point forecast. A residual-standard-deviation interval gives roughly [∑22, +22], which would have covered fewer than half the realised errors. |
| 57 | What does a slowly decaying ACF indicate? | Momentum or an autoregressive process, rather than a fixed cycle. |
| 58 | Why are forecast intervals often too narrow? | They use residual spread without accounting for residual autocorrelation. |
| 59 | What does a seasonal subseries plot reveal? | Whether the seasonal pattern is stable or drifts across years. |
| 60 | Why tune alpha on validation folds? | Because tuning on the test period converts your reported accuracy into a training number. |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
