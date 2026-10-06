# Time Series Analysis - Quiz (15 Questions)

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

**Instructions.** Answer all 15 questions before reading the bold answer lines. Multiple choice, one best answer. Target: 12/15 before you move on to the mini project.

### Q1: Why is a random train/test split invalid for time series?

A) It is slower
B) It lets the model train on future values
C) It changes the metric
D) It requires more data

**Answer: B** - Rolling-origin folds are the only protocol matching deployment.

---

### Q2: What does an ACF spike at lag 7 indicate?

A) A trend
B) A 7-period seasonal component
C) Noise
D) A structural break

**Answer: B** - A spike at a fixed lag is the signature of a cycle.

---

### Q3: When is multiplicative decomposition appropriate?

A) Always
B) When the seasonal amplitude scales with the level
C) For short series
D) When there are no trends

**Answer: B** - Constant amplitude calls for additive decomposition.

---

### Q4: What does alpha control in exponential smoothing?

A) The window length
B) The weight on recent observations, i.e. responsiveness
C) The seasonal period
D) The forecast horizon

**Answer: B** - Effective memory is roughly 1/alpha observations.

---

### Q5: What is seasonal naive forecasting?

A) Averaging the last k values
B) Using the value from one season ago
C) Fitting a linear trend
D) Using the mean

**Answer: B** - It is the baseline every sophisticated forecast must beat.

---

### Q6: Why are forecast intervals often too narrow?

A) The model is wrong
B) They use residual spread without accounting for autocorrelation or horizon
C) There is too little data
D) The intervals are symmetric

**Answer: B** - Empirical rolling-origin errors are more honest.

---

### Q7: What is MASE?

A) Mean absolute signed error
B) Error scaled by a naive benchmark, allowing comparison across series
C) A test statistic
D) A smoothing parameter

**Answer: B** - Scaling by the naive error makes series comparable.

---

### Q8: How do you detect a structural break?

A) A moving average
B) A change-point test on the level, confirmed by persistence
C) Plotting the ACF
D) Comparing means

**Answer: B** - A real level shift persists; noise reverts.

---

### Q9: Why tune smoothing parameters on validation folds?

A) Speed
B) Because tuning on the test period makes the reported error a training number
C) To reduce memory
D) It is required

**Answer: B** - Parameter selection is a fit, so it belongs inside the training process.

---

### Q10: What does a slowly decaying ACF suggest?

A) Seasonality
B) Momentum or an autoregressive process
C) White noise
D) A break

**Answer: B** - A sharp cut-off after lag k instead suggests a moving-average process.

---

### Q11: Why does error grow with forecast horizon?

A) The model degrades
B) Uncertainty compounds and structure becomes less predictable further out
C) The data is noisier
D) The metric changes

**Answer: B** - Reporting error by horizon shows where the forecast stops being useful.

---

### Q12: What is differencing for?

A) Removing a constant offset
B) Making a trending series stationary for AR modelling
C) Smoothing noise
D) Detecting breaks

**Answer: B** - Differencing removes a stochastic trend so AR assumptions can hold.

---

### Q13: How do you know your model beats the baseline?

A) By looking good
B) By comparing rolling-origin errors against the naive baseline on the same folds
C) By having more parameters
D) By using a longer history

**Answer: B** - Baselines must be evaluated on identical folds.

---

### Q14: What makes a seasonal forecast business-usable?

A) Raw point forecasts
B) A forecast with an interval, a horizon and a stated failure mode
C) High R²
D) A short training window

**Answer: B** - A point forecast without uncertainty is not actionable.

---

### Q15: What does a seasonal subseries plot show?

A) The ACF
B) The seasonal pattern per period, revealing whether it drifts
C) Residual variance
D) Trend direction

**Answer: B** - Drift across periods argues against a fixed seasonal index.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
