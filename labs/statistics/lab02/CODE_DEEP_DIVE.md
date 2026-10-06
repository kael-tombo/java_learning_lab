# Probability Distributions - Code Deep Dive

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

## 1. Module Map

```text
src/
  ProbabilityDistributions.java   driver: evaluates and samples each distribution
  NormalDistribution.java     PDF, CDF via erfc, sampling via Box-Muller
  BinomialDistribution.java   PMF in log space, CDF, normal approximation with continuity correction
  PoissonDistribution.java   log-space PMF, CDF via incomplete gamma, dispersion check
  ExponentialDistribution.java PDF, survival, memorylessness check
  MonteCarlo.java            seeded estimator with an interval from repeated runs
```

Binomial and Poisson both evaluate in log space with the same helper, so the underflow fix cannot be applied to one and forgotten in the other.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `NormalDistribution` | PDF, CDF via the complementary error function, Box-Muller sampling |
| `BinomialDistribution` | log-space PMF, exact CDF, approximation with a validity check |
| `PoissonDistribution` | log-space PMF, gamma-function CDF, dispersion statistic |
| `MonteCarlo` | seeded estimator returning a value and an interval |

---

## 3.1 Log-space evaluation that survives large parameters

Everything that can overflow is computed in log space, so tails stay accurate where the decision actually lives.

```java
public static double logPmf(int k, double lambda) {
    if (k < 0 || lambda <= 0) return Double.NEGATIVE_INFINITY;
    // lgamma(k+1) is log(k!) without ever forming k!, which overflows around 170
    return k * Math.log(lambda) - lambda - logGamma(k + 1);
}

public static double cdf(int k, double lambda) {
    if (k < 0) return 0.0;
    // upper regularised incomplete gamma: numerically stable in both tails,
    // unlike summing PMFs which loses all relative accuracy for large k
    return regularisedGammaQ(k + 1.0, lambda);
}

public static double normalCdf(double z) {
    // erfc form, not 1 - Phi(z): the tail keeps its relative accuracy
    return 0.5 * erfc(-z / Math.sqrt(2.0));
}
```


---

## 3.2 Sampling with a seed and validating the result

Seeded sampling makes an estimate reproducible; a chi-square style check confirms the sampler actually matches the intended distribution.

```java
public static double[] sampleNormal(int n, double mu, double sigma, long seed) {
    SplittableRandom rnd = new SplittableRandom(seed);   // reproducible: a Monte Carlo
    double[] out = new double[n];                        // estimate you cannot check is not an estimate
    for (int i = 0; i < n; i += 2) {
        double u1 = Math.max(rnd.nextDouble(), 1e-12);
        double u2 = rnd.nextDouble();
        double r = Math.sqrt(-2 * Math.log(u1));
        double theta = 2 * Math.PI * u2;
        out[i]     = mu + sigma * r * Math.cos(theta);   // Box-Muller: two uniforms,
        out[i + 1] = mu + sigma * r * Math.sin(theta);   // two normals, exactly
    }
    return out;
}

public static boolean validateSampler(double[] sample, double mu, double sigma) {
    Variance acc = sampleMeanAndVariance(sample);         // compare against theory
    return Math.abs(acc.mean() - mu) < 4 * sigma / Math.sqrt(sample.length)
            && Math.abs(acc.sd() - sigma) / sigma < 0.1;   // sampling error aware
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| PDF/CDF evaluation | `O(1) or O(k) for exact tails` | log space keeps it constant |
| Normal sampling | `O(n)` | Box-Muller produces two normals per pair of uniforms |
| Exact Poisson or binomial CDF | `O(k)` | use the gamma form when k is large |
| Monte Carlo estimate with an interval | `O(r x n)` | r repeats, n samples each |

## 5. Correctness and Numerics

- Evaluate in log space whenever a factorial or power can overflow.
- Use the complementary error function for normal tails, not 1 minus the CDF.
- Use a regularised gamma function for large Poisson or binomial tails.
- Seed every generator; an unreproducible estimate cannot be checked.
- Report Monte Carlo results with an interval from repeated independent runs.

## 6. Test Strategy

- Poisson PMF sums to 1 within 1e-9 for lambda = 3, 30 and 300.
- Binomial PMF sums to 1 within 1e-9 for n = 10, 100 and 1000.
- Direct and log-space PMF agree to 1e-12 where direct is finite.
- Normal CDF matches known values at z = 0, 1.96 and 3 to 1e-9.
- A seeded sampler produces identical output across runs and passes the moment check.
- Normal approximation agrees with the exact binomial within 2% when np >= 5, and the validity check rejects it otherwise.

## 7. Extension Points

- Add a negative binomial for overdispersed counts and compare dispersion.
- Add a Weibull for non-memoryless waiting times and compare likelihoods.
- Add importance sampling for rare-event probability estimation.

## 8. Review Checklist

- [ ] All tail evaluation in log space with a stated error
- [ ] Approximations gated by a validity check, not applied blindly
- [ ] Sampling seeded and validated against theoretical moments
- [ ] Monte Carlo results reported with intervals
- [ ] Distributional assumptions checked, especially rate constancy
- [ ] Assumption violations reported rather than silently modelled around
