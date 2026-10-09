# Performance: Estimation Theory

## Costs by method — exact, not benchmarked
- **Closed-form MLEs** (normal μ, σ²; binomial p; exponential λ = n/Σxᵢ): **O(n)**, one pass. Always check whether a closed form exists before deploying an optimizer.
- **Newton–Raphson MLE in p parameters**: each iteration computes score and observed information — **O(n·p)** for the score and **O(n·p²)** for the information (sum of outer products), plus an O(p³) solve. Typical convergence is quadratic, so total cost ≈ (few iterations) × O(n·p²). Fisher-scoring replaces the observed Hessian with expected information, saving constant factors when they differ.
- **Numerical gradient without closed form**: forward differences cost (p+1) likelihood evaluations per gradient → **O(n·p)** per evaluation set, p× worse than analytic score. Derive the score analytically or use AD.
- **Cramér–Rao / Wald SE**: requires inverting p×p information — **O(p³)** after the O(n·p²) accumulation. For p > 10³ use iterative solves (conjugate gradient) or diagonal approximations.

## Bootstrap (Efron 1979)
B resamples of size n: **O(B·n)** time for a statistic costing O(n) per evaluation (e.g. mean), O(B) memory if only the statistic values are kept. Percentile interval = quantiles of the B values, O(B log B) to sort (or O(B) via quickselect). BCa needs jackknife influence values: an extra O(n) per-observation recomputation → O(n²) for a statistic refit per point — or O(n) influence approximations.

Sample-size planning follows the SE law, not the bootstrap: to halve a CI you need 4×n, whether the CI came from t or from resampling.

## Recursive/online estimation
- **Welford moments**: O(1) memory and time per observation — mandatory for streams; the naive stored-sample approach is O(n) memory.
- **Recursive least squares** (RLS, Kalman-style update): **O(p²)** per new sample vs **O(n·p²)** for a batch refit. For fixed p this is constant per row; that is why sensor/adaptive filters do not re-run batch least squares.
- **Exponential forgetting** (λ ∈ (0,1) discount): tracks drifting parameters at the price of effective window 1/(1−λ); cost unchanged, bias toward recent data explicit.

## Where time actually goes
Optimization iterations dominate once p is modest; likelihood *evaluation* dominates when n is huge (10⁹ rows: subsample for optimization, refine once on full data — a standard two-stage trick). Fisher information from the full data is one final O(n·p²) pass.

## Cost table: estimation procedures

| Procedure | Time | Memory | Trigger to use it |
|---|---|---|---|
| Closed-form MLE (normal, binomial, exponential) | O(n), one pass | O(1) | Always check first — never optimize a solvable equation |
| Newton–Raphson, p params | O(iters · (n·p² + p³)) | O(p²) | General smooth likelihood with analytic score |
| Numerical gradient (finite differences) | O(p) likelihood evals per step | O(p²) | No analytic score; p ≤ ~20 before it hurts |
| Bootstrap, B resamples, O(n) statistic | O(B·n) | O(B) if only θ̂'s kept | No closed-form Var(θ̂); B ≥ 1000 for stable 2.5% quantiles |
| Jackknife (n refits) | O(n · cost(refit)) | O(1) | Bias estimation cheaply; deterministic, no RNG |
| Profile LR interval | (solves × 2 endpoints) × O(fit) | O(1) | Boundary/asymmetric parameters where Wald fails |
| Sandwich (White 1980) | O(n·p²) after the fit | O(p²) | Any SE reported on dependent or misspecified data |

## Rules of thumb

- **Bootstrap B × n beats formula derivation when n < ~10⁴ and the statistic has no textbook SE** — one afternoon of compute instead of one week of math, and the same O(B·n) is parallel across resamples (embarrassingly parallel; χ²-tail quantile stability improves ~1/√B, so B = 10⁴ costs 10× for ~3× tighter quantile estimates).
- **The two-stage trick**: optimize on a 10% subsample, then one full-data pass for the final θ̂ and the information — likelihood *evaluation* dominates at n = 10⁹, so don't evaluate it a hundred times there.
- **Sample-size planning is not a performance question**: the SE law (1/√n) decides n; runtime just executes it. Confusing the two leads to "our optimizer is fast so n = 10⁶ is fine" — n = 10⁶ was always required, the optimizer's speed is irrelevant to the inference.
