# Logistic Regression - Code Deep Dive

**Track:** ml  |  **Lab:** lab02  |  **Level:** Foundational

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
src/com/ml/lab02/
  Main.java                 driver: synthetic binary data, fit, report
  LogisticRegression.java   fit(), predictProba(), predict(threshold), coefficients()
  Metrics.java              confusion matrix, precision, recall, F1, AUC, PR curve
  ThresholdSweeper.java     cost-matrix driven threshold selection
  Calibration.java          reliability bins and expected calibration error
```

The stable log-loss lives in one place (`logLoss`) and is used by both the trainer and the reporter — two implementations of log-loss will eventually disagree, and that bug is invisible.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `LogisticRegression` | owns β, the fitted scaler, and the prediction threshold |
| `Metrics` | confusionMatrix(), precision(), recall(), f1(), rocAuc(), prCurve() |
| `ThresholdSweeper` | given a cost matrix, returns the threshold minimising expected cost |
| `Calibration` | reliabilityBins() and expectedCalibrationError() over predicted scores |

---

## 3.1 Numerically stable loss and sigmoid

One place for both, with the two-branch structure documented so nobody later 'simplifies' it back into the overflow bug.

```java
static double logLoss(double z, int y) {
    // max(z,0) form avoids evaluating exp(+huge); log1p keeps precision near 0
    if (y == 1) {
        return z >= 0 ? Math.log1p(Math.exp(-z)) : -z + Math.log1p(Math.exp(z));
    }
    return z >= 0 ? Math.log1p(Math.exp(-z)) - z : Math.log1p(Math.exp(z));
}

static double sigmoid(double z) {
    if (z >= 0) return 1.0 / (1.0 + Math.exp(-z));
    double e = Math.exp(z);            // e in (0,1], no overflow
    return e / (1.0 + e);
}
```


---

## 3.2 Training loop with L2 and a convergence guard

Learning rate, penalty strength and max iterations are constructor arguments, not constants. Convergence is on relative loss change, which is scale-free.

```java
public void fit(double[][] x, int[] y, double lr, double lambda, int maxIter) {
    int n = x.length, p = x[0].length;
    beta = new double[p];
    double prev = Double.POSITIVE_INFINITY;
    for (int it = 0; it < maxIter; it++) {
        double loss = 0;
        double[] grad = new double[p];
        for (int i = 0; i < n; i++) {           // accumulate loss and gradient
            double z = 0;
            for (int j = 0; j < p; j++) z += beta[j] * xs[i][j];
            double pi = sigmoid(z);
            loss += y[i] == 1 ? -Math.log(Math.max(pi, 1e-15))
                              : -Math.log(Math.max(1 - pi, 1e-15));
            double g = pi - y[i];
            for (int j = 0; j < p; j++) grad[j] += g * xs[i][j];
        }
        loss = loss / n + lambda * sumSquares(beta) / 2;
        for (int j = 0; j < p; j++) beta[j] -= lr * (grad[j] / n + lambda * beta[j]);
        if (Math.abs(prev - loss) < 1e-9 * Math.max(1.0, Math.abs(loss))) break;
        prev = loss;
    }
}
```


---

## 3.3 Cost-matrix threshold selection

Sweep every distinct score, compute the realised cost at each candidate threshold, and return the argmin. This is the piece reviewers ask about, so it is explicit rather than buried in a config file.

```java
public static double optimalThreshold(double[] scores, int[] y,
                                         double costFp, double costFn) {
    double[] uniq = Arrays.stream(scores).distinct().sorted().toArray();
    double bestT = 0.5, bestCost = Double.MAX_VALUE;
    for (double t : uniq) {                      // predict 1 iff score >= t
        long fp = 0, fn = 0;
        for (int i = 0; i < scores.length; i++) {
            boolean pred = scores[i] >= t;
            if (pred && y[i] == 0) fp++;
            if (!pred && y[i] == 1) fn++;
        }
        double cost = fp * costFp + fn * costFn;
        if (cost < bestCost) { bestCost = cost; bestT = t; }
    }
    return bestT;
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| One full gradient pass | `O(np)` | row-parallel; accumulate grad into a per-thread buffer then reduce |
| Training for k iterations | `O(k n p)` | k typically 200–2000 with a good learning rate |
| predictProba(row) | `O(p)` | one dot product plus a sigmoid |
| Full metric suite incl. AUC | `O(n log n)` | sort once for ROC and reuse ranks for PR |

## 5. Correctness and Numerics

- Never call log(sigmoid(z)) without the two-branch guard.
- Initialise β = 0 and assert the first loss is within 1e-9 of log 2.
- Standardise features; the Hessian condition number scales with feature scale.
- Use L2 by default — it prevents separation blowups and stabilises β.
- Sweep the threshold on a validation split, never on the test set.

## 6. Test Strategy

- Sanity: at β = 0 all probabilities equal 0.5 and loss equals log 2.
- Separation: perfectly separable data with λ > 0 keeps every |coefficient| below 1/sqrt(λ).
- Stability: no NaN for z in [−1000, 10000] across both label values.
- Monotonicity: increasing a positive coefficient increases p for xⱼ > 0.
- AUC sanity: a perfect ranking gives 1.0, random scores give ≈ 0.5, inverted gives 0.0.
- Calibration: on synthetic data from the model itself, mean predicted ≈ observed rate within 2%.

## 7. Extension Points

- Implement class weighting and show it moves the threshold's optimal position.
- Add Platt scaling / temperature scaling as a post-hoc calibration stage and re-measure ECE.
- Implement multiclass (one-vs-rest and softmax) and compare against the binary path.
- Report the decision curve analysis in addition to ROC so cost-sensitive readers get their curve.

## 8. Review Checklist

- [ ] Stable log-loss in exactly one place
- [ ] Learning rate, penalty and threshold are constructor/config values
- [ ] Threshold chosen on validation data with the cost matrix in the repo
- [ ] Tests cover the extreme-z and separation cases
- [ ] Confusion matrix printed in every example run
- [ ] Model artifact contains β, scaler stats and threshold together
