# Debugging: Hypothesis Testing

### Symptom: p-value is exactly 0.0 (or 1.0)
Underflow of a far-tail probability (z = 40 → e^{−800}) or complement cancellation (`1 - cdf`). Report p < smallest representable (e.g. p < 1e-300) and compute the tail with the survival function/log-scale. A p of exactly 0 is a numerics artifact, never a fact about the data.

### Symptom: simulated Type I error ≠ α
Run size at the nominal level over R null replications: expected 0.05 ± 1.96√(0.05·0.95/R). At R = 10 000 that band is [0.0458, 0.0542]. Out of band? Check: (1) were tails/α chosen post-hoc (rule 2 of COMMON_MISTAKES); (2) is the reference distribution right (z vs t at small n — t₀.₀₂₅,₄ = 2.776 vs 1.96, size ~2.5% not 5%); (3) is data actually null (your sampler's mean ≠ μ₀).

### Symptom: p = 0.03 but the 95% CI excludes... includes the null
They can't disagree if they're the same test: a two-sided 95% CI and a two-sided α = 0.05 test are exact inversions. If they disagree, one is one-sided, one uses a different df/variance assumption (pooled vs Welch), or one was rounded near the boundary (p = 0.0498 with CI touching 0). Audit both code paths for identical statistic and df.

### Symptom: t-test on heavily skewed n = 12 data
t is robust to mild skew but not at n = 12 with exponential-ish tails: the statistic's null distribution departs from t₁₁ and size inflates. Fix: permutation test (shuffle labels, B ≥ 9999 for stable p near 0.05: MC SE √(0.05·0.95/9999) ≈ 0.0022) or Wilcoxon signed-rank (tests symmetry-adjusted shift).

### Symptom: χ² warning about expected counts < 5
The χ² approximation error is O(1/E_min). Merge sparse categories, use Fisher's exact test (2×2) or an exact multinomial Monte Carlo. Do not just *raise* α — the approximation error is not a decision threshold problem.

### Symptom: cluster-aware test disagrees with naive test
The naive test treated 10 000 rows from 40 users as independent: n_eff ≈ 40 (design effect 1 + (m̄ − 1)·ICC). The naive p is absurdly small; the cluster-robust/cluster-level test is correct. Recompute with clusters as the unit (or CRVE sandwich), and record the design effect in the report.

### Symptom: permutation p-values jump between runs
No seed on the permutation RNG, or B too small: at B = 999 the resolution is 0.001 and MC noise at p = 0.05 is √(0.05·0.95/999) ≈ 0.0069. Fix the seed for reproducibility and increase B (or use exact enumeration when the number of labelings is small, e.g. C(10,5) = 252).

## Debugging triage: tests

| Symptom | Most likely cause | Evidence to collect first |
|---|---|---|
| p printed as 0.0 | Tail underflow or `1 - cdf` cancellation | Recompute with the survival function on log scale; report p < smallest representable |
| Simulated size ≠ α (out of [0.0458, 0.0542] at R = 10 000) | Post-hoc tails, wrong reference distribution (z at small n), or a non-null sampler | Size by n; QQ of the test statistic against its reference; verify sampler mean = μ₀ |
| CI and p disagree about the null | One-sided vs two-sided, pooled vs Welch, or rounding at the boundary | Run both from one shared code path; compare statistic and df, not just the outputs |
| t-test flags "non-normal" data | Test is reacting to n, not shape — or genuinely skewed n = 12 | Permutation p (B ≥ 9999, MC SE ≈ 0.0022 at p ≈ 0.05); Wilcoxon as cross-check |
| χ² warning: expected < 5 | Sparse cells — the approximation error is O(1/E_min) | Print the expected table; merge cells or use Fisher; never raise α to silence it |
| Naive p absurdly small, cluster-robust p not | Rows treated as independent when the unit is clusters (design effect 1 + (m̄−1)·ICC) | n vs n_clusters; recompute with clusters as the unit and record the design effect |
| Permutation p jumps between runs | No fixed seed, or B too small (MC noise ≈ 0.0069 at B = 999, p = 0.05) | Fix the seed; raise B; or enumerate exactly when C(n₁+n₂, n₁) is small (C(10,5) = 252) |

## Two-minute checklist before believing a significance claim

- Count the tests actually inspected — including dashboard cards and "just one more" cuts.
- Confirm the stopping rule: fixed n, pre-planned interim, or SPRT — anything else voids α.
- Report effect size and interval next to the p; if you can't, the claim is incomplete regardless of the number.
