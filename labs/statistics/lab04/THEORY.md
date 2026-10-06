# ANOVA

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

## 1. The Problem This Solves

Three or more groups and one question: does at least one of them differ? If yes, the interesting work is finding which pairs differ, not just declaring an omnibus result.

Comparing groups one pair at a time inflates the error rate; ANOVA is the design that avoids it and then localises differences properly.

## 2. Learning Objectives

- Compute one-way and two-way ANOVA tables by hand
- Read the F-statistic and its degrees of freedom correctly
- Explain why post-hoc comparisons need their own correction
- Implement Tukey, Bonferroni and Scheffe methods
- Verify assumptions and know which test replaces ANOVA when they fail
- Report effect size, not just the F-test result

## 3. Core Concepts

### 3.1 Variance partitioning

Total variability splits into between-group and within-group components. The F-statistic is the ratio of mean squares: if groups are really identical, that ratio is approximately 1 regardless of group means.

### 3.2 One-way versus two-way

One-way compares k groups on one factor. Two-way adds a second factor and splits variance into both main effects plus their interaction. The interaction is the part most analyses skip and most often matters.

### 3.3 Post-hoc tests are not optional

A significant omnibus test says something differs, not what. Comparing all pairs with t-tests inflates the family-wise error rate, which is why Tukey, Bonferroni and Scheffe exist: each spends alpha differently across the family of comparisons.

### 3.4 Assumptions matter, and they are checkable

Normality within groups, homogeneity of variance, independent observations. Welch's ANOVA handles unequal variances; rank-based alternatives handle non-normality, and both exist because violations are common.

### 3.5 Effect size is the answer

Eta-squared is the proportion of variance explained by the factor. An F test on large data is significant for trivial effects, so the omnibus test must be paired with an effect size.

### 3.6 Fixed versus random effects

Fixed effects test specific levels you chose. Random effects test whether a sample of levels generalises, which changes the error term and the interpretation of the p-value.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `SS_total = SS_between + SS_within` | Variance decomposition | the identity behind ANOVA |
| `F = MS_between / MS_within` | F-statistic | 1 under a true null |
| `MS_between = SSB/(k−1)` | Mean square between | df for the numerator |
| `MS_within = SSW/(N−k)` | Mean square within | df for the denominator |
| `η² = SSB/SST` | Eta-squared | share of variance explained |
| `interaction SS = SST - SSA - SSB` | Two-way interaction | the term usually skipped |
| `Tukey HSD = q / sqrt(MSS/n)` | Post-hoc | family-wise controlled |
| `Bonferroni: alpha' = alpha / m` | Correction | conservative, always valid |

## 5. How the Pieces Fit Together

1. State the hypothesis: at least one group mean differs, with any planned contrasts specified in advance.

2. Check assumptions: independence, residual normality, homogeneity of variance.

3. Compute the ANOVA table by hand and verify the variance decomposition sums.

4. If significant, run a post-hoc method chosen for the comparison structure.

5. Report the effect size with a confidence interval, not only the F-test.

6. If assumptions fail, switch to Welch's ANOVA or the rank-based alternative.

## 6. Assumptions and Invariants

- Observations are independent within and between groups
- Residuals are approximately normal within each group
- Group variances are homogeneous for the classical F-test
- Groups are independent samples, not repeated measures on the same subject
- Any planned contrasts were specified before seeing the data
- Sample sizes per group are known and reported, since they affect power

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| Significant omnibus test, no idea what differs | stopping at the F-test | run a post-hoc method and report which pairs |
| Pairwise t-tests without correction | family-wise error inflation | Tukey, Bonferroni or Scheffe, chosen for the comparison structure |
| ANOVA on clearly different variances | homogeneity violated | Welch's ANOVA, and check the residual plot |
| A significant result with eta-squared of 0.002 | large n, tiny effect | report the effect size; the F-test alone is uninformative |
| Repeated measures on the same subjects analysed as independent | independence violated | use a repeated-measures ANOVA or a mixed model |
| The interaction term omitted from a two-way design | wrong error term | fit the interaction; it often changes the main-effect conclusions |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `Grouped accumulation for SSB, SSW, SST` | one pass per group with Welford statistics |
| `Incomplete beta for the F CDF` | p-values without lookup tables |
| `Q distribution for Tukey HSD` | studentised range function by numerical integration |
| `record AnovaTable(double f, int df1, int df2, double p, double etaSquared)` | statistic and effect size together |
| `Residual diagnostics from a fitted linear model` | assumption checks feed the choice of test |

## 9. Where This Sits in the Larger System

- **lab03** is the two-group special case ANOVA generalises.
- **lab05** provides the regression machinery that produces the ANOVA decomposition.
- **lab09** provides the rank-based alternatives when assumptions fail.
- **lab10** supplies the power calculation for a given number of groups.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Compute one-way and two-way ANOVA tables by hand
- [ ] 0 — cannot yet — Read the F-statistic and its degrees of freedom correctly
- [ ] 0 — cannot yet — Explain why post-hoc comparisons need their own correction
- [ ] 0 — cannot yet — Implement Tukey, Bonferroni and Scheffe methods
- [ ] 0 — cannot yet — Verify assumptions and know which test replaces ANOVA when they fail
- [ ] 0 — cannot yet — Report effect size, not just the F-test result

## 11. Summary Checklist

- [ ] I can compute an ANOVA table by hand and verify the decomposition sums.
- [ ] I know whether my design is one-way, two-way or repeated measures.
- [ ] I run a post-hoc method after a significant omnibus test.
- [ ] I report an effect size with an interval.
- [ ] I check homogeneity of variance before using the classical F-test.
- [ ] I fit the interaction term in a two-way design.
