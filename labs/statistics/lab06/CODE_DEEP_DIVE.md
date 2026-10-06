# Bayesian Statistics - Code Deep Dive

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

## 1. Module Map

```text
src/
  BayesianStatistics.java     driver: conjugate and sampled posteriors, comparisons
  BetaPosterior.java        conjugate beta-binomial update, mean, HDI
  PriorPredictiveCheck.java simulate from the prior and compare to observed data
  McmcSampler.java          seeded sampler with diagnostics: R-hat, ESS
  PosteriorSummary.java     mean, median, HDI, effective sample size
  PosteriorComparison.java  P(A > B) from draws with a Monte Carlo interval
```

PosteriorSummary carries the effective sample size next to the interval. It is not possible in this codebase to print a posterior interval without also reporting whether the draws justify it.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `BetaPosterior` | conjugate beta-binomial update with mean, variance and HDI |
| `McmcSampler` | seeded sampler exposing R-hat and effective sample size |
| `PriorPredictiveCheck` | simulates from the prior and compares to observed data |
| `PosteriorComparison` | P(A > B) from draws with a Monte Carlo interval |

---

## 3.1 Conjugate update with prior interpretation

Prior parameters are pseudo-counts, which makes the update arithmetic and the prior auditable.

```java
public BetaPosterior update(BetaPrior prior, int successes, int failures) {
    // a and b are interpretable as prior pseudo-successes and pseudo-failures
    double a = prior.a() + successes;
    double b = prior.b() + failures;
    return new BetaPosterior(a, b);
}

public double mean() { return a / (a + b); }

public double variance() {
    // beta variance: a b / ((a+b)^2 (a+b+1))
    return a * b / (Math.pow(a + b, 2) * (a + b + 1));
}

public Interval hdi(double mass, double[] sortedDraws) {
    // narrowest interval containing `mass` of the posterior, which is more
    // informative than equal-tailed for skewed posteriors
    int width = (int) Math.floor(mass * sortedDraws.length);
    int best = 0;
    for (int i = 0; i + width < sortedDraws.length; i++)
        if (sortedDraws[i + width] - sortedDraws[i]
                < sortedDraws[best + width] - sortedDraws[best]) best = i;
    return new Interval(sortedDraws[best], sortedDraws[best + width]);
}
```


---

## 3.2 MCMC with diagnostics that must pass before summarising

Chains are compared and the effective sample size computed, because an interval from unmixed chains is confidently wrong.

```java
public PosteriorSummary summarise(List<double[]> chains, int warmup) {
    // discard warmup, then compare chains: R-hat near 1 means they agree
    List<double[]> kept = chains.stream().map(c -> Arrays.copyOfRange(c, warmup, c.length))
            .toList();
    double rHat = gelmanRubin(kept);
    int ess = effectiveSampleSize(kept);
    double[] pooled = poolDraws(kept);
    Arrays.sort(pooled);
    if (rHat > 1.01 || ess < 1000)
        throw new NotConvergedException("R-hat=" + rHat + " ESS=" + ess
                + "; an interval from these draws would be confidently wrong");
    return new PosteriorSummary(mean(pooled), quantile(pooled, 0.5),
            hdi(pooled, 0.95), ess);      // spread and justification travel together
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| Conjugate update | `O(1)` | arithmetic on two parameters |
| HDI from sorted draws | `O(n log n)` | sort plus a linear window scan |
| Posterior comparison P(A > B) | `O(N)` | Monte Carlo over paired draws |
| MCMC with diagnostics | `O(iterations x cost)` | R-hat and ESS are O(chains x draws) |

## 5. Correctness and Numerics

- Work with log densities for stability when the posterior is concentrated.
- Sort draws once and reuse for both the HDI and quantiles.
- Report Monte Carlo standard error with any sampled probability.
- Increase draws until the reported probability is stable to three decimal places.
- Seed the sampler so a reported probability can be reproduced exactly.

## 6. Test Strategy

- Conjugate posterior mean matches the pseudo-count arithmetic.
- HDI contains the specified posterior mass and is no wider than equal-tailed.
- A non-converged sampler raises rather than returning an interval.
- P(A > B) matches the analytic value for two known posteriors within Monte Carlo error.
- A prior predictive check fails for a prior that cannot generate data like the observed.
- Increasing the number of draws narrows the Monte Carlo interval as expected.

## 7. Extension Points

- Add MCMC for a non-conjugate model with the same diagnostic interface.
- Add posterior predictive p-values for model checking.
- Add a model comparison via Bayes factors for nested models.

## 8. Review Checklist

- [ ] Prior stated with a rationale and a sensitivity check
- [ ] Prior predictive check run before fitting
- [ ] Convergence verified before any posterior summary
- [ ] Intervals are HDIs with the effective sample size reported
- [ ] Decisions expressed as probabilities about parameters
- [ ] Sampler seeded for exact reproducibility
