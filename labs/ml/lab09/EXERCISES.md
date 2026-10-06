# Gradient Boosting - Exercises

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

## How To Work These

Work in order. Each exercise builds the next; do not skip ahead.
Every exercise ends with a *deliverable* you can show someone - code that compiles, a number you can defend, or a table you can regenerate.

Run the lab as you go:

```bash
cd lab09
javac -d out $(Get-ChildItem -Recurse -Filter *.java src | ForEach-Object { $_.FullName })
java -cp out com.ml.lab09.Main
```

## Exercise 1: Boosting from scratch, squared error

**Task.** Implement the full loop by hand once.

**Steps**
- Initialise to the mean target.
- Compute residuals, fit depth-1 stumps, update with eta.
- Track training loss by round; assert it decreases.
- Compare with a single depth-6 tree on the same data.

**Deliverable.** A from-scratch implementation plus a training-loss curve.

## Exercise 2: Functional gradients for three losses

**Task.** Show the framework generalises.

**Steps**
- Implement negative gradients for squared, absolute and logistic loss.
- Fit boosting under each.
- Compare test error and robustness to an outlier.
- Explain why the gradient differs per loss.

**Deliverable.** Three boosting variants with a written comparison.

## Exercise 3: Tune eta and rounds jointly

**Task.** Refuse the one-knob-at-a-time trap.

**Steps**
- Run a grid of eta in {0.3, 0.1, 0.03} x rounds in {50, 200, 800}.
- Plot validation loss against rounds per eta.
- Pick a pair from the surface and justify it.
- Report the cost in training time.

**Deliverable.** A surface plot and a defended (eta, rounds) pair.

## Exercise 4: Early stopping, properly

**Task.** Ship the best round and prove it.

**Steps**
- Implement early stopping with patience = 30.
- Store the full validation history.
- Compare the best round with the last round on the test set.
- Quantify what early stopping saved.

**Deliverable.** A validation curve and a quantified saving.

## Exercise 5: AdaBoost versus gradient boosting

**Task.** Implement the reweighting variant and compare.

**Steps**
- Implement AdaBoost with sample weights.
- Run both on the same data with the same weak learner.
- Compare training curves and test error.
- Explain the difference in one paragraph.

**Deliverable.** Two curves and a written mechanism explanation.

## Exercise 6: Histogram binning

**Task.** Make it fast enough to matter.

**Steps**
- Bin each feature into 128 quantile bins.
- Rewrite split search over bins instead of values.
- Benchmark against exact search on 200k rows.
- Measure the accuracy delta.

**Deliverable.** A benchmark table and a measured accuracy cost.

## Exercise 7: SHAP explanations you can defend

**Task.** Make the additive model explainable.

**Steps**
- Implement exact TreeSHAP or a path-dependent approximation.
- Verify contributions sum to prediction minus baseline.
- Compare explanations against permutation importance.
- Write up three example explanations in plain language.

**Deliverable.** A verified attribution method and three readable explanations.

## Exercise 8: Shadow-mode challenger

**Task.** Practice how boosting actually ships.

**Steps**
- Train a booster on 80% of the data; log predictions on the rest.
- Compare against the current champion model.
- Compute accuracy, ECE and latency for both.
- Write a promotion recommendation with thresholds.

**Deliverable.** A shadow evaluation report with a promotion decision.


---

## Self-Check Before You Move On

- [ ] I can derive the boosting update from the loss gradient
- [ ] I tune eta and rounds jointly with early stopping
- [ ] My explanations are verified additive
- [ ] I ship the best round, not the last
