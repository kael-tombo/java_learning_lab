# Statistical Power & Effect Size - Exercises

**Track:** statistics  |  **Lab:** lab10  |  **Level:** Advanced

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
java -cp out com.statistics.lab10.StatisticalPower
```

## Exercise 1: Effect sizes

**Task.** Compute and interpret them.

**Steps**
- Implement d with pooled and with control-only variance.
- Implement Hedges' correction.
- Express an effect as r and as a proportion difference.
- Translate one into business units.

**Deliverable.** An effect size suite with a business translation.

## Exercise 2: Power curves

**Task.** Power across n and effect sizes.

**Steps**
- Plot power against n for several effect sizes.
- Mark the n reaching 80% power for each.
- Compare two-sided and one-sided curves.
- Read the achievable effect from each curve.

**Deliverable.** Power curves with marked operating points.

## Exercise 3: MDE analysis

**Task.** What your design can see.

**Steps**
- Compute MDE for a grid of n.
- Express MDE in business units for a real metric.
- Explain why small studies are uninformative.
- Recommend a design given a budget.

**Deliverable.** An MDE analysis with a budget recommendation.

## Exercise 4: Pilot variance inflation

**Task.** Plan with a defensible variance.

**Steps**
- Run pilots at several sizes.
- Show the bias in the variance estimate.
- Compare inflated and uninflated required n.
- Justify the inflation factor.

**Deliverable.** A bias demonstration with justified inflation.

## Exercise 5: Multiplicity and power cost

**Task.** Price the cost of many comparisons.

**Steps**
- Compute power with and without a Bonferroni correction.
- Compute the required n increase for m = 5, 10, 50.
- Compare to a false discovery rate approach.
- Recommend a strategy.

**Deliverable.** A multiplicity cost comparison.

## Exercise 6: Post-hoc power critique

**Task.** Show why it is uninformative.

**Steps**
- Simulate studies under the null and at a true effect.
- Compute post-hoc power at the observed effect.
- Show it is a monotone function of the p-value.
- Compute retrospective power at the a priori effect instead.

**Deliverable.** A demonstration with a replacement metric.

## Exercise 7: Power for proportions and counts

**Task.** Beyond means.

**Steps**
- Implement power for a two-proportion test.
- Implement power for a rate comparison with Fisher's z.
- Show how a rare baseline inflates required n.
- Apply to a realistic conversion example.

**Deliverable.** Power calculations for non-mean outcomes.

## Exercise 8: Full power analysis

**Task.** A design document.

**Steps**
- State the business threshold and convert it to an effect size.
- Estimate and inflate the variance.
- Compute required n, horizon and MDE.
- Publish the power curve and the decision rule.

**Deliverable.** A design document a reviewer would approve.


---

## Self-Check Before You Move On

- [ ] My effect size came from a threshold or literature.
- [ ] My variance is inflated if from a small pilot.
- [ ] I report the MDE my sample can achieve.
- [ ] I never quote post-hoc power as evidence.
