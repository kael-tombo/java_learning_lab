# Internals: Hypothesis Testing

## A test is a value object
```
record TestResult(double statistic, Dist nullDist, double pValue,
                  Interval ci, Decision decision, double alpha,
                  TestSpec spec)      // spec frozen BEFORE data
```
`TestSpec` (hypotheses, tails, α, primary endpoint, correction) is constructed first and is immutable; `TestResult` cannot be produced without one. This enforces pre-registration in code: a post-hoc tail change requires constructing a *new* spec, which is visible in review/logs.

## Reference distributions behind one interface
```
interface NullDistribution {
    double cdf(double x);  double sf(double x);  double quantile(double p);
}
```
Implementations: Normal, T(df), ChiSquared(df), F(df1, df2), plus `PermutationNull(B, seed)` and `MonteCarloExact`. p-values always come from `sf` (survival function) for upper-tail statistics — never from `1 - cdf`, which collapses to 0 past z ≈ 8.

## p-value assembly
Upper tail: p = sf(t_obs). Two-sided: 2·min(cdf, sf) with p clamped to [0,1] (protects against rounding at the median). Exact tests (Fisher's): hypergeometric probabilities summed over outcomes no more likely than observed, via log-gamma to avoid factorial overflow.

## Corrections are a post-pass over p-value arrays
`Corrections.bonferroni(p[], α)`, `holm(p[], α)`, `benjaminiHochberg(p[], q)` — all take the *full* vector of m p-values produced by the analysis family (so the multiplicity set is explicit in one call, not inferred). Holm/BH sort indices once (O(m log m)) and step through, recording which hypotheses survive.

## Size and power verification harness
`SizeStudy.run(spec, R)` generates R null datasets, counts rejections, and returns the empirical size with a binomial CI — the test of the *test*. Expected 0.05 ∈ [0.0458, 0.0542] at R = 10 000. `PowerStudy` shifts the alternative by δ and repeats, producing the power curve; both are used as regression tests when a distribution or correction changes.

## Monte Carlo p-values
p̂ = (1 + #{T_b ≥ T_obs})/(B + 1) — the "+1" keeps p̂ > 0 even when no permutation exceeds observed (Phipson & Smyth 2010). Reported with MC SE √(p̂(1−p̂)/B); `B` defaults high enough that SE < 0.005 near p = 0.05 (B ≥ 10 000).

## Layering
`spec → statistic → null distribution → p/CI → corrections → decision`. Each stage is replaceable: the same t-statistic can be tested against Student, Welch, permutation or bootstrap nulls without touching the statistic code — which is exactly how DEBUGGING's z-vs-t and independence bugs get localized.
