# Non-Parametric Statistics

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

## 1. The Problem This Solves

Your data is ordinal, heavily skewed, or simply too small for a t-test. The parametric assumptions are not negotiable, so you need tests that rely on ranks instead.

Real operational data rarely satisfies normality, and switching to a rank-based test is the correct response rather than an admission of defeat.

## 2. Learning Objectives

- Choose the correct rank-based test for each design and data type
- Implement Mann-Whitney, Wilcoxon signed-rank, Kruskal-Wallis and Friedman
- Handle ties correctly in rank-based statistics
- Explain what a rank test does and does not assume
- Compute exact null distributions where the sample is small
- Report an effect size for a rank test, not only a p-value

## 3. Core Concepts

### 3.1 Rank tests replace values with ranks

Under the null of identical distributions, ranks are exchangeable. That is the only assumption, and it holds for ordinal data, heavy tails and small samples where normality is untestable.

### 3.2 The test choice follows the design

Two independent groups: Mann-Whitney. One group, paired observations: Wilcoxon signed-rank. Three or more independent groups: Kruskal-Wallis. Three or more related groups: Friedman. Getting the pairing wrong is the most common error.

### 3.3 Mean ranks versus median ranks

The tests are often described as comparing medians, which is only true under additional shape assumptions. Under a location shift they test a stochastic ordering of distributions. Saying 'median difference' is technically wrong and occasionally consequential.

### 3.4 Ties need explicit handling

With ties, average ranks are assigned and the tie correction adjusts the variance. Ignoring it produces p-values that are too small, so tied data must be handled rather than assumed away.

### 3.5 Exact versus asymptotic p-values

For small samples the rank statistic has a discrete distribution, so a normal approximation is wrong. Computing exact null distributions is tractable up to about 20 per group and is the honest default there.

### 3.6 Rank tests are less powerful when they should be powerful

They discard magnitude information, so a huge effect that is skewed may not reach significance with a modest sample. Conversely, they protect against the extreme outliers that would wreck a t-test.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `U = n₁n₂ + n₁(n₁+1)/2 − R₁` | Mann-Whitney U | two independent groups |
| `W⁻ = min(R⁺, R⁻)` | Wilcoxon statistic | paired differences, zero-differences omitted |
| `H = [12/(N(N+1))]Σ Rⱼ²/(nⱼ) − 3(N+1)` | Kruskal-Wallis | k independent groups |
| `Q = 12/(bk(k+1))Σ Rⱼ² − 3b(k+1)` | Friedman | k treatments, b blocks |
| `rank sum tie correction` | Tie adjustment | average ranks plus variance adjustment |
| `A = rank-biserial correlation` | Effect size | magnitude for a rank test |
| `exact null: enumerate assignments` | Exact p-value | for small n |

## 5. How the Pieces Fit Together

1. Check the measurement scale and the design: independent, paired, or blocked.

2. Check for ties and note their extent, since they change the null distribution.

3. Rank the data, assigning average ranks to ties.

4. Compute the statistic and, for small n, enumerate the exact null distribution.

5. Report the statistic, the exact or asymptotic p-value, and a rank-based effect size with an interval.

6. If the design supports it, follow a significant omnibus test with pairwise comparisons and a correction.

## 6. Assumptions and Invariants

- The response is at least ordinal, so ranks are meaningful
- Under the null, distributions are identical across groups (not merely equal means)
- Observations are independent, or the pairing is respected as designed
- Ties are handled explicitly rather than assumed negligible
- Group shapes are similar if the result is interpreted as a median difference
- Small samples use exact null distributions rather than a normal approximation

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| A rank test reported as a median difference | misstated interpretation | say it tests stochastic ordering unless shapes are shown similar |
| Ties ignored, p-values too small | tie correction omitted | assign average ranks and adjust the variance |
| Wilcoxon used on unpaired data | design mismatch | Mann-Whitney for independent groups |
| Kruskal-Wallis applied to related groups | pairing ignored | Friedman for related groups or blocks |
| An exact test replaced by an asymptotic one at n = 6 | approximation invalid for small samples | enumerate the exact null distribution |
| A non-significant rank test read as no difference | power ignored | report the effect size and confidence interval |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `Arrays.sort on index arrays for ranks` | ranking with stable ordering before tie handling |
| `Average-rank assignment for ties` | the correctness hinge of every rank test |
| `Bitmask enumeration of rank permutations` | exact null distributions for small n |
| `record RankTestResult(String test, double statistic, double p, boolean exact, EffectSize effect)` | exactness recorded alongside the result |
| `Incomplete beta for the chi-square approximation` | asymptotic p-values for larger n |

## 9. Where This Sits in the Larger System

- **lab03** is the parametric default these tests replace when assumptions fail.
- **lab04** is the parametric counterpart to Kruskal-Wallis.
- **lab10** supplies the power analysis that tells you whether a rank test could have found the effect.
- **lab01** provides the rank machinery via order statistics.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Choose the correct rank-based test for each design and data type
- [ ] 0 — cannot yet — Implement Mann-Whitney, Wilcoxon signed-rank, Kruskal-Wallis and Friedman
- [ ] 0 — cannot yet — Handle ties correctly in rank-based statistics
- [ ] 0 — cannot yet — Explain what a rank test does and does not assume
- [ ] 0 — cannot yet — Compute exact null distributions where the sample is small
- [ ] 0 — cannot yet — Report an effect size for a rank test, not only a p-value

## 11. Summary Checklist

- [ ] I matched the test to the design and measurement scale.
- [ ] Ties are handled with average ranks and a variance correction.
- [ ] Small samples use exact null distributions.
- [ ] I state what the null actually is.
- [ ] I report a rank-based effect size with an interval.
- [ ] Omnibus rank tests are followed by corrected pairwise comparisons.
