# MINI_PROJECT — Boosted Classifier with Verified Explanations

**Track:** ml  |  **Lab:** lab09  |  **Level:** Advanced

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

**Brief.** Build a gradient-boosting classifier, tune it with early stopping, and produce SHAP explanations you can check add up.

**Timebox.** 4 hours

## 1. Why This Project Exists

Boosting without explanations is hard to approve in a real review. This project forces the pairing from the start.

## 2. Requirements

- Load a binary classification dataset (adult-income style) or synthesise one with nonlinearity.
- Implement boosting: squared-error or logistic gradient, depth 2–3 trees, subsampling.
- Tune (eta, depth, rounds) on a grid; pick from validation curves, not the last row.
- Compare against a single decision tree and a logistic regression baseline on identical folds.
- Implement exact or path-dependent TreeSHAP; assert contributions sum to prediction minus baseline.
- Write 5 explanations in plain language for 5 specific rows.
- Add a shadow-mode evaluation report comparing to a baseline model on held-out data.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 30m | Load, encode, split stratified; assert no leakage | A reproducible pipeline |
| 2 | 45m | Implement boosting with subsampling and a validation history | Validation loss by round stored |
| 3 | 40m | Grid over eta x depth; plot curves; choose the pair | A surface and a defended choice |
| 4 | 20m | Three-way comparison on identical folds | A comparison table |
| 5 | 45m | Implement SHAP; verify additivity within 1e-9 | A passing additivity test |
| 6 | 30m | Write five plain-language explanations for chosen rows | Five readable explanations |
| 7 | 20m | Model card with the full hyperparameter tuple and limitations | A card a reviewer can approve |

## 4. Architecture Sketch

```text
 dataset --> encode --> stratified folds
                         |
        per (eta, depth) grid: boosting with early stopping
                         |
            validation loss curves --> chosen (eta, depth, best round)
                         |
              +----------+-----------+------------+
              |                      |            |
        boosted model      single tree      logistic
              |                      |            |
              +----------+-----------+------------+
                         |
                 SHAP attribution + additivity check
                         |
            explanations -> model card -> shadow report
```

## 5. Implementation Notes

- Depth 2-3 with eta 0.05-0.1 is a sane starting region; do not start at depth 6.
- Store the validation history per configuration or you cannot choose k honestly.
- Additivity failing usually means the baseline expectation is missing, not that SHAP is broken.
- Compare on identical folds; different splits make the comparison meaningless.

## 6. Deliverables

1. One-command run producing the grid, curves and three-way comparison.
1. SHAP implementation with a passing additivity test.
1. Five plain-language explanations for named rows.
1. Model card with (eta, depth, best round, subsample) and limitations.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Correctness | 30% | Boosting verified against a hand-computed round; SHAP additive |
| Tuning | 25% | Grid, curves and a defended hyperparameter choice |
| Comparison | 20% | Baselines on identical folds with the same protocol |
| Explanations | 15% | Five readable explanations that match the numbers |
| Communication | 10% | Model card names a limitation |

## 8. Stretch Goals

- Add L2 leaf shrinkage (lambda) and show it substitutes for a lower eta.
- Implement quantile loss and compare robustness under label contamination.
- Build a shadow challenger against a baseline and write the promotion gate.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Load a binary classification dataset (adult-income style) or synthesise one with nonlinearity.
- [ ] Implement boosting: squared-error or logistic gradient, depth 2–3 trees, subsampling.
- [ ] Tune (eta, depth, rounds) on a grid; pick from validation curves, not the last row.
- [ ] Compare against a single decision tree and a logistic regression baseline on identical folds.
- [ ] Implement exact or path-dependent TreeSHAP; assert contributions sum to prediction minus baseline.
- [ ] Write 5 explanations in plain language for 5 specific rows.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
