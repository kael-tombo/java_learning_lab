# Linear Regression

**Track:** ml  |  **Lab:** lab01  |  **Level:** Foundational

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

You have a labelled numeric target and you want the simplest honest description of how features move it. Linear regression is that description: a hyperplane through your data whose coefficients are estimated, not guessed.

Every other algorithm in this track is judged against it. If you cannot say what residual a tree is correcting, boosting is just incantation.

## 2. Learning Objectives

- Derive and implement the normal-equation solution for OLS
- Implement batch gradient descent and explain why closed form usually wins
- Compute MSE, MAE, RMSE and R² and know which one to quote
- Diagnose violated Gauss-Markov assumptions from residual plots
- Recognise when multicollinearity makes coefficients uninterpretable
- Explain what ridge and lasso actually change about the estimator

## 3. Core Concepts

### 3.1 The OLS estimator

Ordinary least squares picks the coefficient vector β that minimises the sum of squared residuals, SSR(β) = Σ(yᵢ − xᵢᵀβ)². Because the objective is a convex quadratic in β, the optimum is unique when the design matrix has full column rank. 'Ordinary' just means unweighted squared loss — nothing exotic.

### 3.2 Normal equation versus gradient descent

Setting ∇SSR(β) = 0 gives Xᵀ(Xβ − y) = 0, hence β̂ = (XᵀX)⁻¹Xᵀy. That is one solve. Gradient descent iterates β ← β − α(2/m)Xᵀ(Xβ − y) instead. Use the closed form for small p, gradient descent for large p or for the many variants (ridge, elastic net) that have no closed form.

### 3.3 Conditioning and why you rarely invert

Forming XᵀX squares the condition number: cond(XᵀX) ≈ cond(X)². The stable route is to solve XᵀXβ = Xᵀy directly (QR, Cholesky) or use SVD. Invert only for didactic clarity — and only on well-scaled data.

### 3.4 Residual analysis

Residual eᵢ = yᵢ − ŷᵢ carries the model's complaints. Plot e vs fitted (curvature means you are missing structure), Q-Q of e (tails mean fat-tailed noise and invalid standard errors), and e vs each feature (a random scatter means you exploited the signal).

### 3.5 R² and its limits

R² = 1 − SSR/SST is a *training* in-sample ratio and can be pushed to 1 by adding features. Adjusted R² penalises parameter count. Quoting adjusted R² as if it were out-of-sample performance is a classic interview trap and a classic production mistake.

### 3.6 Regularisation as a bias-variance dial

Ridge minimises SSR + λ||β||²: it shrinks coefficients smoothly and keeps all of them. Lasso uses λ||β||₁ and zeroes small ones, giving sparse models. Both add bias and reduce variance, and both require scaling features first or the penalty is applied arbitrarily.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `β̂ = (XᵀX)⁻¹Xᵀy` | Normal equation | closed-form OLS coefficients (requires invertibility) |
| `SSR(β) = Σ(yᵢ − xᵢᵀβ)²` | Residual sum of squares | the quantity OLS minimises |
| `β ← β − α(2/m)Xᵀ(Xβ − y)` | Gradient step | batch descent on SSR/m |
| `MSE = (1/n)Σ(yᵢ − ŷᵢ)²` | Mean squared error | average squared prediction error |
| `R² = 1 − SSR/SST` | Coefficient of determination | in-sample variance explained |
| `R²_adj = 1 − (1−R²)(n−1)/(n−p−1)` | Adjusted R² | parameter-count-penalised fit |
| `β̂_ridge = (XᵀX + λI)⁻¹Xᵀy` | Ridge solution | shrinkage added to the normal equation |
| `λ_i = σ²/σ_x²` | OLS standard error | uncertainty in the variance of a coefficient |

## 5. How the Pieces Fit Together

1. Load the data and split **before** touching it: 70/15/15 with a fixed seed, stratified if the target is categorical.

2. Fit preprocessing (impute, scale) on the *training fold only* and apply it forward — this is where leakage enters if you skip it.

3. Solve for β̂ with a QR or SVD-based least-squares routine; keep the singular values to diagnose rank deficiency.

4. Compute predictions and the full error suite: MSE, MAE, RMSE, R², adjusted R².

5. Plot residuals against fitted values and each feature; hunt curvature, fans, and outliers.

6. Check the coefficient table: expected sign, plausible magnitude, and VIF for collinearity.

7. Re-run on the held-out split and compare train vs test error — the gap is your variance estimate.

## 6. Assumptions and Invariants

- Linearity in the parameters (not in the features — you may add terms)
- E[ε | X] = 0: no omitted variable correlated with a feature
- Homoscedasticity: Var(ε | X) = σ² (otherwise use HC robust errors)
- No perfect multicollinearity between features (XᵀX invertible)
- Independent observations; for time series, no autocorrelation in ε
- Exogenous sampling — features are not themselves functions of the error

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| Coefficients flip sign on tiny data changes | multicollinearity inflating the variance of β | standardise, drop redundant columns, or report the model not the coefficients |
| R² = 0.99, production error is terrible | in-sample fit quoted as generalisation | always report held-out or cross-validated error next to R² |
| Test score better than train score | you fitted the scaler or imputer on the full dataset | fit preprocessing inside the training fold only |
| MSE explodes when one row has a big label | squared loss is outlier-dominated | report MAE alongside; consider Huber loss for heavy-tailed labels |
| NaN coefficients or LinAlgException | rank-deficient design matrix (constant column, duplicate feature) | drop constant columns, assert rank, regularise |
| Prediction drifts after a feature rescale upstream | model learned on a different unit than production feeds | version the preprocessing into the model artifact |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `java.util.Arrays / streams` | sorting, mean, and in-place normalisation without extra dependencies |
| `Apache Commons Math (RealMatrix)` | a dependable Gaussian-elimination and LU solve for the didactic normal equation |
| `DoubleSummaryStatistics` | streaming mean/variance/count without keeping the whole array |
| `java.util.random.Random / SplittableRandom` | reproducible splits and bootstrap resampling |
| `record FeatureRow(double[] x, double y)` | an immutable row type keeps train/test code honest |
| `Math.log1p / Math.expm1` | numerically stable log and exp when you move to log-link variants |

## 9. Where This Sits in the Larger System

- **Lab 02** replaces the linear output with a probability so you can classify.
- **Lab 05** shows how badly scaling and correlated features hurt distance-based methods.
- **Lab 08 (PCA)** is the regularised answer to 'too many correlated features'.
- **Lab 09 (Gradient Boosting)** repeatedly fits shallow trees to the residuals this lab leaves behind.
- **Lab 10** supplies the honest evaluation protocol this lab deliberately avoids.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Derive and implement the normal-equation solution for OLS
- [ ] 0 — cannot yet — Implement batch gradient descent and explain why closed form usually wins
- [ ] 0 — cannot yet — Compute MSE, MAE, RMSE and R² and know which one to quote
- [ ] 0 — cannot yet — Diagnose violated Gauss-Markov assumptions from residual plots
- [ ] 0 — cannot yet — Recognise when multicollinearity makes coefficients uninterpretable
- [ ] 0 — cannot yet — Explain what ridge and lasso actually change about the estimator

## 11. Summary Checklist

- [ ] I can derive β̂ from ∇SSR = 0 without notes
- [ ] I can explain why forming XᵀX is numerically worse than solving directly
- [ ] I can read a residual plot and name what is wrong
- [ ] I can state the five Gauss-Markov conditions and what each buys me
- [ ] I can justify MAE over MSE for a heavy-tailed target
- [ ] I can explain what ridge changes and why scaling must come first
