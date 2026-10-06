# MINI_PROJECT — Movie Recommendation by Nearest Neighbours

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

**Brief.** Recommend films from user ratings with KNN over users and over items, and report precision@k with a latency budget.

**Timebox.** 3–4 hours

## 1. Why This Project Exists

Recommenders expose every KNN failure mode at once: sparsity, scaling, k choice, cold start, and query cost.

## 2. Requirements

- Load MovieLens-style ratings (ratings.csv + movies.csv) or synthesise a sparse rating matrix.
- Implement item-based KNN: find similar films by co-rating similarity, then score unseen films for a user.
- Standardise (or mean-centre per user, which handles rating-scale bias better).
- Sweep k and measure precision@10 and recall@10 with a leave-one-out evaluation.
- Report a latency benchmark for 1,000 recommendations and state a per-request budget.
- Write a model card covering cold start, popularity bias and what the similarity metric misses.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 25m | Load data; assert sparsity level and build the item-user matrix | A documented sparsity number |
| 2 | 30m | Implement item-item similarity (cosine and adjusted cosine) with a min-support filter | Similarities for 100 items, reproducible |
| 3 | 25m | Implement neighbour-based scoring for a user; exclude already-seen items | A ranked list per user |
| 4 | 30m | Leave-one-out evaluation; sweep k and the similarity metric | Precision@10 and recall@10 curves |
| 5 | 20m | Benchmark 1,000 recommendations and record p50/p95 latency | A latency table with a stated budget |
| 6 | 20m | Analyse cold start and popularity bias; compare against a popularity baseline | A named failure mode with numbers |
| 7 | 20m | Model card plus a serving endpoint for /recommend?user= | A readable card and a working endpoint |

## 4. Architecture Sketch

```text
ratings.csv --> item-user matrix (sparse)
                        |
        +---------------+----------------+
        |                                |
  item-item similarity            popularity baseline
  (cosine / adj-cosine)                  |
        |                                |
   top-k neighbours per item             |
        |                                |
  score = weighted mean of user's ratings |
        |                                |
   exclude seen, rank top-10  ---------->+
                        |
      leave-one-out precision@10 / recall@10
```

## 5. Implementation Notes

- Mean-centring per user removes individual rating harshness; it usually beats raw cosine.
- A min-support threshold stops one co-rater from defining a film's similarity.
- Report recall@10 and NDCG too; precision@10 alone flatters popular catalogues.
- The popularity baseline is the number that makes your recommender look good or bad.

## 6. Deliverables

1. One-command run producing the k sweep and metric table.
1. Latency benchmark with a stated per-request budget.
1. Cold-start and popularity-bias analysis with numbers.
1. Model card plus a /recommend endpoint.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Correctness | 30% | Similarity and scoring verified on a hand-worked example; seen items excluded |
| Evaluation | 25% | Leave-one-out protocol, k sweep, baseline reported |
| Performance | 20% | Latency measured against a stated budget |
| Analysis | 15% | Cold start and popularity bias quantified |
| Communication | 10% | Model card names what the metric misses |

## 8. Stretch Goals

- Add user-based KNN and compare: which wins, and on what kind of user?
- Blend with the popularity baseline and show the gain at the head of the list.
- Index the similarity search with an approximate NN structure and measure the accuracy cost.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Load MovieLens-style ratings (ratings.csv + movies.csv) or synthesise a sparse rating matrix.
- [ ] Implement item-based KNN: find similar films by co-rating similarity, then score unseen films for a user.
- [ ] Standardise (or mean-centre per user, which handles rating-scale bias better).
- [ ] Sweep k and measure precision@10 and recall@10 with a leave-one-out evaluation.
- [ ] Report a latency benchmark for 1,000 recommendations and state a per-request budget.
- [ ] Write a model card covering cold start, popularity bias and what the similarity metric misses.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
