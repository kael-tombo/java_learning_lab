# Exploratory Analysis - Performance Notes

## Complexity (n rows, g groups, p pairs)

- Grouped means: O(n) average with hashing, O(g) memory. One pass.
- Stratum rates: O(n) counting, O(strata x arms) memory - trivial.
- Correlation matrix: O(p x n) time, O(1) per pair. Ten variables (45
  pairs) cost 45 passes naively; single-pass covariance accumulation does
  it in one pass with O(v^2) accumulators.
- Sorting for shape: O(n log n); binning O(n) with O(bins) memory.

## Memory shape

Aggregates stream: sums and counts replace rows, so grouped means and rates
run in O(groups) memory on unbounded data. Displays need samples or bins,
not full retention: reservoir sampling keeps scatters representative at
fixed memory; grids keep densities exact at O(cells).

## JDK-specific guidance

- `computeIfAbsent` with small `double[2]` cells avoids per-row boxing.
- Reuse one `corr` routine across pairs: JIT warms once, results stay
  comparable, code stays reviewable.
- Print rates with raw k/n beside percents - string cost is negligible, audit
  value is not.
- For huge group counts, size the map (expected groups load factor) to avoid
  rehash pauses during the single pass.

## Scaling without libraries

Stratified cubes explode combinatorially (wards x bands x regions); compute
marginals first, then drill only where pooled-vs-stratum signs wobble. EDA
at scale is triage: cheap full scans flag, expensive cuts confirm.

## What is NOT claimed here

No timings: single-pass aggregation is I/O-bound on real data, and rates
depend on hardware. The complexities above size the compute; measure parses
on your own feeds.

## Worked sizing example

Six region rows: everything instant. Sixty million: one streaming pass for
grouped means (O(groups) memory), gridded counters for shape displays,
reservoir samples for scatters. The loop stays identical; only the display
substrate changes from exact arrays to sketches and samples.
