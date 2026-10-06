# Model Evaluation - Exercises

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

## How To Work These

Work in order. Each exercise builds the next; do not skip ahead.
Every exercise ends with a *deliverable* you can show someone - code that compiles, a number you can defend, or a table you can regenerate.

Run the lab as you go:

```bash
cd lab10
javac -d out $(Get-ChildItem -Recurse -Filter *.java src | ForEach-Object { $_.FullName })
java -cp out com.ml.lab10.Main
```

## Exercise 1: Build the metric suite from scratch

**Task.** Every metric from the four counts, cross-checked by hand.

**Steps**
- Implement confusionMatrix(y, yHat).
- Derive precision, recall, F1, specificity and balanced accuracy.
- Compute each by hand on a 10-row example.
- Add trivial-baseline accuracy next to accuracy.

**Deliverable.** A verified metric suite and a hand-worked example.

## Exercise 2: ROC and PR, both curves

**Task.** See the difference a rare positive rate makes.

**Steps**
- Compute ROC by threshold sweep and AUC by trapezoids.
- Compute AUC by the rank (Mann-Whitney) method; assert equality.
- Compute the PR curve and average precision.
- Compare AUC and AP on a 1% positive dataset.

**Deliverable.** Two curves and a comparison showing why AP is the honest metric here.

## Exercise 3: k-fold done correctly

**Task.** The fold strategy is where numbers are won or lost.

**Steps**
- Implement stratified k-fold with a recorded seed.
- Assert each fold's class ratio matches the whole set.
- Cache fold indices and reuse across two models.
- Compute the spread across folds.

**Deliverable.** A fold generator with assertions and a two-model comparison on identical folds.

## Exercise 4: Grouped and time-based splits

**Task.** Handle the cases where i.i.d. is a lie.

**Steps**
- Implement grouped splits by entity id.
- Implement forward-chaining splits for a time series.
- Show leakage: shuffle a time series and compare scores.
- Quantify the optimism the shuffled split introduces.

**Deliverable.** Two split implementations plus a quantified leakage number.

## Exercise 5: Threshold selection from costs

**Task.** Turn business costs into an operating point.

**Steps**
- Implement cost-based threshold selection on validation folds.
- Plot cost and precision/recall against threshold.
- Compare with the 0.5 threshold and with max-F1.
- Write the recommendation with numbers.

**Deliverable.** A cost curve and a defended operating point.

## Exercise 6: Confidence intervals on a metric

**Task.** Know when your difference is real.

**Steps**
- Bootstrap the evaluation set 1,000 times; compute the metric each time.
- Report the 2.5/50/97.5 percentiles.
- Compare two models with a paired bootstrap on identical samples.
- Conclude whether a 0.3% gap is meaningful.

**Deliverable.** An interval and a paired comparison with a verdict.

## Exercise 7: Calibration versus discrimination

**Task.** Two properties, one model.

**Steps**
- Compute AUC and reliability bins for a classifier.
- Report ECE before and after Platt scaling.
- Find a threshold where precision is usable and report the resulting recall.
- Explain the difference to a stakeholder.

**Deliverable.** Two reports and a plain-language explanation.

## Exercise 8: Publish an evaluation report

**Task.** Package the protocol so it is reusable and reviewable.

**Steps**
- Generate a markdown report: protocol, folds, metrics, curves, baseline.
- Include the exact seed, library versions and fold indices hash.
- Have a colleague reproduce the numbers from the repo.
- Write the recommendation and its confidence.

**Deliverable.** A reproducible report and a second pair of eyes confirming the numbers.


---

## Self-Check Before You Move On

- [ ] My report starts with the confusion matrix
- [ ] I can explain why I chose ROC or PR for this task
- [ ] My splits respect time and groups
- [ ] I compared against a trivial baseline
