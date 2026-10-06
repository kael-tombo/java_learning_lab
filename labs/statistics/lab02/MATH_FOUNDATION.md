# Probability Distributions - Mathematical Foundations

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

## Notation

| Symbol | Meaning |
|---|---|
| `f(x) = exp(−(x−μ)²/2σ²) / (σ√2π)` | Normal PDF - continuous density |
| `Φ(z) = P(Z ≤ z), z = (x−μ)/σ` | Normal CDF - standardised to N(0,1) |
| `P(X = k) = C(n,k) p^k (1−p)^(n−k)` | Binomial PMF - k successes in n trials |
| `P(X = k) = λ^k e^−λ / k!` | Poisson PMF - events in an interval at rate λ |
| `f(x) = λ e^−λx` | Exponential PDF - waiting time, x ≥ 0 |
| `P(T > t) = e^−λt` | Survival function - memoryless property |
| `X̃ → N(nμ, nσ²/n)` | CLT - justifies normal approximations |
| `u1, u2 ~ U(0,1) => z = sqrt(−2 ln u1) cos(2π u2)` | Box-Muller - normal sampling |

## Why the Math Matters

The formulas below are not decoration: each one is the place where a wrong assumption silently produces a plausible number. Knowing which formula applies, and when it stops applying, is the skill this lab builds.


---

## 1. Log-space evaluation and cancellation

```text
log P(X=k) = k log(lambda) - lambda - lgamma(k+1)
normal CDF tail: Phi(-z) = 0.5 erfc(z / sqrt(2))
Poisson CDF: P(X <= k) = gammainc(k+1, lambda) upper regularised form
```

Evaluating the raw expressions loses all precision in the tails, which is where decisions are made. Log-space and complementary error function forms keep relative accuracy everywhere.

**Worked example.** Poisson with lambda = 5, k = 40: P(X=40) = 5^40 e^-5/40! ≈ 2.7e-22, which underflows nothing at lambda 5, but at lambda = 200, k = 800 the factorial overflows a double while the true probability is about 1e-14. Log-space returns it correctly.


---

## 2. Normal approximation validity

```text
binomial to normal: require np >= 5 and n(1-p) >= 5
with continuity correction: P(X <= k) ≈ Phi((k + 0.5 - np) / sqrt(np(1-p)))
error of order 1/sqrt(np(1-p))
```

The approximation is a version of the CLT applied to Bernoulli sums. Its error scales inversely with the smaller expected count, which is why the rule of thumb exists.

**Worked example.** n = 10, p = 0.05: np = 0.5, far below 5, so the normal approximation is useless in the tail that matters for a 5% rate. Use the exact binomial or a Poisson approximation with lambda = np = 0.5.


---

## 3. Central limit theorem in practice

```text
X_i i.i.d. with mean mu, variance sigma^2
(Xbar - mu) / (sigma/sqrt(n)) -> N(0,1)
skewness of Xbar ~ skewness(X) / sqrt(n)
```

The CLT justifies normal approximations for large samples and explains why sample means are better behaved than individual observations. It does not make heavy tails disappear at small n.

**Worked example.** Lognormal with median 10, sigma = 1: individual values have skewness 2.1, so a mean ± sd misdescribes them. The mean of 100 such values has skewness 0.21 and an approximate normal shape, so n = 100 makes the mean summary defensible.


---

## 4. Exponential memorylessness and backoff

```text
f(t) = lambda e^(-lambda t)
P(T > s + t | T > s) = e^(-lambda t) = P(T > t)
mean wait 1/lambda, sd 1/lambda
```

Memorylessness means a failure that has not happened after s units of time is indistinguishable from a fresh start. That is exactly the assumption behind exponential backoff, and its limit when the assumption fails.

**Worked example.** lambda = 0.1/s (mean 10 s): the chance of surviving 10 s is e^-1 = 0.368. With backoff doubling instead, after 10 s the effective hazard is halved, which is a different policy against the same unknown dependency.


---

## 5. Poisson overdispersion check

```text
under Poisson: Var(X) = mean(X)
dispersion statistic: Var(X)/mean(X)
values >> 1 indicate a rate that varies in time
```

The Poisson's defining property is variance equal to mean. When the count varies more, the constant-rate assumption has failed and a negative binomial or a model with rate covariates is required.

**Worked example.** Requests per minute with mean 100 and variance 240: the dispersion ratio is 2.4. A single Poisson overpredicts the probability of an extreme peak, which is precisely the tail that matters for capacity planning.


---

## Cheat Sheet

- `f(x) = exp(−(x−μ)²/2σ²) / (σ√2π)` - Normal PDF
- `Φ(z) = P(Z ≤ z), z = (x−μ)/σ` - Normal CDF
- `P(X = k) = C(n,k) p^k (1−p)^(n−k)` - Binomial PMF
- `P(X = k) = λ^k e^−λ / k!` - Poisson PMF
- `f(x) = λ e^−λx` - Exponential PDF
- `P(T > t) = e^−λt` - Survival function
- `X̃ → N(nμ, nσ²/n)` - CLT
- `u1, u2 ~ U(0,1) => z = sqrt(−2 ln u1) cos(2π u2)` - Box-Muller

## Numerical Traps

- Evaluating factorials directly for large Poisson parameters.
- Comparing densities instead of CDFs when drawing a probability conclusion.
- Using a normal approximation with an expected count below 5.
- Applying a homogeneous Poisson model to a rate that varies by time of day.
- Reporting a Monte Carlo estimate without an interval.

## Self-Check Problems

1. Evaluate a Poisson tail at lambda = 200, k = 800 in both direct and log space, and compare.
2. Apply the continuity correction to a binomial tail and compare with the exact value.
3. Sample 100 lognormals, show the skewness of the sample mean is about skew/sqrt(n), and verify with a histogram.
4. Compute the memoryless residual life distribution for an exponential and compare with a Weibull alternative.
5. Compute a dispersion ratio for hourly counts across a day and decide whether Poisson is adequate.
