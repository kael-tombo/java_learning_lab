# Naive Bayes Classifier - Exercises

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

## How To Work These

Work in order. Each exercise builds the next; do not skip ahead.
Every exercise ends with a *deliverable* you can show someone - code that compiles, a number you can defend, or a table you can regenerate.

Run the lab as you go:

```bash
cd lab06
javac -d out $(Get-ChildItem -Recurse -Filter *.java src | ForEach-Object { $_.FullName })
java -cp out com.ml.lab06.Main
```

## Exercise 1: Derive the multinomial NB score

**Task.** Get from Bayes to the log-space scoring formula by hand.

**Steps**
- Write out Bayes' theorem and drop the evidence.
- Substitute the multinomial likelihood and take logs.
- Show the order of terms does not matter after taking logs.
- Implement it and compare against a probability-space version on short docs.

**Deliverable.** A hand derivation and a test that agrees to 1e-12.

## Exercise 2: Prove the underflow

**Task.** Show why probability-space scoring fails on real documents.

**Steps**
- Score a 100, 1,000 and 5,000-token document in probability space.
- Record where the product hits 0.0.
- Score the same documents in log space.
- Confirm identical argmax wherever probability space still works.

**Deliverable.** A table of underflow thresholds and a passing equivalence test below them.

## Exercise 3: Laplace smoothing end to end

**Task.** See exactly what unsmoothed NB does with an unseen word.

**Steps**
- Train without smoothing; score a document with an unseen token.
- Observe the class being eliminated permanently.
- Add alpha = 1 and re-score.
- Sweep alpha over 0, 0.1, 1, 10 and report validation F1.

**Deliverable.** A before/after table and an alpha choice from a curve.

## Exercise 4: Implement all three variants

**Task.** Compare them on data that suits each.

**Steps**
- Implement Gaussian, Multinomial and Bernoulli NB.
- Run all three on a small continuous set and a binary text set.
- Report which variant wins where.
- Explain the mismatch cases in two sentences each.

**Deliverable.** A comparison table with a written explanation of each result.

## Exercise 5: Calibration for NB probabilities

**Task.** Make the posterior publishable.

**Steps**
- Collect log-odds scores on a validation split.
- Bin into deciles and compute ECE.
- Fit Platt scaling (1-D logistic) on the log-odds.
- Report ECE before and after.

**Deliverable.** Two ECE numbers and a reliability table.

## Exercise 6: Class imbalance and complements

**Task.** Handle the case where the minority class matters.

**Steps**
- Train on a 2% positive corpus and report accuracy plus macro-F1.
- Add class priors weighted by inverse frequency.
- Implement complement NB.
- Compare all three on macro-F1.

**Deliverable.** A metrics table and a recommendation.

## Exercise 7: Explainability endpoint

**Task.** Serve the per-token contributions that drove a decision.

**Steps**
- Expose per-token log-likelihood differences between the top two classes.
- Serve POST /classify returning label and the top contributing tokens.
- Verify contributions sum to the score difference.
- Check the explanations against 20 hand-read documents.

**Deliverable.** A running endpoint and 20 spot-checked explanations.

## Exercise 8: Streaming NB training

**Task.** Update counts incrementally instead of retraining.

**Steps**
- Implement fit() and observe() with count updates.
- Stream 100k labelled documents.
- Show predictions update without a full retrain.
- Measure the wall-clock cost of the update path.

**Deliverable.** A streaming demo with a throughput number and identical final counts.


---

## Self-Check Before You Move On

- [ ] I can explain which independence assumption my variant makes
- [ ] My scoring never multiplies probabilities
- [ ] I can state why NB posteriors need calibration before publication
- [ ] I report per-class F1 on imbalanced data
