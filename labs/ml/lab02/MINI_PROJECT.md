# MINI_PROJECT — Fraud Triage Scorer

**Track:** ml  |  **Lab:** lab02  |  **Level:** Foundational

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

**Brief.** Score transactions as fraud, choose a cost-driven threshold, and prove the model beats 'flag nothing' and 'flag everything'.

**Timebox.** 3 hours

## 1. Why This Project Exists

Fraud is the canonical imbalanced, asymmetric-cost problem. If your threshold logic survives here, it survives most risk queues.

## 2. Requirements

- Synthesise 200k transactions with ~2% fraud, including class-conditional features (amount z-score, velocity, hour).
- Implement logistic regression with L2 and a stable log-loss.
- Derive the cost-optimal threshold from a stated cost matrix (false positive = 1, false negative = 60).
- Report the confusion matrix, PR curve, AUC, and expected cost per 10k transactions.
- Check calibration by decile and report ECE.
- Write a 10-line model card including the known attack it will miss.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 20m | Generate data with class-conditional signals and inject 10% label noise | A CSV where a naive majority classifier scores 98% |
| 2 | 25m | Implement LogisticRegression with L2 and stable loss | Converged fit with bounded coefficients |
| 3 | 25m | Implement the full metric suite plus PR curve | PR curve printed, AUC cross-checked two ways |
| 4 | 20m | Run the threshold sweep with the 1:60 cost matrix | Cost curve with a minimum clearly visible |
| 5 | 20m | Calibration deciles and ECE | Reliability table plus one ECE number |
| 6 | 20m | Compare against always-flag and never-flag baselines on cost | Three-row cost table |
| 7 | 15m | Model card with limitations and a retrain trigger | A card a risk manager can read in 2 minutes |

## 4. Architecture Sketch

```text
transactions.csv --> FeatureBuilder (velocity, amount z-score, hour)
                        |
                  stratified split
                        |
            +-----------+-----------+
            |                       |
      LogisticRegression      Baselines (never / always flag)
      (L2, stable loss)               |
            |                       |
     threshold sweep (cost 1:60) <----+
            |
   confusion matrix | PR curve | calibration | cost per 10k
```

## 5. Implementation Notes

- Inject label noise deliberately; a perfectly separable synthetic fraud set teaches you nothing about thresholding.
- Report cost per 10k transactions, not percentages — percentages hide the asymmetry.
- Keep the scaler inside the estimator so the artifact is self-contained.
- Plot the PR curve, not just ROC; at 2% prevalence the two curves say very different things.

## 6. Deliverables

1. Runnable project with one command producing the metrics table.
1. Cost-vs-threshold curve and the chosen operating point marked.
1. Calibration decile table with ECE.
1. Model card: data, features, metrics, limitations, retrain trigger.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Correctness | 30% | Loss is stable, coefficients bounded, metrics verified against hand calculations |
| Operating point | 25% | Threshold derived from the cost matrix and defended |
| Evaluation honesty | 20% | Baselines reported; test set used once; imbalance respected |
| Communication | 15% | Model card names a real limitation |
| Insight | 10% | One quantified finding about which fraud types are detectable |

## 8. Stretch Goals

- Add a velocity-window feature and show the PR-AUC gain it produces.
- Implement cost-sensitive thresholding at prediction time and show the effect on the review queue size.
- Add a score-distribution drift check that flags when incoming traffic stops matching training.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Synthesise 200k transactions with ~2% fraud, including class-conditional features (amount z-score, velocity, hour).
- [ ] Implement logistic regression with L2 and a stable log-loss.
- [ ] Derive the cost-optimal threshold from a stated cost matrix (false positive = 1, false negative = 60).
- [ ] Report the confusion matrix, PR curve, AUC, and expected cost per 10k transactions.
- [ ] Check calibration by decile and report ECE.
- [ ] Write a 10-line model card including the known attack it will miss.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
