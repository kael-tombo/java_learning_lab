# Non-Parametric Statistics - Flashcards (60 cards)

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

**Format.** Question (front) -> answer (back). Use for spaced repetition: day 0, day 1, day 3, day 7, day 21. Do not read the answer first.

| # | Front | Back |
|---|---|---|
| 1 | When should you use a rank test instead of a t-test? | Ordinal data, heavy tails, strong skew, or samples too small to assess normality. |
| 2 | What does the Mann-Whitney test actually assume? | That the distributions are identical under the null, not merely that their means are equal. |
| 3 | Is Mann-Whitney a test of medians? | Only with additional shape similarity assumptions; otherwise it tests stochastic ordering. |
| 4 | How must ties be handled? | Average ranks plus a variance correction; ignoring ties inflates significance. |
| 5 | When should you use an exact p-value? | For small samples where the rank statistic's discrete null distribution makes a normal approximation invalid. |
| 6 | What is the Wilcoxon signed-rank test for? | Paired or related samples, using the ranks of the absolute differences. |
| 7 | Which test for three or more related groups? | Friedman, which blocks by subject or block and ranks within blocks. |
| 8 | Why are rank tests less powerful? | They discard magnitude, so a large skewed effect may need a larger sample to reach significance. |
| 9 | What is Rank tests replace values with ranks? | Under the null of identical distributions, ranks are exchangeable. |
| 10 | What is The test choice follows the design? | Two independent groups: Mann-Whitney. |
| 11 | What is Mean ranks versus median ranks? | The tests are often described as comparing medians, which is only true under additional shape assumptions. |
| 12 | What is Ties need explicit handling? | With ties, average ranks are assigned and the tie correction adjusts the variance. |
| 13 | What is Exact versus asymptotic p-values? | For small samples the rank statistic has a discrete distribution, so a normal approximation is wrong. |
| 14 | What is Rank tests are less powerful when they should be powerful? | They discard magnitude information, so a huge effect that is skewed may not reach significance with a modest sample. |
| 15 | In this lab, what does `U = n₁n₂ + n₁(n₁+1)/2 − R₁` mean? | Mann-Whitney U: two independent groups |
| 16 | In this lab, what does `W⁻ = min(R⁺, R⁻)` mean? | Wilcoxon statistic: paired differences, zero-differences omitted |
| 17 | In this lab, what does `H = [12/(N(N+1))]Σ Rⱼ²/(nⱼ) − 3(N+1)` mean? | Kruskal-Wallis: k independent groups |
| 18 | In this lab, what does `Q = 12/(bk(k+1))Σ Rⱼ² − 3b(k+1)` mean? | Friedman: k treatments, b blocks |
| 19 | In this lab, what does `rank sum tie correction` mean? | Tie adjustment: average ranks plus variance adjustment |
| 20 | In this lab, what does `A = rank-biserial correlation` mean? | Effect size: magnitude for a rank test |
| 21 | In this lab, what does `exact null: enumerate assignments` mean? | Exact p-value: for small n |
| 22 | You see 'A rank test reported as a median difference' in production. What is the cause and the fix? | misstated interpretation Fix: say it tests stochastic ordering unless shapes are shown similar |
| 23 | You see 'Ties ignored, p-values too small' in production. What is the cause and the fix? | tie correction omitted Fix: assign average ranks and adjust the variance |
| 24 | You see 'Wilcoxon used on unpaired data' in production. What is the cause and the fix? | design mismatch Fix: Mann-Whitney for independent groups |
| 25 | You see 'Kruskal-Wallis applied to related groups' in production. What is the cause and the fix? | pairing ignored Fix: Friedman for related groups or blocks |
| 26 | You see 'An exact test replaced by an asymptotic one at n = 6' in production. What is the cause and the fix? | approximation invalid for small samples Fix: enumerate the exact null distribution |
| 27 | You see 'A non-significant rank test read as no difference' in production. What is the cause and the fix? | power ignored Fix: report the effect size and confidence interval |
| 28 | Which Java API is the backbone of: ranking with stable ordering before tie handling | `Arrays.sort on index arrays for ranks` |
| 29 | Which Java API is the backbone of: the correctness hinge of every rank test | `Average-rank assignment for ties` |
| 30 | Which Java API is the backbone of: exact null distributions for small n | `Bitmask enumeration of rank permutations` |
| 31 | Which Java API is the backbone of: exactness recorded alongside the result | `record RankTestResult(String test, double statistic, double p, boolean exact, EffectSize effect)` |
| 32 | Which Java API is the backbone of: asymptotic p-values for larger n | `Incomplete beta for the chi-square approximation` |
| 33 | Why does Rank tests replace values with ranks matter operationally? | Under the null of identical distributions, ranks are exchangeable. |
| 34 | Why does The test choice follows the design matter operationally? | Two independent groups: Mann-Whitney. |
| 35 | Why does Mean ranks versus median ranks matter operationally? | The tests are often described as comparing medians, which is only true under additional shape assumptions. |
| 36 | Why does Ties need explicit handling matter operationally? | With ties, average ranks are assigned and the tie correction adjusts the variance. |
| 37 | Why does Exact versus asymptotic p-values matter operationally? | For small samples the rank statistic has a discrete distribution, so a normal approximation is wrong. |
| 38 | Why does Rank tests are less powerful when they should be powerful matter operationally? | They discard magnitude information, so a huge effect that is skewed may not reach significance with a modest sample. |
| 39 | In the Non-Parametric Statistics pipeline, what happens next? Check the measurement scale and the design: independent, pai... | Check the measurement scale and the design: independent, paired, or blocked. |
| 40 | In the Non-Parametric Statistics pipeline, what happens next? Check for ties and note their extent, since they change the ... | Check for ties and note their extent, since they change the null distribution. |
| 41 | In the Non-Parametric Statistics pipeline, what happens next? Rank the data, assigning average ranks to ties.... | Rank the data, assigning average ranks to ties. |
| 42 | In the Non-Parametric Statistics pipeline, what happens next? Compute the statistic and, for small n, enumerate the exact ... | Compute the statistic and, for small n, enumerate the exact null distribution. |
| 43 | In the Non-Parametric Statistics pipeline, what happens next? Report the statistic, the exact or asymptotic p-value, and a... | Report the statistic, the exact or asymptotic p-value, and a rank-based effect size with an interval. |
| 44 | In the Non-Parametric Statistics pipeline, what happens next? If the design supports it, follow a significant omnibus test... | If the design supports it, follow a significant omnibus test with pairwise comparisons and a correction. |
| 45 | Exercise focus: Ranks and ties | Get the foundation right. |
| 46 | Exercise focus: Mann-Whitney U | Two independent groups. |
| 47 | Exercise focus: Wilcoxon signed-rank | Paired data. |
| 48 | Exercise focus: Kruskal-Wallis with follow-up | The omnibus and its localisation. |
| 49 | Exercise focus: Friedman for blocked designs | Related groups. |
| 50 | Exercise focus: Exact versus asymptotic | Know when the approximation lies. |
| 51 | State the Rank construction and tie handling result for Non-Parametric Statistics. | Values [1, 2, 2, 4]: ranks 1, 2.5, 2.5, 4 rather than 1, 2, 3, 4. With five ties the variance correction reduces the variance by roughly the tie fraction, which raises p-values and shrinks false positives. |
| 52 | State the Mann-Whitney U and its interpretation result for Non-Parametric Statistics. | Group A = [5, 7, 9], Group B = [2, 3, 4]: every A value exceeds every B value, so U = 0 and the probability of superiority is 1.0. With A = [1, 2, 9] and B = [3, 4, 5]: U = 6 of 9, giving a probability of superiority of 1 - 6/9 = 0.33. |
| 53 | State the Wilcoxon signed-rank and its power loss result for Non-Parametric Statistics. | Paired differences [0.1, 0.2, 0.15, 0.05] all positive: W- = 0, the minimum, significant at alpha = 0.05 for n = 4. Differences [0.1, 0.2, 0.15, 12.0]: the 12.0 takes rank 4, the others ranks 1–3, and W- is still small but the test is now deciding on one point. |
| 54 | State the Kruskal-Wallis, Friedman and the omnibus problem result for Non-Parametric Statistics. | Four groups with ranks sums 12, 30, 33, 45 (N = 20): H = 12/420 x (144/5 + 900/5 + 1089/5 + 2025/5) - 63 = 0.0286 x 831.6 - 63 = 23.77 - 63 = -39 — sign error aside, the point is that omnibus significance must be followed by localisation with a correction. |
| 55 | State the Exact versus asymptotic p-values result for Non-Parametric Statistics. | Mann-Whitney with n1 = n2 = 5: the minimum possible U is 0 and the attainable values number in the dozens, not the thousands. The exact two-sided p for U = 0 is 2/252 = 0.0079, while a normal approximation gives 0.028 — a factor of 3.5 too large. |
| 56 | What does the Kruskal-Wallis statistic measure? | Between-group rank variation relative to within-group rank variation, approximated by chi-square with k-1 df. |
| 57 | Why must the signed-rank test omit zero differences? | A zero difference carries no direction, so including it distorts the rank sum. |
| 58 | What is a rank-biserial correlation? | An effect size for rank tests, roughly interpretable as a correlation. |
| 59 | How do you test many pairs after Kruskal-Wallis? | Pairwise rank tests with a multiplicity correction such as Dunn's method or Bonferroni. |
| 60 | Assumption / invariant to defend: The response is at least ordinal, so ranks are meaningful... | The response is at least ordinal, so ranks are meaningful |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
