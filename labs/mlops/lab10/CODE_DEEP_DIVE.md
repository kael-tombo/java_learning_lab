# A/B Testing & Experimentation - Code Deep Dive

**Track:** mlops  |  **Lab:** lab10  |  **Level:** Advanced

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
  ABTestingLab.java         driver: simulate an experiment, report with intervals
  Experiment.java           pre-registered plan: primary metric, alpha, power, horizon
  Assignment.java           stable hash-based assignment on user id
  ABTest.java               two-arm metrics, SRM check, significance, effect intervals
  PowerCalculator.java      sample size and MDE from alpha, power and variance
  SequentialPolicy.java     alpha-spending boundaries and guardrail non-inferiority
```

Assignment is a pure function of user id. That makes the experiment reproducible, stateless and immune to the assignment-service outage that has invalidated real tests.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `Experiment` | the pre-registered plan including alpha, power, MDE and horizon |
| `Assignment` | stable hash-based bucketing with an exposure fraction |
| `ABTest` | metric aggregation, SRM check, significance and effect intervals |
| `SequentialPolicy` | alpha-spending boundaries plus guardrail non-inferiority checks |

---

## 3.1 Stateless stable assignment

Hashing the user id means no assignment state to lose, and the same user always lands in the same arm.

```java
public int arm(String userId, int buckets, double exposureFraction) {
    // pure function of the user id: no state to lose, no session contamination
    long h = stableHash(userId);                 // deterministic across processes
    int bucket = (int) Math.floorMod(h, buckets);
    return bucket < (int) (buckets * exposureFraction) ? 1 : 0;
    // exposureFraction lets you ramp 1% -> 10% -> 50% without changing assignment
}
```


---

## 3.2 SRM check before reading any metric

An unequal split invalidates everything downstream, so it is checked first, every time, and fails loudly.

```java
public void assertSrm(long controlCount, long treatmentCount, int buckets, double alpha) {
    // chi-square goodness of fit against the designed 50/50 split
    double expected = (controlCount + treatmentCount) / 2.0;
    double chi2 = Math.pow(controlCount - expected, 2) / expected
                + Math.pow(treatmentCount - expected, 2) / expected;
    double critical = chiSquareCriticalValue(alpha, 1);        // 3.84 at alpha = 0.05
    if (chi2 > critical)
        throw new SrmDetected(chi2);   // a mismatch invalidates every downstream metric
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| Assignment per request | `O(1) hash` | stateless; no coordination cost |
| Metric aggregation | `O(1) per event` | counters keyed by arm and metric |
| SRM check | `O(1)` | chi-square against the designed split |
| Sequential boundary computation | `O(1) per look` | precomputed spending function |

## 5. Correctness and Numerics

- Check sample ratio mismatch before reading any metric, every time.
- Use the pooled standard error for the two-proportion test.
- Precompute sequential boundaries rather than recomputing alpha at each look.
- Report effect size with an interval, then translate it into business units.
- Use stable hashing rather than a random assignment service.

## 6. Test Strategy

- Assignment is deterministic per user id and stable across processes.
- The split matches the exposure fraction within binomial noise.
- An SRM injection raises rather than silently continuing.
- A known-effect dataset produces the expected significance and effect size.
- Sequential boundaries spend no more than the total alpha across all looks.
- A guardrail breach stops the test even when the primary metric is positive.

## 7. Extension Points

- Add multi-arm bandits with allocation by expected regret reduction.
- Add ratio metrics (revenue per user) with the correct delta-method variance.
- Add cluster randomisation for experiments where interference is likely.

## 8. Review Checklist

- [ ] Plan pre-registered before data collection
- [ ] Assignment is a stable hash, not stored state
- [ ] SRM checked before every metric read
- [ ] One primary metric; guardrails separate with agreed bounds
- [ ] No uncorrected peeking: fixed horizon or sequential boundaries
- [ ] Decision documented with effect size in business units
