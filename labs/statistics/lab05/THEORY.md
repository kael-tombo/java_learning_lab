# Correlation & Regression

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

## 1. The Problem This Solves

Two variables move together. You need to know how strongly, whether linearly, and what the relationship predicts — without pretending association is cause.

It matters because every downstream claim — a feature decision, an experiment conclusion, a capacity forecast — inherits whatever this step got wrong or got right.

## 2. Learning Objectives

- Compute Pearson and Spearman correlation and explain the difference
- Build simple and multiple linear regression by least squares
- Interpret slope, intercept, R² and coefficient uncertainty correctly
- Diagnose residuals for nonlinearity, heteroscedasticity and leverage
- Distinguish association from causation and name the confounding risks
- Use regularisation and transformations when the linear model is inadequate

## 3. Core Concepts

### 3.1 Pearson measures linear association

Pearson correlation is the cosine between centred vectors. It is maximised by any linear relationship and completely blind to monotone non-linear relationships, so a curvilinear relationship can report r near zero.

### 3.2 Spearman measures monotone association

Spearman is Pearson on ranks, so it captures any monotone relationship and is far more robust to outliers. If Spearman is high and Pearson low, you have curvature or heavy tails, not independence.

### 3.3 Least squares minimises vertical error

The regression line is the one with the smallest sum of squared vertical distances. It is not the shortest perpendicular distance, and the slope is influential to outliers, which is why robust regression exists.

### 3.4 R² is in-sample

R² is the share of variance explained in the data you fitted. It rises whenever you add a predictor and falls on new data, so it is a description of the fit rather than evidence of generalisation.

### 3.5 Residuals are the model's complaints

Residual against fitted shows curvature; against a predictor shows unmodelled structure; leverage versus squared residual identifies the points that matter most. Reading these three plots is the difference between fitting and understanding.

### 3.6 Association is not causation

A correlation can arise from a confounder, from reverse causation, or from coincidence. Only a designed experiment or a credible causal design supports a causal claim, and no amount of regression fixes that.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `r = Σ(x−x̄)(y−ϼ) / (s_x s_y)` | Pearson correlation | −1 to 1, linear only |
| `ρ = Pearson on ranks` | Spearman correlation | monotone association, robust |
| `β́ = cov(x,y)/var(x)` | Slope | change in y per unit x |
| `α̂ = ϼ − β́ x̄` | Intercept | y at x = 0, often meaningless |
| `R² = 1 − SS_res/SS_tot` | Coefficient of determination | in-sample variance explained |
| `SE(β́) = s / sqrt(SS_x)` | Slope standard error | uncertainty in the slope |
| `t = β́ / SE(β́)` | Coefficient test | tests H₀: slope = 0 |
| `β̂ = (XᵀX)⁻¹Xᵀy` | Least squares | the normal equation |

## 5. How the Pieces Fit Together

1. Plot the data first; a scatter reveals curvature, clusters and outliers that no coefficient can.

2. Compute Pearson and Spearman; a large gap tells you which one describes the relationship.

3. Fit simple or multiple regression by least squares, checking residual plots afterwards.

4. Inspect residuals against fitted and against each predictor, plus leverage against squared residual.

5. Report coefficients with standard errors, R² and an honest note that it is in-sample.

6. If the linear form fails, transform, regularise or move to a non-parametric model.

## 6. Assumptions and Invariants

- Linearity of the mean response in the predictors
- Independent observations; time series needs autocorrelation-aware errors
- Homoscedastic residuals for the classical standard errors
- No influential outliers distorting the slope
- Predictors measured without error, or errors-in-variables methods used
- For causal claims, no unmeasured confounding, which regression cannot verify

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| r = 0.02 on a clear parabola | Pearson is blind to non-linear relationships | plot the data and compute Spearman; consider a quadratic term |
| R² = 0.95 cited as generalisation | in-sample statistic | report cross-validated error alongside R² |
| A causal claim from an observational regression | confounding and reverse causation | use a designed experiment, or phrase it as association |
| One point moves the slope drastically | high leverage or an outlier | check leverage and squared residual; report a robust fit |
| Coefficients flip sign after adding a variable | multicollinearity or a lurking variable | check VIF and the sign logic of each predictor |
| Confident p99 predictions from a straight line | extrapolation beyond the data range | flag extrapolation; use a model that saturates |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `Arrays.sort for rank-based correlation` | Spearman via Pearson on ranks with tie handling |
| `Apache Commons Math RealMatrix for the solve` | multiple regression via Gaussian elimination or QR |
| `Records for Residuals / Leverage` | e, e², leverage and studentised residuals together |
| `Welford for stable variance in correlation` | avoids cancellation when x and y have large means |
| `record Coefficient(double estimate, double se, double t, double p, double ciLow, double ciHigh)` | uncertainty attached to every coefficient |

## 9. Where This Sits in the Larger System

- **labs/ml/lab01** is the full treatment of the single-predictor case.
- **lab03** provides the significance test attached to each coefficient.
- **lab08** supplies the design that would justify a causal claim.
- **lab06** offers a probabilistic alternative to least squares under uncertainty.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Compute Pearson and Spearman correlation and explain the difference
- [ ] 0 — cannot yet — Build simple and multiple linear regression by least squares
- [ ] 0 — cannot yet — Interpret slope, intercept, R² and coefficient uncertainty correctly
- [ ] 0 — cannot yet — Diagnose residuals for nonlinearity, heteroscedasticity and leverage
- [ ] 0 — cannot yet — Distinguish association from causation and name the confounding risks
- [ ] 0 — cannot yet — Use regularisation and transformations when the linear model is inadequate

## 11. Summary Checklist

- [ ] I plot the data before computing any coefficient.
- [ ] I compute Spearman as well as Pearson and explain any gap.
- [ ] I inspect residuals against fitted, against predictors, and leverage.
- [ ] I report coefficients with standard errors and intervals.
- [ ] I label R² as in-sample and report validated error alongside it.
- [ ] I never make a causal claim from observational data alone.
