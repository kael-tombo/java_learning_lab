# Architecture: Hypothesis Testing Implementation

## Package layout
```
com.mathlab.testing
├── spec/       TestSpec (H0, H1, α, tails, endpoint)   — built first, immutable
├── statistic/  TTest, ZTest, ChiSquareGOF, FTest, MannWhitney, Permutation
├── null/       Normal, StudentT, ChiSquare, F, PermutationNull, MonteCarloExact
├── interval/   Inversion of the test → CI (Wald, exact, profile)
├── correct/    Bonferroni, Holm, BenjaminiHochberg, BY
├── sequential/ SPRT, OBrienFleming, CUSUM
├── power/      PowerCurve, SampleSizeSolve, EffectSize
└── verify/     SizeStudy, PowerStudy (regression harness)
```

## Design decisions
1. **Spec before data.** `TestResult.of(spec, data)` — no overload accepts α after seeing data. One-tailed requires an explicit `TailDirection` in the spec; flipping it later creates a new spec object with a new identity (auditable).
2. **p-values via `sf` only.** `NullDistribution.sf` is the sole entry point for tail probabilities; `cdf` is package-private where possible. Eliminates the `1 - cdf` underflow class permanently.
3. **Corrections take the whole p-vector.** `holm(p[])` rejects `holm(p_i)` — multiplicity must be declared as a set, so "we tested 20 things" cannot be lost between analysis and reporting.
4. **CIs are inversions, not parallel code.** A two-sided 95% CI is computed by inverting the same test (root-find the null value where p = 0.05), guaranteeing test/CI agreement — the DEBUGGING "p and CI disagree" symptom becomes unrepresentable.

## Validation invariants
- Test at α with data generated under H₀ rejects in [0.0458, 0.0542] over R = 10 000 runs (binomial 95% band around 0.05).
- Power at the design point (n = 63, δ = 0.5) ∈ [0.78, 0.82] — the normal-approximation target is 0.80, the t-based value slightly lower.
- p ∈ [0, 1] always (clamp on two-sided doubling at the median).
- χ² tests assert expected-count ≥ 5 or set an `ExactApproximation` flag.
- Corrections guarantee: Holm/ Bonferroni FWER ≤ α under any dependence; BH FDR ≤ q under positive dependence (asserted empirically in `verify`).

## Test topology
Oracle cases computed by hand: t = 1.25 (df 24) → p = 0.223; 0.95²⁰ → 0.3585 → FWER 0.6415; n = 63 power 0.80; Bonferroni threshold 0.0025 for m = 20. Plus size studies as above and a seeded permutation test on a 2×2 table cross-checked against Fisher's exact p.
