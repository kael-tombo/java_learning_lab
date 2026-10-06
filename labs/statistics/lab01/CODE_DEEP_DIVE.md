# Descriptive Statistics - Code Deep Dive

**Track:** statistics  |  **Lab:** lab01  |  **Level:** Foundational

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
  DescriptiveStatistics.java   driver: summarises the dataset and prints a report
  Summary.java                immutable record of every measure
  CentralTendency.java        mean, median, mode with tie handling
  Dispersion.java             variance (Welford and two-pass), sd, IQR, range
  Quantiles.java              interpolated quantiles, p50/p90/p99
  Shape.java                  skewness, excess kurtosis, histogram bins
  OutlierFence.java           1.5 IQR fence returning flagged rows, not deletions
```

Summary is a single record, so a caller cannot report a mean without the median and standard deviation travelling with it. That is a small design choice that prevents a whole category of bad reports.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `Summary` | immutable record of centre, dispersion, shape and percentiles |
| `CentralTendency` | mean, median and mode with tie handling |
| `Dispersion` | Welford and two-pass variance, standard deviation, IQR |
| `Shape` | skewness, excess kurtosis and a histogram with declared bin width |

---

## 3.1 Welford streaming variance

One pass, no cancellation, no retained data. The deltas form is the whole point, so it is written in the stable ordering.

```java
public static Variance update(Variance acc, double x) {
    acc.n++;
    double delta = x - acc.mean;
    acc.mean += delta / acc.n;               // stable: mean moves a little each step
    acc.m2 += delta * (x - acc.mean);        // second moment of deviations
    return acc;
}

public static double sampleVariance(Variance acc) {
    // n - 1 because one degree of freedom went to estimating the mean
    return acc.n > 1 ? acc.m2 / (acc.n - 1) : Double.NaN;
}

// verify against the naive formula on data with a large mean and small spread:
// sum-of-squares loses precision that Welford keeps
static double naiveVariance(double[] xs) {
    double sum = 0, sumSq = 0;
    for (double x : xs) { sum += x; sumSq += x * x; }
    double mean = sum / xs.length;
    return sumSq / xs.length - mean * mean;   // cancellation: avoid this in production
}
```


---

## 3.2 A summary that cannot be reported partially

Centre, dispersion, shape and percentiles are computed together so a skewed distribution cannot be reported with a mean alone.

```java
public Summary summarise(double[] x) {
    Variance acc = new Variance();
    for (double v : x) acc = update(acc, v);        // one stable pass
    double[] sorted = x.clone();
    Arrays.sort(sorted);
    double p50 = quantile(sorted, 0.50);
    double p90 = quantile(sorted, 0.90);
    double p99 = quantile(sorted, 0.99);
    Map<Double, Integer> counts = modeCounts(x);
    double iqr = quantile(sorted, 0.75) - quantile(sorted, 0.25);
    // skewness is reported so the caller sees when the mean is unrepresentative
    return new Summary(acc.mean / acc.n, p50, mostFrequent(counts),
                       Math.sqrt(sampleVariance(acc)), iqr, skewness(x, acc),
                       p90, p99, Math.abs(p50 - acc.mean / acc.n) > 0.5 * sdOf(acc)
                               ? DistributionShape.SKEWED : DistributionShape.SYMMETRIC);
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| Streaming mean and variance | `O(n) time, O(1) space` | the default for large data |
| Quantiles | `O(n log n) with a sort` | or O(n) expected with a selection algorithm |
| Mode | `O(n) time, O(distinct) space` | a hash map of frequencies |
| Histogram | `O(n + bins)` | bin width must be declared, not assumed |

## 5. Correctness and Numerics

- Use Welford or a two-pass algorithm for variance, never sum-of-squares.
- Use n−1 for sample variance and state the divisor in the output.
- Compare mean against the median; a large gap is the signal that shape matters.
- Compute percentiles by interpolation and state the convention.
- Flag outliers with the IQR fence and inspect them; never delete silently.

## 6. Test Strategy

- Welford variance matches a two-pass computation to 1e-10 on random data.
- Welford beats the naive formula on data with a large mean and small spread.
- Sample variance of a constant array is zero; population variance likewise.
- Median of an even-length array averages the two central values.
- The IQR fence flags a planted outlier and leaves a uniform sample unflagged.
- A right-skewed dataset is reported as skewed and the summary carries percentiles.

## 7. Extension Points

- Add a trimmed mean and compare its sensitivity to the median.
- Add robust scale estimators such as the median absolute deviation.
- Add histogram bin-width sensitivity analysis so mode claims are bin-independent.

## 8. Review Checklist

- [ ] Variance computed with a numerically stable algorithm
- [ ] Divisor (n or n−1) stated in the output
- [ ] Mean, median and mode reported together
- [ ] Percentiles included whenever skewness is non-trivial
- [ ] Outliers flagged with rows retained for inspection
- [ ] Per-segment summaries available alongside aggregates
