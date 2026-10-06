# MINI_PROJECT — Evaluation Suite for an Imbalanced Classifier

**Track:** ml  |  **Lab:** lab10  |  **Level:** Intermediate

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

**Brief.** Build a complete evaluation suite: correct folds, all metrics, curves, intervals, and a cost-based operating point.

**Timebox.** 3–4 hours

## 1. Why This Project Exists

This is the lab you will reuse for every model you ever ship. Doing it once, properly, is worth more than any new algorithm.

## 2. Requirements

- Load a rare-positive binary dataset (fraud, churn or credit) with at least 1,000 positives.
- Implement stratified k-fold, and additionally grouped and forward-chaining folds where relevant.
- Move all preprocessing inside the fold; add an assertion that would fail if you leaked.
- Report the confusion matrix, accuracy with trivial baseline, precision, recall, F1, F2, balanced accuracy, ROC-AUC and average precision.
- Plot ROC and PR; compute AUC two independent ways and assert they agree.
- Bootstrap a 95% interval on the headline metric and compare two models with a paired test.
- Choose the threshold from a cost matrix and report expected cost per 10,000 cases.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 25m | Load data; assert class ratio and positivity count | A documented base rate |
| 2 | 30m | Stratified folds with assertions; cache fold indices | Reusable, inspectable folds |
| 3 | 30m | In-fold preprocessing pipeline; leakage assertion that fails on the naive version | A passing leakage test |
| 4 | 25m | Full metric suite plus both curves | A metrics table and two curves |
| 5 | 30m | Bootstrap interval and paired comparison between two models | Intervals and a verdict |
| 6 | 20m | Cost-matrix threshold sweep; expected cost per 10,000 | A cost curve with a chosen point |
| 7 | 25m | Publish a markdown report: protocol, folds hash, seed, metrics, recommendation | A reproducible report |

## 4. Architecture Sketch

```text
 dataset (rare positives)
        |
  stratified folds (cached, asserted)      forward-chaining folds
        |                                       |
   in-fold preprocessing (scaler/imputer)      |
        |                                       |
   model A / model B  --> same folds, paired comparison
        |
   confusion matrix -> all metrics (with trivial baseline)
        |
   ROC (two methods, assert equal) | PR | average precision
        |
   bootstrap 95% CI  +  cost-matrix threshold  --> expected cost / 10k
        |
   markdown report (seed, folds hash, versions, recommendation)
```

## 5. Implementation Notes

- The leakage assertion is the highest-value line in the project: it must fail on the naive pipeline.
- PR curves at 1% positives look nothing like ROC curves; show both to whoever reads the report.
- Paired comparisons on identical folds remove the dominant variance term.
- Cache fold indices to disk so a colleague's rerun is truly identical.

## 6. Deliverables

1. One-command run producing the full report.
1. Two curves (ROC, PR) with AUC computed two ways and an equality assertion.
1. Bootstrap intervals plus a paired comparison verdict between two models.
1. Cost curve with the chosen operating point and expected cost per 10,000.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Protocol correctness | 30% | Correct folds, in-fold preprocessing, leakage assertion present |
| Metric completeness | 20% | Confusion matrix, all metrics, trivial baseline, both curves |
| Statistical rigor | 25% | Intervals and a paired comparison with a stated verdict |
| Decision | 15% | Cost-based threshold with expected cost per 10,000 |
| Reproducibility | 10% | Seed, fold hash and versions in the report |

## 8. Stretch Goals

- Add slice-based evaluation: metrics per segment, and report the worst slice.
- Implement a sequential-testing guard for peeking at results during an A/B test.
- Correlate an offline metric with a simulated online outcome to justify the choice.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Load a rare-positive binary dataset (fraud, churn or credit) with at least 1,000 positives.
- [ ] Implement stratified k-fold, and additionally grouped and forward-chaining folds where relevant.
- [ ] Move all preprocessing inside the fold; add an assertion that would fail if you leaked.
- [ ] Report the confusion matrix, accuracy with trivial baseline, precision, recall, F1, F2, balanced accuracy, ROC-AUC and average precision.
- [ ] Plot ROC and PR; compute AUC two independent ways and assert they agree.
- [ ] Bootstrap a 95% interval on the headline metric and compare two models with a paired test.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
