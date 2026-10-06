# MINI_PROJECT — Email Spam Filter with Calibrated Probabilities

**Track:** ml  |  **Lab:** lab06  |  **Level:** Intermediate

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

**Brief.** Build a spam filter with Naive Bayes, calibrate the posteriors, and make the threshold a cost decision.

**Timebox.** 3 hours

## 1. Why This Project Exists

Spam is the canonical NB problem: sparse counts, imbalance, and an asymmetric cost that makes the threshold the interesting part.

## 2. Requirements

- Load a labelled spam corpus (Enron-Spam is public) or synthesise one with class-conditional token counts.
- Implement multinomial and Bernoulli NB; report both on the same split.
- Sweep alpha over 7 values and plot macro-F1 and calibration error.
- Platt-calibrate the log-odds; report ECE before and after.
- Choose a threshold from a cost matrix (false positive = 1, false negative = 20) and report cost per 1,000 messages.
- Expose per-token contributions that justify each classification, and audit 20 of them by hand.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 20m | Load corpus, build the in-fold vectoriser, assert no empty documents | A reproducible corpus loader |
| 2 | 25m | Implement multinomial NB with log-space scoring and smoothing | A fitted model with finite scores on long documents |
| 3 | 20m | Implement Bernoulli NB and compare | A variant comparison table |
| 4 | 25m | Sweep alpha; plot macro-F1 and ECE against alpha | Two curves and a chosen alpha |
| 5 | 25m | Platt calibration on a validation split; recompute ECE | Before/after calibration numbers |
| 6 | 20m | Cost-matrix threshold sweep; report cost per 1,000 messages | A cost curve with a marked optimum |
| 7 | 25m | Per-token contribution endpoint; hand-audit 20 messages | An audited explanation sample |

## 4. Architecture Sketch

```text
messages --> Tokeniser --> in-fold vocabulary --> counts | indicators
                                          |
                     +--------------------+--------------------+
                     |                                         |
              Multinomial NB                             Bernoulli NB
                     |                                         |
                     +--------------------+--------------------+
                                          |
                        log-odds score --> calibration curve
                                          |
                    cost-based threshold --> /classify
                    (label, p, top tokens)
```

## 5. Implementation Notes

- Stopwords help little for NB; the model handles them but they add noise to explanations.
- Report macro-F1: accuracy on a 10% spam corpus is mostly measuring the absence of spam.
- The audit step is the point of the project — explanations you have not read are not explanations.
- Keep the calibration split separate from both training and threshold tuning.

## 6. Deliverables

1. One-command run producing the variant table, alpha sweep and cost curve.
1. Calibration report before and after Platt scaling.
1. 20 hand-audited explanations with your verdict on each.
1. Model card covering limitations, cost assumptions and a retrain trigger.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Correctness | 30% | Log-space scoring, in-fold vectoriser, smoothing proven |
| Calibration | 25% | ECE measured and improved with evidence |
| Operating point | 20% | Threshold from the cost matrix, cost per 1,000 reported |
| Analysis | 15% | Variant comparison and 20 audited explanations |
| Communication | 10% | Model card states what the filter will miss |

## 8. Stretch Goals

- Add complement NB and show where it helps on the imbalanced class.
- Implement NB-SVM (log-count ratio features plus logistic regression) and compare.
- Add a streaming incremental fit and demonstrate adaptation to a campaign.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Load a labelled spam corpus (Enron-Spam is public) or synthesise one with class-conditional token counts.
- [ ] Implement multinomial and Bernoulli NB; report both on the same split.
- [ ] Sweep alpha over 7 values and plot macro-F1 and calibration error.
- [ ] Platt-calibrate the log-odds; report ECE before and after.
- [ ] Choose a threshold from a cost matrix (false positive = 1, false negative = 20) and report cost per 1,000 messages.
- [ ] Expose per-token contributions that justify each classification, and audit 20 of them by hand.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
