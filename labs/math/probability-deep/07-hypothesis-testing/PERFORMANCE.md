# Performance: Hypothesis Testing

## Cost of a test — exact statements
- **One-sample t/z**: O(n) to accumulate mean and variance (streaming, O(1) memory), then O(1) per test. The reference distribution is a table/erf lookup — constant time.
- **χ² goodness-of-fit**: one O(n) pass to bin the data plus O(k) for Σ(O−E)²/E over k cells. Sparse cells: use the exact multinomial test — cost grows combinatorially with cell count, so merging cells (Cochran's expected-count ≥ 5 rule) is a *performance* decision as well as an accuracy one.
- **Nonparametric tests**: Mann–Whitney/rank tests need a sort — **O(n log n)** (vs O(n) t-test); permutation tests are **O(B·n)** for B permutations, or O(n log n) closed-form exact for small n. Kruskal–Wallis/k-sample: same sort cost.
- **Repeated measures / many endpoints**: each additional test is +O(n); the multiplicity correction itself is O(m log m) (sorting p-values for Benjamini–Hochberg) — negligible next to the data passes.

## Corrections and their cost in power
- **Bonferroni**: threshold α/m — m = 100 at α = 0.05 → 5×10⁻⁴; power loss is real but the arithmetic is O(1). It controls FWER ≤ α regardless of dependence (union bound).
- **Holm (1979)**: same O(m log m) sort, uniformly ≥ Bonferroni power, still FWER-valid under arbitrary dependence.
- **Benjamini–Hochberg (1995)**: controls FDR at q — appropriate when you *expect* many true effects (genomics, A/B platforms); costs the weaker guarantee.

## Sequential testing: fewer samples, same error rate
SPRT (Wald–Wolfowitz 1945) stops as soon as the log-likelihood ratio crosses boundaries at ±log((1−β)/α): the expected sample size under either hypothesis is approximately (log of the boundary) / KL(p₀‖p₁) — i.e. **O(1/KL)** instead of a pre-fixed n, so easy-to-separate alternatives finish in a handful of observations. Group-sequential boundaries (O'Brien–Fleming) keep the fixed-n design while allowing interim looks at O(1) cost per look.

## What actually dominates in practice
Streaming/binning the data (O(n)), not the statistics. One exception: **bootstrap or permutation p-values** cost O(B·n) — for n = 10⁶ and B = 10⁴ that is 10¹⁰ statistic evaluations, so use the analytic null (CLT/chi-square) or a fast approximate permutation (pool adjacent violators for ranks) instead of naive resampling.

## Precision claims to avoid
Do not quote "the p-value is accurate to 0.0001" — its Monte Carlo SE (from B permutations) is √(p(1−p)/B); at p = 0.05 and B = 10 000 that is 0.0022. Either report p̂ ± MC-error or use an exact/closed-form null.

## Cost table: choosing a test under a compute budget

| Test | Cost | Memory | Reach for it when |
|---|---|---|---|
| One-sample z/t | O(n) pass, O(1) per test | O(1) streaming | Mean vs a threshold; n moderate and tails light |
| Welch two-sample | O(n₁ + n₂) | O(1) | Default for two means — no equality-of-variance assumption |
| Pooled Student t | O(n₁ + n₂) | O(1) | Equal variances by design (paired/stratified experiments) |
| χ² goodness-of-fit | O(n) binning + O(k) cells | O(k) | Expected counts ≥ 5 (Cochran); else Fisher/exact |
| Mann–Whitney / Kruskal–Wallis | O(n log n) (the sort) | O(n) | Ordinal/skewed data; tests stochastic ordering, not means |
| Permutation | O(B·n), B ≥ 9999 for stable p | O(n) labels | Small n, exchangeable, no closed form (MC SE ≈ 0.0022 at p ≈ 0.05) |
| SPRT (sequential) | O(n̄), n̄ data-dependent | O(1) | Early stopping on strong signals; error holds under optional stopping |
| BH / Holm correction | O(m log m) sort | O(m) | Any family of m inspected tests; negligible next to data passes |

## Rules of thumb

- **The data pass dominates**: only resampling methods (permutation/bootstrap) cost more than O(n) — for n = 10⁶ and B = 10⁴, 10¹⁰ evaluations, so reach for the analytic null (CLT/χ²) or an exact enumeration (C(10,5) = 252 labelings) instead.
- **Correction is nearly free; power is not**: Holm costs one sort, but Bonferroni's threshold 0.05/m at m = 10⁶ is 5×10⁻⁸ — the cost appears as required n (≈ (2.807/1.96)² ≈ 2× the z-critical margin's share of n), not as runtime.
- **Never quote p to more digits than its Monte Carlo SE allows**: √(p(1−p)/B) at p = 0.05, B = 10 000 → ±0.0022; report p̂ ± MC error or use a closed-form null.
