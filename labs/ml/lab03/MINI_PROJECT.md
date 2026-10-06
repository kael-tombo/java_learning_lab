# MINI_PROJECT — Customer Churn Classifier

**Track:** ml  |  **Lab:** lab03  |  **Level:** Intermediate

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

**Brief.** Predict churn from a tabular dataset with a forest, calibrate the operating point against the cost of a retention call, and report importance honestly.

**Timebox.** 3 hours

## 1. Why This Project Exists

Churn is imbalanced, priced, and full of traps: a tenure feature that leaks the label, an account ID that looks important, and a business that cannot afford false alarms.

## 2. Requirements

- Load or synthesise 30k customers with tenure, plan, monthly spend, support tickets, region, churn.
- Split stratified; keep customer_id out of the feature set and add a test asserting it.
- Train a single tuned tree, then a 200-tree forest with mtry = sqrt(p).
- Report OOB error, held-out accuracy, PR-AUC and a confusion matrix at a cost-justified threshold.
- Compute permutation importance with 30 repeats; explain the top three features.
- Ship the forest as a serialised artifact with a score endpoint that returns the rule path.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 20m | Assemble the feature matrix; assert no identifier or post-outcome field is present | A feature list a reviewer can read |
| 2 | 20m | Tune a single tree's depth on validation data | A depth curve and a chosen depth |
| 3 | 25m | Train the 200-tree forest; log OOB and held-out metrics per tree count | Two curves showing where extra trees stop helping |
| 4 | 20m | Threshold sweep with retention-call cost vs lost-customer cost | A cost curve with a marked optimum |
| 5 | 25m | Permutation importance with repeats and standard errors | A ranked table you would defend in a review |
| 6 | 20m | Serialise the forest; serve /predict with the rule path | Reload from disk and assert identical predictions |
| 7 | 15m | Model card: metrics, threshold, cost, limitations, retrain trigger | A card the retention team can act on |

## 4. Architecture Sketch

```text
customers.csv --> FeatureBuilder (drops id, adds tenure buckets)
                        |
             stratified split (train / valid / test)
                        |
     +------------------+------------------+
     |                  |                  |
 single tree (tuned)  forest (200)    baseline (predict churn=1)
     |                  |                  |
     +------------------+------------------+
                        |
      OOB + held-out metrics | threshold sweep | permutation importance
                        |
           serialise forest --> /predict (score + rule path)
```

## 5. Implementation Notes

- A customer_id column will dominate impurity importance; that is the lesson, not a nuisance.
- Churn labels drift with the calendar; keep the test split in the future relative to training.
- Trees cannot extrapolate, so a rare high-spend segment will be under-predicted — flag it in the card.
- Log tree count vs OOB error so the 200-tree choice is justified rather than assumed.

## 6. Deliverables

1. One-command reproduction script producing the metrics table.
1. Depth curve, OOB-vs-tree-count curve, and the cost-vs-threshold curve.
1. Permutation importance table with error bars and a written interpretation.
1. Model card plus a serialised forest artifact.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Correctness | 30% | Tree implementation verified; identifier excluded; serialisation round-trips |
| Evaluation honesty | 25% | OOB and held-out both reported; baseline compared; one test set |
| Tuning justification | 20% | Depth and threshold each chosen from a plotted curve |
| Interpretation | 15% | Importance defended with repeats and error bars |
| Communication | 10% | Model card names a real limitation |

## 8. Stretch Goals

- Add a monotone constraint (higher tenure must not increase churn) and measure the accuracy cost.
- Quantile forest for calibrated intervals on the churn probability.
- Isolation-forest detector for OOD customers and a report on what it flags.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Load or synthesise 30k customers with tenure, plan, monthly spend, support tickets, region, churn.
- [ ] Split stratified; keep customer_id out of the feature set and add a test asserting it.
- [ ] Train a single tuned tree, then a 200-tree forest with mtry = sqrt(p).
- [ ] Report OOB error, held-out accuracy, PR-AUC and a confusion matrix at a cost-justified threshold.
- [ ] Compute permutation importance with 30 repeats; explain the top three features.
- [ ] Ship the forest as a serialised artifact with a score endpoint that returns the rule path.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
