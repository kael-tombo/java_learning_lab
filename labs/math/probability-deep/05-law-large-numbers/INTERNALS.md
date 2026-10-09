# Internals: Law of Large Numbers and CLT

## Streaming estimators (the LLN made operational)
`RunningMoments` holds (n, mean, M2) and updates per observation:
```
n += 1; delta = x - mean; mean += delta/n; M2 += delta*(x - mean)
```
Variance = M2/(n−1). Numerically stable (each step's error is local), O(1) memory, trivially parallelizable only with care — parallel updates must merge via Chan's formula (combine (n, mean, M2) pairs) rather than interleaving per-element deltas.

## Confidence intervals on the fly
After k observations: SE = √(s²/k), CI = mean ± z·SE with z = 1.959964 for 95% (inverse-normal via AS241). For k < 30 fall back to Student t with k−1 degrees of freedom — the switch is a lookup, and the same code path serves both. The class exposes `covers(mu)` so tests can count empirical coverage over replications (expected 95% ± Monte Carlo error).

## Effective sample size for dependent series
`Autocorr` computes ρ̂ₖ up to lag L (FFT-based autocorrelation: O(n log n) instead of O(n·L)), sums the sequence while the pairs are still significant, and returns n_eff = n/(1 + 2Σρ̂ₖ). Any "mean ± SE" computed from correlated data routes through it — this is the internal guard against the most common misuse.

## Simulation layout
To *demonstrate* the LLN: R independent replications × n steps, accumulating only the final mean per path — O(R) memory, O(R·n) time. Replications need independent RNG streams: a splittable generator (splitmix64/seeder) per replication, never `new Random(seed)` in a loop with adjacent seeds for LCGs.

## Summation discipline
Left-to-right float summation has worst-case error O(nε); pairwise (binary tree) reduction is O(ε log n) and is what `DoubleStream.sum()` / BLAS-level reductions use. For long streams prefer compensated (Neumaier) accumulation: 1 extra add + 1 extra sub per element, error ~ε regardless of n.

## Berry–Esseen diagnostics
`BerryEsseen` computes ρ = E|X − μ|³, σ³ and the bound C·ρ/(σ³√n) (C = 0.4748 worst case; a tighter family-specific C when known). It is exposed as a *guarantee* on the normal-approximation error so callers can decide whether the CLT interval is justified at their n — no benchmarks, just the theorem's own constant.

## Layering
`moments(stream) → interval(clt|t) → coverage(replications)`; `autocorr → ess → interval` (interval takes n_eff, never raw n). Both paths converge on one `Interval` type so nothing can accidentally quote a raw-n interval for correlated data.

## Coverage harness (the CLT audited empirically)

```
for r in 1..R:                        # R independent replications
    x = sample(n, stream[r])          # splittable RNG per replication
    ci[r] = mean(x) +- 1.959964*sd(x)/sqrt(n)
covered = count(ci[r] covers mu) / R   # expect 0.95
```
Monte Carlo error on that expectation is √(0.95·0.05/R): at R = 10 000 it is 0.00218, so the harness itself should report **95.0% ± 0.43%** — a coverage reading outside [94.6%, 95.4%] is a real defect, not harness noise. The harness is the only place a claimed interval rate is falsifiable: unit tests check formulas, this checks the long-run property the formula claims.

## Determinism contract

Each replication gets its own stream (splittable generator, never `seed, seed+1, …` for LCGs), the harness stores only (R, covered) — never the samples — and re-running with the same master seed reproduces the coverage count bit-for-bit. That makes a coverage regression bisectable like any other test failure.
