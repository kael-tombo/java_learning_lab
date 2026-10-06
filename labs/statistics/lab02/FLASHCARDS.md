# Probability Distributions - Flashcards (60 cards)

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

**Format.** Question (front) -> answer (back). Use for spaced repetition: day 0, day 1, day 3, day 7, day 21. Do not read the answer first.

| # | Front | Back |
|---|---|---|
| 1 | When is Poisson appropriate? | Counts of events in a fixed interval at a constant rate with independent occurrences. |
| 2 | What does overdispersion indicate? | The rate is not constant, so events cluster and the variance exceeds the mean. |
| 3 | Why does the normal approximation to the binomial need np and n(1−p) above 5? | The approximation is asymptotic, and small expected counts in a tail make it invalid exactly where decisions are made. |
| 4 | What is the memoryless property? | P(T > s + t \| T > s) = P(T > t), which is why exponential backoff has that shape. |
| 5 | What does the central limit theorem actually say? | Sums of independent, non-identically distributed variables with finite variance tend toward normal as n grows. |
| 6 | How do you sample from a normal distribution? | Box-Muller: transform two independent uniforms into two normals. |
| 7 | Why compare CDFs rather than densities? | A density value is not a probability; the CDF is the cumulative probability. |
| 8 | When does an exponential distribution fail? | When the event rate varies with time, such as rush hour arrivals. |
| 9 | What is Discrete versus continuous? | Discrete distributions put mass on countable outcomes (counts), continuous ones describe measurements over a range. |
| 10 | What is Normal distribution? | The workhorse for continuous data, symmetric with mean μ and variance σ². |
| 11 | What is Binomial distribution? | Counts of successes in n independent Bernoulli trials. |
| 12 | What is Poisson distribution? | Counts of events in a fixed interval at a constant rate with independent occurrences. |
| 13 | What is Exponential distribution? | Waiting time between Poisson events, memoryless. |
| 14 | What is Sampling and simulation? | Sampling algorithms let you reason about distributions you cannot evaluate in closed form, and they let you estimate quantities analytically available. |
| 15 | In this lab, what does `f(x) = exp(−(x−μ)²/2σ²) / (σ√2π)` mean? | Normal PDF: continuous density |
| 16 | In this lab, what does `Φ(z) = P(Z ≤ z), z = (x−μ)/σ` mean? | Normal CDF: standardised to N(0,1) |
| 17 | In this lab, what does `P(X = k) = C(n,k) p^k (1−p)^(n−k)` mean? | Binomial PMF: k successes in n trials |
| 18 | In this lab, what does `P(X = k) = λ^k e^−λ / k!` mean? | Poisson PMF: events in an interval at rate λ |
| 19 | In this lab, what does `f(x) = λ e^−λx` mean? | Exponential PDF: waiting time, x ≥ 0 |
| 20 | In this lab, what does `P(T > t) = e^−λt` mean? | Survival function: memoryless property |
| 21 | In this lab, what does `X̃ → N(nμ, nσ²/n)` mean? | CLT: justifies normal approximations |
| 22 | In this lab, what does `u1, u2 ~ U(0,1) => z = sqrt(−2 ln u1) cos(2π u2)` mean? | Box-Muller: normal sampling |
| 23 | You see 'A Poisson count is far more variable than predicted' in production. What is the cause and the fix? | the rate is not constant, so events cluster Fix: use a negative binomial or model rate variation |
| 24 | You see 'Normal approximation used with np below 5' in production. What is the cause and the fix? | approximation invalid in the tail that matters Fix: check the continuity correction and both expected counts |
| 25 | You see 'Densities compared instead of CDFs' in production. What is the cause and the fix? | density values are not probabilities Fix: integrate to a CDF before drawing a conclusion |
| 26 | You see 'A simulation gives different answers each run' in production. What is the cause and the fix? | unseeded generator Fix: seed it; an unreproducible estimate cannot be checked |
| 27 | You see 'Exponential used for a rate that varies with time of day' in production. What is the cause and the fix? | non-homogeneous process Fix: split the interval or use a time-varying hazard |
| 28 | You see 'Binomial applied to dependent events' in production. What is the cause and the fix? | independence assumption violated Fix: correlated trials inflate variance; use a different model |
| 29 | Which Java API is the backbone of: reproducible sampling | `SplittableRandom / Random with an explicit seed` |
| 30 | Which Java API is the backbone of: avoiding catastrophic cancellation in the tails | `Math.log1p, Math.expm1 for CDF tails` |
| 31 | Which Java API is the backbone of: two uniforms to two normals, exactly | `Box-Muller transform for normal sampling` |
| 32 | Which Java API is the backbone of: avoiding factorial overflow for large k | `Incomplete gamma for the Poisson CDF` |
| 33 | Which Java API is the backbone of: Monte Carlo estimates with intervals | `record Estimate(String name, double value, double lower, double upper)` |
| 34 | Why does Discrete versus continuous matter operationally? | Discrete distributions put mass on countable outcomes (counts), continuous ones describe measurements over a range. |
| 35 | Why does Normal distribution matter operationally? | The workhorse for continuous data, symmetric with mean μ and variance σ². |
| 36 | Why does Binomial distribution matter operationally? | Counts of successes in n independent Bernoulli trials. |
| 37 | Why does Poisson distribution matter operationally? | Counts of events in a fixed interval at a constant rate with independent occurrences. |
| 38 | Why does Exponential distribution matter operationally? | Waiting time between Poisson events, memoryless. |
| 39 | Why does Sampling and simulation matter operationally? | Sampling algorithms let you reason about distributions you cannot evaluate in closed form, and they let you estimate quantities analytically available. |
| 40 | In the Probability Distributions pipeline, what happens next? Classify the variable: a count, a waiting time, or a continu... | Classify the variable: a count, a waiting time, or a continuous measurement. |
| 41 | In the Probability Distributions pipeline, what happens next? Check the distributional assumptions: independence, constant... | Check the distributional assumptions: independence, constant rate, finite variance. |
| 42 | In the Probability Distributions pipeline, what happens next? Estimate parameters by maximum likelihood or method of momen... | Estimate parameters by maximum likelihood or method of moments, and state which. |
| 43 | In the Probability Distributions pipeline, what happens next? Evaluate the CDF at the decision point rather than reasoning... | Evaluate the CDF at the decision point rather than reasoning in densities. |
| 44 | In the Probability Distributions pipeline, what happens next? Approximate where closed forms do not exist, and state the e... | Approximate where closed forms do not exist, and state the error bound you can justify. |
| 45 | In the Probability Distributions pipeline, what happens next? Sample with a seeded generator when you need to simulate rat... | Sample with a seeded generator when you need to simulate rather than evaluate. |
| 46 | Exercise focus: Implement the four distributions | PDF, CDF and PMF for each. |
| 47 | Exercise focus: Numerical stability | Break and fix the direct formulas. |
| 48 | Exercise focus: Seeded sampling and validation | Make simulation trustworthy. |
| 49 | Exercise focus: Normal approximation with validity checks | Know when it is allowed. |
| 50 | Exercise focus: Central limit theorem demonstration | See non-normal data become normal in the mean. |
| 51 | Exercise focus: Poisson overdispersion | Find the violated assumption. |
| 52 | State the Log-space evaluation and cancellation result for Probability Distributions. | Poisson with lambda = 5, k = 40: P(X=40) = 5^40 e^-5/40! ≈ 2.7e-22, which underflows nothing at lambda 5, but at lambda = 200, k = 800 the factorial overflows a double while the true probability is about 1e-14. Log-space returns it correctly. |
| 53 | State the Normal approximation validity result for Probability Distributions. | n = 10, p = 0.05: np = 0.5, far below 5, so the normal approximation is useless in the tail that matters for a 5% rate. Use the exact binomial or a Poisson approximation with lambda = np = 0.5. |
| 54 | State the Central limit theorem in practice result for Probability Distributions. | Lognormal with median 10, sigma = 1: individual values have skewness 2.1, so a mean ± sd misdescribes them. The mean of 100 such values has skewness 0.21 and an approximate normal shape, so n = 100 makes the mean summary defensible. |
| 55 | State the Exponential memorylessness and backoff result for Probability Distributions. | lambda = 0.1/s (mean 10 s): the chance of surviving 10 s is e^-1 = 0.368. With backoff doubling instead, after 10 s the effective hazard is halved, which is a different policy against the same unknown dependency. |
| 56 | State the Poisson overdispersion check result for Probability Distributions. | Requests per minute with mean 100 and variance 240: the dispersion ratio is 2.4. A single Poisson overpredicts the probability of an extreme peak, which is precisely the tail that matters for capacity planning. |
| 57 | What is a continuity correction for? | Correcting the discrete-to-continuous step when approximating a binomial or Poisson tail with a normal. |
| 58 | How do you estimate a Poisson rate? | By maximum likelihood or method of moments; both give the sample mean of the counts. |
| 59 | What is the variance of a binomial? | np(1−p), which is why the proportion estimator's standard error shrinks as sqrt(n). |
| 60 | Why does overflow matter in a Poisson PMF? | The k! term overflows a double around k = 170; a log-space or gamma-function evaluation avoids it. |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
