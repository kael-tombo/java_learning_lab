# Probability Distributions

**Track:** statistics  |  **Lab:** lab02  |  **Level:** Foundational

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

You need to say how likely things are: a wait time, a count of events in an hour, a measurement that clusters around a mean.

Choosing the wrong distribution turns a real signal into noise. Knowing which family a process belongs to is what lets you compute probabilities at all.

## 2. Learning Objectives

- Distinguish discrete from continuous distributions and pick between them
- Implement normal, binomial, Poisson and exponential densities and CDFs
- Compute CDF values without a lookup table, using approximations with stated error
- Sample from each distribution with a correct, seedable algorithm
- Use the central limit theorem to justify normal approximations
- Recognise when a Poisson assumption (constant rate, independent events) is violated

## 3. Core Concepts

### 3.1 Discrete versus continuous

Discrete distributions put mass on countable outcomes (counts), continuous ones describe measurements over a range. Normal and exponential are continuous; binomial and Poisson are discrete. Mixing them up is why probabilities come out above one.

### 3.2 Normal distribution

The workhorse for continuous data, symmetric with mean μ and variance σ². Its practical importance comes from the central limit theorem: sums of independent, non-identically distributed variables tend toward normal, which is why it appears everywhere.

### 3.3 Binomial distribution

Counts of successes in n independent Bernoulli trials. It is the right model for a proportion or a small count with a known rate. The normal approximation to the binomial needs np and n(1−p) both above about 5.

### 3.4 Poisson distribution

Counts of events in a fixed interval at a constant rate with independent occurrences. If the rate varies with time (rush hour, seasonality) the Poisson assumption breaks and the count is overdispersed — a real risk in operational data.

### 3.5 Exponential distribution

Waiting time between Poisson events, memoryless. It is the basis of exponential backoff in retries, and its memoryless property is exactly why backoff has that shape.

### 3.6 Sampling and simulation

Sampling algorithms let you reason about distributions you cannot evaluate in closed form, and they let you estimate quantities analytically available. Seeded sampling makes Monte Carlo estimates reproducible, which is what turns an estimate into a testable result.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `f(x) = exp(−(x−μ)²/2σ²) / (σ√2π)` | Normal PDF | continuous density |
| `Φ(z) = P(Z ≤ z), z = (x−μ)/σ` | Normal CDF | standardised to N(0,1) |
| `P(X = k) = C(n,k) p^k (1−p)^(n−k)` | Binomial PMF | k successes in n trials |
| `P(X = k) = λ^k e^−λ / k!` | Poisson PMF | events in an interval at rate λ |
| `f(x) = λ e^−λx` | Exponential PDF | waiting time, x ≥ 0 |
| `P(T > t) = e^−λt` | Survival function | memoryless property |
| `X̃ → N(nμ, nσ²/n)` | CLT | justifies normal approximations |
| `u1, u2 ~ U(0,1) => z = sqrt(−2 ln u1) cos(2π u2)` | Box-Muller | normal sampling |

## 5. How the Pieces Fit Together

1. Classify the variable: a count, a waiting time, or a continuous measurement.

2. Check the distributional assumptions: independence, constant rate, finite variance.

3. Estimate parameters by maximum likelihood or method of moments, and state which.

4. Evaluate the CDF at the decision point rather than reasoning in densities.

5. Approximate where closed forms do not exist, and state the error bound you can justify.

6. Sample with a seeded generator when you need to simulate rather than evaluate.

## 6. Assumptions and Invariants

- Binomial: fixed n, independent trials, constant success probability
- Poisson: constant rate λ, independent occurrences, counts in a fixed interval
- Exponential: the underlying process is Poisson, so waiting times are memoryless
- Normal approximations need a variance that exists and a sufficiently large n
- Parameter estimates treat the observed sample as i.i.d.
- Sampling algorithms use a seeded generator so results are reproducible

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| A Poisson count is far more variable than predicted | the rate is not constant, so events cluster | use a negative binomial or model rate variation |
| Normal approximation used with np below 5 | approximation invalid in the tail that matters | check the continuity correction and both expected counts |
| Densities compared instead of CDFs | density values are not probabilities | integrate to a CDF before drawing a conclusion |
| A simulation gives different answers each run | unseeded generator | seed it; an unreproducible estimate cannot be checked |
| Exponential used for a rate that varies with time of day | non-homogeneous process | split the interval or use a time-varying hazard |
| Binomial applied to dependent events | independence assumption violated | correlated trials inflate variance; use a different model |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `SplittableRandom / Random with an explicit seed` | reproducible sampling |
| `Math.log1p, Math.expm1 for CDF tails` | avoiding catastrophic cancellation in the tails |
| `Box-Muller transform for normal sampling` | two uniforms to two normals, exactly |
| `Incomplete gamma for the Poisson CDF` | avoiding factorial overflow for large k |
| `record Estimate(String name, double value, double lower, double upper)` | Monte Carlo estimates with intervals |

## 9. Where This Sits in the Larger System

- **lab03** uses these CDFs to compute p-values for tests.
- **lab09** needs them when checking normality before a rank test.
- **lab10** needs them to compute the standard error of an estimate.
- **lab07** uses the exponential distribution as the basis for backoff.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Distinguish discrete from continuous distributions and pick between them
- [ ] 0 — cannot yet — Implement normal, binomial, Poisson and exponential densities and CDFs
- [ ] 0 — cannot yet — Compute CDF values without a lookup table, using approximations with stated error
- [ ] 0 — cannot yet — Sample from each distribution with a correct, seedable algorithm
- [ ] 0 — cannot yet — Use the central limit theorem to justify normal approximations
- [ ] 0 — cannot yet — Recognise when a Poisson assumption (constant rate, independent events) is violated

## 11. Summary Checklist

- [ ] I classify the variable before choosing a distribution.
- [ ] I check the distributional assumptions, especially rate constancy for Poisson.
- [ ] I evaluate CDFs rather than comparing densities.
- [ ] My approximations state their validity conditions.
- [ ] All sampling is seeded and reproducible.
- [ ] I check for overdispersion before trusting a Poisson model.
