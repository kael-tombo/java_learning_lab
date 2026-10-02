# Lab 01: Linear Regression

## Topics Covered
- Ordinary Least Squares (OLS)
- Gradient Descent
- R² (Coefficient of Determination)
- MSE / MAE
- Assumptions of Linear Regression

## Objective
Build a linear regression model from scratch using OLS and gradient descent. Evaluate performance with R², MSE, and MAE.

## Key Concepts
| Concept | Description |
|---|---|
| OLS | Closed-form solution minimizing sum of squared residuals |
| Gradient Descent | Iterative optimization for model parameters |
| R² | Proportion of variance explained by the model |
| MSE | Mean Squared Error |
| MAE | Mean Absolute Error |
| Assumptions | Linearity, independence, homoscedasticity, normality of errors |

## Files
- `GUIDE.md` — Step-by-step lab walkthrough
- `INTERVIEW.md` — Interview Q&A on Linear Regression
- `src/com/ml/lab01/Main.java` — Compilable Java source with test cases

## Sourced field notes (fetched Oct 2026 — verify before citing)
- "LinearRegression — scikit-learn 1.9.1 documentation" (stable API docs, 2007–2026; accessed Oct 2026) — https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html — takeaway for this lab: OLS fits `w` to minimize residual sum of squares via `scipy.linalg.lstsq`, the closed-form counterpart to the lab's from-scratch OLS vs gradient-descent comparison.
- "LinearRegression — scikit-learn 1.9.1 documentation" (stable API docs, 2007–2026; accessed Oct 2026) — https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html — takeaway for this lab: `score()` defines R² as `1 - u/v` (residual vs total sum of squares), matching the lab's R²/MSE/MAE evaluation objective.
- "LinearRegression — scikit-learn 1.9.1 documentation" (stable API docs, 2007–2026; accessed Oct 2026) — https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html — takeaway for this lab: `fit_intercept`, `positive` (NNLS), and See Also links to Ridge/Lasso frame the lab's assumptions discussion (linearity, homoscedasticity) and when plain OLS needs regularization.
