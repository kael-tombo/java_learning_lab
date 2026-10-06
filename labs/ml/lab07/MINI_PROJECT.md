# MINI_PROJECT — Customer Segmentation with a Stability Report

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

**Brief.** Segment customers with k-means and agglomerative clustering, choose k with evidence, prove the segmentation is stable, and serve it.

**Timebox.** 3–4 hours

## 1. Why This Project Exists

Segmentation projects fail at the validation step. This one forces stability, size distributions and an external-outcome check before any segment gets a name.

## 2. Requirements

- Load a customer dataset (RFM-style or the Online Retail dataset) or synthesise one with realistic structure.
- Standardise features inside the pipeline; log the scaler statistics.
- Run k-means for k = 2..10 with 10 restarts; plot inertia and mean silhouette; print size distributions.
- Run agglomerative with Ward; cut it at a variance budget and compare to the k-means cut with adjusted Rand index.
- Bootstrap 20 times; report the ARI distribution as a stability measure.
- Validate against an external outcome (spend or churn) and name the segments only if they differ on it.
- Serve POST /segment returning cluster id, distance to centroid and population drift per day.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 25m | Load data, engineer 2-4 features, standardise inside the estimator | A documented feature pipeline |
| 2 | 30m | k-means sweep with 10 restarts; inertia and silhouette curves | Two curves plus size distributions |
| 3 | 25m | Agglomerative Ward; cut by variance budget | A dendrogram and a cut height |
| 4 | 20m | ARI between the two segmentations | An agreement number |
| 5 | 30m | Bootstrap stability: 20 resamples, ARI distribution | A stability verdict |
| 6 | 25m | External-outcome validation by cluster | A table of spend/churn per segment |
| 7 | 25m | Segment endpoint with population drift tracking | A working endpoint and a drift chart |

## 4. Architecture Sketch

```text
customers --> features (recency, frequency, value, tenure)
                        |
                   Standardiser (in-pipeline)
                        |
     +------------------+------------------+
     |                  |                  |
   k-means            Ward cut          sizes + drift
   (10 restarts)      (variance budget)      |
     |                  |                  |
     +--------+---------+---------+---------+
                              |
        ARI agreement | bootstrap ARI | external outcome table
                              |
                    POST /segment (id, distance, top features)
```

## 5. Implementation Notes

- If your segments do not differ on an external outcome, stop: you have found geometry, not customers.
- ARI is the right agreement metric because it is invariant to cluster label permutations.
- A 9,000-vs-100 split is a modelling problem, not a segment — investigate before naming.
- Population drift per day is the first production question; build it in from the start.

## 6. Deliverables

1. One-command run producing curves, sizes, ARI agreement and stability.
1. Dendrogram with the chosen cut height marked.
1. External-outcome validation table.
1. Segment endpoint plus a population-by-day drift chart.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Correctness | 30% | Algorithms verified; scaling in-pipeline; ARI implemented correctly |
| k selection | 20% | Curves, sizes and a written justification |
| Validation | 25% | Stability plus external-outcome evidence |
| Engineering | 15% | Deterministic, endpoint works, drift tracked |
| Communication | 10% | Segments named only where evidence supports it |

## 8. Stretch Goals

- Add DBSCAN to capture a crescent-shaped segment and compare segment shapes.
- Replace the hand-chosen features with a PCA-whitened space and see if segmentation changes.
- Build an active-labelling queue that picks the most informative boundary rows.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Load a customer dataset (RFM-style or the Online Retail dataset) or synthesise one with realistic structure.
- [ ] Standardise features inside the pipeline; log the scaler statistics.
- [ ] Run k-means for k = 2..10 with 10 restarts; plot inertia and mean silhouette; print size distributions.
- [ ] Run agglomerative with Ward; cut it at a variance budget and compare to the k-means cut with adjusted Rand index.
- [ ] Bootstrap 20 times; report the ARI distribution as a stability measure.
- [ ] Validate against an external outcome (spend or churn) and name the segments only if they differ on it.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
