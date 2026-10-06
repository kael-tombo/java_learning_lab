# Bayesian Statistics

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

## 1. The Problem This Solves

You have a prior belief, new evidence, and a parameter you care about. Frequentist testing answers a different question than the one you have.

Bayesian methods let you express prior knowledge, propagate uncertainty and make probability statements about parameters — which is what most business decisions actually require.

## 2. Learning Objectives

- Apply Bayes' theorem to update a belief with evidence
- Use conjugate priors where appropriate and recognise their limits
- Compute a posterior distribution and summarise it properly
- Compute credible intervals and interpret them correctly
- Compare posteriors, such as P(A better than B), by sampling
- Choose and justify a prior, including when to use a weakly informative one

## 3. Core Concepts

### 3.1 Bayes in three lines

Posterior is proportional to likelihood times prior. The posterior is a distribution over the parameter, so you can make direct probability statements about it: P(p > 0.5 | data) is exactly the question you want.

### 3.2 Conjugate priors simplify, sometimes too much

A beta prior with a binomial likelihood yields a beta posterior in closed form. Convenience is real, but conjugate pairs often encode a strong assumption about the prior shape, and modern computation makes the closed form unnecessary.

### 3.3 Weakly informative priors do real work

With little data, the prior dominates; with lots of data, the likelihood overwhelms it. A prior that rules out absurd values — negative rates, probabilities above one, variances of zero — regularises without materially moving the answer when the data is informative.

### 3.4 Prior sensitivity must be checked

Run the analysis under two or more defensible priors. If the conclusion changes, that is a finding to report. 'The prior does not matter' is something to demonstrate, not assert.

### 3.5 Credible intervals are not confidence intervals

A 95% credible interval contains the parameter with probability 0.95 under the posterior. A 95% confidence interval covers the parameter in 95% of repeated samples. Only the first answers 'what is the probability that the parameter is in this range'.

### 3.6 MCMC is a tool, not a method

Posterior draws are computed by a sampler. Convergence diagnostics are not optional: chains that have not mixed produce confident nonsense, and the effective sample size, not the iteration count, is what determines interval accuracy.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `p(θ | data) ∝ p(data | θ) p(θ)` | Bayes' rule | posterior proportional to likelihood times prior |
| `Beta(a + s, b + f)` | Beta-binomial posterior | conjugate update |
| `E[post] = a'/(a' + b')` | Posterior mean | the point estimate |
| `HDI = narrowest interval with 95% posterior mass` | Highest density interval | the honest summary |
| `P(A > B) from posterior draws` | Posterior comparison | the decision-relevant quantity |
| `Posterior predictive: p(y_new | data)` | Predictive distribution | includes parameter uncertainty |
| `P(data) = ∫ p(data | θ) p(θ) dθ` | Evidence | the normalising constant |

## 5. How the Pieces Fit Together

1. State the question as a probability about a parameter, not a test of a null.

2. Choose a prior with a stated rationale, and check at least one alternative.

3. Compute the posterior by closed form, or by sampling with convergence diagnostics.

4. Summarise with a posterior mean or median plus an interval, never a point alone.

5. Answer the decision question directly, such as P(A beats B) or P(effect exceeds a threshold).

6. Produce a prior-predictive check before fitting, to confirm the prior permits data like yours.

## 6. Assumptions and Invariants

- A prior is chosen deliberately and its influence assessed, not defaulted
- The likelihood is correctly specified for the data-generating process
- Convergence of the sampler is demonstrated, not assumed
- Summaries report posterior spread, not just a point estimate
- Prior predictive checks are run so the model is falsifiable before seeing data
- Posterior comparisons account for parameter uncertainty rather than comparing point estimates

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| A confident conclusion from a vague prior | prior not stated or not varied | state the prior rationale and run a sensitivity check |
| MCMC chains have not mixed but the interval looks tight | convergence ignored | check R-hat and effective sample size before summarising |
| 95% credible interval described as 95% confidence | conceptual confusion | credible intervals are statements about the parameter given the model |
| Comparing two point estimates instead of posteriors | parameter uncertainty ignored | sample from both posteriors and compute P(A > B) |
| Prior rules out the observed data | prior predictive not checked | run a prior predictive check and adjust the prior |
| Using conjugate priors only for convenience | the conjugacy encodes a strong prior shape | use a weakly informative prior with modern computation |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `SplittableRandom for MCMC and prior sampling` | reproducible posterior draws |
| `logGamma for the beta and gamma densities` | stable log-density evaluation |
| `Sorted draws plus cumulative mass for an HDI` | the interval containing the specified mass |
| `record PosteriorSummary(double mean, double median, double hdiLow, double hdiHigh, int ess)` | spread reported alongside the point |
| `Empirical quantiles from posterior draw arrays` | posterior comparison by sampling |

## 9. Where This Sits in the Larger System

- **lab03** is the frequentist comparison; the same data supports both readings.
- **lab10** supplies the effect-size thinking that a posterior makes explicit.
- **mlops/lab10** applies P(A beats B) to a live A/B decision.
- **lab08** supplies the design that makes a prior defensible rather than a guess.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Apply Bayes' theorem to update a belief with evidence
- [ ] 0 — cannot yet — Use conjugate priors where appropriate and recognise their limits
- [ ] 0 — cannot yet — Compute a posterior distribution and summarise it properly
- [ ] 0 — cannot yet — Compute credible intervals and interpret them correctly
- [ ] 0 — cannot yet — Compare posteriors, such as P(A better than B), by sampling
- [ ] 0 — cannot yet — Choose and justify a prior, including when to use a weakly informative one

## 11. Summary Checklist

- [ ] I state the prior and why it is defensible for this problem.
- [ ] I run a sensitivity check with an alternative prior.
- [ ] I verify convergence before summarising any sampler output.
- [ ] I report an interval or a posterior distribution, not a point estimate.
- [ ] I run a prior predictive check before fitting.
- [ ] I answer the decision question as a probability about parameters.
