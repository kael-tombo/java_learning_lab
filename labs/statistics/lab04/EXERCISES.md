# ANOVA - Exercises

**Track:** statistics  |  **Lab:** lab04  |  **Level:** Intermediate

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
cd lab04
javac -d out $(Get-ChildItem -Recurse -Filter *.java src | ForEach-Object { $_.FullName })
java -cp out com.statistics.lab04.Anova
```

## Exercise 1: One-way ANOVA from scratch

**Task.** The table, computed and verified.

**Steps**
- Compute group means, grand mean, SSB, SSW and SST.
- Assert the decomposition sums.
- Compute F, df and the p-value.
- Compute eta-squared and verify on a hand example.

**Deliverable.** A verified ANOVA implementation.

## Exercise 2: Post-hoc comparisons

**Task.** Localise the differences properly.

**Steps**
- Implement Tukey HSD with the studentised range.
- Implement Bonferroni and Scheffe.
- Compare pairwise p-values across methods on the same data.
- Explain the conservatism differences.

**Deliverable.** A three-method comparison with an explanation.

## Exercise 3: Assumptions and alternatives

**Task.** Know when ANOVA is the wrong tool.

**Steps**
- Generate residual plots and test homogeneity.
- Show the classical F-test is anti-conservative under unequal variances.
- Implement Welch's ANOVA and compare.
- Route non-normal residuals to the rank-based test.

**Deliverable.** A violation demonstration with a working alternative.

## Exercise 4: Two-way ANOVA

**Task.** Main effects and the interaction.

**Steps**
- Decompose variance into A, B, interaction and error.
- Test each against the residual mean square.
- Construct data where the interaction is significant.
- Explain why main effects must not be read alone.

**Deliverable.** A two-way analysis with an interaction story.

## Exercise 5: Effect size and power

**Task.** Is the difference worth anything?

**Steps**
- Compute eta-squared for a large-n, tiny-effect design.
- Compute statistical power for a given effect and group count.
- Report the minimum detectable effect at the chosen n.
- Write the interpretation for a non-technical reader.

**Deliverable.** An effect size and power report.

## Exercise 6: Multiple comparisons in practice

**Task.** Measure the inflation you create.

**Steps**
- Run all pairwise t-tests on data with one real difference.
- Measure the family-wise false positive rate.
- Apply Tukey and Bonferroni and re-measure.
- Compare the false discovery counts.

**Deliverable.** A measured correction comparison.

## Exercise 7: Planned contrasts

**Task.** Test what you actually planned.

**Steps**
- Implement contrast coefficients summing to zero.
- Test planned contrasts against the correct error term.
- Compare with post-hoc after a significant omnibus.
- Explain why planning reduces the burden.

**Deliverable.** A contrast implementation with a comparison.

## Exercise 8: Full ANOVA report

**Task.** Produce something defensible.

**Steps**
- Design the study with a power calculation.
- Run the analysis with assumption checks.
- Run post-hoc and report pairwise differences with intervals.
- Write the conclusion in business terms with limitations.

**Deliverable.** A report a reviewer would accept.


---

## Self-Check Before You Move On

- [ ] I can build an ANOVA table by hand.
- [ ] My omnibus test always comes with an effect size.
- [ ] I know which post-hoc method my comparison structure needs.
- [ ] I check homogeneity before using the classical F-test.
