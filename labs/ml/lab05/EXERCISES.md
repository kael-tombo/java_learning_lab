# K-Nearest Neighbors - Exercises

**Track:** ml  |  **Lab:** lab05  |  **Level:** Intermediate

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
cd lab05
javac -d out $(Get-ChildItem -Recurse -Filter *.java src | ForEach-Object { $_.FullName })
java -cp out com.ml.lab05.Main
```

## Exercise 1: Implement the three distance metrics

**Task.** Get the geometry right, including the p parameterisation.

**Steps**
- Implement euclidean, manhattan and minkowski(p).
- Verify triangle inequality numerically on random points.
- Show minkowski(p=1) equals manhattan and p=2 equals euclidean.
- Plot the difference on a 2D grid of pairs.

**Deliverable.** A metrics class plus a numerical identity test.

## Exercise 2: Full scan and heap must agree

**Task.** Two implementations, one answer.

**Steps**
- Implement a full-sort neighbour finder.
- Implement the bounded heap version.
- Assert index equality on 1,000 random queries.
- Benchmark both.

**Deliverable.** A passing equivalence test and a benchmark table.

## Exercise 3: Majority versus weighted voting

**Task.** See exactly what weighting changes.

**Steps**
- Implement both aggregations.
- Test on hand-built 3-neighbour cases.
- Measure the effect on a noisy synthetic dataset.
- Plot accuracy vs k for both.

**Deliverable.** Two curves and a written rule for when weighting helps.

## Exercise 4: The k sweep, done honestly

**Task.** Repeated cross-validation, not one split.

**Steps**
- Run 5-fold CV for k in {1,3,5,7,9,15,21,31,51}.
- Repeat 5 times with different seeds.
- Plot mean ± std accuracy versus log k.
- Pick k inside the plateau and report the uncertainty.

**Deliverable.** A plateau plot with error bars and a justified k.

## Exercise 5: Demonstrate the curse of dimensionality

**Task.** Make the problem visible with your own numbers.

**Steps**
- Generate isotropic Gaussian blobs at p = 2, 5, 10, 20, 50, 100.
- Hold n fixed; measure 1-NN accuracy at each p.
- Measure the nearest-to-farthest distance ratio.
- Add PCA to 2 dimensions and re-measure.

**Deliverable.** A table of accuracy versus p, with and without PCA.

## Exercise 6: Scaling invariance test

**Task.** Prove the estimator handles units.

**Steps**
- Fit on standardised features.
- Predict on raw features.
- Assert predictions agree to 1e-9.
- Show what happens when you fit on raw features (the failure case).

**Deliverable.** A test that fails on the raw-fit version and passes on the correct one.

## Exercise 7: Missing values and duplicates

**Task.** Handle the messy cases explicitly.

**Steps**
- Introduce 10% missing values with an imputer and a distance mask.
- Add duplicate rows and assert deterministic predictions.
- Compare accuracy with and without the mask.
- Document the tie rule.

**Deliverable.** A decision table of the four cases and their outcomes.

## Exercise 8: Latency budget for a lookup service

**Task.** Make prediction fast enough to serve.

**Steps**
- Batch 1,000 queries and time brute force.
- Implement a simple grid index and re-time.
- Report accuracy lost by the index.
- Set an explicit latency SLO and a fallback.

**Deliverable.** A latency/accuracy table and a stated SLO.


---

## Self-Check Before You Move On

- [ ] I can state why scaling is required, with a failing test that proves it
- [ ] I picked k from a curve rather than an argmax
- [ ] I measured the curse of dimensionality on my own data
- [ ] I know my prediction latency budget and how I would enforce it
