# Correlation & Regression - Quiz (15 Questions)

**Track:** statistics  |  **Lab:** lab05  |  **Level:** Intermediate

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

### Q1: What does Pearson correlation measure?

A) Any association
B) Linear association only
C) Causation
D) Agreement

**Answer: B** - It is a cosine between centred vectors, so curvature is invisible to it.

---

### Q2: Why is Pearson near zero for y = x²?

A) The relationship is weak
B) Symmetry makes the covariance zero even though knowing x predicts y
C) The sample is small
D) It is a computational error

**Answer: B** - The linear component cancels; a quadratic term recovers the relationship.

---

### Q3: When should Spearman be preferred?

A) Large samples
B) Monotone but curved relationships, or with influential outliers
C) Categorical data
D) Whenever n is odd

**Answer: B** - Ranks capture any monotone relationship and are robust to outliers.

---

### Q4: Why can adding a predictor increase R² with no real gain?

A) It cannot
B) R² is in-sample and rises whenever a predictor is added
C) Because R² is random
D) Because of rounding

**Answer: B** - Use adjusted R² or, better, validated error.

---

### Q5: What does a residual-versus-fitted parabola indicate?

A) Random noise
B) Wrong functional form: curvature left unmodelled
C) Heteroscedasticity
D) An outlier

**Answer: B** - Symmetry means residual means stay zero, so only the plot reveals it.

---

### Q6: Which diagnostics find influential points?

A) Residual histogram
B) Leverage against squared residual
C) Q-Q plot
D) Scatter of the predictors

**Answer: B** - Both high leverage and large residual together make a point influential.

---

### Q7: What does high VIF indicate?

A) Good fit
B) That the predictor's variance is inflated by correlation with others, so its coefficient is unstable
C) Multicollinearity in the residuals
D) A nonlinear relationship

**Answer: B** - Predictions may be fine while individual coefficients are meaningless.

---

### Q8: Can a regression coefficient be called an effect?

A) Always
B) Only from a designed experiment or a credible causal design
C) If p < 0.05
D) If R² is high

**Answer: B** - Exchangeability cannot be tested from observational data.

---

### Q9: Why does SE of the slope depend on the spread of x?

A) It does not
B) Because the slope is a ratio of covariance to variance in x
C) Because of sample size
D) Because of the units of y

**Answer: B** - Small variation in x makes the slope poorly determined even when the relationship is real.

---

### Q10: What does the intercept mean when x = 0 is out of range?

A) The true y at zero
B) A mathematical artefact with no physical meaning
C) The sample mean of y
D) Nothing at all, and it should be dropped

**Answer: B** - Dropping the intercept changes the slopes, so it is a modelling decision, not a cleanup.

---

### Q11: Heteroscedastic residuals invalidate what?

A) The point estimates
B) The classical standard errors and confidence intervals
C) R²
D) The residual plots

**Answer: B** - Coefficients stay unbiased; the inference needs robust errors or a transform.

---

### Q12: What is the difference between correlation and regression?

A) None
B) Correlation measures association; regression estimates a relationship and quantifies uncertainty
C) Correlation is for categorical data
D) Regression requires normality

**Answer: B** - Regression gives coefficients with standard errors, which correlation does not.

---

### Q13: Why should you plot before fitting?

A) It looks professional
B) Scatter reveals curvature, clusters and outliers that no coefficient exposes
C) Plotting is required by software
D) To compute R²

**Answer: B** - Coefficients are summaries; they hide structure that the scatter shows immediately.

---

### Q14: What does a sign flip after adding a predictor suggest?

A) Randomness
B) Multicollinearity or an omitted variable absorbing the effect
C) A calculation error always
D) Normal residuals

**Answer: A** - Both are plausible, and both need checking rather than dismissal.

---

### Q15: How should you report predictive performance?

A) R²
B) Validated error on data not used for fitting, with the interval
C) The residual standard deviation
D) The correlation

**Answer: B** - R² describes the fit; validated error describes performance.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
