# Hypothesis Testing - Flashcards (60 cards)

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

**Format.** Question (front) -> answer (back). Use for spaced repetition: day 0, day 1, day 3, day 7, day 21. Do not read the answer first.

| # | Front | Back |
|---|---|---|
| 1 | What does a p-value actually mean? | P(data at least as extreme as observed \| the null is true). It is not P(null \| data). |
| 2 | What are Type I and Type II errors? | Rejecting a true null (controlled by alpha) and failing to reject a false null (beta). |
| 3 | Why prefer Welch's t? | It does not assume equal variances, and with unequal n and small samples it is much less prone to distortion. |
| 4 | When is a paired test correct? | When observations are paired, such as before and after on the same subject; the test runs on the differences. |
| 5 | What does failing to reject mean? | Insufficient evidence at the chosen power, not evidence of no effect. |
| 6 | Why does p < 0.05 not mean a 5% chance of being wrong? | The p-value is conditional on the null and does not express the probability that the conclusion is false. |
| 7 | Why is a very small p-value on a tiny effect a problem? | With a large enough n any tiny difference becomes significant, which says nothing about business value. |
| 8 | How do multiple looks break Type I error? | Each look is another chance to cross alpha, so the effective error rate far exceeds the nominal one. |
| 9 | What is Hypotheses are claims, not conclusions? | The null is usually 'no difference' or 'no association'. |
| 10 | What is Type I and Type II error? | Type I is rejecting a true null, controlled by alpha. |
| 11 | What is p-values are not what people say they are? | A p-value is the probability of data at least as extreme as observed, *given* the null. |
| 12 | What is Choosing the test follows the data type? | Means with unknown variance use t; proportions use z or chi-square; paired observations use a paired t on the differences. |
| 13 | What is Multiple looks break the error rate? | Testing daily and stopping when p < 0. |
| 14 | What is Practical significance is separate? | A 0. |
| 15 | In this lab, what does `H₀: μ_A = μ_B vs H₁: μ_A ≠ μ_B` mean? | Two-sample hypothesis: state direction before data |
| 16 | In this lab, what does `t = (x̄_A − x̄_B) / (s_p sqrt(1/n_A + 1/n_B))` mean? | Two-sample t: Welch unless equal variances |
| 17 | In this lab, what does `df = n_A + n_B − 2` mean? | Degrees of freedom: pooled version only |
| 18 | In this lab, what does `z = (x̄ − μ₀) / (σ/sqrt(n))` mean? | One-sample z: known sigma |
| 19 | In this lab, what does `χ² = Σ(Oᵢ − Eᵢ)² / Eᵢ` mean? | Chi-square: counts, not means |
| 20 | In this lab, what does `df = k − 1` mean? | Chi-square df: k categories |
| 21 | In this lab, what does `p = P(T ≥ \|t\|) under H₀` mean? | p-value: conditional on the null, not P(H₀) |
| 22 | In this lab, what does `power = P(reject H₀ \| H₁ true)` mean? | Power: 1 − beta |
| 23 | You see ''There is a 5% chance this is due to chance'' in production. What is the cause and the fix? | p-value misquoted Fix: a p-value is P(data \| H₀), not P(H₀ \| data) |
| 24 | You see 'p < 0.05 and reported as a 0.4% improvement worth shipping' in production. What is the cause and the fix? | effect size ignored Fix: report the interval and translate to a business decision |
| 25 | You see 'The null was not rejected, so the treatments are equivalent' in production. What is the cause and the fix? | absence of evidence read as evidence of absence Fix: report the confidence interval and power |
| 26 | You see 'Twenty daily tests, one reached p < 0.05' in production. What is the cause and the fix? | uncorrected multiple looks Fix: fix the horizon, correct for looks, or use a sequential test |
| 27 | You see 'A pooled t used with unequal variances and small n' in production. What is the cause and the fix? | assumption violated Fix: Welch's test by default |
| 28 | You see 'Direction chosen after seeing the improvement' in production. What is the cause and the fix? | post-hoc one-sided test Fix: pre-specify, or adjust the alpha for the two looks |
| 29 | Which Java API is the backbone of: p-values without lookup tables | `logGamma / incomplete beta for t and F CDFs` |
| 30 | Which Java API is the backbone of: accurate in the far tail where p is small | `erfc for the normal CDF tail` |
| 31 | Which Java API is the backbone of: means and variances in one stable pass | `Welford statistics per group` |
| 32 | Which Java API is the backbone of: p-value and effect size travel together | `record TestResult(String test, double statistic, int df, double p, EffectSize effect, Interval ci)` |
| 33 | Which Java API is the backbone of: confidence intervals as a first-class type | `record Interval(double low, double high, double level)` |
| 34 | Why does Hypotheses are claims, not conclusions matter operationally? | The null is usually 'no difference' or 'no association'. |
| 35 | Why does Type I and Type II error matter operationally? | Type I is rejecting a true null, controlled by alpha. |
| 36 | Why does p-values are not what people say they are matter operationally? | A p-value is the probability of data at least as extreme as observed, *given* the null. |
| 37 | Why does Choosing the test follows the data type matter operationally? | Means with unknown variance use t; proportions use z or chi-square; paired observations use a paired t on the differences. |
| 38 | Why does Multiple looks break the error rate matter operationally? | Testing daily and stopping when p < 0. |
| 39 | Why does Practical significance is separate matter operationally? | A 0. |
| 40 | In the Hypothesis Testing pipeline, what happens next? Pre-specify the hypothesis, the direction, alpha, the test a... | Pre-specify the hypothesis, the direction, alpha, the test and the sample size. |
| 41 | In the Hypothesis Testing pipeline, what happens next? Verify the assumptions: independence, approximate normality ... | Verify the assumptions: independence, approximate normality for small n, equal variances for the pooled t. |
| 42 | In the Hypothesis Testing pipeline, what happens next? Choose the test from the data type and design: paired, indep... | Choose the test from the data type and design: paired, independent, proportion or count. |
| 43 | In the Hypothesis Testing pipeline, what happens next? Compute the statistic and the p-value from the appropriate d... | Compute the statistic and the p-value from the appropriate distribution. |
| 44 | In the Hypothesis Testing pipeline, what happens next? Report the effect size with a confidence interval alongside ... | Report the effect size with a confidence interval alongside the p-value. |
| 45 | In the Hypothesis Testing pipeline, what happens next? If the test is inconclusive, report power rather than declar... | If the test is inconclusive, report power rather than declaring no difference. |
| 46 | Exercise focus: Implement the test suite | Correct statistics and honest reporting. |
| 47 | Exercise focus: Assumptions that fail | Test the edge cases. |
| 48 | Exercise focus: Interpretation drill | Fix the sentences people actually write. |
| 49 | Exercise focus: Power and sample size | Size the test before running it. |
| 50 | Exercise focus: Multiple looks | Measure the inflation you create by watching. |
| 51 | Exercise focus: Permutation and bootstrap alternatives | Reduce distributional assumptions. |
| 52 | State the Test statistic and the reference distribution result for Hypothesis Testing. | n_A = n_B = 20, means differ by 0.4, s_A = s_B = 1.0: SE = sqrt(2/20) = 0.316, t = 1.265, df = 38, p ≈ 0.21. With unequal variances, say s_A = 1.0 and s_B = 3.0, Welch gives SE = sqrt(0.05 + 0.45) = 0.707, t = 0.566, p ≈ 0.58, whereas the pooled test wrongly reports t = 2.29 and p = 0.03. |
| 53 | State the Type I, Type II and power result for Hypothesis Testing. | Effect size d = 0.5, alpha = 0.05 two-sided, power 0.80: n = 64 per group. Power 0.50 needs only n = 33, so the same study at half the size would miss half the real effects it was designed to find. |
| 54 | State the Confidence interval versus p-value result for Hypothesis Testing. | d-hat = 0.40, SE = 0.12, CI = [0.16, 0.64], p = 0.001. The p-value says 'significant'; the interval says the effect could plausibly be 0.16, which may or may not matter commercially. |
| 55 | State the Multiple looks and the inflation result for Hypothesis Testing. | A metric monitored daily for 14 days with a stop at first p < 0.05 has an effective error rate near 52%. A sequential design with alpha spending holds the true rate at 5% while still permitting early stopping. |
| 56 | What does the confidence interval tell you that the p-value does not? | The range of plausible effect sizes, which is what a decision actually needs. |
| 57 | Why is 'no significant difference' not 'the same'? | Because you only know the data was insufficient to detect a difference at your power. |
| 58 | What is the standard error of a mean? | s / sqrt(n): the standard deviation divided by the square root of the sample size. |
| 59 | What does one-sided versus two-sided really change? | The alternative hypothesis, and therefore the threshold; choosing after seeing data inflates error. |
| 60 | Assumption / invariant to defend: Observations are independent within groups... | Observations are independent within groups |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
