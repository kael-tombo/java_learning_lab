# K-Nearest Neighbors

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

## 1. The Problem This Solves

You have no model to train and no distributional assumption you trust. All you can say is that similar things have similar outcomes.

KNN is the cheapest credible baseline and the clearest demonstration of the curse of dimensionality — it is the algorithm that makes scaling and feature selection non-optional.

## 2. Learning Objectives

- Implement Euclidean, Manhattan and Minkowski distances and know when each is appropriate
- Find the k nearest neighbours with a sorted full scan and with a bounded max-heap
- Aggregate by majority vote and by distance weighting, and explain the difference
- Select k by cross-validation and explain the bias-variance direction of the trade-off
- Demonstrate the curse of dimensionality quantitatively
- Decide when KNN is inappropriate and say what to use instead

## 3. Core Concepts

### 3.1 Instance-based learning

KNN keeps the whole training set and defers all work to prediction time. There is no training phase to speak of — only an indexing one. That is its attraction (trivial to get right, no assumptions) and its production cost (latency grows with n and with the query rate).

### 3.2 Distance metrics

Euclidean favours large single-axis differences; Manhattan accumulates small ones along many axes and suits sparse high-dimensional text. Minkowski interpolates via p: p=1 Manhattan, p=2 Euclidean, p→∞ Chebyshev. In high dimensions all distances concentrate — see below.

### 3.3 Choosing k and the bias-variance trade

k = 1 gives a jagged, high-variance boundary that memorises noise; k = n gives a constant predictor. Cross-validation picks k, and the useful range is usually surprisingly narrow. With noisy labels, small k is actively harmful because a mislabelled neighbour votes.

### 3.4 Distance weighting

Instead of counting votes, weight each by 1/d (or 1/d²). This makes the nearest neighbour dominant, effectively interpolating. It also makes predictions sensitive to a single outlier point, which is a real risk.

### 3.5 The curse of dimensionality

In high dimensions the ratio max(d)/min(d) of distances concentrates near 1. For d = 100 uniformly random points, the 1st and 100th neighbour distances differ by only tens of percent — 'nearest' stops being informative. Dimension reduction or feature selection is mandatory, not optional.

### 3.6 Scaling, missing values and duplicates

KNN is a geometric method, so units are part of the model: a salary in cents outweighs every other feature. Missing values need an explicit imputation strategy *and* a distance that ignores the imputed dimension, or you are rewarding rows for being incomplete.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `d_p(x,z) = (Σ|xᵢ − zᵢ|ᵖ)^(1/p)` | Minkowski distance | p=1 Manhattan, p=2 Euclidean |
| `d(x,z) = √Σ(xᵢ−zᵢ)²` | Euclidean distance | default; penalises large single-axis gaps |
| `wᵢ = 1/d(xᵢ,x)` | Inverse-distance weight | nearer neighbours dominate the vote |
| `ŷ(x) = argmax_c Σ_{i in kNN} wᵢ · 1[yᵢ = c]` | KNN prediction | weighted class vote |
| `d_bias ∝ 1/k` | Bias decreases with k | smoother boundary as k grows |
| `Var ∝ 1/k² (naively)` | Variance decreases with k | the opposite force, hence a U-shaped curve |

## 5. How the Pieces Fit Together

1. Split, then scale using statistics from the training fold only.

2. Choose a distance metric and justify it for the data's shape and sparsity.

3. Reduce dimension or select features if p > ~20; record the decision.

4. Sweep k and the weighting scheme on validation folds — plot the whole curve, not the argmax.

5. At prediction time, find the k neighbours, vote, and return the winning class plus the vote fraction.

6. Set a latency budget: if the query rate is high, add an index (KD-tree, ball tree) and measure the effect.

## 6. Assumptions and Invariants

- Features are scaled and of comparable units, or the metric is dominated by one axis
- Locally constant density: nearby points share a label
- No informative signal was lost by removing features
- Independent, non-adversarial data — poison points can flip predictions
- The query rate allows O(n·d) search, or an index is in place
- Labels are locally consistent; otherwise small k amplifies label noise

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| Accuracy craters when one feature changes units | unscaled features dominate every distance | standardise inside the estimator and test scaling invariance |
| Predictions flip when a duplicate row is added | 1/d weighting with d = 0 | guard zero distance and define the tie rule explicitly |
| k = 1 chosen because it validated best by 0.2% | validation noise at a single fold | use repeated CV and prefer the plateau, not the peak |
| Performance collapses above p = 50 | curse of dimensionality, distances concentrate | apply PCA or supervised feature selection first |
| Prediction takes 400 ms | full scan per query with no index | cache, batch, or index with a KD-tree/ball tree and measure |
| Bad predictions on rows with nulls | imputed zeros make incomplete rows look similar | impute with a real strategy and mask the dimension in the distance |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `PriorityQueue<Neighbour>` | a bounded max-heap keeps the k nearest in O(n log k) instead of sorting n |
| `Arrays.sort on primitive distances` | the simple reference path, useful as a correctness oracle |
| `IntStream / double[] for squared distance` | avoids allocation in the hot inner loop |
| `SplittableRandom` | reproducible bootstrap-style sampling for k-fold |
| `record Neighbour(int index, double distance)` | immutable pair that sorts and heapifies cleanly |

## 9. Where This Sits in the Larger System

- **Lab 08** (PCA) is the standard answer to the curse of dimensionality.
- **Lab 04** (SVM) shares the margin intuition but trains a parametric model instead of memorising.
- **Lab 10** supplies the cross-validation protocol you need to choose k honestly.
- **Lab 07** (K-Means) is the unsupervised relative: neighbours for labels, centroids for structure.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Implement Euclidean, Manhattan and Minkowski distances and know when each is appropriate
- [ ] 0 — cannot yet — Find the k nearest neighbours with a sorted full scan and with a bounded max-heap
- [ ] 0 — cannot yet — Aggregate by majority vote and by distance weighting, and explain the difference
- [ ] 0 — cannot yet — Select k by cross-validation and explain the bias-variance direction of the trade-off
- [ ] 0 — cannot yet — Demonstrate the curse of dimensionality quantitatively
- [ ] 0 — cannot yet — Decide when KNN is inappropriate and say what to use instead

## 11. Summary Checklist

- [ ] I can explain why scaling is not optional here
- [ ] I can show distance concentration numerically in high dimensions
- [ ] I choose k from a curve, not a single number
- [ ] I know when distance weighting helps and when it adds fragility
- [ ] I can state the prediction-time cost and how to reduce it
- [ ] I can name three cases where KNN is the wrong tool
