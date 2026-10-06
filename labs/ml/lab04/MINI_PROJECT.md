# MINI_PROJECT — Spam Classifier with a Defensible Margin

**Track:** ml  |  **Lab:** lab04  |  **Level:** Advanced

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

**Brief.** Classify spam with an SVM, tune C and gamma from a validation surface, calibrate the margin, and explain the boundary.

**Timebox.** 3–4 hours

## 1. Why This Project Exists

Spam is small enough for a kernel SVM and asymmetric enough that the threshold matters. It also forces the habit of tuning on a surface instead of a lucky point.

## 2. Requirements

- Load a labelled spam corpus (or synthesise one with class-conditional n-gram counts).
- Standardise features; log TF-IDF or binary counts and keep the vocabulary fixed.
- Train a linear SVM, then an RBF SVM; sweep C × gamma over at least 25 combinations with 5-fold CV.
- Plot the validation surface and pick a point in the plateau, explaining why.
- Platt-calibrate the decision margin and report ECE before and after.
- Write a model card: expected precision at the chosen operating point, known spam classes it misses, and a retrain trigger.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 20m | Build the feature matrix with a frozen vocabulary; assert no empty documents | A reproducible matrix loader |
| 2 | 20m | Fit a linear SVM; report margin, support vectors and training error | A baseline margin number |
| 3 | 35m | Run the 5×5 C×gamma sweep with 5-fold CV | A surface table, not a single number |
| 4 | 20m | Choose a plateau point and refit on all training data | A documented hyperparameter choice |
| 5 | 25m | Platt calibration on a validation split; compute ECE before and after | Two reliability numbers |
| 6 | 20m | Error analysis on 30 misclassified messages | Three named failure patterns |
| 7 | 20m | Model card and a serialised artifact with the calibrator | A reloadable model plus a readable card |

## 4. Architecture Sketch

```text
messages --> Tokeniser --> vocabulary (frozen) --> TF-IDF matrix
                                                        |
                                              stratified 5-fold CV
                                                        |
                                    +-------------------+-------------------+
                                    |                                       |
                          linear SVM (baseline)                  C x gamma sweep (RBF)
                                    |                                       |
                                    +---------------+-----------------------+
                                                    |
                                        best plateau point (documented)
                                                    |
                                        refit on full training set
                                                    |
                                 Platt calibrator --> /classify (label + calibrated p)
```

## 5. Implementation Notes

- Binary counts often beat TF-IDF for short text; try both and report the difference.
- A validation surface is a plateau; the peak is usually noise.
- Support-vector fraction above ~0.8 means the kernel is too wiggly for this data.
- Keep the vocabulary frozen in the artifact — a refitted vocabulary silently changes every score.

## 6. Deliverables

1. One-command run producing the surface table and the metrics.
1. ASCII validation surface with the chosen point marked.
1. Calibration before/after with ECE.
1. Model card, serialised model and calibrator.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Correctness | 30% | Dual/margin implementation verified; CV protocol clean; vocabulary frozen |
| Tuning | 25% | Surface swept, plateau point chosen and justified |
| Calibration | 20% | Margins converted to probabilities with evidence of improvement |
| Analysis | 15% | Named failure patterns from real misclassifications |
| Communication | 10% | Model card states precision at the operating point |

## 8. Stretch Goals

- Add a linear kernel with hashed features and push n past 100k.
- Compare against a bag-of-words logistic regression on cost, not just accuracy.
- Use the support vectors to build a nearest-neighbour explanation endpoint.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Load a labelled spam corpus (or synthesise one with class-conditional n-gram counts).
- [ ] Standardise features; log TF-IDF or binary counts and keep the vocabulary fixed.
- [ ] Train a linear SVM, then an RBF SVM; sweep C × gamma over at least 25 combinations with 5-fold CV.
- [ ] Plot the validation surface and pick a point in the plateau, explaining why.
- [ ] Platt-calibrate the decision margin and report ECE before and after.
- [ ] Write a model card: expected precision at the chosen operating point, known spam classes it misses, and a retrain trigger.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
