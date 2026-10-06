# Correlation & Regression - Flashcards (60 cards)

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

**Format.** Question (front) -> answer (back). Use for spaced repetition: day 0, day 1, day 3, day 7, day 21. Do not read the answer first.

| # | Front | Back |
|---|---|---|
| 1 | What does Pearson correlation fail to see? | Monotone non-linear relationships, because it only measures linear association. |
| 2 | When is Spearman the better choice? | When the relationship is monotone but curved, or when outliers would dominate Pearson. |
| 3 | Why can R² rise with useless predictors? | It is in-sample and increases whenever a predictor is added, even with no real gain. |
| 4 | What do residuals against fitted values reveal? | Curvature, which means the functional form is wrong rather than the parameters. |
| 5 | What identifies the influential points? | Leverage against squared residual in a leverage-versus-residuals-squared plot. |
| 6 | Does a strong correlation support a causal claim? | No; confounding and reverse causation can both produce it. |
| 7 | Why does adding a variable flip a coefficient's sign? | Multicollinearity or an omitted variable that was absorbing the effect. |
| 8 | What does the intercept mean? | The predicted response at x = 0, which is meaningless when zero lies outside the data range. |
| 9 | What is Pearson measures linear association? | Pearson correlation is the cosine between centred vectors. |
| 10 | What is Spearman measures monotone association? | Spearman is Pearson on ranks, so it captures any monotone relationship and is far more robust to outliers. |
| 11 | What is Least squares minimises vertical error? | The regression line is the one with the smallest sum of squared vertical distances. |
| 12 | What is R² is in-sample? | R² is the share of variance explained in the data you fitted. |
| 13 | What is Residuals are the model's complaints? | Residual against fitted shows curvature; against a predictor shows unmodelled structure; leverage versus squared residual identifies the points that matter most. |
| 14 | What is Association is not causation? | A correlation can arise from a confounder, from reverse causation, or from coincidence. |
| 15 | In this lab, what does `r = Σ(x−x̄)(y−ϼ) / (s_x s_y)` mean? | Pearson correlation: −1 to 1, linear only |
| 16 | In this lab, what does `ρ = Pearson on ranks` mean? | Spearman correlation: monotone association, robust |
| 17 | In this lab, what does `β́ = cov(x,y)/var(x)` mean? | Slope: change in y per unit x |
| 18 | In this lab, what does `α̂ = ϼ − β́ x̄` mean? | Intercept: y at x = 0, often meaningless |
| 19 | In this lab, what does `R² = 1 − SS_res/SS_tot` mean? | Coefficient of determination: in-sample variance explained |
| 20 | In this lab, what does `SE(β́) = s / sqrt(SS_x)` mean? | Slope standard error: uncertainty in the slope |
| 21 | In this lab, what does `t = β́ / SE(β́)` mean? | Coefficient test: tests H₀: slope = 0 |
| 22 | In this lab, what does `β̂ = (XᵀX)⁻¹Xᵀy` mean? | Least squares: the normal equation |
| 23 | You see 'r = 0.02 on a clear parabola' in production. What is the cause and the fix? | Pearson is blind to non-linear relationships Fix: plot the data and compute Spearman; consider a quadratic term |
| 24 | You see 'R² = 0.95 cited as generalisation' in production. What is the cause and the fix? | in-sample statistic Fix: report cross-validated error alongside R² |
| 25 | You see 'A causal claim from an observational regression' in production. What is the cause and the fix? | confounding and reverse causation Fix: use a designed experiment, or phrase it as association |
| 26 | You see 'One point moves the slope drastically' in production. What is the cause and the fix? | high leverage or an outlier Fix: check leverage and squared residual; report a robust fit |
| 27 | You see 'Coefficients flip sign after adding a variable' in production. What is the cause and the fix? | multicollinearity or a lurking variable Fix: check VIF and the sign logic of each predictor |
| 28 | You see 'Confident p99 predictions from a straight line' in production. What is the cause and the fix? | extrapolation beyond the data range Fix: flag extrapolation; use a model that saturates |
| 29 | Which Java API is the backbone of: Spearman via Pearson on ranks with tie handling | `Arrays.sort for rank-based correlation` |
| 30 | Which Java API is the backbone of: multiple regression via Gaussian elimination or QR | `Apache Commons Math RealMatrix for the solve` |
| 31 | Which Java API is the backbone of: e, e², leverage and studentised residuals together | `Records for Residuals / Leverage` |
| 32 | Which Java API is the backbone of: avoids cancellation when x and y have large means | `Welford for stable variance in correlation` |
| 33 | Which Java API is the backbone of: uncertainty attached to every coefficient | `record Coefficient(double estimate, double se, double t, double p, double ciLow, double ciHigh)` |
| 34 | Why does Pearson measures linear association matter operationally? | Pearson correlation is the cosine between centred vectors. |
| 35 | Why does Spearman measures monotone association matter operationally? | Spearman is Pearson on ranks, so it captures any monotone relationship and is far more robust to outliers. |
| 36 | Why does Least squares minimises vertical error matter operationally? | The regression line is the one with the smallest sum of squared vertical distances. |
| 37 | Why does R² is in-sample matter operationally? | R² is the share of variance explained in the data you fitted. |
| 38 | Why does Residuals are the model's complaints matter operationally? | Residual against fitted shows curvature; against a predictor shows unmodelled structure; leverage versus squared residual identifies the points that matter most. |
| 39 | Why does Association is not causation matter operationally? | A correlation can arise from a confounder, from reverse causation, or from coincidence. |
| 40 | In the Correlation & Regression pipeline, what happens next? Plot the data first; a scatter reveals curvature, clusters a... | Plot the data first; a scatter reveals curvature, clusters and outliers that no coefficient can. |
| 41 | In the Correlation & Regression pipeline, what happens next? Compute Pearson and Spearman; a large gap tells you which on... | Compute Pearson and Spearman; a large gap tells you which one describes the relationship. |
| 42 | In the Correlation & Regression pipeline, what happens next? Fit simple or multiple regression by least squares, checking... | Fit simple or multiple regression by least squares, checking residual plots afterwards. |
| 43 | In the Correlation & Regression pipeline, what happens next? Inspect residuals against fitted and against each predictor,... | Inspect residuals against fitted and against each predictor, plus leverage against squared residual. |
| 44 | In the Correlation & Regression pipeline, what happens next? Report coefficients with standard errors, R² and an honest n... | Report coefficients with standard errors, R² and an honest note that it is in-sample. |
| 45 | In the Correlation & Regression pipeline, what happens next? If the linear form fails, transform, regularise or move to a... | If the linear form fails, transform, regularise or move to a non-parametric model. |
| 46 | Exercise focus: Correlation, both kinds | Linear versus monotone. |
| 47 | Exercise focus: Simple regression by hand | The full arithmetic. |
| 48 | Exercise focus: Multiple regression with intervals | More than one predictor. |
| 49 | Exercise focus: Diagnostics | Read the complaints. |
| 50 | Exercise focus: Multicollinearity and VIF | See coefficients become unstable. |
| 51 | Exercise focus: Nonlinearity and transforms | Repair the functional form. |
| 52 | State the Correlation as cosine and what it misses result for Correlation & Regression. | y = x² for x uniform on [-1, 1]: r = 0 because the covariance is zero by symmetry. Adding a quadratic term raises R² from 0 to about 1, which shows the information was always there and the model form was wrong. |
| 53 | State the Regression coefficients and their uncertainty result for Correlation & Regression. | x with sd 0.1 instead of 1.0, same true relationship: SE(b) grows by 10x, so the t-statistic falls by 10x. The same data with x spread across its range is far more informative, which is why design beats analysis here. |
| 54 | State the Residual diagnostics result for Correlation & Regression. | Fitting a straight line to y = 2x + 0.5x² leaves a symmetric parabola of residuals against fitted: average residual is zero, so a residual mean check passes while the model is wrong. Only the residual-versus-fitted plot shows it. |
| 55 | State the Multiple regression and multicollinearity result for Correlation & Regression. | Two predictors correlated at r = 0.99: VIF ≈ 50, so standard errors grow about 7x. Both coefficients can wander in magnitude and sign across samples while their sum, the interpretable quantity, stays stable. |
| 56 | State the Association versus causation result for Correlation & Regression. | Ice cream sales and drownings correlate strongly; temperature confounds both. Adjusting for temperature removes the association entirely, and no amount of significance survives that adjustment. |
| 57 | What is VIF and why does it matter? | Variance inflation factor per predictor: how much its variance is inflated by correlation with the others. |
| 58 | Why is least squares called least squares? | It minimises the sum of squared vertical residuals, not perpendicular distances. |
| 59 | How do you test a slope? | t = slope divided by its standard error, referenced to the t distribution with n minus 2 degrees of freedom. |
| 60 | When should you regularise? | When predictors are correlated or numerous relative to n, and the goal is prediction rather than interpretation. |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
