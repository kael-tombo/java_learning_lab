# Descriptive Statistics - Exercises

**Track:** statistics  |  **Lab:** lab01  |  **Level:** Foundational

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
cd lab01
javac -d out $(Get-ChildItem -Recurse -Filter *.java src | ForEach-Object { $_.FullName })
java -cp out com.statistics.lab01.DescriptiveStatistics
```

## Exercise 1: Implement the summaries

**Task.** Centre and dispersion, correctly.

**Steps**
- Implement mean, median and mode.
- Implement variance with n−1 and compare against n.
- Compute standard deviation, IQR and range.
- Verify on a hand-worked example.

**Deliverable.** A Summary implementation verified by hand.

## Exercise 2: Numerical stability lab

**Task.** See the naive formula fail.

**Steps**
- Implement naive and Welford variance.
- Construct data with a large mean and small spread.
- Quantify the relative error of each.
- Document when the naive version is acceptable.

**Deliverable.** A measured error comparison.

## Exercise 3: Quantiles and the fence

**Task.** Percentiles plus outlier screening.

**Steps**
- Implement interpolated p50, p90 and p99.
- Implement the 1.5 IQR fence.
- Flag rows and inspect them for data-quality causes.
- Report summaries with and without flagged rows.

**Deliverable.** A fence report with row-level detail.

## Exercise 4: Shape statistics

**Task.** Decide which summary family to use.

**Steps**
- Implement skewness and excess kurtosis.
- Apply to symmetric, right-skewed and bimodal samples.
- Show the log transform reduces right skew.
- Write the reporting rule you would adopt.

**Deliverable.** A shape report with a reporting rule.

## Exercise 5: Streaming statistics

**Task.** One pass, no retention.

**Steps**
- Implement Welford for mean and variance.
- Stream 10M generated values.
- Compare against a two-pass result on a subset.
- Report throughput.

**Deliverable.** A streaming implementation with a benchmark.

## Exercise 6: Segment versus aggregate

**Task.** Find the reversal.

**Steps**
- Build three segments with opposite trends.
- Compute aggregate and per-segment statistics.
- Show the aggregate reversing.
- Write the reporting practice that prevents it.

**Deliverable.** A Simpson's paradox demonstration.

## Exercise 7: Robust alternatives

**Task.** Compare the summaries.

**Steps**
- Implement the trimmed mean and MAD.
- Compare sensitivity to planted outliers.
- Choose a primary and a secondary summary per dataset.
- Document the choice criteria.

**Deliverable.** A robustness comparison table.

## Exercise 8: Summary reporting tool

**Task.** Produce a report that cannot mislead.

**Steps**
- Emit a summary with centre, dispersion, shape and percentiles.
- Include a histogram and a quantile table.
- Flag skewness and outliers explicitly in the output.
- Print the divisor and quantile convention used.

**Deliverable.** A report tool whose output is defensible.


---

## Self-Check Before You Move On

- [ ] I can explain why my variance is stable.
- [ ] I report the divisor I used.
- [ ] My summary would be wrong to read if the data were skewed.
- [ ] I have not deleted flagged rows.
