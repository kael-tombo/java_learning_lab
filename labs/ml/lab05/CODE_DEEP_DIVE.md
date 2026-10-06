# K-Nearest Neighbors - Code Deep Dive

**Track:** ml  |  **Lab:** lab05  |  **Level:** Intermediate

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
src/com/ml/lab05/
  Main.java             driver: synthetic 2D blobs, k sweep, boundary plot
  KnnClassifier.java    fit (store + scale), predict via heap, k and weighting config
  Distance.java         @FunctionalInterface + euclidean/manhattan/minkowski
  NeighbourIndex.java   bounded PriorityQueue keep-k helper
  KSweep.java           cross-validated k curve and weighting comparison
```

The bounded heap is the only interesting code. Everything else is bookkeeping, and getting the heap wrong silently returns the k farthest points — so KSweep cross-checks it against a full sort.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `KnnClassifier` | stores the scaled training matrix plus labels; predict() does the work |
| `Distance` | a functional interface so metrics are swappable and testable |
| `NeighbourIndex` | bounded max-heap keeping the k smallest distances seen |
| `KSweep` | cross-validated accuracy curve over k and weighting scheme |

---

## 3.1 Keeping the k nearest with a bounded max-heap

A max-heap of size k lets you discard anything worse than the current worst kept neighbour in O(1). Heapify once at the end to order them.

```java
static int[] kNearest(double[] q, double[][] xs, int k, Distance d) {
    // max-heap keyed on distance: the root is the *worst* kept neighbour
    PriorityQueue<Neighbour> heap =
        new PriorityQueue<>(k, Comparator.comparingDouble(Neighbour::distance));
    for (int i = 0; i < xs.length; i++) {
        double dist = d.of(q, xs[i]);
        if (heap.size() < k) {
            heap.add(new Neighbour(i, dist));
        } else if (dist < heap.peek().distance()) {
            heap.poll();                       // evict the farthest kept
            heap.add(new Neighbour(i, dist));
        }
    }
    Neighbour[] kept = heap.toArray(new Neighbour[0]);
    Arrays.sort(kept, Comparator.comparingDouble(Neighbour::distance));
    int[] out = new int[kept.length];          // nearest first
    for (int i = 0; i < kept.length; i++) out[i] = kept[i].index();
    return out;
}
```


---

## 3.2 Prediction with voting, weights and a zero-distance guard

Both aggregation modes live here. The zero-distance case is handled first and explicitly, because it is the one that produces NaN in the weighted path.

```java
public int predict(double[] raw, int k, boolean weighted) {
    double[] q = scaler.transform(raw);           // scaling lives in the estimator
    int[] idx = NeighbourIndex.kNearest(q, xs, k, distance);
    Map<Integer, Double> votes = new HashMap<>();
    for (int i : idx) {
        double d = distance.of(q, xs[i]);
        if (d < 1e-12) return labels[i];          // exact duplicate: no vote needed
        double w = weighted ? 1.0 / d : 1.0;
        votes.merge(labels[i], w, Double::sum);
    }
    return votes.entrySet().stream()
        .max(Map.Entry.comparingByValue())
        .orElseThrow()
        .getKey();
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| Brute-force neighbour search per query | `O(n d)` | the dominant per-request cost |
| Keeping the k nearest with a heap | `O(n log k)` | beats sorting when k << n |
| Sorting the training set once by each dimension | `O(n log n · d)` | enables partial-sort tricks and grid indexes |
| Prediction memory | `O(k)` | only neighbours are retained; the model is the dataset |

## 5. Correctness and Numerics

- Standardise inside the estimator; add a test that asserts identical predictions after rescaling.
- Guard d = 0 before taking 1/d, and define the duplicate rule explicitly.
- Tie-break by index so identical distances give deterministic predictions.
- Use squared distance consistently for ranking and 1/d for weighting only if you have thought it through.
- Report k, the metric and the weighting scheme next to every accuracy number.

## 6. Test Strategy

- A hand-computed 4-point dataset returns the expected neighbour indices for k = 2.
- The heap implementation agrees with a full sort on 1,000 random points.
- Scaling a feature by 1000 leaves predictions unchanged.
- Adding a duplicate of a training row does not change the prediction or produce NaN.
- k = n predicts the majority class exactly.
- Prediction is deterministic across runs and across JVM invocations.

## 7. Extension Points

- Implement a KD-tree index and measure where it stops beating brute force in p.
- Add a local outlier factor pre-filter and report the latency/metric trade.
- Use PCA to k dimensions and show the accuracy recovered on a high-p dataset.

## 8. Review Checklist

- [ ] Scaling, metric, k and weighting are all estimator state, not caller choices
- [ ] Zero distance handled before any division
- [ ] Tie-breaking is deterministic
- [ ] k chosen from a plotted curve and recorded
- [ ] A test cross-checks the heap against a reference sort
- [ ] Prediction latency measured and reported with the accuracy
