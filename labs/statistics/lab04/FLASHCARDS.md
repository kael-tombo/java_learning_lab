# ANOVA - Flashcards (60 cards)

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

**Format.** Question (front) -> answer (back). Use for spaced repetition: day 0, day 1, day 3, day 7, day 21. Do not read the answer first.

| # | Front | Back |
|---|---|---|
| 1 | What does an F-statistic of 1 mean? | The between-group variance equals the within-group variance, exactly what a true null predicts. |
| 2 | Why is eta-squared reported alongside the F-test? | Because with large n any tiny effect becomes significant, so the F-test alone says nothing about magnitude. |
| 3 | Why not run pairwise t-tests after ANOVA? | The family-wise error rate inflates with the number of pairs, producing false differences. |
| 4 | What does Tukey's HSD control? | The family-wise error rate across all pairwise comparisons, using the studentised range distribution. |
| 5 | How does Bonferroni differ from Tukey? | Bonferroni divides alpha by the number of comparisons and is conservative; Tukey uses the range distribution and is less conservative. |
| 6 | What violates the ANOVA assumptions most often? | Unequal variances and non-normal residuals, especially with small n. |
| 7 | What is Welch's ANOVA for? | Unequal variances; it adjusts the error degrees of freedom instead of assuming homogeneity. |
| 8 | When does the interaction term matter most? | When the effect of one factor depends on the level of another, which changes the main-effect interpretation. |
| 9 | What is Variance partitioning? | Total variability splits into between-group and within-group components. |
| 10 | What is One-way versus two-way? | One-way compares k groups on one factor. |
| 11 | What is Post-hoc tests are not optional? | A significant omnibus test says something differs, not what. |
| 12 | What is Assumptions matter, and they are checkable? | Normality within groups, homogeneity of variance, independent observations. |
| 13 | What is Effect size is the answer? | Eta-squared is the proportion of variance explained by the factor. |
| 14 | What is Fixed versus random effects? | Fixed effects test specific levels you chose. |
| 15 | In this lab, what does `SS_total = SS_between + SS_within` mean? | Variance decomposition: the identity behind ANOVA |
| 16 | In this lab, what does `F = MS_between / MS_within` mean? | F-statistic: 1 under a true null |
| 17 | In this lab, what does `MS_between = SSB/(k−1)` mean? | Mean square between: df for the numerator |
| 18 | In this lab, what does `MS_within = SSW/(N−k)` mean? | Mean square within: df for the denominator |
| 19 | In this lab, what does `η² = SSB/SST` mean? | Eta-squared: share of variance explained |
| 20 | In this lab, what does `interaction SS = SST - SSA - SSB` mean? | Two-way interaction: the term usually skipped |
| 21 | In this lab, what does `Tukey HSD = q / sqrt(MSS/n)` mean? | Post-hoc: family-wise controlled |
| 22 | In this lab, what does `Bonferroni: alpha' = alpha / m` mean? | Correction: conservative, always valid |
| 23 | You see 'Significant omnibus test, no idea what differs' in production. What is the cause and the fix? | stopping at the F-test Fix: run a post-hoc method and report which pairs |
| 24 | You see 'Pairwise t-tests without correction' in production. What is the cause and the fix? | family-wise error inflation Fix: Tukey, Bonferroni or Scheffe, chosen for the comparison structure |
| 25 | You see 'ANOVA on clearly different variances' in production. What is the cause and the fix? | homogeneity violated Fix: Welch's ANOVA, and check the residual plot |
| 26 | You see 'A significant result with eta-squared of 0.002' in production. What is the cause and the fix? | large n, tiny effect Fix: report the effect size; the F-test alone is uninformative |
| 27 | You see 'Repeated measures on the same subjects analysed as independent' in production. What is the cause and the fix? | independence violated Fix: use a repeated-measures ANOVA or a mixed model |
| 28 | You see 'The interaction term omitted from a two-way design' in production. What is the cause and the fix? | wrong error term Fix: fit the interaction; it often changes the main-effect conclusions |
| 29 | Which Java API is the backbone of: one pass per group with Welford statistics | `Grouped accumulation for SSB, SSW, SST` |
| 30 | Which Java API is the backbone of: p-values without lookup tables | `Incomplete beta for the F CDF` |
| 31 | Which Java API is the backbone of: studentised range function by numerical integration | `Q distribution for Tukey HSD` |
| 32 | Which Java API is the backbone of: statistic and effect size together | `record AnovaTable(double f, int df1, int df2, double p, double etaSquared)` |
| 33 | Which Java API is the backbone of: assumption checks feed the choice of test | `Residual diagnostics from a fitted linear model` |
| 34 | Why does Variance partitioning matter operationally? | Total variability splits into between-group and within-group components. |
| 35 | Why does One-way versus two-way matter operationally? | One-way compares k groups on one factor. |
| 36 | Why does Post-hoc tests are not optional matter operationally? | A significant omnibus test says something differs, not what. |
| 37 | Why does Assumptions matter, and they are checkable matter operationally? | Normality within groups, homogeneity of variance, independent observations. |
| 38 | Why does Effect size is the answer matter operationally? | Eta-squared is the proportion of variance explained by the factor. |
| 39 | Why does Fixed versus random effects matter operationally? | Fixed effects test specific levels you chose. |
| 40 | In the ANOVA pipeline, what happens next? State the hypothesis: at least one group mean differs, with ... | State the hypothesis: at least one group mean differs, with any planned contrasts specified in advance. |
| 41 | In the ANOVA pipeline, what happens next? Check assumptions: independence, residual normality, homogen... | Check assumptions: independence, residual normality, homogeneity of variance. |
| 42 | In the ANOVA pipeline, what happens next? Compute the ANOVA table by hand and verify the variance deco... | Compute the ANOVA table by hand and verify the variance decomposition sums. |
| 43 | In the ANOVA pipeline, what happens next? If significant, run a post-hoc method chosen for the compari... | If significant, run a post-hoc method chosen for the comparison structure. |
| 44 | In the ANOVA pipeline, what happens next? Report the effect size with a confidence interval, not only ... | Report the effect size with a confidence interval, not only the F-test. |
| 45 | In the ANOVA pipeline, what happens next? If assumptions fail, switch to Welch's ANOVA or the rank-bas... | If assumptions fail, switch to Welch's ANOVA or the rank-based alternative. |
| 46 | Exercise focus: One-way ANOVA from scratch | The table, computed and verified. |
| 47 | Exercise focus: Post-hoc comparisons | Localise the differences properly. |
| 48 | Exercise focus: Assumptions and alternatives | Know when ANOVA is the wrong tool. |
| 49 | Exercise focus: Two-way ANOVA | Main effects and the interaction. |
| 50 | Exercise focus: Effect size and power | Is the difference worth anything? |
| 51 | Exercise focus: Multiple comparisons in practice | Measure the inflation you create. |
| 52 | State the One-way ANOVA decomposition result for ANOVA. | Groups [10, 12, 11], [14, 16, 15], [9, 10, 8]: means 11, 15, 9; grand mean 11.667. SSB = 3(0.667² + 3.333² + 2.667²) = 48.67; SSW = 2(1 + 1 + 0) + 2(1 + 1 + 0) + 2(1 + 0 + 1.333) = 8.67. F = 16.22/2.89 = 5.62 with df (2, 6), p ≈ 0.046. |
| 53 | State the Effect size and why the F-test alone is misleading result for ANOVA. | n = 10,000 per group with a true difference of 0.02 standard deviations: t ≈ 2.83, p ≈ 0.005, yet eta² = 0.0002, explaining 0.02% of variance. Statistically significant, operationally irrelevant. |
| 54 | State the Multiple comparisons and family-wise error result for ANOVA. | m = 10 comparisons at alpha = 0.05: unadjusted FWER is 1 - 0.95^10 = 0.40. Bonferroni uses alpha' = 0.005 per test, giving FWER at most 0.05. Tukey typically needs alpha' around 0.017 for the same family. |
| 55 | State the Welch's ANOVA and unequal variances result for ANOVA. | Group variances of 1, 1 and 9 with n = 10 each: the classical F test is dominated by the noisy group and its p-value is anti-conservative. Welch's df falls well below 27, widening the interval and correcting the p-value. |
| 56 | State the Two-way ANOVA and the interaction result for ANOVA. | Factor A at two levels, B at two, with a 5-unit effect of A at B=low and zero at B=high: SSA is positive, but the true story is the interaction. Reporting only main effects would say 'A matters, B does not' and be wrong about half the cells. |
| 57 | What is the error term in a two-way ANOVA? | Usually the residual mean square, including the interaction; omitting the interaction changes it. |
| 58 | How do I choose between Tukey, Bonferroni and Scheffe? | Tukey for all pairs, Bonferroni for a few pre-planned contrasts, Scheffe for all possible contrasts including complex ones. |
| 59 | What does fixed versus random effect change? | Which levels the error term is estimated from, and therefore how the p-value generalises. |
| 60 | Why does ANOVA need replication? | Without within-cell replication the error term cannot be separated from the interaction. |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
