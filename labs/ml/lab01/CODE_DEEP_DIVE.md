# Linear Regression - Code Deep Dive

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

## 1. Module Map

```text
src/com/ml/lab01/
  Main.java                 driver: loads data, fits, reports metrics
  LinearRegression.java     the estimator: fit(), predict(), coefficients()
  Matrix.java               minimal double[][] helpers (solve, transpose, identity)
  Metrics.java              mse, mae, rmse, r2, adjustedR2
  ResidualDiagnostics.java  residual stats, VIF, autocorrelation at lag k
```

Deliberately dependency-free so every operation is visible. Swap `Matrix.solve` for a QR or SVD implementation and watch the conditioning section of THEORY.md stop being academic.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `LinearRegression` | holds β, the fitted mean, and a fit()/predict() pair; stateless w.r.t. data |
| `Matrix` | static double[][] utilities: transpose, identity, matMul, solve (Gaussian elimination) |
| `Metrics` | static double[] errorMetrics(y, yHat) returning MSE, MAE, RMSE, R², adjR² |
| `ResidualDiagnostics` | residual(), vif(), durbinWatson() — the assumption checkers |

---

## 3.1 Fitting by QR-free Gaussian elimination (the didactic path)

Build the normal equations once, then solve. Never invert in production code; this method is here because it makes the derivation checkable by hand.

```java
public static double[] solve(double[][] a, double[] b) {
    int n = b.length;
    double[][] m = new double[n][n + 1];           // augmented
    for (int i = 0; i < n; i++) {
        System.arraycopy(a[i], 0, m[i], 0, n);
        m[i][n] = b[i];
    }
    for (int col = 0; col < n; col++) {             // forward elimination
        int piv = col;
        for (int r = col + 1; r < n; r++) {
            if (Math.abs(m[r][col]) > Math.abs(m[piv][col])) piv = r;
        }
        if (Math.abs(m[piv][col]) < 1e-12) {
            throw new IllegalStateException("singular matrix at column " + col);
        }
        double[] tmp = m[col]; m[col] = m[piv]; m[piv] = tmp;
        for (int r = col + 1; r < n; r++) {
            double f = m[r][col] / m[col][col];
            for (int c = col; c <= n; c++) m[r][c] -= f * m[col][c];
        }
    }
    double[] x = new double[n];                     // back substitution
    for (int r = n - 1; r >= 0; r--) {
        double s = m[r][n];
        for (int c = r + 1; c < n; c++) s -= m[r][c] * x[c];
        x[r] = s / m[r][r];
    }
    return x;
}
```


---

## 3.2 The estimator with a feature-scaling step baked in

Scaling lives inside the estimator so it cannot be forgotten at prediction time. `fit` records the scaler; `predict` reuses it. This is the single biggest defence against train/serve skew.

```java
public final class LinearRegression {
    private double[] beta;                 // scaled-space coefficients
    private double[] featureMean, featureScale;
    private double yMean;

    public void fit(double[][] x, double[] y) {
        int n = x.length, p = x[0].length;
        featureMean = colMeans(x);  featureScale = colScales(x);
        double[][] xs = standardize(x, featureMean, featureScale);
        double[][] xtx = new double[p][p];
        double[]  xty = new double[p];
        for (int i = 0; i < n; i++)                 // accumulate X^T X and X^T y
            for (int a = 0; a < p; a++) {
                xty[a] += xs[i][a] * y[i];
                for (int b = 0; b < p; b++) xtx[a][b] += xs[i][a] * xs[i][b];
            }
        for (int a = 0; a < p; a++) xtx[a][a] += 1e-8;  // tiny ridge for stability
        beta = Matrix.solve(xtx, xty);
        yMean = Arrays.stream(y).average().orElseThrow();
    }

    public double predict(double[] row) {
        double s = 0;
        for (int j = 0; j < beta.length; j++)
            s += beta[j] * (row[j] - featureMean[j]) / featureScale[j];
        return s + yMean;                          // un-standardise y
    }
}
```


---

## 3.3 Streaming metrics that do not need the whole array

Welford's algorithm gives variance in one pass with excellent numerical behaviour. Use it in the training loop and in any streaming production metric where retaining rows is not an option.

```java
public static double[] streamingMetrics(DoubleStream ys,
                                           ToDoubleFunction<Double> predict) {
    // Welford: numerically stable mean/M2 in a single pass
    class Acc {
        double n, mean, m2;
        void add(double x) {
            n++;
            double d = x - mean;
            mean += d / n;
            m2 += d * (x - mean);
        }
    }
    Acc truth = new Acc(), err = new Acc();
    ys.forEach(y -> { truth.add(y); err.add(predict.applyAsDouble(y)); });
    double mse = err.m2 / err.n;
    double sst = truth.m2;
    return new double[] { mse, Math.sqrt(mse), Math.abs(err.mean), 1 - err.m2 / sst };
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| Build XᵀX | `O(n p²)` | dominant cost; parallelise over rows if p is large |
| Gaussian elimination on p×p | `O(p³)` | fine to p ≈ 1000; switch to iterative above that |
| One prediction | `O(p)` | pure dot product with the coefficient vector |
| Full metric suite | `O(n p)` | two passes, memory O(1) with Welford |

## 5. Correctness and Numerics

- Standardise features before solving; scaling is a preconditioner for the normal equations.
- Add a token ridge (1e-8) only to make the solve total, and say so in a comment — do not hide real collinearity.
- Compare against a one-feature baseline; if the full model cannot beat it, the extra features are noise.
- Use `Math.fma` where available to avoid cancellation in long dot products.
- Report coefficient uncertainty (σ²(XᵀX)⁻¹ diagonal) alongside point estimates — a coefficient with a t-statistic of 0.1 is not a finding.

## 6. Test Strategy

- Perfect-fit test: y = 3 + 2x synthetically ⇒ β = (2, 3) within 1e-9 and R² = 1.
- Invariance test: scaling a feature by 1000 must not change R² and must scale β by 0.001.
- Singularity test: duplicate a column and assert the explicit failure, not a silent garbage answer.
- Symmetry test: adding a constant to every y must shift the intercept by exactly that constant.
- Property test: for random X with full rank, OLS residuals must be orthogonal to every column of X (Xᵀe ≈ 0).
- Golden test: a fixed tiny dataset with hand-computed coefficients locked in as expected values.

## 7. Extension Points

- Swap `Matrix.solve` for QR and add an assertion that both agree to 1e-10 on well-conditioned data.
- Implement ridge by augmenting XᵀX with λI and sweep λ; plot train/test error to pick it honestly.
- Add iteratively reweighted least squares (IRLS) for a target whose variance grows with its mean.
- Report bootstrap confidence intervals on each coefficient using `SplittableRandom` for determinism.

## 8. Review Checklist

- [ ] Preprocessing lives inside the estimator, not the caller
- [ ] Singular matrices fail loudly with a message naming the column
- [ ] Seeds and splits are constants, not ambient randomness
- [ ] Metrics are computed on held-out data and both are reported
- [ ] No `double` accumulation without considering Kahan or Welford
- [ ] Every numeric constant has a comment explaining why that value
