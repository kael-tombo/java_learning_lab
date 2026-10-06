# K-Nearest Neighbors - Mathematical Foundations

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

## Notation

| Symbol | Meaning |
|---|---|
| `d_p(x,z) = (Σ|xᵢ − zᵢ|ᵖ)^(1/p)` | Minkowski distance - p=1 Manhattan, p=2 Euclidean |
| `d(x,z) = √Σ(xᵢ−zᵢ)²` | Euclidean distance - default; penalises large single-axis gaps |
| `wᵢ = 1/d(xᵢ,x)` | Inverse-distance weight - nearer neighbours dominate the vote |
| `ŷ(x) = argmax_c Σ_{i in kNN} wᵢ · 1[yᵢ = c]` | KNN prediction - weighted class vote |
| `d_bias ∝ 1/k` | Bias decreases with k - smoother boundary as k grows |
| `Var ∝ 1/k² (naively)` | Variance decreases with k - the opposite force, hence a U-shaped curve |

## Why the Math Matters

KNN is the lab where geometry becomes a complexity question. The same distance function that makes the method intuitive also creates the curse of dimensionality and the O(n) query cost — both are consequences of having no model at all.


---

## 1. Distance metrics and their geometry

```text
L1: d1 = sum |xi - zi|
L2: d2 = sqrt(sum (xi - zi)^2)
Lp: dp = (sum |xi - zi|^p)^(1/p)
```

L2 squares before summing, so one large axis difference dominates. L1 sums before powering, so many small differences add up. That single choice decides whether high-dimensional sparse data looks close or far.

**Worked example.** x = (1, 0), z = (0, 10): d2 = sqrt(1+100) = 10.05 (one axis dominates); d1 = 1 + 10 = 11. For 20 features each differing by 1: d2 = sqrt(20) = 4.47, d1 = 20 (many small gaps accumulate).


---

## 2. Weighted vote versus counting

```text
majority:  yhat = argmax_c #{i in kNN : yi = c}
weighted: yhat = argmax_c sum_i (1/d_i) 1[yi = c]
```

Counting treats a neighbour at d=1 the same as one at d=1000. Weighting restores locality, at the cost of one outlier dominating a region.

**Worked example.** k = 3: labels A(0.9), B(1.1), B(1.2). Majority gives B. Weighted gives A with 1.111 vs B's 0.909 + 0.833 = 1.742, so B still wins — but if A is at d = 0.1, A wins 10 to 1.74.


---

## 3. Distance concentration

```text
for uniform points in [0,1]^d: E[d] ~ d/2, Var[d] ~ (1/12) d(d+2)
relative std dev ~ sqrt(12/(d+2)) / sqrt(d)
c1 = (dmax - dmin)/dmean -> 1 as d grows
```

Absolute distances grow with d while their spread shrinks proportionally. The ratio between the nearest and farthest neighbour stops depending on the point, which is exactly what kills k-NN in high dimensions.

**Worked example.** d = 10: relative spread ~ 30%; d = 100: ~9%; d = 1000: ~3%. Neighbour ratios move from meaningful to indistinguishable as dimension climbs.


---

## 4. Cost of the search

```text
brute force: O(n d) per query, O(n d) to sort, or O(n log k) with a heap
precompute distance matrix: O(n^2 d) once, O(n) per query
KD-tree: ~O(log n) average, degrades to O(n) as d grows
```

The full-scan cost is per query, so total cost is O(q n d) for q queries. Precomputing the matrix moves work to a one-off O(n²d) and is only worth it for small n with many repeated queries.

**Worked example.** n = 10,000, d = 20, q = 1,000: brute force = 200M operations per query batch. With a precomputed matrix, each query is a 10,000-element partial sort — three orders of magnitude cheaper.


---

## 5. Bias-variance in k

```text
prediction variance ~ roughly 1/k near the neighbourhood
bias ~ grows like the local curvature, roughly as k grows
total loss = bias + variance has a U-shape in k
```

Neither extreme is right: k = 1 memorises, k = n predicts the majority class. The optimum is where the two curves cross, which is why sweeping k is mandatory rather than optional.

**Worked example.** On 2D Gaussian blobs with 5% label noise: k = 1 gives 88% (high variance), k = 15 gives 93%, k = 200 gives 82% (swamped). The plateau is broad: k from 10 to 30 all score 93%.


---

## 6. Scaling and the effective condition number

```text
after scaling each feature to unit variance, the average squared distance
E||x-z||^2 = sum_j Var_j (unscaled) vs 2p (scaled)
ratio unscaled/scaled = (sum_j Var_j) / (2p)
```

If one feature has variance 100× the rest, it contributes 100× more to every distance, so neighbour selection is effectively decided by that feature alone.

**Worked example.** p = 5, one feature with variance 100 and four with variance 1: the dominant feature is 100/104 = 96% of the squared distance. Neighbours are chosen almost entirely by it.


---

## Cheat Sheet

- `d_p(x,z) = (Σ|xᵢ − zᵢ|ᵖ)^(1/p)` - Minkowski distance
- `d(x,z) = √Σ(xᵢ−zᵢ)²` - Euclidean distance
- `wᵢ = 1/d(xᵢ,x)` - Inverse-distance weight
- `ŷ(x) = argmax_c Σ_{i in kNN} wᵢ · 1[yᵢ = c]` - KNN prediction
- `d_bias ∝ 1/k` - Bias decreases with k
- `Var ∝ 1/k² (naively)` - Variance decreases with k

## Numerical Traps

- Comparing distances without checking for zero (duplicate rows) before taking 1/d.
- Using squared distance with distance weighting — consistent, but note that k(x) is then weighted by 1/d², not 1/d.
- Interpreting a k-fold argmax of one decimal place of accuracy as a real difference.
- Assuming a KD-tree keeps its logarithmic behaviour in 30 dimensions — it does not.
- Reporting accuracy for a nearest-neighbour method that has no generalisation story without a held-out set.

## Self-Check Problems

1. Compute d1, d2 and d∞ for the pairs (1,0)/(0,10) and (1,1,1)/(2,2,2).
2. For neighbours at distances 0.5, 1, 2 and 4, compare majority vote and 1/d weighting.
3. Generate uniform random points and measure the nearest-to-farthest distance ratio for d = 2, 10, 100, 1000.
4. Show that with p features of unit variance, E||x-z||² = 2p; derive it from the variance sum.
5. Time brute-force KNN for n = 10⁴ and n = 10⁵ and explain what changes when you add an index.
