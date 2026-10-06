# K-Nearest Neighbors - Vision & Where This Is Going

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

## 1. The Future State

KNN survives as the baseline that exposes whether a fancy model is actually learning. Approximate nearest-neighbour indexes (HNSW, IVF) and learned metric learning extend it to embeddings and retrieval, which is where most production KNN now lives.

The test of that future state is boring: a new engineer ships a change to k-nearest neighbors on day two without asking anyone where the magic lives.

## 2. What "Good" Looks Like in Practice

- Every KNN score is reported with k, the metric, the weighting and the scaling in the same table.
- Distance concentration is measured, not assumed, when p is large.
- Prediction latency has a budget and an index behind it.
- A parametric baseline sits next to it so 'KNN won' means something.

## 3. Capability Ladder

| Level | Capability | You can... |
|---|---|---|
| L1 | Classify | Implement euclidean KNN, pick k = 5, report accuracy. |
| L2 | Tune honestly | Cross-validate k and the metric, plot the curve, defend the choice. |
| L3 | Make it fast | Add a bounded heap and an index; measure latency versus accuracy. |
| L4 | Know when to stop | Measure distance concentration and switch to a parametric or embedding-based method. |

## 4. Behaviours to Build

Baseline first, complexity second. Measure the query cost as carefully as the metric. When the neighbourhood stops meaning anything, say so with numbers.

## 5. Anti-Vision (the failure mode we are avoiding)

- Reporting KNN accuracy without the k or the metric it used.
- Leaving unscaled features in a distance-based model.
- Assuming a KD-tree is fast regardless of dimension.
- Choosing k from a single train/validation split.

## 6. Technology Shifts That Change the Work

1. Approximate nearest-neighbour indexes (HNSW, IVF-PQ) enabling vector search at billions of scale.
1. Learned metric and embedding spaces making distance meaningful where raw features are not.
1. Graph-based ANN systems powering retrieval-augmented generation.
1. Hybrid sparse-dense retrieval that blends lexical and vector scores.

## 7. Your 30/60/90 Commitment

- **30 days.** Implement the three metrics and a full-sort neighbour finder, verified against hand calculations.
- **60 days.** Add the bounded heap and prove it matches the sort; benchmark both.
- **90 days.** Run a repeated k sweep, measure distance concentration on a high-p dataset, and publish the trade-off table.

## 8. How To Tell You Are Actually Getting Better

- I can state k, metric, weighting and scaling in one sentence for any KNN number I quote.
- I can measure rather than guess the dimensionality cliff for a dataset.
- I can put a latency number next to an accuracy number.
- I know when not to use KNN and can name the replacement.

## 9. Principles That Should Not Change

- **Implement Euclidean, Manhattan** Implement Euclidean, Manhattan and Minkowski distances and know when each is appropriate
- **Find the k nearest neighbours with a sorted full scan** Find the k nearest neighbours with a sorted full scan and with a bounded max-heap
- **Aggregate by majority vote** Aggregate by majority vote and by distance weighting, and explain the difference

> KNN is the model that teaches you what the other models are buying: assumptions in exchange for speed and structure.
