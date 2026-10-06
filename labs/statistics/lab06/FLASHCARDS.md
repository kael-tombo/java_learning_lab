# Bayesian Statistics - Flashcards (60 cards)

**Track:** statistics  |  **Lab:** lab06  |  **Level:** Advanced

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
| 1 | What does a credible interval mean? | The posterior places 95% probability on the parameter being in that range, given the model and data. |
| 2 | How does it differ from a confidence interval? | A confidence interval concerns repeated sampling; a credible interval is a probability statement about the parameter itself. |
| 3 | What is conjugate convenience hiding? | That the conjugate prior is a specific shape, often stronger than intended. |
| 4 | When does the prior matter most? | When the data is uninformative; with lots of data the likelihood overwhelms any reasonable prior. |
| 5 | Why run a prior predictive check? | To see whether the prior permits data like yours, before you look at the real data. |
| 6 | What does R-hat measure? | Whether independent chains agree; values near 1 indicate convergence, higher values indicate mixing problems. |
| 7 | What is effective sample size? | The number of effectively independent draws, which determines interval accuracy far better than iteration count. |
| 8 | How do you compare two models with posteriors? | Sample from both and compute P(A > B), which accounts for parameter uncertainty. |
| 9 | What is Bayes in three lines? | Posterior is proportional to likelihood times prior. |
| 10 | What is Conjugate priors simplify, sometimes too much? | A beta prior with a binomial likelihood yields a beta posterior in closed form. |
| 11 | What is Weakly informative priors do real work? | With little data, the prior dominates; with lots of data, the likelihood overwhelms it. |
| 12 | What is Prior sensitivity must be checked? | Run the analysis under two or more defensible priors. |
| 13 | What is Credible intervals are not confidence intervals? | A 95% credible interval contains the parameter with probability 0. |
| 14 | What is MCMC is a tool, not a method? | Posterior draws are computed by a sampler. |
| 15 | In this lab, what does `p(θ \| data) ∝ p(data \| θ) p(θ)` mean? | Bayes' rule: posterior proportional to likelihood times prior |
| 16 | In this lab, what does `Beta(a + s, b + f)` mean? | Beta-binomial posterior: conjugate update |
| 17 | In this lab, what does `E[post] = a'/(a' + b')` mean? | Posterior mean: the point estimate |
| 18 | In this lab, what does `HDI = narrowest interval with 95% posterior mass` mean? | Highest density interval: the honest summary |
| 19 | In this lab, what does `P(A > B) from posterior draws` mean? | Posterior comparison: the decision-relevant quantity |
| 20 | In this lab, what does `Posterior predictive: p(y_new \| data)` mean? | Predictive distribution: includes parameter uncertainty |
| 21 | In this lab, what does `P(data) = ∫ p(data \| θ) p(θ) dθ` mean? | Evidence: the normalising constant |
| 22 | You see 'A confident conclusion from a vague prior' in production. What is the cause and the fix? | prior not stated or not varied Fix: state the prior rationale and run a sensitivity check |
| 23 | You see 'MCMC chains have not mixed but the interval looks tight' in production. What is the cause and the fix? | convergence ignored Fix: check R-hat and effective sample size before summarising |
| 24 | You see '95% credible interval described as 95% confidence' in production. What is the cause and the fix? | conceptual confusion Fix: credible intervals are statements about the parameter given the model |
| 25 | You see 'Comparing two point estimates instead of posteriors' in production. What is the cause and the fix? | parameter uncertainty ignored Fix: sample from both posteriors and compute P(A > B) |
| 26 | You see 'Prior rules out the observed data' in production. What is the cause and the fix? | prior predictive not checked Fix: run a prior predictive check and adjust the prior |
| 27 | You see 'Using conjugate priors only for convenience' in production. What is the cause and the fix? | the conjugacy encodes a strong prior shape Fix: use a weakly informative prior with modern computation |
| 28 | Which Java API is the backbone of: reproducible posterior draws | `SplittableRandom for MCMC and prior sampling` |
| 29 | Which Java API is the backbone of: stable log-density evaluation | `logGamma for the beta and gamma densities` |
| 30 | Which Java API is the backbone of: the interval containing the specified mass | `Sorted draws plus cumulative mass for an HDI` |
| 31 | Which Java API is the backbone of: spread reported alongside the point | `record PosteriorSummary(double mean, double median, double hdiLow, double hdiHigh, int ess)` |
| 32 | Which Java API is the backbone of: posterior comparison by sampling | `Empirical quantiles from posterior draw arrays` |
| 33 | Why does Bayes in three lines matter operationally? | Posterior is proportional to likelihood times prior. |
| 34 | Why does Conjugate priors simplify, sometimes too much matter operationally? | A beta prior with a binomial likelihood yields a beta posterior in closed form. |
| 35 | Why does Weakly informative priors do real work matter operationally? | With little data, the prior dominates; with lots of data, the likelihood overwhelms it. |
| 36 | Why does Prior sensitivity must be checked matter operationally? | Run the analysis under two or more defensible priors. |
| 37 | Why does Credible intervals are not confidence intervals matter operationally? | A 95% credible interval contains the parameter with probability 0. |
| 38 | Why does MCMC is a tool, not a method matter operationally? | Posterior draws are computed by a sampler. |
| 39 | In the Bayesian Statistics pipeline, what happens next? State the question as a probability about a parameter, not a... | State the question as a probability about a parameter, not a test of a null. |
| 40 | In the Bayesian Statistics pipeline, what happens next? Choose a prior with a stated rationale, and check at least o... | Choose a prior with a stated rationale, and check at least one alternative. |
| 41 | In the Bayesian Statistics pipeline, what happens next? Compute the posterior by closed form, or by sampling with co... | Compute the posterior by closed form, or by sampling with convergence diagnostics. |
| 42 | In the Bayesian Statistics pipeline, what happens next? Summarise with a posterior mean or median plus an interval, ... | Summarise with a posterior mean or median plus an interval, never a point alone. |
| 43 | In the Bayesian Statistics pipeline, what happens next? Answer the decision question directly, such as P(A beats B) ... | Answer the decision question directly, such as P(A beats B) or P(effect exceeds a threshold). |
| 44 | In the Bayesian Statistics pipeline, what happens next? Produce a prior-predictive check before fitting, to confirm ... | Produce a prior-predictive check before fitting, to confirm the prior permits data like yours. |
| 45 | Exercise focus: Conjugate beta-binomial | The arithmetic, then the intuition. |
| 46 | Exercise focus: Prior sensitivity | Does the prior matter here? |
| 47 | Exercise focus: Prior predictive checks | Test the model before the data. |
| 48 | Exercise focus: MCMC with diagnostics | Do not trust unverified draws. |
| 49 | Exercise focus: Posterior comparison | Answer the decision question. |
| 50 | Exercise focus: Posterior predictive checking | Test the model, not just the parameters. |
| 51 | State the Conjugate beta-binomial update result for Bayesian Statistics. | Prior Beta(1,1) (uniform), 240 successes and 760 failures: posterior Beta(241,761), mean 0.2405, 95% HDI roughly [0.212, 0.271]. Prior Beta(20,20) with the same data: mean 0.2616 — a different answer, which is a sensitivity finding to report. |
| 52 | State the Prior versus likelihood influence result for Bayesian Statistics. | Prior Beta(1,1) with n = 20 observations: posterior mean is (1+10)/22 = 0.500, entirely prior-driven. With n = 10,000: (1+4900)/10002 = 0.4900, where the prior is negligible. Same prior, completely different reliance. |
| 53 | State the Credible intervals and highest density intervals result for Bayesian Statistics. | Posterior samples concentrated near 0.1 with a long right tail: equal-tailed 95% is roughly [0.08, 0.22], while the HDI is roughly [0.086, 0.135]. The latter is the honest summary of where the mass is. |
| 54 | State the Posterior comparison for decisions result for Bayesian Statistics. | Posterior A: mean 0.2405, sd 0.015; posterior B: mean 0.2400, sd 0.020. The means differ by 0.0005, yet sampling gives P(A > B) ≈ 0.48. The honest answer is 'a coin flip', not 'A is marginally better'. |
| 55 | State the Prior predictive check and MCMC diagnostics result for Bayesian Statistics. | Prior Beta(0.1, 0.1) with 5,000 observed successes out of 10,000: the prior predicts rates near 0 or 1, so simulated datasets look nothing like yours. A Beta(1,1) or a weakly informative rate prior passes the check. |
| 56 | Why not just compare posterior means? | Means hide uncertainty; two posteriors with the same mean can imply very different odds. |
| 57 | What is posterior predictive checking? | Comparing data simulated from the posterior to the observed data, testing the model rather than the parameters. |
| 58 | What makes a prior weakly informative? | It encodes genuine prior knowledge while regularising away absurd values without dominating informative data. |
| 59 | What is the evidence P(data)? | The normalising constant, which lets you compare models by Bayes factors but is hard to compute. |
| 60 | Assumption / invariant to defend: A prior is chosen deliberately and its influence assessed, not default... | A prior is chosen deliberately and its influence assessed, not defaulted |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
