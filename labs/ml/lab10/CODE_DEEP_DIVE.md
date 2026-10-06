# Model Evaluation - Code Deep Dive

**Track:** ml  |  **Lab:** lab10  |  **Level:** Intermediate

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
src/com/ml/lab10/
  Main.java               driver: several datasets, full metric report
  ConfusionMatrix.java    int[] confusionMatrix + all derived metrics
  RocCurve.java           TPR/FPR sweep by rank, trapezoidal AUC
  PrCurve.java            precision/recall sweep + average precision
  CrossValidator.java     stratified k-fold, grouped folds, forward-chaining folds
  ThresholdSelector.java  cost-matrix driven threshold choice on validation folds
```

CrossValidator returns explicit index arrays (record Fold) rather than running a callback. Being able to print a fold is how you catch leakage in grouped and time-ordered data.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `ConfusionMatrix` | counts plus every derived metric, and the trivial-baseline comparison |
| `RocCurve / PrCurve` | rank-based curves with AUC and average precision |
| `CrossValidator` | stratified, grouped and forward-chaining fold generation |
| `ThresholdSelector` | cost-matrix threshold selection on validation folds only |

---

## 3.1 Confusion matrix as the single source of truth

Every metric derives from the four counts. Returning them as a record makes it impossible to report accuracy without also reporting the matrix.

```java
public record Metrics(int tp, int fp, int fn, int tn,
                      double precision, double recall, double f1,
                      double specificity, double balancedAccuracy,
                      double accuracy, double trivialAccuracy) {

    public static Metrics of(int[] y, int[] yHat) {
        int tp = 0, fp = 0, fn = 0, tn = 0;
        for (int i = 0; i < y.length; i++) {
            if (y[i] == 1 && yHat[i] == 1) tp++;
            else if (y[i] == 0 && yHat[i] == 1) fp++;
            else if (y[i] == 1 && yHat[i] == 0) fn++;
            else tn++;
        }
        int n = y.length;
        int pos = tp + fn;
        double p = safe(tp, tp + fp);                 // guard zero denominators
        double r = safe(tp, pos);
        double spec = safe(tn, tn + fp);
        return new Metrics(tp, fp, fn, tn, p, r, harmonic(p, r), spec,
                0.5 * (r + spec), safe(tp + tn, n), safe(Math.max(tp + tn, fn + fp), n));
    }
    static double safe(double num, double den) { return den == 0 ? 0.0 : num / den; }
    static double harmonic(double a, double b) { return (a + b) == 0 ? 0 : 2 * a * b / (a + b); }
}
```


---

## 3.2 Splits that respect how the data was generated

Three strategies behind one interface. Using the wrong one is the most common evaluation leak, so the type name says which is which.

```java
public interface Folding { List<Fold> folds(int n); }

record Fold(int[] train, int[] test) {}

static Folding stratified(int[] y, int k) {
    // shuffle within each class, then deal rows round-robin into k folds:
    // guarantees every fold keeps the class ratio
}

static Folding grouped(int[] groupId, int k) {
    // group ids are hashed to folds so no entity can appear in train and test
}

static Folding forwardChaining(int n, int k, int minTrain) {
    // test folds walk forward in time: [minTrain, minTrain+w), [minTrain+w, minTrain+2w), ...
    // no fold ever trains on data at or after its test window
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| Confusion matrix and metrics | `O(n)` | one pass |
| ROC curve by rank sort | `O(n log n)` | sort once; AUC from ranks, no sweep loop needed |
| PR curve and average precision | `O(n log n)` | same sort reused |
| k-fold evaluation with a model fit | `O(k · fit_cost)` | fits dominate; cache fold indices across runs |

## 5. Correctness and Numerics

- Guard every metric's denominator; a model that predicts one class has no precision.
- Compute AUC from ranks (Mann-Whitney) rather than a trapezoid sweep; it is exact and faster.
- Cache fold indices so repeated runs compare like for like.
- Print the trivial baseline next to accuracy in every report.
- Round metrics consistently; mixed precision in a report reads as sloppiness.

## 6. Test Strategy

- A perfect classifier yields tp = n, fp = fn = 0, precision = recall = 1.
- A trivial all-positive classifier yields recall 1.0, precision = pi, FPR 1.0.
- AUC by rank equals AUC by trapezoid within 1e-9.
- Stratified folds preserve the class ratio within one row.
- Grouped folds never place the same group id in both train and test.
- Forward-chaining folds always have max(train index) < min(test index).
- Two runs with the same seed produce identical folds.

## 7. Extension Points

- Implement stratified k-fold with a documented fold count and cache the indices to disk.
- Add bootstrap confidence intervals on a metric and a paired test between two models.
- Implement cost-based threshold selection and report the cost curve alongside PR.

## 8. Review Checklist

- [ ] Every metric derives from one confusion matrix
- [ ] Trivial baseline printed with accuracy
- [ ] Fold type chosen to match data generation, and asserted
- [ ] Fold indices cached and reproducible from a seed
- [ ] Threshold selected on validation folds only
- [ ] Interval or repeated-fold spread reported for the headline metric
