# K-Means & Hierarchical Clustering - Flashcards (60 cards)

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

**Format.** Question (front) -> answer (back). Use for spaced repetition: day 0, day 1, day 3, day 7, day 21. Do not read the answer first.

| # | Front | Back |
|---|---|---|
| 1 | Why does inertia always decrease with k? | More clusters means more freedom to fit; with k = n every point is its own cluster and inertia is zero. |
| 2 | What does k-means++ fix? | Bad initialisation. Sampling centroids with probability proportional to squared distance avoids collapsing several centroids together. |
| 3 | What does the silhouette score assume? | Spherical, similarly sized clusters — the same assumption k-means makes, so it cannot diagnose that failure. |
| 4 | Single linkage's characteristic flaw? | Chaining: distant points get linked through a chain of close neighbours. |
| 5 | Why prefer Ward linkage? | Each merge minimises the increase in within-cluster variance, so the dendrogram height is a variance budget. |
| 6 | Can k-means find non-convex clusters? | No. Voronoi cells are convex, so a ring or a crescent cannot be recovered. |
| 7 | Why scale before clustering? | Distance is dominated by the largest-variance axis, so unscaled data lets one feature define the segments. |
| 8 | How do you validate clusters without labels? | Stability under resampling and initialisation, size distribution, feature profiles, and correlation with an external business outcome. |
| 9 | What is Lloyd's algorithm? | Alternate assignment (each point to its nearest centroid) and update (centroid = mean of its members). |
| 10 | What is k-means++ initialisation? | Pick the first centroid uniformly, then pick each subsequent centroid with probability proportional to its squared distance from the nearest existing centroid. |
| 11 | What is Inertia and the elbow? | Inertia (within-cluster sum of squares) always falls as k grows, so it cannot choose k on its own. |
| 12 | What is Silhouette and its limitations? | For each point, s = (b − a)/max(a, b) where a is mean intra-cluster distance and b the mean distance to the nearest other cluster. |
| 13 | What is Agglomerative clustering and linkage? | Start with n singleton clusters and repeatedly merge the closest pair. |
| 14 | What is Dendrograms and the cut? | The dendrogram records merge order and merge height. |
| 15 | In this lab, what does `Inertia = Σ_{c} Σ_{i in c} \|\|xᵢ − μ_c\|\|²` mean? | Within-cluster sum of squares: the quantity k-means minimises |
| 16 | In this lab, what does `argmin_c \|\|xᵢ − μ_c\|\|²` mean? | Assignment step: hard assignment, nearest centroid |
| 17 | In this lab, what does `μ_c = (1/\|c\|)Σ_{i in c} xᵢ` mean? | Update step: centroid as cluster mean |
| 18 | In this lab, what does `s(i) = (b(i) − a(i)) / max(a(i), b(i))` mean? | Silhouette coefficient: −1..1, higher is better |
| 19 | In this lab, what does `d(A,B) = min_{a in A,b in B} d(a,b)` mean? | Single linkage: prone to chaining |
| 20 | In this lab, what does `d(A,B) = Σ\|a\|\|b\|d(a,b)/(\|A\|\|B\|)` mean? | Average linkage: compromise between single and complete |
| 21 | In this lab, what does `ΔW(A∪B) = \|A\|\|B\|/(\|A\|+\|B\|) \|\|μ_A − μ_B\|\|²` mean? | Ward merge cost: variance added by a merge |
| 22 | You see 'One huge cluster plus k-1 tiny ones' in production. What is the cause and the fix? | initialisation or feature scale dominated by outliers Fix: standardise, use k-means++, try multiple restarts |
| 23 | You see 'Same input, different clusters each run' in production. What is the cause and the fix? | single random initialisation, unseeded Fix: seed k-means++ and report the best-of-r inertia |
| 24 | You see 'Silhouette says 0.7 and the segments are useless' in production. What is the cause and the fix? | the metric scored the shape assumption, not business usefulness Fix: validate segments against an external outcome |
| 25 | You see 'Curved clusters are shredded' in production. What is the cause and the fix? | k-means assumes spherical clusters Fix: use DBSCAN or spectral clustering, or apply PCA/whitening first |
| 26 | You see 'Agglomerative runs out of memory' in production. What is the cause and the fix? | O(n²) distance matrix at n = 50k Fix: cap n, use Ward with a priority queue, or use k-means |
| 27 | You see 'A cluster is a data-quality artefact' in production. What is the cause and the fix? | duplicates or a missing-value sentinel in one group Fix: audit cluster membership before acting on the segment |
| 28 | Which Java API is the backbone of: the heap makes agglomerative O(n² log n) instead of a full pairwise re-scan | `PriorityQueue for Ward merges` |
| 29 | Which Java API is the backbone of: finding the k nearest centroid per point | `Arrays.sort / partial selection for top-k` |
| 30 | Which Java API is the backbone of: seeded k-means++ so runs are reproducible | `SplittableRandom` |
| 31 | Which Java API is the backbone of: an inspectable cluster object | `record Cluster(int id, double[] centroid, List<Integer> members)` |
| 32 | Which Java API is the backbone of: recomputed once per iteration, reused in the assignment loop | `double[][] centroidDistances cache` |
| 33 | Why does Lloyd's algorithm matter operationally? | Alternate assignment (each point to its nearest centroid) and update (centroid = mean of its members). |
| 34 | Why does k-means++ initialisation matter operationally? | Pick the first centroid uniformly, then pick each subsequent centroid with probability proportional to its squared distance from the nearest existing centroid. |
| 35 | Why does Inertia and the elbow matter operationally? | Inertia (within-cluster sum of squares) always falls as k grows, so it cannot choose k on its own. |
| 36 | Why does Silhouette and its limitations matter operationally? | For each point, s = (b − a)/max(a, b) where a is mean intra-cluster distance and b the mean distance to the nearest other cluster. |
| 37 | Why does Agglomerative clustering and linkage matter operationally? | Start with n singleton clusters and repeatedly merge the closest pair. |
| 38 | Why does Dendrograms and the cut matter operationally? | The dendrogram records merge order and merge height. |
| 39 | In the K-Means & Hierarchical Clustering pipeline, what happens next? Scale features. Clustering is geometric, and an unscaled axi... | Scale features. Clustering is geometric, and an unscaled axis will define the clusters for you. |
| 40 | In the K-Means & Hierarchical Clustering pipeline, what happens next? Decide whether you want k-means (fast, spherical) or agglome... | Decide whether you want k-means (fast, spherical) or agglomerative (interpretable, small n). |
| 41 | In the K-Means & Hierarchical Clustering pipeline, what happens next? Run k-means with k-means++ initialisation and multiple resta... | Run k-means with k-means++ initialisation and multiple restarts; keep the lowest inertia. |
| 42 | In the K-Means & Hierarchical Clustering pipeline, what happens next? Plot inertia vs k for the elbow, and compute the mean silhou... | Plot inertia vs k for the elbow, and compute the mean silhouette for the same range. |
| 43 | In the K-Means & Hierarchical Clustering pipeline, what happens next? Inspect the actual clusters — size distribution, feature pro... | Inspect the actual clusters — size distribution, feature profiles and outliers — never just the score. |
| 44 | In the K-Means & Hierarchical Clustering pipeline, what happens next? Validate the segmentation against a business outcome; unlabe... | Validate the segmentation against a business outcome; unlabelled structure is a hypothesis until something external confirms it. |
| 45 | Exercise focus: Implement k-means from scratch | Lloyd's algorithm plus k-means++ seeding. |
| 46 | Exercise focus: Choose k with evidence | Elbow plus silhouette plus a business constraint. |
| 47 | Exercise focus: Agglomerative with four linkages | See the difference the linkage makes. |
| 48 | Exercise focus: Cut the dendrogram as a variance budget | Turn the dendrogram into a decision. |
| 49 | Exercise focus: Stability under resampling | The only real validation available without labels. |
| 50 | Exercise focus: Outlier detection from cluster geometry | Use the clustering to find rows worth inspecting. |
| 51 | State the Lloyd's algorithm as hard EM result for K-Means & Hierarchical Clustering. | Two blobs at (0,0) and (10,0) with k=2 always converge to a sensible split. The same data with k=3 splits the second blob, because inertia is lower — which is why you need more than inertia to choose k. |
| 52 | State the k-means++ seeding result for K-Means & Hierarchical Clustering. | With 3 well-separated blobs and k=3: uniform seeding fails to cover all three about 22% of the time; k-means++ essentially never fails. |
| 53 | State the Inertia as a function of k result for K-Means & Hierarchical Clustering. | Inertia 5200, 2400, 1500, 1200, 1080 for k = 1..5: the drop from 2 to 3 is large, from 4 to 5 is small. k = 3 is defensible; k = 5 is not. |
| 54 | State the Silhouette coefficient result for K-Means & Hierarchical Clustering. | Silhouette 0.71 with cluster sizes 9,900 and 100 is a warning, not a success — the score hides a singleton. Always print the size distribution with the score. |
| 55 | State the Agglomerative linkage costs result for K-Means & Hierarchical Clustering. | Two distant groups bridged by one intermediate point: single linkage merges everything into one cluster; complete and Ward keep three. |
| 56 | State the Cost of agglomerative clustering result for K-Means & Hierarchical Clustering. | n = 5,000 needs 200 MB for the matrix; n = 50,000 needs 20 GB. Ward with a heap is fine to ~20k, k-means has no such ceiling. |
| 57 | What is a stopping criterion for k-means? | Inertia change below a tolerance, or centroids moving less than eps. It always terminates because inertia is non-increasing. |
| 58 | Why is agglomerative O(n²) memory? | It needs pairwise distances between every pair of points (or every pair of clusters), unlike k-means. |
| 59 | When should you prefer DBSCAN to k-means? | Irregular cluster shapes, unknown k, and a genuine interest in noise points as outliers. |
| 60 | What does a very uneven cluster size distribution suggest? | Either real heterogeneity, or a scaling/init problem worth checking before naming segments. |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
