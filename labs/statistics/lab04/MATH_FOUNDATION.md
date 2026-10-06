# ANOVA - Mathematical Foundations

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

## Notation

| Symbol | Meaning |
|---|---|
| `SS_total = SS_between + SS_within` | Variance decomposition - the identity behind ANOVA |
| `F = MS_between / MS_within` | F-statistic - 1 under a true null |
| `MS_between = SSB/(k−1)` | Mean square between - df for the numerator |
| `MS_within = SSW/(N−k)` | Mean square within - df for the denominator |
| `η² = SSB/SST` | Eta-squared - share of variance explained |
| `interaction SS = SST - SSA - SSB` | Two-way interaction - the term usually skipped |
| `Tukey HSD = q / sqrt(MSS/n)` | Post-hoc - family-wise controlled |
| `Bonferroni: alpha' = alpha / m` | Correction - conservative, always valid |

## Why the Math Matters

The formulas below are not decoration: each one is the place where a wrong assumption silently produces a plausible number. Knowing which formula applies, and when it stops applying, is the skill this lab builds.


---

## 1. One-way ANOVA decomposition

```text
SSB = sum_j n_j (xbar_j - xbar)^2
SSW = sum_j sum_i (x_ij - xbar_j)^2
SST = SSB + SSW
F = (SSB/(k-1)) / (SSW/(N-k)), df = (k-1, N-k)
```

The decomposition holds identically, which makes it easy to verify by hand. The F statistic compares variance explained by grouping against variance left over, so it is 1 in expectation under a true null regardless of group means.

**Worked example.** Groups [10, 12, 11], [14, 16, 15], [9, 10, 8]: means 11, 15, 9; grand mean 11.667. SSB = 3(0.667² + 3.333² + 2.667²) = 48.67; SSW = 2(1 + 1 + 0) + 2(1 + 1 + 0) + 2(1 + 0 + 1.333) = 8.67. F = 16.22/2.89 = 5.62 with df (2, 6), p ≈ 0.046.


---

## 2. Effect size and why the F-test alone is misleading

```text
eta^2 = SSB/SST
with large N, t ≈ effect_size * sqrt(N)
so p can be tiny while eta^2 is negligible
```

The test statistic grows with sample size while the effect size does not. A large-n study can detect a difference of almost no practical consequence, which is why the omnibus test must be reported with an effect size and ideally a confidence interval on it.

**Worked example.** n = 10,000 per group with a true difference of 0.02 standard deviations: t ≈ 2.83, p ≈ 0.005, yet eta² = 0.0002, explaining 0.02% of variance. Statistically significant, operationally irrelevant.


---

## 3. Multiple comparisons and family-wise error

```text
family-wise error = 1 - (1 - alpha)^m for m independent tests at alpha
Bonferroni: alpha' = alpha/m, exact bound by union inequality
Tukey: uses the studentised range, less conservative and still FWER controlled
```

Any pair of comparisons increases the chance of at least one false positive. Bonferroni is valid by the union bound regardless of dependence, which is why it is the safe default; Tukey is more powerful because it exploits the joint distribution.

**Worked example.** m = 10 comparisons at alpha = 0.05: unadjusted FWER is 1 - 0.95^10 = 0.40. Bonferroni uses alpha' = 0.005 per test, giving FWER at most 0.05. Tukey typically needs alpha' around 0.017 for the same family.


---

## 4. Welch's ANOVA and unequal variances

```text
group i weight w_i = n_i/s_i^2
F = sum w_i (xbar_i - xbar_w)^2 / (k-1)
df = ((sum w_i (xbar_i - xbar_w)^2)^2 / (k-1)) / (sum (1/(n_i-1))(1 - w_i/W)^2)
```

Equal variances are not needed; Welch down-weights noisy groups. The fractional error degrees of freedom are smaller than the classical N-k, which is the conservative direction, and Welch's test is never less powerful asymptotically than the classical one.

**Worked example.** Group variances of 1, 1 and 9 with n = 10 each: the classical F test is dominated by the noisy group and its p-value is anti-conservative. Welch's df falls well below 27, widening the interval and correcting the p-value.


---

## 5. Two-way ANOVA and the interaction

```text
SST = SSA + SSB + SSAB + SSE
SSAB = SST - SSA - SSB - SSE
test each against SSE
```

The interaction captures whether the effect of one factor depends on the level of the other. When it is significant, main effects should not be interpreted on their own, and a separate-effects analysis is the honest follow-up.

**Worked example.** Factor A at two levels, B at two, with a 5-unit effect of A at B=low and zero at B=high: SSA is positive, but the true story is the interaction. Reporting only main effects would say 'A matters, B does not' and be wrong about half the cells.


---

## Cheat Sheet

- `SS_total = SS_between + SS_within` - Variance decomposition
- `F = MS_between / MS_within` - F-statistic
- `MS_between = SSB/(k−1)` - Mean square between
- `MS_within = SSW/(N−k)` - Mean square within
- `η² = SSB/SST` - Eta-squared
- `interaction SS = SST - SSA - SSB` - Two-way interaction
- `Tukey HSD = q / sqrt(MSS/n)` - Post-hoc
- `Bonferroni: alpha' = alpha / m` - Correction

## Numerical Traps

- Computing MS within as SSW/N instead of SSW/(N-k).
- Reporting an F-test p-value with no effect size.
- Comparing pairs with unadjusted t-tests.
- Omitting the interaction from a two-way design.
- Using the classical F-test when variances differ substantially.

## Self-Check Problems

1. Compute a full one-way ANOVA table by hand for three groups and verify SST = SSB + SSW.
2. Compute eta-squared and a confidence interval for it for a given design.
3. Show the family-wise error inflation for m comparisons at alpha = 0.05.
4. Compare classical and Welch ANOVA on data with variances in a 1:9 ratio.
5. Fit a two-way design with replication and decompose the interaction term.
