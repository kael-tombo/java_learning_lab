# Descriptive Statistics - Architecture

## Summary pipeline

```text
column --> CENTER (mean, median, mode) --> SPREAD (ss, var_n, var_n-1, sds)
   --> QUARTILES (sort, Q1/Med/Q3, IQR) --> SHAPE (skew, kurtosis)
pair --> ASSOCIATION (s_xy, s_xx, s_yy, cov, r)
```

## Component responsibilities

- **Center:** single-pass sum for the mean; sorted copy for median;
  frequency map for mode. Never mutates the input array.
- **Spread:** one deviation loop producing ss, then both normalizations
  with labels. The two variances share ss so they cannot disagree.
- **Quartiles:** owns the sort and the type-7 position formula; IQR is a
  pure function of Q1, Q3.
- **Shape:** owns centered power sums (2nd/3rd/4th) and the two ratios.
- **Association:** one joint loop over the pair accumulating all three
  cross-sums; covariance and r derive from the same triple.

## JDK mapping

- Sorting: `Arrays.sort` on a cloned `double[]` (input stays pristine).
- Frequencies: `LinkedHashMap<Double, Integer>` with `merge`.
- Roots and powers: `Math.sqrt`; powers by repeated multiplication
  (d*d*d), not `Math.pow`, for exactness and speed.
- Output: `Arrays.toString` for the sorted column; labeled scalars.

## Invariants

1. Median/mode code paths never see uncloned mutable state.
2. Both variances derive from one ss - reported side by side, always.
3. Quartile positions use one interpolation rule everywhere (type-7).
4. Covariance and r share cross-sums; r is checked to land in [-1, 1].

## Trace: the value 21 through the pipeline

Center: adds 21 to the sum (74 total). Spread: contributes (21-10.57)^2 =
108.76, half of ss. Quartiles: becomes max, stretches the right whisker.
Shape: dominates m_3 (+1134.5 of +1391 raw cubic total). One value, four
roles - the pipeline's layering is what keeps its influence visible and
attributed instead of silently averaged away.
