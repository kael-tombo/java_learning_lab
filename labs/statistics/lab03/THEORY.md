# Hypothesis Testing

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

## 1. The Problem This Solves

A metric moved. Is it a real effect worth acting on, or the kind of movement that appears in every dataset you have ever looked at?

Testing is the discipline that separates an engineer who measures from one who narrates. The failure mode is not a wrong formula; it is the wrong test or an uncorrected test after twenty looks.

## 2. Learning Objectives

- State null and alternative hypotheses precisely, including direction
- Compute t, z and chi-square statistics with correct degrees of freedom
- Compute p-values without a lookup table and interpret them correctly
- Distinguish Type I and Type II error and relate them to alpha and power
- Choose between paired and independent designs correctly
- Explain why p-values are not effect sizes and never say '5% chance it is null'

## 3. Core Concepts

### 3.1 Hypotheses are claims, not conclusions

The null is usually 'no difference' or 'no association'. The alternative may be one-sided (a specific direction worth acting on) or two-sided. Choosing the direction after seeing the data inflates the false positive rate, so it must be pre-specified.

### 3.2 Type I and Type II error

Type I is rejecting a true null, controlled by alpha. Type II is failing to reject a false null, equal to beta, and 1−beta is power. Every significance choice is a trade between these two, which is why 'just lower alpha' is not a free improvement.

### 3.3 p-values are not what people say they are

A p-value is the probability of data at least as extreme as observed, *given* the null. It is not the probability the null is true, and not the probability the result is a fluke. Reports that say '5% chance this is noise' are wrong in a way that misleads decisions.

### 3.4 Choosing the test follows the data type

Means with unknown variance use t; proportions use z or chi-square; paired observations use a paired t on the differences. Chi-square tests categorical counts; it does not test means.

### 3.5 Multiple looks break the error rate

Testing daily and stopping when p < 0.05 inflates the false positive rate far above 5%. Either fix the sample size and horizon in advance, or use a sequential method that controls the error rate while permitting early stopping.

### 3.6 Practical significance is separate

A 0.3% difference can be highly significant on large samples and irrelevant as a business outcome. Report the effect size with an interval, then translate it. Statistical significance answers whether it is noise; it never answers whether it matters.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `H₀: μ_A = μ_B vs H₁: μ_A ≠ μ_B` | Two-sample hypothesis | state direction before data |
| `t = (x̄_A − x̄_B) / (s_p sqrt(1/n_A + 1/n_B))` | Two-sample t | Welch unless equal variances |
| `df = n_A + n_B − 2` | Degrees of freedom | pooled version only |
| `z = (x̄ − μ₀) / (σ/sqrt(n))` | One-sample z | known sigma |
| `χ² = Σ(Oᵢ − Eᵢ)² / Eᵢ` | Chi-square | counts, not means |
| `df = k − 1` | Chi-square df | k categories |
| `p = P(T ≥ |t|) under H₀` | p-value | conditional on the null, not P(H₀) |
| `power = P(reject H₀ | H₁ true)` | Power | 1 − beta |

## 5. How the Pieces Fit Together

1. Pre-specify the hypothesis, the direction, alpha, the test and the sample size.

2. Verify the assumptions: independence, approximate normality for small n, equal variances for the pooled t.

3. Choose the test from the data type and design: paired, independent, proportion or count.

4. Compute the statistic and the p-value from the appropriate distribution.

5. Report the effect size with a confidence interval alongside the p-value.

6. If the test is inconclusive, report power rather than declaring no difference.

## 6. Assumptions and Invariants

- Observations are independent within groups
- The test statistic's reference distribution is approximately correct at this n
- Equal variances hold for the pooled t; Welch is safer without that assumption
- The sample size was chosen for a target power, not for convenience
- The direction of the alternative was fixed before looking at the data
- Multiple comparisons across tests are accounted for

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| 'There is a 5% chance this is due to chance' | p-value misquoted | a p-value is P(data | H₀), not P(H₀ | data) |
| p < 0.05 and reported as a 0.4% improvement worth shipping | effect size ignored | report the interval and translate to a business decision |
| The null was not rejected, so the treatments are equivalent | absence of evidence read as evidence of absence | report the confidence interval and power |
| Twenty daily tests, one reached p < 0.05 | uncorrected multiple looks | fix the horizon, correct for looks, or use a sequential test |
| A pooled t used with unequal variances and small n | assumption violated | Welch's test by default |
| Direction chosen after seeing the improvement | post-hoc one-sided test | pre-specify, or adjust the alpha for the two looks |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `logGamma / incomplete beta for t and F CDFs` | p-values without lookup tables |
| `erfc for the normal CDF tail` | accurate in the far tail where p is small |
| `Welford statistics per group` | means and variances in one stable pass |
| `record TestResult(String test, double statistic, int df, double p, EffectSize effect, Interval ci)` | p-value and effect size travel together |
| `record Interval(double low, double high, double level)` | confidence intervals as a first-class type |

## 9. Where This Sits in the Larger System

- **lab04** extends mean comparison to three or more groups.
- **lab05** covers association and the regression model behind these tests.
- **lab09** provides the alternatives when normality fails.
- **lab10** supplies the power calculation that fixes sample size in advance.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — State null and alternative hypotheses precisely, including direction
- [ ] 0 — cannot yet — Compute t, z and chi-square statistics with correct degrees of freedom
- [ ] 0 — cannot yet — Compute p-values without a lookup table and interpret them correctly
- [ ] 0 — cannot yet — Distinguish Type I and Type II error and relate them to alpha and power
- [ ] 0 — cannot yet — Choose between paired and independent designs correctly
- [ ] 0 — cannot yet — Explain why p-values are not effect sizes and never say '5% chance it is null'

## 11. Summary Checklist

- [ ] Hypothesis, direction, alpha and sample size are pre-specified.
- [ ] I report the effect size and interval, not just the p-value.
- [ ] I never describe a p-value as the probability the null is true.
- [ ] I use Welch's t unless equal variances are justified.
- [ ] A non-significant result is reported with power, not as 'no effect'.
- [ ] Multiple looks and multiple comparisons are corrected.
