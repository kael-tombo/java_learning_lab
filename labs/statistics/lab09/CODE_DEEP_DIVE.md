# Non-Parametric Statistics - Code Deep Dive

**Track:** statistics  |  **Lab:** lab09  |  **Level:** Advanced

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
  NonParametricTests.java    driver: selects and runs the right rank test
  Ranks.java                 ranking with average ranks for ties
  MannWhitneyTest.java       independent groups, exact and asymptotic
  WilcoxonSignedRankTest.java paired differences, zero-differences omitted
  KruskalWallisTest.java     k independent groups with a corrected omnibus
  FriedmanTest.java          k treatments within blocks
  ExactNull.java             enumeration of rank permutations for small n
  RankEffectSize.java        probability of superiority with an interval
```

ExactNull enumerates label assignments with a bitmask and counts how many are at least as extreme, which is both fast and obviously correct at the sample sizes where exactness matters.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `Ranks` | ranking with average ranks for ties |
| `MannWhitneyTest` | independent groups with exact and asymptotic paths |
| `ExactNull` | enumeration of rank permutations for small samples |
| `RankEffectSize` | probability of superiority with a bootstrap interval |

---

## 3.1 Ranking with ties handled correctly

Average ranks for tied values, which is the hinge of every rank test's correctness.

```java
public double[] ranks(double[] values) {
    int n = values.length;
    Integer[] idx = new Integer[n];                    // sort indices, not a copy
    for (int i = 0; i < n; i++) idx[i] = i;
    Arrays.sort(idx, (a, b) -> Double.compare(values[a], values[b]));
    double[] r = new double[n];
    int i = 0;
    while (i < n) {                                    // walk runs of equal values
        int j = i;
        while (j + 1 < n && values[idx[j + 1]] == values[idx[i]]) j++;
        double averageRank = (i + j + 2) / 2.0;        // ranks i+1..j+1, averaged
        for (int k = i; k <= j; k++) r[idx[k]] = averageRank;
        tieTerm += (j - i + 1L) * (j - i + 1L) * (j - i + 1L) - (j - i + 1L);   // variance correction
        i = j + 1;
    }
    return r;
}
```


---

## 3.2 Exact null distribution by enumeration

For small samples the rank statistic is discrete, so enumeration beats an approximation and is trivially verifiable.

```java
public static ExactResult exactMannWhitney(double[] group1, double[] group2) {
    double[] pooled = concat(group1, group2);
    int n1 = group1.length, n2 = group2.length, n = n1 + n2;
    double[] r = ranks(pooled);
    int observed = (int) Math.round(rankSum(r, 0, n1));
    long atLeastAsExtreme = 0, total = 0;
    // every way of choosing which n1 pooled values are group 1
    for (int mask = 0; mask < (1 << n); mask++) {
        if (Integer.bitCount(mask) != n1) continue;
        total++;
        int stat = 0;
        for (int i = 0; i < n; i++) if (((mask >> i) & 1) == 1) stat += (int) Math.round(r[i]);
        if (stat <= observed || stat >= (n1 * (n + 1)) - observed) atLeastAsExtreme++;
    }
    return new ExactResult(observed, (double) atLeastAsExtreme / total, true);
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| Ranking with tie handling | `O(n log n)` | one index sort |
| Kruskal-Wallis | `O(n log n + k)` | one ranking, group sums after |
| Friedman | `O(bk log k)` | ranking within each block |
| Exact null enumeration | `O(C(N, n₁) × N)` | fine below about 20 per group |

## 5. Correctness and Numerics

- Assign average ranks to ties; the variance correction follows from tie sizes.
- Use exact enumeration below roughly 20 per group.
- Report the probability of superiority as the effect size.
- Bootstrap rank-test effect sizes with a stated resampling scheme.
- Follow a significant omnibus test with corrected pairwise comparisons.

## 6. Test Strategy

- Ranks with ties match hand-computed average ranks.
- Mann-Whitney with completely separated groups gives the minimum statistic and p = 0 to machine precision.
- The exact p-value at n = 5 per group matches the enumerated value.
- The exact and asymptotic p-values agree closely at n = 30 per group.
- Kruskal-Wallis on identical groups is not significant.
- Friedman on a complete block design recovers the known ordering.

## 7. Extension Points

- Add Dunn's test for pairwise comparisons after Kruskal-Wallis with a correction.
- Add Cliff's delta as a rank-based effect size with an interval.
- Add permutation tests as a general framework covering the same questions.

## 8. Review Checklist

- [ ] Test chosen from the design and measurement scale
- [ ] Ties handled with average ranks and a variance correction
- [ ] Exact p-values for small samples, asymptotic for large
- [ ] Null hypothesis stated as distributional, not mean-based
- [ ] Effect size reported with an interval
- [ ] Omnibus results followed by corrected pairwise comparisons
