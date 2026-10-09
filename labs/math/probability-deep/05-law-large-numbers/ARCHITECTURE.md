# Architecture: Law of Large Numbers and CLT Implementation

## Package layout
```
com.mathlab.limits
├── stream/      RunningMoments, WeightedMoments, BlockMoments
├── rng/         SplitableSource (splitmix64), per-replication streams
├── interval/    CltInterval, TInterval, ChebyshevInterval, Coverage
├── dependency/  Autocorr, EffectiveSampleSize, ThinLag
├── bounds/      BerryEsseen, Chebyshev, LawOfIteratedLogarithm
├── simulate/    ConvergencePaths, ReplicationStudy
└── diag/        AssumptionChecks (finite moments, normality QQ, independence)
```

## Two central type decisions
1. **`Interval` carries its provenance.** Every interval is constructed with a `Provenance` enum (CLT, T, CHEBYSHEV, BOOTSTRAP) and the n it used — raw or effective. Printing without provenance is a compile-time-impossible path, which kills the "which SE is this?" class of review errors.
2. **RNG streams are split, not seeded adjacently.** `ReplicationStudy(R)` creates R child streams by splitting one root seed; adjacent seeds of an LCG produce correlated paths that make convergence *look* better than it is.

## Validation rules
- `RunningMoments` throws if fewer than 2 observations when variance is requested.
- `CltInterval` requires n_eff ≥ 30 (or a passed Berry–Esseen bound below the caller's tolerance) — otherwise it returns a `TInterval` instead of silently mis-covering.
- `EffectiveSampleSize` refuses to return n_eff > n (indicates negative-lag truncation error) and caps at n.
- Assumption checks run before intervals are trusted: Jarque–Bera-style normality hint on block means, ρ̂₁ significance for independence.

## Method → guarantee map
| Component | Statement it implements | Failure if skipped |
|---|---|---|
| RunningMoments | LLN (mean/variance consistent) | drifting accumulators |
| CltInterval | CLT: mean ± z·σ/√n | under-coverage from skew/dependence |
| ChebyshevInterval | P(‖ deviation ‖ ≥ k·SE) ≤ 1/k² | no assumptions, loose bound |
| EffectiveSampleSize | Var(X̄) with autocorrelation | over-confident SEs |
| BerryEsseen | supₓ|F − Φ| ≤ Cρ/(σ³√n) | unjustified normal approximation |

## Test topology
Oracle tests: n = 36 → SE = 0.2846 and n = 144 → 0.1423 (exact halving); empirical coverage of CltInterval over 10 000 replications lands in [0.945, 0.955]; an AR(1) ρ = 0.9 stream reports n_eff ≈ n/19; a deliberate float32 naive sum drifts while compensated summation does not.
