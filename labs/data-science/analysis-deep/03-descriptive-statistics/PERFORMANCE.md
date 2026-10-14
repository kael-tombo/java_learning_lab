# Descriptive Statistics - Performance Notes

## Complexity (n values)

- Mean, variance, skew, kurtosis: O(n) time, O(1) extra space - single or
  double streaming passes with a few accumulators.
- Median, quartiles: O(n log n) via sort, O(n) for the clone; selection
  (quickselect) recovers O(n) average when only quartiles are needed.
- Mode: O(n) average with hashing, O(distinct) memory.
- Correlation: O(n) joint pass, O(1) space.

## Memory shape

Moments stream: running sums replace storage, so 100M rows need O(1)
working memory for mean/variance/skew/kurtosis. Order statistics (median,
quartiles) fundamentally need the values (or a selection structure) - that
is the memory cliff between moments and quantiles.

## JDK-specific guidance

- Accumulate in `double` even for integer inputs; `long` sums overflow
  silently on big data while double degrades gracefully.
- Multiply out powers (`d*d*d`) instead of `Math.pow` in hot loops.
- Sort primitives with `Arrays.sort(double[])`, never boxed lists.
- For huge n, consider Kahan-style compensated summation only after
  profiling shows drift - two-pass already removes the dominant error.

## Streaming without libraries

Welford's recurrence maintains mean and M2 online for variance; extend with
higher-moment recurrences for skew/kurtosis. Exact quantiles still need
sketches or partitions - approximate deliberately, labelled as such.

## What is NOT claimed here

No timings: throughput depends on hardware, JVM flags, and data shape. The
complexities above size the work; measure your own passing millions.

## Worked sizing example

Seven values: everything is instant and exact. Seventy million: moments
stream in O(1) memory while median needs selection or sorting - budget one
pass for moments plus a sampling/selection stage for quantiles, and say so
in the methods note rather than silently swapping exact for approximate.
