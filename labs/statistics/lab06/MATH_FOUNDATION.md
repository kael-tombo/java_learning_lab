# Bayesian Statistics - Mathematical Foundations

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

## Notation

| Symbol | Meaning |
|---|---|
| `p(θ | data) ∝ p(data | θ) p(θ)` | Bayes' rule - posterior proportional to likelihood times prior |
| `Beta(a + s, b + f)` | Beta-binomial posterior - conjugate update |
| `E[post] = a'/(a' + b')` | Posterior mean - the point estimate |
| `HDI = narrowest interval with 95% posterior mass` | Highest density interval - the honest summary |
| `P(A > B) from posterior draws` | Posterior comparison - the decision-relevant quantity |
| `Posterior predictive: p(y_new | data)` | Predictive distribution - includes parameter uncertainty |
| `P(data) = ∫ p(data | θ) p(θ) dθ` | Evidence - the normalising constant |

## Why the Math Matters

The formulas below are not decoration: each one is the place where a wrong assumption silently produces a plausible number. Knowing which formula applies, and when it stops applying, is the skill this lab builds.


---

## 1. Conjugate beta-binomial update

```text
prior p ~ Beta(a, b)
data: s successes, f failures
posterior p ~ Beta(a + s, b + f)
mean = (a+s)/(a+b+s+f)
```

Conjugacy turns the integral into arithmetic. The update is exactly the prior pseudo-counts plus the observed counts, which is why a and b are interpretable as prior successes and failures.

**Worked example.** Prior Beta(1,1) (uniform), 240 successes and 760 failures: posterior Beta(241,761), mean 0.2405, 95% HDI roughly [0.212, 0.271]. Prior Beta(20,20) with the same data: mean 0.2616 — a different answer, which is a sensitivity finding to report.


---

## 2. Prior versus likelihood influence

```text
posterior mean with conjugate prior = (a + s)/(a + b + n)
weight on prior ~ (a + b)/(a + b + n)
so a + b acts as pseudo-observations
```

The prior's influence scales as its total pseudo-count relative to n. With 10 prior pseudo-observations and n = 10,000, the prior moves the answer by roughly 0.1%, which is the justification for calling it weakly informative.

**Worked example.** Prior Beta(1,1) with n = 20 observations: posterior mean is (1+10)/22 = 0.500, entirely prior-driven. With n = 10,000: (1+4900)/10002 = 0.4900, where the prior is negligible. Same prior, completely different reliance.


---

## 3. Credible intervals and highest density intervals

```text
equal-tailed: quantiles at 2.5% and 97.5%
HDI: narrowest interval containing 95% of the mass
for skewed posteriors the two differ
```

Equal-tailed intervals can be arbitrarily wide while the posterior is extremely concentrated in the middle, so the HDI is usually the more informative summary for skewed posteriors.

**Worked example.** Posterior samples concentrated near 0.1 with a long right tail: equal-tailed 95% is roughly [0.08, 0.22], while the HDI is roughly [0.086, 0.135]. The latter is the honest summary of where the mass is.


---

## 4. Posterior comparison for decisions

```text
draw p_A^(1..N) from posterior A, p_B^(1..N) from B
P(A > B) = mean(1[p_A > p_B])
with N = 10,000 the Monte Carlo SE of this proportion is about 0.005
```

This is the decision-relevant quantity and it accounts for parameter uncertainty on both sides. Comparing point estimates answers a different and usually less useful question.

**Worked example.** Posterior A: mean 0.2405, sd 0.015; posterior B: mean 0.2400, sd 0.020. The means differ by 0.0005, yet sampling gives P(A > B) ≈ 0.48. The honest answer is 'a coin flip', not 'A is marginally better'.


---

## 5. Prior predictive check and MCMC diagnostics

```text
prior predictive: y_sim ~ p(y | θ ~ prior)
compare distribution of y_sim to observed y
R-hat near 1 and ESS >> iteration count indicate usable draws
```

A prior predictive check tests the model before the data: if simulated data cannot look like your data, the model is wrong. MCMC diagnostics test whether the draws are usable, which is a separate question.

**Worked example.** Prior Beta(0.1, 0.1) with 5,000 observed successes out of 10,000: the prior predicts rates near 0 or 1, so simulated datasets look nothing like yours. A Beta(1,1) or a weakly informative rate prior passes the check.


---

## Cheat Sheet

- `p(θ | data) ∝ p(data | θ) p(θ)` - Bayes' rule
- `Beta(a + s, b + f)` - Beta-binomial posterior
- `E[post] = a'/(a' + b')` - Posterior mean
- `HDI = narrowest interval with 95% posterior mass` - Highest density interval
- `P(A > B) from posterior draws` - Posterior comparison
- `Posterior predictive: p(y_new | data)` - Predictive distribution
- `P(data) = ∫ p(data | θ) p(θ) dθ` - Evidence

## Numerical Traps

- Comparing posterior means instead of sampling both posteriors.
- Reporting a credible interval as if it were a confidence interval.
- Trusting chains that have not mixed.
- Using conjugacy without checking whether the prior shape is defensible.
- Skipping the prior predictive check and discovering a model misspecification late.

## Self-Check Problems

1. Compute a beta-binomial posterior by hand and verify against a sampled posterior.
2. Show prior weight as a function of prior pseudo-counts and n; find the n at which the prior moves the mean by under 1%.
3. Compare equal-tailed and HDI intervals on a skewed posterior sample.
4. Compute P(A > B) by sampling and report the Monte Carlo standard error.
5. Run a prior predictive check for a rate model and adjust the prior when it fails.
