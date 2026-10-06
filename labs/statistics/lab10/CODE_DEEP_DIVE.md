# Statistical Power & Effect Size - Code Deep Dive

**Track:** statistics  |  **Lab:** lab10  |  **Level:** Advanced

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
  StatisticalPower.java   driver: power, MDE and required n for each test
  EffectSize.java         Cohen's d, Hedges' g, Glass's delta, r, proportion measures
  PowerFunction.java      power for means and proportions under a stated alternative
  NonCentralT.java        exact small-sample power via the non-central t
  PowerCurve.java         power across a grid of n and effect sizes
  BusinessTranslation.java effect size rendered in the units the business uses
```

BusinessTranslation exists because a d of 0.5 means nothing to a planning meeting. Converting the effect into units — dollars, minutes, tickets — is the step that makes the analysis actionable.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `EffectSize` | d, Hedges' g, Glass's delta, r and proportion measures |
| `PowerFunction` | power for means and proportions under a stated alternative |
| `PowerCurve` | power across a grid of n and effect sizes |
| `PowerResult` | power, minimum detectable effect, n per arm and alpha together |

---

## 3.1 Power under a stated alternative with MDE reported

The alternative is an argument, not an assumption, and the resolution of the design travels with the power number.

```java
public PowerResult powerMeans(double delta, double sigma, int nPerArm,
                                double alpha, boolean oneSided) {
    double se = sigma * Math.sqrt(2.0 / nPerArm);
    double lambda = delta / se;                        // non-centrality under the alternative
    int df = 2 * nPerArm - 2;
    double critical = oneSided ? quantile(1 - alpha, df) : quantile(1 - alpha / 2, df);
    // two-sided power sums both tails; one-sided sums one
    double p = oneSided ? nonCentralTCdf(-critical, df, lambda)
                        : nonCentralTCdf(-critical, df, lambda)
                          + nonCentralTSf(critical, df, lambda);
    // MDE reported alongside power: the design's resolution, not just its sensitivity
    double mde = (oneSided ? zQuantile(1 - alpha) + zQuantile(0.8)
                          : zQuantile(1 - alpha / 2) + zQuantile(0.8)) * se;
    return new PowerResult(1 - p, mde / sigma, nPerArm, alpha);
}
```


---

## 3.2 Variance inflation from a small pilot

Pilot variances are biased low at small n, so inflate them explicitly and record the factor with the study.

```java
public double planningVariance(double[] pilot) {
    // variance of a sample variance is roughly 2 sigma^4 / (n-1): small pilots
    // understate variance, so inflate rather than plan with a biased-low estimate
    double n = pilot.length;
    double observed = sampleVariance(pilot);
    double inflation = 1.0 + Math.sqrt(2.0 / (n - 1));      // documented, not arbitrary
    PlanningVariance pv = new PlanningVariance(observed * inflation * inflation, inflation);
    System.out.printf("pilot n=%d, inflation x%.2f, planning sd=%.4f%n",
            (int) n, pv.inflation(), Math.sqrt(pv.variance()));
    return pv;
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| Normal-approximation power | `O(1)` | closed-form quantiles |
| Exact non-central t power | `O(1) per evaluation` | numerical integration or series |
| Power curve grid | `O(grid size)` | cheap; render freely |
| Bootstrap MDE | `O(r x n)` | only when the analytic form does not apply |

## 5. Correctness and Numerics

- Compute power under the stated alternative, never under the null.
- Inflate pilot variances and record the factor with the study.
- Report MDE alongside power so the design's resolution is explicit.
- Use Hedges' g below about n = 20 per group.
- Apply the same multiplicity correction to alpha in the power calculation.

## 6. Test Strategy

- Power increases with n and with the effect size, monotonically.
- Two-sided power is lower than one-sided power for the same alternative.
- MDE at the n computed for target power equals the specified effect.
- Hedges' g equals d to within 1% at n = 200 per group.
- Inflated pilot variance produces a larger required n than the raw estimate.
- Post-hoc power computed from the observed effect reproduces a known function of the p-value.

## 7. Extension Points

- Add power for logistic regression and count outcomes.
- Add equivalence testing power, which inverts the usual framing.
- Add a design optimiser allocating a fixed budget across several comparisons.

## 8. Review Checklist

- [ ] Effect size specified before data collection, from a threshold or literature
- [ ] Variance defensible and inflated if from a pilot
- [ ] Power computed under the correct sided alternative
- [ ] MDE reported with every power number
- [ ] Multiplicity reflected in the alpha used
- [ ] Retrospective power computed at the a priori effect, not the observed one
