# K-Means & Hierarchical Clustering - Quiz (15 Questions)

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

**Instructions.** Answer all 15 questions before reading the bold answer lines. Multiple choice, one best answer. Target: 12/15 before you move on to the mini project.

### Q1: Why can k-means not find crescent-shaped clusters?

A) It is too slow
B) Voronoi cells are convex
C) It requires scaling
D) It minimises a linear objective

**Answer: B** - Assignment regions are convex, so non-convex shapes cannot be recovered.

---

### Q2: What does k-means++ improve?

A) Convergence speed only
B) The probability of reaching a good local optimum
C) Memory usage
D) Cluster interpretability

**Answer: B** - Distance-weighted seeding avoids several centroids landing in the same cluster.

---

### Q3: Inertia always...

A) Increases with k
B) Decreases with k
C) Stays constant
D) Is undefined for k > n

**Answer: B** - More clusters always fit better, which is why inertia cannot select k by itself.

---

### Q4: A silhouette of 0.7 with cluster sizes 9,900 and 100 means...

A) Excellent segmentation
B) The score hides a possible singleton and needs the size distribution
C) k should be doubled
D) Features must be scaled

**Answer: B** - Report sizes alongside the average; large clusters dominate the mean.

---

### Q5: Which linkage is most prone to chaining?

A) Ward
B) Complete
C) Single
D) Average

**Answer: C** - Single linkage merges via the single closest pair, so a chain of near neighbours joins distant clusters.

---

### Q6: Why standardise before clustering?

A) It makes k-means faster
B) Otherwise the largest-variance axis defines the geometry
C) It reduces the number of clusters
D) It is required for Ward

**Answer: B** - Distance-based methods inherit the units of the features.

---

### Q7: Ward linkage minimises...

A) Maximum pairwise distance
B) The increase in within-cluster variance
C) Total pairwise distance
D) Cluster count

**Answer: B** - Its cost is |A||B|/(|A|+|B|) ||mu_A - mu_B||², the variance added by merging.

---

### Q8: What is agglomerative clustering's memory limit?

A) O(n)
B) O(n²) for the distance matrix
C) O(n log n)
D) No practical limit

**Answer: B** - All pairwise distances must be held, so 8n² bytes bounds n at a few tens of thousands.

---

### Q9: Silhouette assumes clusters are...

A) Uniformly distributed in density
B) Spherical and similarly sized
C) Linearly separable
D) Gaussian with equal covariance

**Answer: B** - It is a convexity and separation measure, so it inherits those assumptions.

---

### Q10: How do you validate clusters with no labels?

A) Trust the silhouette
B) Stability under resampling plus external outcome correlation
C) Pick the smallest k
D) Look at the inertia curve

**Answer: B** - Stability and external validation are the only honest options.

---

### Q11: Lloyd's algorithm is best described as...

A) Gradient descent
B) Hard-assignment EM
C) Newton's method
D) Genetic search

**Answer: B** - EM for spherical equal-variance Gaussians with responsibilities fixed to 0/1.

---

### Q12: What does an uneven cluster size distribution suggest?

A) A good model
B) A scaling or initialisation problem worth investigating
C) Perfect separation
D) The data is normal

**Answer: B** - One cluster absorbing almost everything usually signals a feature-scale or seeding problem.

---

### Q13: A dendrogram cut at a fixed height is...

A) Always optimal
B) A variance-budget decision under Ward linkage
C) Guaranteed stable
D) Equivalent to choosing k

**Answer: B** - Ward heights are variance increases, so the height choice is a budget.

---

### Q14: Which is the best use of clustering in a production system?

A) Replacing labelled models everywhere
B) Exploratory segmentation and outlier detection
C) Automatically creating training labels
D) Reducing model latency

**Answer: B** - Clusters are hypotheses; using them as ground truth is circular.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
