# Gradient Boosting - Code Deep Dive

**Track:** ml  |  **Lab:** lab09  |  **Level:** Advanced

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
src/com/ml/lab09/
  Main.java               driver: synthetic classification, boosting vs baseline
  GradientBoosting.java   fit (rounds, eta, depth, subsample), predict, stagedPredict
  RegressionTreeRegressor.java  the weak learner: shallow, histogram-binned splits
  AdaBoost.java           sample-reweighting variant for comparison
  ShApValues.java         exact TreeSHAP attribution over ensemble paths
  EarlyStopping.java      validation-loss tracking, best-round retention
```

stagedPredict(m) returning the model truncated at round m is the single most useful method for debugging boosting: it turns a training curve into something you can plot against validation loss.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `GradientBoosting` | rounds, eta, depth, subsample; fit/predict/stagedPredict |
| `RegressionTreeRegressor` | shallow histogram-binned tree fitting a target vector |
| `EarlyStopping` | best-round tracking with a patience window |
| `ShApValues` | exact per-feature attributions with the additivity identity |

---

## 3.1 One boosting round: gradient, weak learner, scaled update

The whole algorithm in one method. Initialisation is the loss-minimising constant, which is why the first prediction is already sensible.

```java
public double[] fitOneRound(double[][] x, double[] target) {
    double[] residual = new double[x.length];        // negative gradient of the loss
    for (int i = 0; i < x.length; i++) residual[i] = target[i] - predictRaw(x[i]);
    RegressionTreeRegressor tree = new RegressionTreeRegressor(maxDepth, numBins);
    tree.fit(x, residual, subsample);                // weak learner fits the gradient
    double[][] contrib = new double[x.length][x[0].length];
    for (int i = 0; i < x.length; i++) {
        double step = eta * tree.predict(x[i]);
        for (int j = 0; j < x[0].length; j++) contrib[i][j] += step;  // accumulate deltas
    }
    addGlobal(contrib);                              // keep a bias term for the deltas
    return contrib;                                  // exact additivity for SHAP
}
```


---

## 3.2 Early stopping that keeps the best round, not the last

Track validation loss every round, retain the best contribution matrix, and expose the chosen round count so it can be logged and shipped.

```java
public int fit(double[][] xtr, double[] ytr, double[][] xval, double[] yval) {
    double base = mean(ytr);                          // loss-minimising constant
    init(base);
    double bestLoss = Double.MAX_VALUE;
    double[][] best = null; int bestRound = 0, stale = 0;
    for (int m = 1; m <= maxRounds; m++) {
        double[][] d = fitOneRound(xtr, ytr);         // one boosting round
        applyDelta(d);
        double loss = squaredError(yval, rawPredict(xval));
        if (loss < bestLoss - 1e-6) {
            bestLoss = loss; best = snapshotDelta(); bestRound = m; stale = 0;
        } else if (++stale >= patience) {             // patience, not just bestRound
            break;
        }
    }
    restore(best);                                    // ship the best round, not the last
    return bestRound;
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| One round (exact splits) | `O(n · f · log n · depth)` | impractical above ~10·7 rows |
| One round (histogram binning) | `O(n · f · bins · depth)` | the practical production path |
| Prediction over M trees | `O(M · 2^depth)` | trivially cheap compared to training |
| TreeSHAP attribution | `O(T · L · D²)` | exact, and cheap for shallow trees |

## 5. Correctness and Numerics

- Initialise to the loss-minimising constant, not to zero.
- Use histogram binning above ~100k rows or ~50 features.
- Keep contributions in a matrix so SHAP additivity is checkable, not reconstructed.
- Guard against empty leaves when subsampling small datasets.
- Assert SHAP contributions sum to prediction minus baseline within 1e-9.

## 6. Test Strategy

- The initial prediction equals the mean target (squared error) or the log-odds (logistic).
- Shallow trees with tiny eta reduce training loss monotonically.
- Early stopping returns the best round, verified against a full stored history.
- SHAP values sum to prediction minus base value within 1e-9.
- The same seed produces the same forest; different seeds produce slightly different models.
- Predicting with 0 rounds equals the base value.

## 7. Extension Points

- Implement lambda (L2 leaf shrinkage) and show it substitutes for a lower learning rate.
- Add feature subsampling per split and compare against row subsampling.
- Implement quantile or Huber loss and compare robustness on contaminated targets.

## 8. Review Checklist

- [ ] Initial value is the loss-minimising constant
- [ ] Learning rate, depth, subsample and rounds are constructor arguments
- [ ] Early stopping with patience, shipping the best round
- [ ] Contributions retained so explanations are exact
- [ ] Histogram binning used above the size where exact splits hurt
- [ ] Validation loss curve logged on every run
