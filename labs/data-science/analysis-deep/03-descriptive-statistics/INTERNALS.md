# Descriptive Statistics - Internals (JDK Mechanics)

## Two-pass deviation loops

The snippets compute the mean first, then sum squared (and cubed, fourth)
deviations in a second loop. Two passes cost 2n operations but avoid the
catastrophic cancellation of the one-pass `sum(x^2) - n*mean^2` form, where
two large near-equal numbers subtract. On the lab's magnitudes both forms
agree; the two-pass habit protects large-mean data.

## Sorting a clone

`x.clone()` then `Arrays.sort` (dual-pivot quicksort, O(n log n)) leaves the
caller's array untouched. Median reads index n/2 for odd n. Quartiles use
the type-7 position `h = 1 + (n-1)*p` with fractional blending between
neighbors - for n = 7, p = 0.25 gives h = 2.5, the average of 2nd and 3rd.

## Frequency map with merge

`freq.merge(v, 1, Integer::sum)` boxes doubles as keys - fine at lab scale.
The argmax scan keeps the first value reaching the top count, so ties break
toward first-seen; ties should be reported, not silently picked, in any
extension.

## Power accumulation by multiplication

`d*d*d` and `d*d*d*d` compile to a few multiplications with no call
overhead and no `Math.pow` edge cases (pow(negative, fraction) is NaN).
Division by n happens once per moment, after accumulation.

## Correlation denominator guard

`Math.sqrt(sxx * syy)` is zero only for constant inputs; then r is 0/0
(NaN). Production code must branch on zero spread before dividing - the lab
data has spread 10.0 and 40.8, so the guard never triggers but belongs in
the design.

## Determinism notes

Same arrays, same prints, every run: no randomness, no locale formatting,
shortest round-trip double printing. Expected strings are pinned exactly in
tests.
