# Non-Parametric Statistics - Exercises

**Track:** statistics  |  **Lab:** lab09  |  **Level:** Advanced

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
java -cp out com.statistics.lab09.NonParametricTests
```

## Exercise 1: Ranks and ties

**Task.** Get the foundation right.

**Steps**
- Implement ranking with average ranks for ties.
- Compute the tie correction term.
- Verify on hand-worked examples including heavy ties.
- Show the effect of ignoring ties on a p-value.

**Deliverable.** A verified ranking implementation.

## Exercise 2: Mann-Whitney U

**Task.** Two independent groups.

**Steps**
- Compute U from rank sums.
- Implement the probability-of-superiority interpretation.
- Implement exact enumeration for small n.
- Compare exact and asymptotic p-values across n.

**Deliverable.** A test with an effect size and both p-value paths.

## Exercise 3: Wilcoxon signed-rank

**Task.** Paired data.

**Steps**
- Compute differences, omit zeros, rank absolute differences.
- Handle ties in the absolute differences.
- Compare with a signed test on raw values under skew.
- Explain where the power difference comes from.

**Deliverable.** A paired test with a power comparison.

## Exercise 4: Kruskal-Wallis with follow-up

**Task.** The omnibus and its localisation.

**Steps**
- Compute H and the tie-corrected chi-square p-value.
- Follow a significant result with corrected pairwise comparisons.
- Compare power against one-way ANOVA under skew.
- Report an effect size such as epsilon squared.

**Deliverable.** An omnibus test with a corrected follow-up.

## Exercise 5: Friedman for blocked designs

**Task.** Related groups.

**Steps**
- Rank within blocks, sum by treatment, compute Q.
- Apply the tie correction.
- Compare with repeated-measures ANOVA.
- Report an effect size.

**Deliverable.** A blocked rank test.

## Exercise 6: Exact versus asymptotic

**Task.** Know when the approximation lies.

**Steps**
- Enumerate the exact null for n = 5 to 12.
- Compare exact and asymptotic p-values across the range.
- Identify where the approximation becomes acceptable.
- Write the rule you would codify.

**Deliverable.** A comparison table with a documented rule.

## Exercise 7: Power analysis for rank tests

**Task.** Size a rank test properly.

**Steps**
- Compute power via simulation for a rank test.
- Compare power against the parametric equivalent.
- Show the sample size inflation under heavy skew.
- Report the required n.

**Deliverable.** A power comparison with required n.

## Exercise 8: Full rank analysis report

**Task.** Defensible end to end.

**Steps**
- State the design, scale and assumptions.
- Choose and justify the test, handle ties, decide exactness.
- Report statistic, p-value and effect size with an interval.
- State what the result does and does not support.

**Deliverable.** A report with a clear interpretation boundary.


---

## Self-Check Before You Move On

- [ ] I matched the test to the design.
- [ ] My ranking handles ties.
- [ ] Small samples use exact p-values.
- [ ] I report an effect size, not only a p-value.
