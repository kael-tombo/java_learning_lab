# ANOVA - Code Deep Dive

**Track:** statistics  |  **Lab:** lab04  |  **Level:** Intermediate

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
  Anova.java              driver: one-way, two-way, post-hoc, diagnostics
  AnovaTable.java         SSB, SSW, SST, df, F, p, eta-squared
  OneWayAnova.java        variance partitioning and the F test
  TwoWayAnova.java        main effects plus interaction
  PostHoc.java            Tukey, Bonferroni, Scheffe
  AssumptionChecks.java   residual normality, homogeneity, independence notes
```

AnovaTable carries eta-squared alongside the p-value, so the omnibus result cannot be reported as a bare 'significant' in this codebase.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `AnovaTable` | sums of squares, degrees of freedom, F, p-value and effect size |
| `OneWayAnova` | single-factor partition and F test with a Welch variant |
| `TwoWayAnova` | both main effects plus interaction, each against the residual |
| `PostHoc` | Tukey HSD, Bonferroni and Scheffe with a declared method |

---

## 3.1 Variance partitioning verified by identity

The decomposition is asserted to sum, which catches transcription errors immediately, and eta-squared travels with the p-value.

```java
public AnovaTable oneWay(List<double[]> groups) {
    double grand = 0; int n = 0;
    for (double[] g : groups) { for (double v : g) grand += v; n += g.length; }
    grand /= n;
    double ssb = 0, ssw = 0;
    for (double[] g : groups) {                        // within-group deviations
        double m = mean(g);
        ssb += g.length * (m - grand) * (m - grand);
        for (double v : g) ssw += (v - m) * (v - m);
    }
    double sst = ssb + ssw;                            // identity, asserted below
    assertClose(sst, totalSumOfSquares(groups, grand), 1e-9);
    int k = groups.size();
    double f = (ssb / (k - 1)) / (ssw / (n - k));
    return new AnovaTable(ssb, ssw, sst, f, k - 1, n - k,
            fSurvival(f, k - 1, n - k), ssb / sst);     // effect size, not optional
}
```


---

## 3.2 Assumption checks that choose the test

Homogeneity is tested and the decision recorded; unequal variances route to Welch rather than being ignored.

```java
public AnovaTable analyse(List<double[]> groups, boolean allowWelch) {
    AssumptionReport checks = AssumptionChecks.inspect(groups);
    if (checks.heteroscedastic() && !allowWelch)
        return AnovaTable.withWarning(oneWayWelch(groups),
                "variances differ materially; classical F p-value is anti-conservative");
    if (!checks.normalResiduals())
        return AnovaTable.withWarning(oneWayWelch(groups),
                "residual normality doubtful at this n; prefer the rank-based alternative");
    return oneWay(groups);
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| Group statistics | `O(N)` | one Welford pass per group |
| One-way F test | `O(1) after statistics` | incomplete beta evaluation |
| Two-way decomposition | `O(N)` | same data, more partitions |
| All-pairs post-hoc | `O(k²) comparisons` | studentised range per comparison |

## 5. Correctness and Numerics

- Compute SSW with n-k, not n, for the denominator mean square.
- Evaluate the F distribution with an incomplete beta function, not a table.
- Always report an effect size with the omnibus test.
- Test homogeneity before choosing classical or Welch.
- Fit the interaction term whenever a second factor is present.

## 6. Test Strategy

- SSB + SSW equals SST to 1e-9 for random data.
- Data from identical distributions yields F near 1 and a large p-value.
- Eta-squared equals SSB/SST and lies in [0, 1].
- Welch reproduces classical results when variances are equal.
- A two-way decomposition with an additive design shows near-zero interaction.
- Tukey's family-wise error is at or below alpha in a simulation under the null.

## 7. Extension Points

- Add Welch's ANOVA and the rank-based alternative in the same interface.
- Add planned contrasts with the correct error term.
- Add repeated-measures ANOVA for within-subject designs.

## 8. Review Checklist

- [ ] Variance decomposition asserted to sum
- [ ] Effect size reported with every omnibus test
- [ ] Post-hoc method declared and family-wise error controlled
- [ ] Assumption checks recorded and used to choose the test
- [ ] Interaction fitted whenever a second factor exists
- [ ] Degrees of freedom reported for both numerator and denominator
