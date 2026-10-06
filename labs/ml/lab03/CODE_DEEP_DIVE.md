# Decision Trees & Random Forests - Code Deep Dive

**Track:** ml  |  **Lab:** lab03  |  **Level:** Intermediate

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
src/com/ml/lab03/
  Main.java                driver on the play-tennis style dataset
  Tree.java                node structure, recursive build, predict
  SplitFinder.java         impurity, candidate thresholds, best split
  RandomForest.java        bootstrap, feature subsets, aggregate, OOB error
  FeatureImportance.java   impurity and permutation importance
```

Split search is the only hot loop. Thresholds are precomputed once per node from sorted feature values so the inner scan is a linear scan with running left/right sums, not a sort per candidate.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `Tree / Node` | feature, threshold, left, right, prediction, depth — a plain record tree |
| `SplitFinder` | bestSplit(rows, features) returning a Split with gain |
| `RandomForest` | fit/predict/predictProba, plus oobError() and treeCorrelation() |
| `FeatureImportance` | permutationImportance(model, X, y, repeats) |

---

## 3.1 Best-threshold search with running sums

Sort once per (node, feature), then scan candidate splits maintaining left/right class counts. O(n log n) per feature per node instead of O(n²).

```java
static Split bestSplit(int[][] x, int[] y, int[] candidates) {
    int n = y.length;
    double bestGain = 0; int bestF = -1; double bestT = 0;
    for (int f : candidates) {
        Integer[] idx = new Integer[n];                 // one sort per feature
        for (int i = 0; i < n; i++) idx[i] = i;
        java.util.Arrays.sort(idx, (a, b) -> Double.compare(x[a][f], x[b][f]));
        int totalPos = 0;
        for (int i = 0; i < n; i++) totalPos += y[i];
        int leftPos = 0, leftN = 0;                      // running counts
        for (int k = 0; k < n - 1; k++) {
            int i = idx[k];
            leftPos += y[i]; leftN++;
            if (x[i][f] == x[idx[k + 1]][f]) continue;   // keep distinct thresholds
            double t = (x[i][f] + x[idx[k + 1]][f]) / 2.0;
            int rightN = n - leftN, rightPos = totalPos - leftPos;
            double gain = giniImpurity(leftPos, leftN) * (leftN / (double) n)
                        + giniImpurity(rightPos, rightN) * (rightN / (double) n);
            gain = 1 - gain;                             // impurity drop, not increase
            if (gain > bestGain) { bestGain = gain; bestF = f; bestT = t; }
        }
    }
    return bestF < 0 ? null : new Split(bestF, bestT, bestGain);
}
```


---

## 3.2 Bagging with deterministic per-tree seeds and OOB scoring

One seed per tree keeps the forest reproducible while guaranteeing independent bootstrap samples. OOB errors are accumulated during the same pass, so validation costs nothing extra.

```java
public void fit(int[][] x, int[] y, int nTrees) {
    int n = y.length, p = x[0].length, mtry = (int) Math.round(Math.sqrt(p));
    long baseSeed = 0x9E3779B97F4A7C15L;               // golden ratio, arbitrary but fixed
    for (int t = 0; t < nTrees; t++) {
        SplittableRandom rnd = new SplittableRandom(baseSeed + t);  // independent per tree
        int[] bag = new int[n];
        boolean[] inBag = new boolean[n];
        for (int i = 0; i < n; i++) { bag[i] = rnd.nextInt(n); inBag[bag[i]] = true; }
        trees.add(growTree(x, y, bag, mtry, rnd));
        for (int i = 0; i < n; i++)                       // out-of-bag accumulation
            if (!inBag[i]) oobCorrect[i] += trees.get(t).predict(x[i]) == y[i] ? 1 : 0;
        oobCounts[i0(n)]++;                                // per-row OOB tree count
    }
}

public double oobError() {
    double err = 0; int seen = 0;
    for (int i = 0; i < oobCounts.length; i++)
        if (oobCounts[i] > 0) { err += 1.0 - oobCorrect[i] / (double) oobCounts[i]; seen++; }
    return err / seen;
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| One split search over all features | `O(np log n)` | sorting dominates; restrict to mtry features in a forest |
| Building one tree | `O(n log n · features · depth)` | shallow trees dominate with max_depth 4–8 |
| Prediction | `O(depth)` | no matrix multiply, no scaling needed |
| Full forest prediction | `O(B · depth)` | parallelise across trees; it is embarrassingly parallel |

## 5. Correctness and Numerics

- Guard log(0) in entropy when a node has no positive examples.
- Compare gains with a small epsilon so ties do not produce split thrash.
- Use `Math.sqrt(p)` for mtry and expose it; it is a real hyperparameter.
- Compare tree importances only after permutation importance, with repeats >= 30 for error bars.

## 6. Test Strategy

- Pure-label node returns a single-class leaf and no split is proposed.
- Permutation importance is ~0 for a random noise feature.
- A forest with nTrees = 1 equals a single tree's prediction exactly.
- OOB tree counts average to about 0.368 · nTrees per row for large n.
- Trees are invariant to feature scaling (assert identical predictions after scaling).
- Run twice with the same seed and assert identical predictions.

## 7. Extension Points

- Implement Extra-Trees (random thresholds as well as random features) and measure the speed/accuracy trade.
- Add cost-complexity pruning with a validation-set alpha and plot the pruning curve.
- Compute pairwise tree correlation and show it falls as mtry grows.

## 8. Review Checklist

- [ ] Per-tree seeds, not one shared Random
- [ ] Thresholds precomputed once per node
- [ ] Depth, leaf size and mtry are constructor arguments
- [ ] Importance reported by permutation, with repeats
- [ ] OOB error printed in every example run
- [ ] Categorical encodings documented in the class JavaDoc
