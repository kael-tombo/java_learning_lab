# Correlation & Regression - Mathematical Foundations

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

## Notation

| Symbol | Meaning |
|---|---|
| `r = Σ(x−x̄)(y−ϼ) / (s_x s_y)` | Pearson correlation - −1 to 1, linear only |
| `ρ = Pearson on ranks` | Spearman correlation - monotone association, robust |
| `β́ = cov(x,y)/var(x)` | Slope - change in y per unit x |
| `α̂ = ϼ − β́ x̄` | Intercept - y at x = 0, often meaningless |
| `R² = 1 − SS_res/SS_tot` | Coefficient of determination - in-sample variance explained |
| `SE(β́) = s / sqrt(SS_x)` | Slope standard error - uncertainty in the slope |
| `t = β́ / SE(β́)` | Coefficient test - tests H₀: slope = 0 |
| `β̂ = (XᵀX)⁻¹Xᵀy` | Least squares - the normal equation |

## Why the Math Matters

The formulas below are not decoration: each one is the place where a wrong assumption silently produces a plausible number. Knowing which formula applies, and when it stops applying, is the skill this lab builds.


---

## 1. Correlation as cosine and what it misses

```text
r = sum((x-xbar)(y-ybar)) / (n sx sy)
since z-scored vectors have unit length, r = cos(theta)
so r is maximal for a linear relationship and blind to curvature
```

Because r is a cosine between centred vectors, only the component of y aligned with x is measured. A symmetric parabola has near-zero correlation with x even though knowing x tells you a great deal about y.

**Worked example.** y = x² for x uniform on [-1, 1]: r = 0 because the covariance is zero by symmetry. Adding a quadratic term raises R² from 0 to about 1, which shows the information was always there and the model form was wrong.


---

## 2. Regression coefficients and their uncertainty

```text
slope b = Sxy/Sxx, intercept a = ybar - b xbar
SE(b) = s / sqrt(Sxx)
R² = Sxy²/(Sxx Syy), t = b/SE(b) with df = n - 2
```

The slope is a ratio of covariance to variance, so its uncertainty depends on the spread of x: with little variation in x, the slope is poorly determined even when the relationship is real.

**Worked example.** x with sd 0.1 instead of 1.0, same true relationship: SE(b) grows by 10x, so the t-statistic falls by 10x. The same data with x spread across its range is far more informative, which is why design beats analysis here.


---

## 3. Residual diagnostics

```text
e_i = y_i - yhat_i
e vs fitted: curvature => wrong functional form
e vs predictor: structure left unmodelled
leverage vs e²: points with both high leverage and large residual are influential
```

Residuals are the only direct evidence about model adequacy, and the three standard plots test different failures. Looking at a single residual histogram tests only normality.

**Worked example.** Fitting a straight line to y = 2x + 0.5x² leaves a symmetric parabola of residuals against fitted: average residual is zero, so a residual mean check passes while the model is wrong. Only the residual-versus-fitted plot shows it.


---

## 4. Multiple regression and multicollinearity

```text
beta_hat = (X'X)^-1 X'y
VIF_j = 1/(1 - R²_j) where R²_j regresses x_j on the others
sign flips occur when correlated predictors split a shared effect
```

Least squares is unbiased but its variance grows sharply with collinearity, so coefficients become unstable without necessarily being wrong. The prediction may be fine while the individual coefficients are meaningless.

**Worked example.** Two predictors correlated at r = 0.99: VIF ≈ 50, so standard errors grow about 7x. Both coefficients can wander in magnitude and sign across samples while their sum, the interpretable quantity, stays stable.


---

## 5. Association versus causation

```text
observed association: y = β₀ + β₁x₁ + β₂x₂ + ε
requires for a causal reading: exchangeability (no unmeasured confounding), consistency, positivity
regression cannot test any of these
```

Regression adjusts for measured variables only. The causal assumption that matters most, exchangeability, is untestable from the data, which is why observational coefficients are associations no matter how significant they look.

**Worked example.** Ice cream sales and drownings correlate strongly; temperature confounds both. Adjusting for temperature removes the association entirely, and no amount of significance survives that adjustment.


---

## Cheat Sheet

- `r = Σ(x−x̄)(y−ϼ) / (s_x s_y)` - Pearson correlation
- `ρ = Pearson on ranks` - Spearman correlation
- `β́ = cov(x,y)/var(x)` - Slope
- `α̂ = ϼ − β́ x̄` - Intercept
- `R² = 1 − SS_res/SS_tot` - Coefficient of determination
- `SE(β́) = s / sqrt(SS_x)` - Slope standard error
- `t = β́ / SE(β́)` - Coefficient test
- `β̂ = (XᵀX)⁻¹Xᵀy` - Least squares

## Numerical Traps

- Reporting R² without cross-validated error.
- Using Pearson where the relationship is monotone but curved.
- Interpreting a coefficient's sign when VIF is high.
- Extrapolating beyond the observed range of x and reporting confident intervals.
- Describing an observational coefficient as an effect.

## Self-Check Problems

1. Show r = 0 for y = x² on a symmetric interval, then show a quadratic fit recovers the relationship.
2. Compute Pearson and Spearman for a dataset with an outlier and compare.
3. Compute slope, intercept, SE, t and R² by hand and verify against a code implementation.
4. Compute VIF for two predictors correlated at r = 0.9 and explain the standard error inflation.
5. Take an observational dataset, adjust for an obvious confounder, and describe how the conclusion changes.
