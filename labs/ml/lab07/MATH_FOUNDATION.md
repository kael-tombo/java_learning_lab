# K-Means & Hierarchical Clustering - Mathematical Foundations

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

## Notation

| Symbol | Meaning |
|---|---|
| `Inertia = Σ_{c} Σ_{i in c} ||xᵢ − μ_c||²` | Within-cluster sum of squares - the quantity k-means minimises |
| `argmin_c ||xᵢ − μ_c||²` | Assignment step - hard assignment, nearest centroid |
| `μ_c = (1/|c|)Σ_{i in c} xᵢ` | Update step - centroid as cluster mean |
| `s(i) = (b(i) − a(i)) / max(a(i), b(i))` | Silhouette coefficient - −1..1, higher is better |
| `d(A,B) = min_{a in A,b in B} d(a,b)` | Single linkage - prone to chaining |
| `d(A,B) = Σ|a||b|d(a,b)/(|A||B|)` | Average linkage - compromise between single and complete |
| `ΔW(A∪B) = |A||B|/(|A|+|B|) ||μ_A − μ_B||²` | Ward merge cost - variance added by a merge |

## Why the Math Matters

k-means is EM for equal-covariance spherical Gaussians with hard responsibilities. Once you see that, the monotonic decrease of inertia, the local-optimum problem and the spherical assumption all become one argument instead of three facts.


---

## 1. Lloyd's algorithm as hard EM

```text
E-step: z_ic = 1[argmin_k ||x_i - mu_k||^2]
M-step: mu_k = (1/n_k) sum_i z_ic x_i
J = sum_i ||x_i - z_i||^2 decreases monotonically
```

Each iteration assigns points to their nearest centroid, then recomputes centroids. Because hard assignment means no responsibility smoothing, the objective can only fall, so termination is guaranteed — to a local optimum.

**Worked example.** Two blobs at (0,0) and (10,0) with k=2 always converge to a sensible split. The same data with k=3 splits the second blob, because inertia is lower — which is why you need more than inertia to choose k.


---

## 2. k-means++ seeding

```text
pick c1 uniformly
P(ci) proportional to min_j ||x - c_j||^2
E[clusters covered] rises, bad optima become exponentially unlikely
```

The guarantee is on the quality of the objective achieved in one run, compared with the O(log k) restarts k-means++ makes unnecessary in practice.

**Worked example.** With 3 well-separated blobs and k=3: uniform seeding fails to cover all three about 22% of the time; k-means++ essentially never fails.


---

## 3. Inertia as a function of k

```text
Inertia(k) is non-increasing; Inertia(n) = 0
knee heuristic: argmax_k [Inertia(k) - Inertia(k+1)] / (k+1)
or the 'elbow' by visual curvature
```

There is no statistical test here — the elbow is a judgement. Report the curve, name the chosen k, and give the business reason.

**Worked example.** Inertia 5200, 2400, 1500, 1200, 1080 for k = 1..5: the drop from 2 to 3 is large, from 4 to 5 is small. k = 3 is defensible; k = 5 is not.


---

## 4. Silhouette coefficient

```text
a(i) = mean distance from i to others in its cluster
b(i) = min over other clusters c of mean distance to c
s(i) = (b - a) / max(a, b),  in [-1, 1]
```

s near 1 means compact and well separated; near 0 means on the boundary; negative means misassigned. Averaging over points gives the reported score.

**Worked example.** Silhouette 0.71 with cluster sizes 9,900 and 100 is a warning, not a success — the score hides a singleton. Always print the size distribution with the score.


---

## 5. Agglomerative linkage costs

```text
single:    min pair distance      -> chains, can produce long thin clusters
complete:  max pair distance      -> compact, biased to equal sizes
average:   mean pair distance     -> compromise
Ward:       |A||B|/(|A|+|B|) ||mu_A - mu_B||^2
```

Each linkage encodes a different notion of similarity. Ward is preferred because its merge cost is interpretable as variance added, matching k-means' objective.

**Worked example.** Two distant groups bridged by one intermediate point: single linkage merges everything into one cluster; complete and Ward keep three.


---

## 6. Cost of agglomerative clustering

```text
distance matrix: n^2 doubles = 8n^2 bytes
naive implementation: O(n^3)
with a priority queue on Ward costs: O(n^2 log n)
rule of thumb: n < 10,000
```

Memory is the binding constraint, exactly like kernel SVMs. For larger n, sample, use k-means, or use a sparse-tree approximation.

**Worked example.** n = 5,000 needs 200 MB for the matrix; n = 50,000 needs 20 GB. Ward with a heap is fine to ~20k, k-means has no such ceiling.


---

## Cheat Sheet

- `Inertia = Σ_{c} Σ_{i in c} ||xᵢ − μ_c||²` - Within-cluster sum of squares
- `argmin_c ||xᵢ − μ_c||²` - Assignment step
- `μ_c = (1/|c|)Σ_{i in c} xᵢ` - Update step
- `s(i) = (b(i) − a(i)) / max(a(i), b(i))` - Silhouette coefficient
- `d(A,B) = min_{a in A,b in B} d(a,b)` - Single linkage
- `d(A,B) = Σ|a||b|d(a,b)/(|A||B|)` - Average linkage
- `ΔW(A∪B) = |A||B|/(|A|+|B|) ||μ_A − μ_B||²` - Ward merge cost

## Numerical Traps

- Reading the elbow as an objective criterion rather than a judgement call.
- Averaging the silhouette over clusters instead of over points, which lets a huge cluster dominate.
- Forgetting to standardise and then blaming the algorithm.
- Cutting the dendrogram at an arbitrary height and calling the segments 'natural'.
- Computing the Ward merge cost on raw scales where variance is not comparable.

## Self-Check Problems

1. Run Lloyd's algorithm by hand on 6 two-dimensional points with k=2, starting from given centroids.
2. Show inertia(k) is non-increasing by proving that the optimal k-cluster solution has inertia at most that of the optimal (k+1)-cluster solution.
3. Compute the silhouette for a point with a = 1.0 and b = 4.0, and again with a = 4.0 and b = 1.0.
4. Apply Ward's cost formula to merge clusters of size 3 (mean (0,0)) and size 5 (mean (2,0)).
5. Compute memory for agglomerative at n = 2,000, 10,000 and 50,000, and state the crossover to k-means.
