# Hypothesis Testing - Code Deep Dive

**Track:** statistics  |  **Lab:** lab03  |  **Level:** Intermediate

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
  HypothesisTesting.java     driver: runs each test on fixtures and prints results
  TestResult.java            statistic, df, p-value, effect size, interval together
  TTest.java                 one-sample, two-sample Welch, paired on differences
  ZTest.java                 one-sample and two-proportion with a known sigma
  ChiSquareTest.java         goodness of fit and independence on counts
  EffectSize.java            Cohen's d, Hedges' g, risk difference, ratio
  Interval.java              confidence interval with its level as a type
```

TestResult carries the effect size and interval alongside the p-value. It is structurally impossible in this codebase to print a p-value without the effect attached.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `TestResult` | statistic, degrees of freedom, p-value, effect size and interval together |
| `TTest` | one-sample, two-sample Welch, and paired implemented on differences |
| `ChiSquareTest` | goodness of fit and independence on integer counts with expected-count checks |
| `EffectSize` | Cohen's d, Hedges' g, risk difference and risk ratio |

---

## 3.1 Welch's t with fractional degrees of freedom

No equal-variance assumption, and the fractional df is what makes the reference distribution conservative.

```java
public static TestResult welch(double[] a, double[] b) {
    Variance va = meanAndVariance(a), vb = meanAndVariance(b);
    double seA = va.variance() / a.length, seB = vb.variance() / b.length;
    double se = Math.sqrt(seA + seB);
    double t = (va.mean() - vb.mean()) / se;
    // Welch-Satterthwaite: fractional df, always smaller than the pooled version,
    // so the reference distribution is conservative when variances differ
    double df = Math.pow(seA + seB, 2)
            / (Math.pow(seA, 2) / (a.length - 1) + Math.pow(seB, 2) / (b.length - 1));
    double p = 2 * (1 - studentTCdf(Math.abs(t), df));
    return new TestResult("welch", t, df, p,
            effectSize(a, b), meanDifferenceInterval(va, vb, df));
}
```


---

## 3.2 Effect size and interval attached to every test

The p-value never travels alone, which removes the most common reporting failure in practice.

```java
public record TestResult(String test, double statistic, double df, double pValue,
                      double effectSize, Interval effectCi, String assumptions) {}

static TestResult interpret(TestResult r, double alpha) {
    // a non-significant result must be reported with power, never as 'no effect'
    if (r.pValue() >= alpha)
        return r.withNote("inconclusive at alpha=" + alpha
                + "; report the confidence interval and the achieved power");
    // a significant result must carry magnitude, because significance says nothing about value
    return r.withNote("significant, effect " + fmt(r.effectSize())
            + " with CI " + r.effectCi() + "; decide on the interval, not the p-value");
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| Statistic computation | `O(n)` | one stable pass per group |
| p-value from t, F or chi-square | `O(1) to O(k)` | incomplete beta and gamma evaluations |
| Bootstrap interval | `O(r x n)` | r resamples when no closed form exists |
| Power calculation | `O(1)` | non-central t or normal approximations |

## 5. Correctness and Numerics

- Compute p-values from incomplete beta and gamma functions, not lookup tables.
- Use erfc for normal tails so small p-values stay accurate.
- Prefer Welch's t; use the pooled version only with an explicit variance check.
- Attach the effect size and interval to every result, structurally.
- Report power alongside a non-significant result.

## 6. Test Strategy

- Welch's t reduces to the pooled t when variances are equal.
- A paired test on identical groups gives a zero difference and p = 1.
- Chi-square expected counts below 5 are detected and reported as a warning.
- The confidence interval excludes 0 exactly when p < alpha.
- A result with p >= alpha carries a note demanding power reporting.
- Simulating the null at alpha = 0.05 yields a rejection rate within tolerance.

## 7. Extension Points

- Add bootstrap and permutation alternatives that assume less.
- Add multiple-comparison correction across a family of tests.
- Add a sequential test with alpha spending for monitoring-style data.

## 8. Review Checklist

- [ ] Hypothesis, direction and alpha pre-specified before computation
- [ ] Welch's t by default; pooled only with justification
- [ ] p-values computed from distributions, not tables
- [ ] Effect size and confidence interval attached to every result
- [ ] Non-significant results reported with power, not as no effect
- [ ] Multiple looks and comparisons accounted for
