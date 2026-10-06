# K-Means & Hierarchical Clustering - Vision & Where This Is Going

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

## 1. The Future State

Clustering fragments into three live uses: unsupervised exploration, outlier and novelty detection, and embedding-space segmentation for retrieval systems. The centre of gravity is away from 'find k clusters' toward density-aware and embedding-based methods that admit non-convex structure.

The test of that future state is boring: a new engineer ships a change to k-means & hierarchical clustering on day two without asking anyone where the magic lives.

## 2. What "Good" Looks Like in Practice

- k is chosen with a written reason combining an internal metric and a business constraint.
- Cluster size distributions and stability are reported with every segmentation.
- Features are scaled inside the pipeline and the decision is recorded.
- Clusters are treated as hypotheses until an external outcome validates them.

## 3. Capability Ladder

| Level | Capability | You can... |
|---|---|---|
| L1 | Segment | Run k-means, print inertia and sizes, describe the clusters. |
| L2 | Choose k honestly | Elbow plus silhouette plus sizes, with the reasoning written down. |
| L3 | Test stability | Resample, recluster, report adjusted Rand index across runs. |
| L4 | Operate it | Track population drift, flag outlier rows, and version the segmentation. |

## 4. Behaviours to Build

Print the sizes before the score. Treat k-means as a first pass, not a verdict. Validate against something outside the data before anyone builds a campaign on your segments.

## 5. Anti-Vision (the failure mode we are avoiding)

- Naming clusters from a two-line k-means run and shipping a campaign.
- Clustering unscaled features and calling the result a customer taxonomy.
- Reporting a silhouette without the size distribution.
- Using clusters as pseudo-labels and then 'validating' with a model trained on them.

## 6. Technology Shifts That Change the Work

1. Density-based methods (HDBSCAN, UMAP-based density) for irregular shapes and noise.
1. Embedding-space clustering where a neural encoder supplies the geometry.
1. Concept drift in segmentation becoming a first-class monitoring signal.
1. Cluster-based sampling for active labelling and rare-case discovery.

## 7. Your 30/60/90 Commitment

- **30 days.** Implement k-means with k-means++ and multiple restarts; verify on 3 blobs.
- **60 days.** Implement all four linkages and produce dendrograms you can read.
- **90 days.** Build a stability harness with adjusted Rand index and serve a segment endpoint with drift tracking.

## 8. How To Tell You Are Actually Getting Better

- I can state my k choice and defend it in writing.
- I always print cluster sizes next to a quality score.
- I can measure stability across resamples.
- I know which algorithm to switch to when k-means fails.

## 9. Principles That Should Not Change

- **Implement k-means++ initialisation** Implement k-means++ initialisation and Lloyd iterations to convergence
- **Explain inertia, the elbow method** Explain inertia, the elbow method and the silhouette score, and their limits
- **Implement agglomerative clustering with single, average, complete** Implement agglomerative clustering with single, average, complete and Ward linkage

> Clustering produces the questions; only validation produces the decisions.
