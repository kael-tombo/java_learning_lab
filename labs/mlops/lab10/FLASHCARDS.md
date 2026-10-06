# A/B Testing & Experimentation - Flashcards (60 cards)

**Track:** mlops  |  **Lab:** lab10  |  **Level:** Advanced

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
| 1 | What makes an A/B test valid? | Random, stable assignment of units to arms; everything else is analysis. |
| 2 | What is power? | The probability of detecting a real effect of a given size, given the sample size. |
| 3 | What is MDE? | The smallest effect the test can detect at your sample size; it decides how long you must run. |
| 4 | Why is peeking a problem? | Each look inflates the false positive rate, so crossing 0.05 early is often just noise. |
| 5 | What are guardrail metrics? | Non-inferiority bounds on metrics that must not degrade, checked continuously with a stop rule. |
| 6 | What is sample ratio mismatch? | The arms receiving traffic in different proportions than designed, which invalidates the analysis. |
| 7 | When do you use a shadow test? | When user-facing exposure is unacceptable; it measures score distribution and latency but not business outcomes. |
| 8 | Statistical versus practical significance? | Statistical says the effect is unlikely to be noise; practical says it is worth the rollout cost. |
| 9 | What is Randomisation is the whole design? | Everything else is bookkeeping. |
| 10 | What is Power, MDE and horizon? | Power is the probability of detecting a real effect. |
| 11 | What is Peeking is a real problem? | Checking significance daily and stopping when it crosses 0. |
| 12 | What is Guardrail metrics protect the downside? | A model can improve conversion and increase complaints, refunds or latency. |
| 13 | What is Shadow tests when exposure is unacceptable? | A shadow test scores the challenger on live traffic without affecting decisions. |
| 14 | What is Practical versus statistical significance? | A 0. |
| 15 | In this lab, what does `n = 2 (z_{1-a/2} + z_{1-b})^2 sigma^2 / delta^2` mean? | Sample size for means: the MDE-driven horizon |
| 16 | In this lab, what does `z = (p1 - p2) / sqrt(p1(1-p1)/n1 + p2(1-p2)/n2)` mean? | Two-proportion z: standard A/B test |
| 17 | In this lab, what does `power = P(reject \| true effect)` mean? | Power: 1 - beta, fixed before launch |
| 18 | In this lab, what does `delta_MDE = (z_{1-a/2} + z_{1-b}) sigma sqrt(2/n)` mean? | MDE: the effect you can actually see |
| 19 | In this lab, what does `false positive with peeking ~ alpha x looks` mean? | Peeking inflation: why fixed horizons or sequential tests |
| 20 | In this lab, what does `guardrail breach: lower bound < -delta_guard` mean? | Non-inferiority: stop regardless of primary metric |
| 21 | You see 'Test declared a winner after 3 days of daily peeking' in production. What is the cause and the fix? | repeated uncorrected looks Fix: fixed horizon or a sequential test with alpha control |
| 22 | You see 'Sample ratio mismatch not checked' in production. What is the cause and the fix? | assignment bug or bot traffic Fix: assert SRM on every check before looking at metrics |
| 23 | You see 'No difference found and the test shipped anyway' in production. What is the cause and the fix? | underpowered design Fix: compute power and MDE before launch, not after |
| 24 | You see 'Conversion up 40%, complaints up 300%' in production. What is the cause and the fix? | no guardrails Fix: non-inferiority guardrails with a stop rule |
| 25 | You see 'Result depends on excluding outliers after the fact' in production. What is the cause and the fix? | post-hoc filtering Fix: pre-register inclusion and exclusion rules |
| 26 | You see 'Winning arm introduced novelty effects' in production. What is the cause and the fix? | short horizon on a new experience Fix: extend the horizon or exclude novelty-sensitive segments |
| 27 | You see 'Users in both arms' in production. What is the cause and the fix? | non-sticky assignment Fix: hash on user id, not session |
| 28 | Which Java API is the backbone of: assignment without state and stable across sessions | `SplittableRandom / stable hash on user id` |
| 29 | Which Java API is the backbone of: concurrent metric counters with SRM checks | `AtomicLongArray per arm per metric` |
| 30 | Which Java API is the backbone of: z-values for power and MDE | `NormalDistribution quantile function` |
| 31 | Which Java API is the backbone of: the pre-registered plan | `record Experiment(String id, String primaryMetric, int alpha, double power, Instant horizonEnd)` |
| 32 | Which Java API is the backbone of: non-inferiority checks that can stop early | `Interleaved guardrail evaluation` |
| 33 | Why does Randomisation is the whole design matter operationally? | Everything else is bookkeeping. |
| 34 | Why does Power, MDE and horizon matter operationally? | Power is the probability of detecting a real effect. |
| 35 | Why does Peeking is a real problem matter operationally? | Checking significance daily and stopping when it crosses 0. |
| 36 | Why does Guardrail metrics protect the downside matter operationally? | A model can improve conversion and increase complaints, refunds or latency. |
| 37 | Why does Shadow tests when exposure is unacceptable matter operationally? | A shadow test scores the challenger on live traffic without affecting decisions. |
| 38 | Why does Practical versus statistical significance matter operationally? | A 0. |
| 39 | In the A/B Testing & Experimentation pipeline, what happens next? State the primary metric, the minimum detectable effect, alp... | State the primary metric, the minimum detectable effect, alpha, power and the horizon before launching. |
| 40 | In the A/B Testing & Experimentation pipeline, what happens next? Define guardrail metrics with non-inferiority bounds and a s... | Define guardrail metrics with non-inferiority bounds and a stop rule. |
| 41 | In the A/B Testing & Experimentation pipeline, what happens next? Assign traffic by a stable hash on user id, with an exposure... | Assign traffic by a stable hash on user id, with an exposure fraction you can ramp. |
| 42 | In the A/B Testing & Experimentation pipeline, what happens next? Pre-register the analysis: the test statistic, the horizon a... | Pre-register the analysis: the test statistic, the horizon and the stopping rule. |
| 43 | In the A/B Testing & Experimentation pipeline, what happens next? Monitor guardrails continuously; check the primary metric on... | Monitor guardrails continuously; check the primary metric only at planned look points. |
| 44 | In the A/B Testing & Experimentation pipeline, what happens next? Decide on effect size with an interval, in business units, n... | Decide on effect size with an interval, in business units, not on the p-value alone. |
| 45 | Exercise focus: Power and sample size | Design before you launch. |
| 46 | Exercise focus: Two-arm analysis | The statistics, done correctly. |
| 47 | Exercise focus: SRM detection | Catch the bug that invalidates everything. |
| 48 | Exercise focus: Peeking and sequential tests | Stop lying to yourself. |
| 49 | Exercise focus: Guardrails | Protect the downside. |
| 50 | Exercise focus: Shadow test | Learn something without exposure. |
| 51 | State the Sample size and MDE result for A/B Testing & Experimentation. | Baseline conversion 4%, want to detect a 0.2% relative lift (4.008% to 4.016%), alpha 0.05, power 0.8: n is roughly 190k per arm, about 8 days at 1M sessions/day. An MDE of 0.5% would need 12k per arm, under a day. |
| 52 | State the Two-proportion significance result for A/B Testing & Experimentation. | p1 = 0.0402 with n1 = 200k, p2 = 0.0400 with n2 = 200k: p_pool = 0.0401, SE = 0.000632, z = 0.317, p-value 0.75. Nowhere near significance; the MDE at this n is about 0.18 percentage points. |
| 53 | State the Peeking inflates the false positive rate result for A/B Testing & Experimentation. | A test run for 14 days with daily significance checks has an effective false positive rate near 50% if run until 'significant'. That is how teams ship noise. |
| 54 | State the Guardrail non-inferiority result for A/B Testing & Experimentation. | Latency guardrail: control p99 180 ms, treatment 196 ms, delta_guard 10%. Effect +16 ms is +8.9%, and with a tight interval the lower bound stays above +10 ms, so it passes. At +25 ms the bound crosses and the test stops. |
| 55 | State the Sequential testing with alpha control result for A/B Testing & Experimentation. | O'Brien-Fleming spends very little alpha early and most at the end, so an early stop requires an enormous effect. Pocock spends evenly, so early stops are easier but the final test is weaker. |
| 56 | How do you control error rate with early stopping? | Use a sequential design such as group sequential boundaries or always-valid confidence sequences. |
| 57 | What does novelty effect look like? | An early spike in the treatment arm that decays as users adapt; a short horizon will call it a win. |
| 58 | Why hash on user id rather than session? | So a user stays in one arm; otherwise cross-arm contamination dilutes and confuses the result. |
| 59 | How do you choose the horizon? | From the sample size your MDE and power require; there is no other honest way. |
| 60 | Assumption / invariant to defend: Assignment is random, stable per unit, and independent of the outcome... | Assignment is random, stable per unit, and independent of the outcome |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
