# Internals: Estimation Theory

## Estimator as a value type
```
interface Estimator<T> {
    T point(DataView x);                 // one number (or vector)
    Interval interval(DataView x, double level);
    double biasOrder(int n);             // known analytic bias, if any
}
```
`point()` returns an *estimate*; the sampling distribution lives in `interval()`. Callers cannot accidentally print a point estimate as if it carried an uncertainty — the types are separate.

## MLE core: score + information, then Newton
Maximize ℓ by Newton–Raphson on the score: θ_{k+1} = θ_k − H⁻¹∇ℓ. The implementation:
1. `score(θ)` — analytic gradient, sum over observations, O(n·p).
2. `observedInfo(θ)` — negative Hessian, sum of outer products of per-observation score contributions, O(n·p²).
3. Solve (never invert) Hδ = ∇ℓ with Cholesky — O(p³), fails fast on non-positive-definite H.
4. Step-halving line search: accept only if ℓ(θ + δ) > ℓ(θ); halve δ up to 30 times, then throw `NonConvergence`.

Expected information (Fisher scoring) is an option for canonical exponential families where E[H] has closed form.

## Wald, likelihood-ratio and score intervals
Three intervals from the same fit: Wald θ̂ ± z·√(Var), LR from {θ : 2(ℓ(θ̂) − ℓ(θ)) ≤ χ²₁,₀.₉₅}, and score from the profile. LR is computed by a *profile* optimization over the nuisance parameters — one extra solve per reported limit. They coincide asymptotically; internal tests assert agreement within tolerance at large n so divergence flags a bug early.

## Bootstrap internals
`Bootstrap.run(B, statistic)` draws B resample indices with a per-replication split RNG stream (never re-seeded adjacently), evaluates the statistic, and retains only the B values — O(B) memory. Percentile and BCa are computed from those values; BCa additionally takes jackknife influence values as an input array so the O(n) jackknife is explicit and optional.

## Unbiased corrections are declared, not implied
`VarianceEstimate` carries `divisor` (MLE: n; unbiased: n−1; survey: Horvitz–Thompson weights). `toString()` prints it. Downstream `StandardError` *requires* an unbiased variance or a model-based one — requesting SE from the MLE variance throws a typed error.

## Layering
`data → closed-form point estimates / optimizer → information → intervals (Wald|LR|score) → diagnostics (bias, coverage, LRT)`. Diagnostics consume intervals only, so a coverage study can be run over any estimator without new code.
