# Performance: Law of Large Numbers and CLT

## Streaming costs, exactly
- **Running mean/variance (Welford)**: 1 pass, **O(1) memory** (n, mean, M2) and 3 flops per observation — independent of n. The naive two-array approach (store everything, then average) is O(n) memory and is the difference between fitting 10⁹ observations in RAM and not.
- **Parallel/streaming mean**: pair-wise tree summation has rounding error O(ε log n) versus O(nε) for naive left-to-right accumulation. For float32 accumulators over 10⁸ values, that is the difference between ~0.01% and ~2% drift.

## How many samples for a given precision?
Three distinct formulas — pick the honest one:
1. **CLT / normal approximation**: to estimate a proportion within ±e at 95%, n ≥ (1.96)²·0.25/e² — e = 0.03 → n ≥ 1068; e = 0.01 → n ≥ 9604. Precision linear in cost → quadratic in 1/e.
2. **Distribution-free (Chebyshev, confidence 1−δ)**: n ≥ σ²/(e²δ) — for σ = 1, e = 0.1, δ = 0.05: n ≥ 1/(0.01 × 0.05) = 2000, versus CLT's n ≥ (1.96 × 1/0.1)² = 384. The ~5× gap is the price of not assuming normality (it widens in the tails); Berry–Esseen (bound C·ρ/(σ³√n), best known C ≤ 0.4748) is the rigorous bridge between the two.
3. **Monte Carlo event probability**: SE = √(p(1−p)/N) ≤ 1/(2√N), so resolving p to ±0.005 needs N ≥ 10 000 trials; ±0.0005 needs 10⁶ — four zeros of precision, 100× the work.

## Simulating convergence
R replications of a path of length n: O(R·n) time and O(1) memory per path. To *display* the 1/√n funnel, the SE of the plotted spread at each n is itself ~spread/√(2(R−1)) — with R = 100 paths the funnel band wobbles ~10%, so don't read wiggle as theory violation.

## When the CLT accelerates work
- Confidence intervals from one pass: no bootstrap needed (O(1) vs O(B·n)).
- Normal quantile lookups replace exact distributions for large n (t with 1000 df vs normal differ in the 3rd decimal of the critical value).

## When it doesn't
Dependent draws: use n_eff = n/(1 + 2Σρₖ). Estimating ρₖ costs O(n) per lag; a truncation at lag L is a bias/variance trade in the SE itself — underestimating Σρₖ understates the SE *and* overstates precision.

## Choosing the estimator by cost, not habit

| Task | Estimator | Cost | Note |
|---|---|---|---|
| Mean of n streaming values | Welford | 3 flops/value, O(1) memory | default; never buffer the sample |
| Mean of a parallel tree | pairwise reduction | O(log n) depth | rounding O(ε log n) vs O(nε) sequential |
| Proportion to ±e at 95% | CLT n ≥ 0.9604/e² | e = 0.01 → 9604 draws | the 1/e² wall: +1 zero of precision = 100× work |
| Any quantity, no normality | Chebyshev n ≥ σ²/(e²δ) | ~5× the CLT count | pay 5× for dropping one assumption |
| Rare-event probability p ≈ 10⁻⁶ | analytic bound / importance sampling | — | naive MC would need ~10¹² trials for a usable count |
| Dependent stream's SE | ACF → n_eff → σ/√n_eff | O(n log n) (FFT autocorrelation) | cheaper than collecting n× more data when ρ is high |

## Where the CLT *is* the optimization

With an honest σ/√n in hand, downstream work skips entirely: no bootstrap (saving O(B·n) with B ≥ 1000), no exact table (t with 1000 df differs from z 1.959964 by only ~0.002), no stored samples (mean and M2 suffice). The performance argument for the CLT is that three floats replace the dataset for every interval you will ever compute from it — which is why `RunningMoments` (INTERNALS) is the only state the lab keeps.
