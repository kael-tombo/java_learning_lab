# K-Means & Hierarchical Clustering - Code Deep Dive

**Track:** ml  |  **Lab:** lab07  |  **Level:** Intermediate

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
src/com/ml/lab07/
  Main.java                driver: 3 blobs + a crescent, k sweep
  KMeans.java              k-means++ seeding, Lloyd iterations, predict, inertia
  Agglomerative.java       single/average/complete/Ward linkage, dendrogram merge list
  Dendrogram.java          merge records with heights, cut(tree, k)
  ClusterEvaluator.java    inertia curve, silhouette, size distribution
```

KMeans caches the full centroid-by-point distance matrix once per iteration; recomputing inside the assignment loop is the usual 10x slowdown people hit before optimising anything else.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `KMeans` | fit with k-means++ and restarts; exposes inertia() and predict() |
| `Agglomerative` | linkage strategy, merge list, cut(nClusters) |
| `Dendrogram` | ordered merge records with heights, printable as text |
| `ClusterEvaluator` | inertia curve, mean silhouette, cluster size report |

---

## 3.1 k-means++ seeding and Lloyd iteration with an inertia cache

Seeding samples centroids proportional to squared distance; the loop caches centroid distances so assignment is a matrix scan.

```java
public double fit(double[][] x, int k, int restarts) {
    double best = Double.POSITIVE_INFINITY;
    for (int r = 0; r < restarts; r++) {
        double[][] centroids = kMeansPlusPlusInit(x, k, seed + r);   // independent seeding
        for (int iter = 0; iter < maxIter; iter++) {
            double[][] d = assign(x, centroids);                      // one full cache
            double inertia = 0;
            int[] counts = new int[k];
            double[][] sums = new double[k][x[0].length];
            for (int i = 0; i < x.length; i++) {
                int c = nearest(d[i]);
                inertia += d[i][c];
                counts[c]++;
                for (int j = 0; j < x[0].length; j++) sums[c][j] += x[i][j];
            }
            for (int c = 0; c < k; c++)                          // update step
                if (counts[c] > 0) for (int j = 0; j < sums[c].length; j++)
                    centroids[c][j] = sums[c][j] / counts[c];
            if (iter > 0 && Math.abs(inertia - prevInertia) < 1e-9) break;
            prevInertia = inertia;
        }
        if (inertia < best) { best = inertia; bestCentroids = centroids; }
    }
    return best;                                                 // best of restarts
}
```


---

## 3.2 Ward merge selection with a priority queue

Merge costs are recomputed only for the clusters touched by the previous merge; the heap holds the rest. That turns O(n³) into roughly O(n² log n).

```java
public List<Merge> ward(double[][] x) {
    int n = x.length;
    int[] parent = new int[n];
    double[] size = new double[n];
    double[][] sum = new double[n][];
    for (int i = 0; i < n; i++) { parent[i] = i; size[i] = 1; sum[i] = x[i].clone(); }
    PriorityQueue<Merge> pq = new PriorityQueue<>(Merge::compareTo);
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++) pq.add(new Merge(i, j, wardCost(i, j)));
    List<Merge> merges = new ArrayList<>();
    while (pq.size() > 1 && merges.size() < n - 1) {
        Merge m = pq.poll();
        if (parent[m.a] != m.a || parent[m.b] != m.b) continue;  // stale heap entry
        merges.add(new Merge(rootOf(m.a), rootOf(m.b), m.height));
        int r = union(rootOf(m.a), rootOf(m.b));                  // size-weighted sums
        for (int j = 0; j < n; j++)
            if (parent[j] == j && j != r) pq.add(new Merge(j, r, wardCost(j, r)));
    }
    return merges;
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| k-means iteration | `O(n k d)` | cache centroid distances to avoid recomputation |
| k-means++ seeding | `O(n k d)` | one pass per new centroid, negligible in total |
| Agglomerative with a heap | `O(n² log n) time, O(n²) memory` | memory is the real limit |
| Silhouette computation | `O(n²)` | can be approximated by sampling 1,000 points |

## 5. Correctness and Numerics

- Standardise before clustering; assert stability after scaling in a test.
- Seed k-means++ and run at least 5 restarts, reporting the best inertia.
- Stop on inertia change below tolerance, not on a fixed iteration count.
- Print the cluster size distribution alongside any silhouette score.
- Use `Math.fma` in the distance loop where available; the accumulation is long.

## 6. Test Strategy

- Well-separated 3-blob data with k = 3 recovers the true labels up to permutation.
- k-means++ with 5 restarts never returns worse inertia than a single random seed on average.
- Single linkage chains through an intermediate point; Ward does not.
- Scaling every feature by 1000 leaves the cluster assignment unchanged.
- Silhouette of a perfectly separated synthetic set exceeds 0.8.
- Two runs with the same seed produce identical labels.

## 7. Extension Points

- Implement DBSCAN for irregular shapes and compare against k-means on a crescent dataset.
- Add a stability test: bootstrap the data, recluster, and report the adjusted Rand index across runs.
- Implement Gaussian mixtures with EM and show it beats k-means on unequal-variance clusters.

## 8. Review Checklist

- [ ] Scaling happens inside the estimator
- [ ] k-means++ seeding with an explicit seed and multiple restarts
- [ ] Convergence on inertia change, logged per iteration
- [ ] Cluster size distribution printed with every score
- [ ] Agglomerative respects the O(n²) memory limit, enforced by an n guard
- [ ] Clusters are validated against an external outcome before being named
