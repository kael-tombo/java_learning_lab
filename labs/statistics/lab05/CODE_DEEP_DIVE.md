# Correlation & Regression - Code Deep Dive

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

## 1. Module Map

```text
src/
  CorrelationAndRegression.java  driver: correlation, fits, diagnostics, report
  Correlation.java          Pearson and Spearman with tie-aware ranking
  LinearModel.java          coefficients, fitted values, residuals, leverage
  Regression.java          simple and multiple least squares with SEs
  Diagnostics.java          residual plots, influence, VIF, curvature test
  Coefficient.java          estimate, standard error, t, p, interval together
```

Coefficient carries the interval, so a table of coefficients without uncertainty cannot be produced from this API. Influence diagnostics live next to residuals rather than in a separate tool, because they are read together.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `Correlation` | Pearson and Spearman with tie-aware average ranks |
| `LinearModel` | coefficients, fitted values, residuals, leverage |
| `Diagnostics` | residual plots, influence measures, VIF, curvature check |
| `Coefficient` | estimate, standard error, t, p-value and interval |

---

## 3.1 Regression with uncertainty attached to every coefficient

The covariance matrix gives standard errors directly, and the coefficient record makes an interval mandatory.

```java
public Regression fit(double[][] x, double[] y) {
    int n = x.length, p = x[0].length + 1;                 // +1 for the intercept
    double[][] design = new double[n][p];
    for (int i = 0; i < n; i++) { design[i][0] = 1.0; System.arraycopy(x[i], 0, design[i], 1, p - 1); }
    double[][] xtx = new double[p][p];
    double[] xty = new double[p];
    for (int i = 0; i < n; i++)
        for (int a = 0; a < p; a++) {
            xty[a] += design[i][a] * y[i];
            for (int b = 0; b < p; b++) xtx[a][b] += design[i][a] * design[i][b];
        }
    double[] beta = Matrix.solve(xtx, xty);
    double sse = 0;
    for (int i = 0; i < n; i++) { double e = y[i] - dot(beta, design[i]); sse += e * e; }
    double s2 = sse / (n - p);                            // residual variance
    double[][] inv = Matrix.inverse(xtx);                  // SE_j = sqrt(s2 * inv_jj)
    Coefficient[] coefs = new Coefficient[p];
    for (int j = 0; j < p; j++) {
        double se = Math.sqrt(s2 * inv[j][j]);
        double t = beta[j] / se;
        coefs[j] = new Coefficient(beta[j], se, t, tSurvivalTwoSided(t, n - p),
                beta[j] - 1.96 * se, beta[j] + 1.96 * se);
    }
    return new Regression(coefs, 1 - sse / totalSumOfSquares(y), residuals(design, beta, y));
}
```


---

## 3.2 Influence and diagnostics computed with the residuals

Leverage, squared residuals and Cook's distance come from the same decomposition, so they are read together as they should be.

```java
public Diagnostics diagnose(Regression r) {
    double[] e = r.residuals();
    double n = e.length, p = r.coefficients().length;
    double[] leverage = new double[(int) n];
    for (int i = 0; i < n; i++) {
        leverage[i] = designRow.dot(invXtX, designRow);   // h_i in [0, 1]
        if (leverage[i] < 0 || leverage[i] > 1) throw new IllegalStateException("bad leverage");
    }
    double[] cooks = new double[(int) n];
    for (int i = 0; i < n; i++) {
        double studentised = e[i] / (r.residualSd() * Math.sqrt(1 - leverage[i]));
        cooks[i] = studentised * studentised * leverage[i] / (p * (1 - leverage[i]));
    }
    // curvature: compare residual correlation with fitted against what independence implies
    double curvature = pearson(r.fitted(), e);
    return new Diagnostics(leverage, e, cooks, vif(r), curvature);
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| Pearson correlation | `O(n)` | one pass with Welford-style accumulators |
| Spearman correlation | `O(n log n)` | two sorts plus tie-aware ranking |
| Multiple regression fit | `O(np² + p³)` | building XᵀX dominates |
| Diagnostics including VIF | `O(np²)` | auxiliary regressions per predictor |

## 5. Correctness and Numerics

- Compute correlation from centred deviations, not from raw products, to reduce cancellation.
- Handle ties in Spearman with average ranks.
- Compute standard errors from the covariance matrix rather than by differencing sums of squares.
- Report the interval with every coefficient, not the estimate alone.
- Inspect leverage and squared residual together; neither alone finds influence.

## 6. Test Strategy

- Pearson on a perfect positive line is 1 and on a negative line is -1.
- Pearson on y = x² over a symmetric interval is approximately 0.
- Spearman on any strictly monotone relationship is approximately 1.
- A perfect fit reproduces coefficients exactly and gives zero residuals.
- Standard errors match a known analytical case for simple regression.
- VIF exceeds a threshold when two predictors are strongly correlated.

## 7. Extension Points

- Add weighted least squares for heteroscedastic errors.
- Add robust regression to down-weight outliers in the slope estimate.
- Add polynomial and spline bases with the same diagnostic discipline.

## 8. Review Checklist

- [ ] Data plotted before coefficients computed
- [ ] Pearson and Spearman both reported with any gap explained
- [ ] Every coefficient carries a standard error and interval
- [ ] Residuals inspected against fitted, predictors and leverage
- [ ] R² labelled in-sample with validated error alongside
- [ ] Language distinguishes association from causation
