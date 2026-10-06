# Linear Regression - Mathematical Foundations

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

## Notation

| Symbol | Meaning |
|---|---|
| `β̂ = (XᵀX)⁻¹Xᵀy` | Normal equation - closed-form OLS coefficients (requires invertibility) |
| `SSR(β) = Σ(yᵢ − xᵢᵀβ)²` | Residual sum of squares - the quantity OLS minimises |
| `β ← β − α(2/m)Xᵀ(Xβ − y)` | Gradient step - batch descent on SSR/m |
| `MSE = (1/n)Σ(yᵢ − ŷᵢ)²` | Mean squared error - average squared prediction error |
| `R² = 1 − SSR/SST` | Coefficient of determination - in-sample variance explained |
| `R²_adj = 1 − (1−R²)(n−1)/(n−p−1)` | Adjusted R² - parameter-count-penalised fit |
| `β̂_ridge = (XᵀX + λI)⁻¹Xᵀy` | Ridge solution - shrinkage added to the normal equation |
| `λ_i = σ²/σ_x²` | OLS standard error - uncertainty in the variance of a coefficient |

## Why the Math Matters

Linear regression is the cleanest place to see three ideas that recur for the rest of the track: a convex objective with a unique optimum, the geometry of least squares as projection, and the variance of an estimator growing with feature collinearity.


---

## 1. Least-squares normal equation

```text
grad_beta SSR = 2 X^T (X beta - y) = 0
  =>  X^T X beta = X^T y
  =>  beta_hat = (X^T X)^-1 X^T y
```

The gradient vanishes at the optimum because SSR is convex. If X^T X is singular the objective is flat along some direction and β̂ is not unique.

**Worked example.** Two features, x1 = [1,2,3,4], x2 = 2*x1. X^T X is singular; RSSO(8) throws LinAlgException. Fix: drop x2 or use ridge (λ>0 makes X^T X + λI PD).


---

## 2. Projection geometry

```text
SSR_min = ||y||^2 - y^T P_X y,   P_X = X (X^T X)^-1 X^T
R^2 = 1 - SSR/SST = y^T P_X y / y^T y
```

OLS is the orthogonal projection of y onto the column space of X. R² is literally the squared cosine between y and its projection — that is why it is bounded by 1 and why it cannot go negative once an intercept is present.

**Worked example.** y perfectly predicted: R² = 1. Adding p useless features to n points with an intercept still gives R² ≈ 1 in sample, and a negative value out of sample.


---

## 3. Gauss-Markov and the variance of beta

```text
Var(beta_hat | X) = sigma^2 (X^T X)^-1
Var(beta_j) = sigma^2 / (SST_xj (1 - R_j^2))
```

The diagonal of (X^T X)⁻¹ is the variance of each coefficient. As R²_j → 1 (collinearity) the denominator vanishes and the variance explodes. This is the mechanism behind sign-flipping coefficients.

**Worked example.** Add a feature that is 0.99-correlated with an existing one: R²_j = 0.98, so (1-R²_j) = 0.02 and the standard error grows about 7× versus an uncorrelated feature.


---

## 4. Gradient descent convergence

```text
f(beta_k) - f(beta*) <= 2 L ||beta_0 - beta*||^2 / (2^k alpha L)
```

For L-smooth convex f, the gap shrinks geometrically. The condition number κ = L/μ sets the stable range alpha ∈ (0, 2/L): too small and you crawl, too large and you diverge or ring around the optimum.

**Worked example.** L = 2XᵀX's largest eigenvalue, say 12. alpha = 0.05 (stable); alpha = 0.5 diverges. With κ = 500, ridge's λ and the shape of X should be standardised.


---

## 5. Ridge as Bayesian MAP

```text
beta_hat(lam) = (X^T X + lam I)^-1 X^T y
 equivalent to: beta ~ N(0, sigma^2/lam I), noise ~ N(0, sigma^2 I)
```

Ridge is the MAP estimate under a zero-mean Gaussian prior on the weights. That is a real modelling statement, not just a numerical hack — it says large weights need more evidence.

**Worked example.** With lam = 1 and a feature whose OLS coefficient was 12.0, the ridge coefficient lands near 1.1: shrunk hard, still ordered, never exactly zero.


---

## 6. Evaluation arithmetic and units

```text
RMSE = sqrt(MSE);  MAE = mean|e|
RMSE/MAE ratio: 1 for Gaussian noise, >1 for heavy tails
MAPE is undefined when any y = 0
```

RMSE and MAE live in the target's units, which makes them quotable in a SLO. Their ratio is a cheap tail diagnostic; MAPE explodes near zero and should be replaced with sMAPE or WAPE.

**Worked example.** Residuals: 100 points at 1, one at 100. MAE = 1.9, RMSE = 10.0, ratio 5.3 — the metric you shipped must match the business loss function.


---

## Cheat Sheet

- `β̂ = (XᵀX)⁻¹Xᵀy` - Normal equation
- `SSR(β) = Σ(yᵢ − xᵢᵀβ)²` - Residual sum of squares
- `β ← β − α(2/m)Xᵀ(Xβ − y)` - Gradient step
- `MSE = (1/n)Σ(yᵢ − ŷᵢ)²` - Mean squared error
- `R² = 1 − SSR/SST` - Coefficient of determination
- `R²_adj = 1 − (1−R²)(n−1)/(n−p−1)` - Adjusted R²
- `β̂_ridge = (XᵀX + λI)⁻¹Xᵀy` - Ridge solution
- `λ_i = σ²/σ_x²` - OLS standard error

## Numerical Traps

- Dividing by n instead of n−1 for sample variance — silently biased low.
- Computing R² without an intercept: it can go negative and means something different.
- Standardising the target and then quoting RMSE in standardised units to stakeholders.
- Using a Gauss-Jordan inverse instead of a solve: same answer for a 4×4 matrix, different answer for a 400×400.
- Rounding coefficients before deployment — 0.1% coefficient error can move a decision threshold.

## Self-Check Problems

1. For x = [1,2,3,4,5] and y = [2,4,5,4,5], compute β̂, MSE and R² by hand and verify with code.
2. Show that adding a constant column to X makes XᵀX singular, then explain why an intercept column is safe only with β₀ excluded.
3. Derive the gradient of SSR/m and confirm it equals (2/m)XᵀXβ − (2/m)Xᵀy by finite differences.
4. Given σ = 2 and SST_x = 10 for a feature, compute the standard error of its coefficient when R²_x = 0 and again at R²_x = 0.9.
5. For ridge with p = 3, compute β̂ at λ = 0, 0.1, 1, 10 and plot coefficient magnitude against λ.
