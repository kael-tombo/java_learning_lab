# Experimental Design - Flashcards (60 cards)

**Track:** statistics  |  **Lab:** lab08  |  **Level:** Advanced

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
| 1 | What is an estimand? | The precise quantity you want to estimate, defined before any data is collected. |
| 2 | Why compute sample size before collecting data? | Power is a function of n, effect size and variance; collecting first risks a study that cannot detect the effect you care about. |
| 3 | What does blocking accomplish? | It removes between-unit variation from the error term by randomising within homogeneous groups. |
| 4 | Why run a factorial design rather than separate experiments? | Each treatment is compared across both levels of the other factor, so you estimate main effects and interactions from one set of runs. |
| 5 | When is a randomised block design appropriate? | When units differ systematically, such as machines, operators or locations, and that variation is nuisance rather than of interest. |
| 6 | Why test the interaction first? | A significant interaction means a factor's effect depends on the other's level, so marginal main effects are misleading. |
| 7 | What does confounding prevent? | Separating the effects of two factors that vary together; no sample size can repair it. |
| 8 | How much can blocking reduce sample size? | Often by an order of magnitude, because the blocked variance is subtracted from the error term. |
| 9 | What is The estimand comes first? | Before any sample size, write down the quantity you want to estimate. |
| 10 | What is Power is a design property? | Power depends on the effect you want to detect, the noise, and n. |
| 11 | What is Blocking reduces variance? | Grouping similar units into blocks and randomising within blocks removes the between-unit variation from the error term. |
| 12 | What is Factorial designs answer more per run? | Testing two factors in all four combinations estimates both main effects and their interaction. |
| 13 | What is Interaction changes the analysis? | A significant interaction means main effects must not be interpreted on their own: the effect of one factor depends on the other. |
| 14 | What is Confounding is a design failure? | When two factors vary together, their effects are not separable, and no amount of data fixes it. |
| 15 | In this lab, what does `n = 2 (z_{1α/2} + z_{1−β})² σ² / δ²` mean? | Sample size for means: per-arm, two-sided |
| 16 | In this lab, what does `n = (z_{α/2} sqrt(2 p̄ q̄) + z_{1−β} sqrt(p1q1 + p2q2))² / (p1−p2)²` mean? | Sample size for proportions: pooled under the null |
| 17 | In this lab, what does `SE with blocking: σ sqrt(1/n + 1/N · ρ)` mean? | Blocked variance: rho is the correlation within blocks |
| 18 | In this lab, what does `main effect A = mean(y at A+) − mean(y at A−)` mean? | Factorial main effect: averaged over B levels |
| 19 | In this lab, what does `interaction AB = (E++ − E+-) − (E-+ − E--)` mean? | Interaction contrast: the term usually skipped |
| 20 | In this lab, what does `δ = (z_{1−α/2} + z_{1−β}) σ sqrt(2/n)` mean? | Minimum detectable effect: what your design can see |
| 21 | In this lab, what does `VIF / variance share = 1 − R²_block` mean? | Variance reduction from blocking: quantifies the gain |
| 22 | You see 'The study ran out of power and concluded nothing' in production. What is the cause and the fix? | sample size never computed Fix: compute power from alpha, MDE and pilot variance before starting |
| 23 | You see 'A treatment effect is smaller than machine variation' in production. What is the cause and the fix? | no blocking Fix: block on machine, operator and batch, cutting variance substantially |
| 24 | You see 'Main effects reported despite a significant interaction' in production. What is the cause and the fix? | interaction not tested Fix: test the interaction first and interpret conditionally |
| 25 | You see 'Two factors are confounded' in production. What is the cause and the fix? | design coupled their levels Fix: replicate cells or redesign; no sample size fixes this |
| 26 | You see 'Power computed from a pilot variance that is too small' in production. What is the cause and the fix? | unreliable pilot estimate Fix: inflate the pilot variance before computing n |
| 27 | You see 'Randomisation done by hand or by a non-random method' in production. What is the cause and the fix? | randomisation not genuinely random Fix: use a seeded generator with a recorded seed and verify assignment counts |
| 28 | Which Java API is the backbone of: reproducible randomisation | `SplittableRandom with a recorded seed` |
| 29 | Which Java API is the backbone of: z-values for power and sample size | `Normal quantile function` |
| 30 | Which Java API is the backbone of: variance reduction visible in the error term | `Blocked arrays for the analysis` |
| 31 | Which Java API is the backbone of: the plan, recorded before data | `record Design(int factors, int[] levelsPerFactor, int nPerCell, String estimand)` |
| 32 | Which Java API is the backbone of: power computed for the specified alternative | `Non-central t or normal for power` |
| 33 | Why does The estimand comes first matter operationally? | Before any sample size, write down the quantity you want to estimate. |
| 34 | Why does Power is a design property matter operationally? | Power depends on the effect you want to detect, the noise, and n. |
| 35 | Why does Blocking reduces variance matter operationally? | Grouping similar units into blocks and randomising within blocks removes the between-unit variation from the error term. |
| 36 | Why does Factorial designs answer more per run matter operationally? | Testing two factors in all four combinations estimates both main effects and their interaction. |
| 37 | Why does Interaction changes the analysis matter operationally? | A significant interaction means main effects must not be interpreted on their own: the effect of one factor depends on the other. |
| 38 | Why does Confounding is a design failure matter operationally? | When two factors vary together, their effects are not separable, and no amount of data fixes it. |
| 39 | In the Experimental Design pipeline, what happens next? Write the estimand and the unit of randomisation; both const... | Write the estimand and the unit of randomisation; both constrain everything else. |
| 40 | In the Experimental Design pipeline, what happens next? Identify blocking variables and nuisance factors to hold fix... | Identify blocking variables and nuisance factors to hold fixed. |
| 41 | In the Experimental Design pipeline, what happens next? Choose the design: completely randomised, randomised block, ... | Choose the design: completely randomised, randomised block, or factorial. |
| 42 | In the Experimental Design pipeline, what happens next? Compute sample size from alpha, power and the minimum effect... | Compute sample size from alpha, power and the minimum effect worth detecting. |
| 43 | In the Experimental Design pipeline, what happens next? Randomise, execute, and verify randomisation actually happen... | Randomise, execute, and verify randomisation actually happened. |
| 44 | In the Experimental Design pipeline, what happens next? Pre-specify the analysis: main effects, interactions and pla... | Pre-specify the analysis: main effects, interactions and planned contrasts. |
| 45 | Exercise focus: Sample size for means and proportions | The arithmetic behind power. |
| 46 | Exercise focus: Blocking and variance reduction | Quantify the gain. |
| 47 | Exercise focus: Factorial design analysis | Main effects and interaction. |
| 48 | Exercise focus: Confounding demonstration | What no sample size can fix. |
| 49 | Exercise focus: Power curves | Design against a range of effects. |
| 50 | Exercise focus: Simulation study | Validate the design end to end. |
| 51 | State the Sample size for means result for Experimental Design. | delta = 0.5 sigma, alpha = 0.05, power = 0.8: n = 2 x 7.85 / 0.25 = 63 per arm. With blocking where within-block correlation rho = 0.6, the variance falls to 1 - 0.6 = 0.4 of the unblocked value, so n drops to about 25. |
| 52 | State the Sample size for proportions result for Experimental Design. | p1 = 0.10, p2 = 0.11: n ≈ 15,500 per arm. p1 = 0.10, p2 = 0.12: n ≈ 3,900. p1 = 0.10, p2 = 0.20: n ≈ 380. A tenfold difference in required n across three targets that all sound reasonable. |
| 53 | State the Blocking and the variance reduction result for Experimental Design. | Machine-to-machine variation with rho = 0.5: half the error variance is removed, so the same power needs half the observations. With rho = 0.9, a quarter of the sample — which is why blocking on batch or machine is standard practice in manufacturing experiments. |
| 54 | State the Factorial effects and interaction result for Experimental Design. | Cells: (A+B+) = 10, (A+B-) = 8, (A-B+) = 5, (A-B-) = 2. Main effect of A = 7 - 3.5 = 3.5, which says 'A helps'. Interaction = (10-8) - (5-2) = -1, so A actually helps at B+ and hurts at B-. The marginal main effect is meaningless here. |
| 55 | State the Confounding and identifiability result for Experimental Design. | Training data in a study where price was only ever tested at one level per region: price and region effects are confounded, and the price coefficient absorbs regional differences. No sample size fixes this; only varying price within region does. |
| 56 | Why might a pilot variance underestimate the needed sample size? | Pilots are small, so variance estimates are noisy and often biased low; inflate before computing n. |
| 57 | What is a completely randomised design for? | Homogeneous units, or when no systematic nuisance variation exists to block on. |
| 58 | What does one degree of replication per cell buy? | An error term; without it the interaction cannot be separated from residual variation. |
| 59 | How do you verify randomisation happened? | Check assignment counts per arm against expected proportions, as in a sample-ratio check. |
| 60 | Assumption / invariant to defend: The estimand is defined before data collection and is estimable under ... | The estimand is defined before data collection and is estimable under the design |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
