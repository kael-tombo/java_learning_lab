# K-Means & Hierarchical Clustering

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

## 1. The Problem This Solves

Nobody labelled your data, but you still need structure: segments, outliers, or a lower-dimensional view of the space.

Clustering is unsupervised, so every conclusion is a hypothesis rather than a measurement. That constraint shapes how you evaluate, and lab10's habits do not transfer for free.

## 2. Learning Objectives

- Implement k-means++ initialisation and Lloyd iterations to convergence
- Explain inertia, the elbow method and the silhouette score, and their limits
- Implement agglomerative clustering with single, average, complete and Ward linkage
- Read a dendrogram and decide where to cut it
- Explain why k-means assumes spherical, similarly sized clusters
- Detect outliers from cluster distance and decide what to do about them

## 3. Core Concepts

### 3.1 Lloyd's algorithm

Alternate assignment (each point to its nearest centroid) and update (centroid = mean of its members). This is EM with equal-variance spherical Gaussians and hard assignments. It monotonically decreases inertia, so it converges — but only to a local optimum, which is why initialisation matters.

### 3.2 k-means++ initialisation

Pick the first centroid uniformly, then pick each subsequent centroid with probability proportional to its squared distance from the nearest existing centroid. This makes bad local optima exponentially less likely and costs nothing extra.

### 3.3 Inertia and the elbow

Inertia (within-cluster sum of squares) always falls as k grows, so it cannot choose k on its own. Plot inertia against k and look for the elbow — the knee past which each extra cluster buys almost nothing. It is a visual judgement, and you should say so rather than pretending it is a test.

### 3.4 Silhouette and its limitations

For each point, s = (b − a)/max(a, b) where a is mean intra-cluster distance and b the mean distance to the nearest other cluster. It ranges −1..1 and is scale-free, but it assumes roughly spherical, similarly sized clusters — exactly what k-means assumes. It cannot tell you k is wrong; it can only say the shape assumption failed.

### 3.5 Agglomerative clustering and linkage

Start with n singleton clusters and repeatedly merge the closest pair. Linkage defines 'closest': single (chaining), complete (compact), average (compromise), Ward (minimises variance increase). Ward is the one that behaves like k-means and is the usual default.

### 3.6 Dendrograms and the cut

The dendrogram records merge order and merge height. Choosing k means cutting at a height. Ward's height is interpretable as the within-cluster variance added by that merge, which makes the cut a variance budget decision rather than a guess.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `Inertia = Σ_{c} Σ_{i in c} ||xᵢ − μ_c||²` | Within-cluster sum of squares | the quantity k-means minimises |
| `argmin_c ||xᵢ − μ_c||²` | Assignment step | hard assignment, nearest centroid |
| `μ_c = (1/|c|)Σ_{i in c} xᵢ` | Update step | centroid as cluster mean |
| `s(i) = (b(i) − a(i)) / max(a(i), b(i))` | Silhouette coefficient | −1..1, higher is better |
| `d(A,B) = min_{a in A,b in B} d(a,b)` | Single linkage | prone to chaining |
| `d(A,B) = Σ|a||b|d(a,b)/(|A||B|)` | Average linkage | compromise between single and complete |
| `ΔW(A∪B) = |A||B|/(|A|+|B|) ||μ_A − μ_B||²` | Ward merge cost | variance added by a merge |

## 5. How the Pieces Fit Together

1. Scale features. Clustering is geometric, and an unscaled axis will define the clusters for you.

2. Decide whether you want k-means (fast, spherical) or agglomerative (interpretable, small n).

3. Run k-means with k-means++ initialisation and multiple restarts; keep the lowest inertia.

4. Plot inertia vs k for the elbow, and compute the mean silhouette for the same range.

5. Inspect the actual clusters — size distribution, feature profiles and outliers — never just the score.

6. Validate the segmentation against a business outcome; unlabelled structure is a hypothesis until something external confirms it.

## 6. Assumptions and Invariants

- Features are scaled, or the highest-variance axis dominates the geometry
- k-means: clusters are spherical and of similar size
- K is chosen with domain input, not only by an internal metric
- The data is not better served by density-based methods (DBSCAN) if shapes are irregular
- n is small enough for agglomerative's O(n²) cost and O(n²) memory, or you use Ward with n < ~10k
- Cluster identity is stable enough to name; a cluster you cannot describe is not actionable

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| One huge cluster plus k-1 tiny ones | initialisation or feature scale dominated by outliers | standardise, use k-means++, try multiple restarts |
| Same input, different clusters each run | single random initialisation, unseeded | seed k-means++ and report the best-of-r inertia |
| Silhouette says 0.7 and the segments are useless | the metric scored the shape assumption, not business usefulness | validate segments against an external outcome |
| Curved clusters are shredded | k-means assumes spherical clusters | use DBSCAN or spectral clustering, or apply PCA/whitening first |
| Agglomerative runs out of memory | O(n²) distance matrix at n = 50k | cap n, use Ward with a priority queue, or use k-means |
| A cluster is a data-quality artefact | duplicates or a missing-value sentinel in one group | audit cluster membership before acting on the segment |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `PriorityQueue for Ward merges` | the heap makes agglomerative O(n² log n) instead of a full pairwise re-scan |
| `Arrays.sort / partial selection for top-k` | finding the k nearest centroid per point |
| `SplittableRandom` | seeded k-means++ so runs are reproducible |
| `record Cluster(int id, double[] centroid, List<Integer> members)` | an inspectable cluster object |
| `double[][] centroidDistances cache` | recomputed once per iteration, reused in the assignment loop |

## 9. Where This Sits in the Larger System

- **Lab 08** (PCA) is often the right preprocessing step before clustering.
- **Lab 10**'s cross-validation does not transfer — unsupervised structure needs external validation.
- **Lab 05** (KNN) is the supervised cousin of the same distance geometry.
- **mlops/lab08** is where cluster drift becomes an operational alert.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Implement k-means++ initialisation and Lloyd iterations to convergence
- [ ] 0 — cannot yet — Explain inertia, the elbow method and the silhouette score, and their limits
- [ ] 0 — cannot yet — Implement agglomerative clustering with single, average, complete and Ward linkage
- [ ] 0 — cannot yet — Read a dendrogram and decide where to cut it
- [ ] 0 — cannot yet — Explain why k-means assumes spherical, similarly sized clusters
- [ ] 0 — cannot yet — Detect outliers from cluster distance and decide what to do about them

## 11. Summary Checklist

- [ ] I can explain inertia and why it cannot choose k alone
- [ ] I use k-means++ and report the best of several restarts
- [ ] I know when the silhouette score is lying to me
- [ ] I can state the spherical-cluster assumption and when it fails
- [ ] I choose the dendrogram cut as a variance budget, not a vibe
- [ ] I validate clusters against something outside the data
