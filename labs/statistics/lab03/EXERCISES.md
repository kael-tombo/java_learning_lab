# Hypothesis Testing - Exercises

**Track:** statistics  |  **Lab:** lab03  |  **Level:** Intermediate

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
cd lab03
javac -d out $(Get-ChildItem -Recurse -Filter *.java src | ForEach-Object { $_.FullName })
java -cp out com.statistics.lab03.HypothesisTesting
```

## Exercise 1: Implement the test suite

**Task.** Correct statistics and honest reporting.

**Steps**
- Implement one-sample, Welch two-sample and paired t.
- Implement chi-square goodness of fit and independence.
- Compute effect sizes and confidence intervals for each.
- Verify against hand calculations.

**Deliverable.** A verified test suite with effect sizes attached.

## Exercise 2: Assumptions that fail

**Task.** Test the edge cases.

**Steps**
- Use highly unequal variances with small n; show the pooled test failing.
- Compare pooled and Welch p-values.
- Detect expected counts below 5 in chi-square.
- Write the reporting note for each violated assumption.

**Deliverable.** A comparison showing why assumptions matter.

## Exercise 3: Interpretation drill

**Task.** Fix the sentences people actually write.

**Steps**
- Take ten real reported results.
- Rewrite each p-value claim correctly.
- Attach effect sizes and intervals.
- Mark which conclusions were unsupported.

**Deliverable.** A rewritten report with corrected reasoning.

## Exercise 4: Power and sample size

**Task.** Size the test before running it.

**Steps**
- Compute required n for an effect size, alpha and power.
- Compute achievable MDE at a given n.
- Show power at a deliberately underpowered n.
- Report the risk of a false negative.

**Deliverable.** A power table with an underpowered example.

## Exercise 5: Multiple looks

**Task.** Measure the inflation you create by watching.

**Steps**
- Simulate the null metric over k looks.
- Measure the false positive rate for k = 1, 5, 10, 20.
- Implement a sequential alpha-spending correction.
- Show the corrected rate.

**Deliverable.** An inflation measurement with a correction.

## Exercise 6: Permutation and bootstrap alternatives

**Task.** Reduce distributional assumptions.

**Steps**
- Implement a permutation test for a difference in means.
- Implement a bootstrap interval for a median.
- Compare results against the parametric tests.
- Explain where each agrees and where they diverge.

**Deliverable.** An assumption-light comparison.

## Exercise 7: Multiple comparisons

**Task.** Correct for the family of tests.

**Steps**
- Run 20 tests under the null.
- Measure the family-wise false positive rate.
- Apply Bonferroni and false discovery rate control.
- Show how many true findings survive.

**Deliverable.** A correction comparison with a verdict.

## Exercise 8: Full analysis write-up

**Task.** Produce something you would defend.

**Steps**
- Design a pre-registered test with power.
- Run it on a real or realistic dataset.
- Report hypothesis, assumptions, statistic, p, effect, interval and limitations.
- Write the decision and its business translation.

**Deliverable.** A complete write-up a reviewer accepts.


---

## Self-Check Before You Move On

- [ ] I can state what my p-value means in one sentence.
- [ ] My reports never show a p-value without an effect size.
- [ ] I report power when a result is inconclusive.
- [ ] My test choice matches the data type and design.
