# K-Nearest Neighbors - Flashcards (60 cards)

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

**Format.** Question (front) -> answer (back). Use for spaced repetition: day 0, day 1, day 3, day 7, day 21. Do not read the answer first.

| # | Front | Back |
|---|---|---|
| 1 | Why does KNN require feature scaling? | Distance is geometric: a feature in cents contributes a squared term orders of magnitude larger than one in dollars. |
| 2 | What does k control? | Smoothness. Small k is jagged and high-variance; large k is smooth and high-bias. The validation curve is U-shaped. |
| 3 | What is the curse of dimensionality, concretely? | As dimensions grow, all pairwise distances converge to similar values, so 'nearest' stops discriminating. |
| 4 | Euclidean or Manhattan for text? | Usually Manhattan (p=1): it accumulates small per-token differences instead of squaring them into one large gap. |
| 5 | How does inverse-distance weighting change the result? | The nearest neighbour dominates; predictions approach a local interpolation and become sensitive to outliers. |
| 6 | What is KNN's main production disadvantage? | No training, all cost at prediction: latency grows linearly with n and the query rate. |
| 7 | Why is k = 1 risky with noisy labels? | A single mislabelled neighbour becomes the entire prediction for that region. |
| 8 | Does KNN need a training phase? | Only an indexing one. Everything expensive happens at query time. |
| 9 | What is Instance-based learning? | KNN keeps the whole training set and defers all work to prediction time. |
| 10 | What is Distance metrics? | Euclidean favours large single-axis differences; Manhattan accumulates small ones along many axes and suits sparse high-dimensional text. |
| 11 | What is Choosing k and the bias-variance trade? | k = 1 gives a jagged, high-variance boundary that memorises noise; k = n gives a constant predictor. |
| 12 | What is Distance weighting? | Instead of counting votes, weight each by 1/d (or 1/d²). |
| 13 | What is The curse of dimensionality? | In high dimensions the ratio max(d)/min(d) of distances concentrates near 1. |
| 14 | What is Scaling, missing values and duplicates? | KNN is a geometric method, so units are part of the model: a salary in cents outweighs every other feature. |
| 15 | In this lab, what does `d_p(x,z) = (Σ\|xᵢ − zᵢ\|ᵖ)^(1/p)` mean? | Minkowski distance: p=1 Manhattan, p=2 Euclidean |
| 16 | In this lab, what does `d(x,z) = √Σ(xᵢ−zᵢ)²` mean? | Euclidean distance: default; penalises large single-axis gaps |
| 17 | In this lab, what does `wᵢ = 1/d(xᵢ,x)` mean? | Inverse-distance weight: nearer neighbours dominate the vote |
| 18 | In this lab, what does `ŷ(x) = argmax_c Σ_{i in kNN} wᵢ · 1[yᵢ = c]` mean? | KNN prediction: weighted class vote |
| 19 | In this lab, what does `d_bias ∝ 1/k` mean? | Bias decreases with k: smoother boundary as k grows |
| 20 | In this lab, what does `Var ∝ 1/k² (naively)` mean? | Variance decreases with k: the opposite force, hence a U-shaped curve |
| 21 | You see 'Accuracy craters when one feature changes units' in production. What is the cause and the fix? | unscaled features dominate every distance Fix: standardise inside the estimator and test scaling invariance |
| 22 | You see 'Predictions flip when a duplicate row is added' in production. What is the cause and the fix? | 1/d weighting with d = 0 Fix: guard zero distance and define the tie rule explicitly |
| 23 | You see 'k = 1 chosen because it validated best by 0.2%' in production. What is the cause and the fix? | validation noise at a single fold Fix: use repeated CV and prefer the plateau, not the peak |
| 24 | You see 'Performance collapses above p = 50' in production. What is the cause and the fix? | curse of dimensionality, distances concentrate Fix: apply PCA or supervised feature selection first |
| 25 | You see 'Prediction takes 400 ms' in production. What is the cause and the fix? | full scan per query with no index Fix: cache, batch, or index with a KD-tree/ball tree and measure |
| 26 | You see 'Bad predictions on rows with nulls' in production. What is the cause and the fix? | imputed zeros make incomplete rows look similar Fix: impute with a real strategy and mask the dimension in the distance |
| 27 | Which Java API is the backbone of: a bounded max-heap keeps the k nearest in O(n log k) instead of sorting n | `PriorityQueue<Neighbour>` |
| 28 | Which Java API is the backbone of: the simple reference path, useful as a correctness oracle | `Arrays.sort on primitive distances` |
| 29 | Which Java API is the backbone of: avoids allocation in the hot inner loop | `IntStream / double[] for squared distance` |
| 30 | Which Java API is the backbone of: reproducible bootstrap-style sampling for k-fold | `SplittableRandom` |
| 31 | Which Java API is the backbone of: immutable pair that sorts and heapifies cleanly | `record Neighbour(int index, double distance)` |
| 32 | Why does Instance-based learning matter operationally? | KNN keeps the whole training set and defers all work to prediction time. |
| 33 | Why does Distance metrics matter operationally? | Euclidean favours large single-axis differences; Manhattan accumulates small ones along many axes and suits sparse high-dimensional text. |
| 34 | Why does Choosing k and the bias-variance trade matter operationally? | k = 1 gives a jagged, high-variance boundary that memorises noise; k = n gives a constant predictor. |
| 35 | Why does Distance weighting matter operationally? | Instead of counting votes, weight each by 1/d (or 1/d²). |
| 36 | Why does The curse of dimensionality matter operationally? | In high dimensions the ratio max(d)/min(d) of distances concentrates near 1. |
| 37 | Why does Scaling, missing values and duplicates matter operationally? | KNN is a geometric method, so units are part of the model: a salary in cents outweighs every other feature. |
| 38 | In the K-Nearest Neighbors pipeline, what happens next? Split, then scale using statistics from the training fold on... | Split, then scale using statistics from the training fold only. |
| 39 | In the K-Nearest Neighbors pipeline, what happens next? Choose a distance metric and justify it for the data's shape... | Choose a distance metric and justify it for the data's shape and sparsity. |
| 40 | In the K-Nearest Neighbors pipeline, what happens next? Reduce dimension or select features if p > ~20; record the d... | Reduce dimension or select features if p > ~20; record the decision. |
| 41 | In the K-Nearest Neighbors pipeline, what happens next? Sweep k and the weighting scheme on validation folds — plot ... | Sweep k and the weighting scheme on validation folds — plot the whole curve, not the argmax. |
| 42 | In the K-Nearest Neighbors pipeline, what happens next? At prediction time, find the k neighbours, vote, and return ... | At prediction time, find the k neighbours, vote, and return the winning class plus the vote fraction. |
| 43 | In the K-Nearest Neighbors pipeline, what happens next? Set a latency budget: if the query rate is high, add an inde... | Set a latency budget: if the query rate is high, add an index (KD-tree, ball tree) and measure the effect. |
| 44 | Exercise focus: Implement the three distance metrics | Get the geometry right, including the p parameterisation. |
| 45 | Exercise focus: Full scan and heap must agree | Two implementations, one answer. |
| 46 | Exercise focus: Majority versus weighted voting | See exactly what weighting changes. |
| 47 | Exercise focus: The k sweep, done honestly | Repeated cross-validation, not one split. |
| 48 | Exercise focus: Demonstrate the curse of dimensionality | Make the problem visible with your own numbers. |
| 49 | Exercise focus: Scaling invariance test | Prove the estimator handles units. |
| 50 | State the Distance metrics and their geometry result for K-Nearest Neighbors. | x = (1, 0), z = (0, 10): d2 = sqrt(1+100) = 10.05 (one axis dominates); d1 = 1 + 10 = 11. For 20 features each differing by 1: d2 = sqrt(20) = 4.47, d1 = 20 (many small gaps accumulate). |
| 51 | State the Weighted vote versus counting result for K-Nearest Neighbors. | k = 3: labels A(0.9), B(1.1), B(1.2). Majority gives B. Weighted gives A with 1.111 vs B's 0.909 + 0.833 = 1.742, so B still wins — but if A is at d = 0.1, A wins 10 to 1.74. |
| 52 | State the Distance concentration result for K-Nearest Neighbors. | d = 10: relative spread ~ 30%; d = 100: ~9%; d = 1000: ~3%. Neighbour ratios move from meaningful to indistinguishable as dimension climbs. |
| 53 | State the Cost of the search result for K-Nearest Neighbors. | n = 10,000, d = 20, q = 1,000: brute force = 200M operations per query batch. With a precomputed matrix, each query is a 10,000-element partial sort — three orders of magnitude cheaper. |
| 54 | State the Bias-variance in k result for K-Nearest Neighbors. | On 2D Gaussian blobs with 5% label noise: k = 1 gives 88% (high variance), k = 15 gives 93%, k = 200 gives 82% (swamped). The plateau is broad: k from 10 to 30 all score 93%. |
| 55 | State the Scaling and the effective condition number result for K-Nearest Neighbors. | p = 5, one feature with variance 100 and four with variance 1: the dominant feature is 100/104 = 96% of the squared distance. Neighbours are chosen almost entirely by it. |
| 56 | How do you pick k in practice? | Repeated k-fold over a range, plot the mean curve, pick inside the plateau, and report the variance of that choice. |
| 57 | What is a KD-tree and when does it fail? | A spatial index that prunes search; it degrades sharply once p exceeds about 10–20 dimensions. |
| 58 | How do you handle ties in a distance? | Define it explicitly — nearest-first with a stable index tiebreak — otherwise results depend on array order. |
| 59 | Why does KNN not extrapolate? | Predictions are votes or weighted averages of observed labels, so they stay inside the label set of nearby rows. |
| 60 | Assumption / invariant to defend: Features are scaled and of comparable units, or the metric is dominate... | Features are scaled and of comparable units, or the metric is dominated by one axis |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
