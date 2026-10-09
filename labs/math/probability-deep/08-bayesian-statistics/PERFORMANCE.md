# Performance: Bayesian Statistics

## Exact/conjugate updating — the fast path
Beta–Binomial, Gamma–Poisson, Normal–Normal updates are **O(1) per observation** (add counts to α, β / λ, r / update precision and mean) and **O(1) memory**. Streaming posterior tracking for 10⁶ users with Beta models is 10⁶ × O(1) — no optimization, no sampling, exact. Always check conjugacy before reaching for MCMC.

## Grid and quadrature
1-D posterior on a grid of G points: **O(G·n)** to evaluate the likelihood at all points (or O(G) if sufficient statistics suffice), O(G) memory, exact up to discretization (error O(1/G²) for trapezoid on smooth densities). G = 1000 is a standard default for 1-D — not a benchmark, a resolution argument: the posterior must be resolved to ~1/1000 of its width.

## MCMC — the honest cost statement
- Per iteration cost = **one likelihood evaluation O(n·p)** (Metropolis/Gibbs) or **O(n·p) for the gradient** (HMC needs ~L leapfrog steps with gradient each, so O(L·n·p) per iteration; L is chosen to control the trajectory, typically O(10)).
- Total cost = iterations × per-iteration cost, but *effective* samples are what matter: **ESS = N / τ** with autocorrelation time τ = 1 + 2Σₖρₖ. A chain with τ = 50 turning out 100 000 draws gives 2 000 effective draws — 50× wasted work.
- Diagnostics: **split-R̂ < 1.01** across ≥ 4 chains (Vehtari et al. 2021) and **ESS ≥ 400** for every reported quantity (the recommendation behind those thresholds: relative error of MCMC estimates ≲ 10% with high probability).
- HMC's cost is per-*gradient*, and gradients via automatic differentiation cost a constant multiple of the log-likelihood — so HMC is preferred not because it is cheaper per iteration but because its τ is far smaller (well-separated draws per unit compute).

## Variational inference as the speed/accuracy trade
ADVI and friends optimize an approximate posterior in **O(iterations × n × p)** without sampling, typically an order or two of magnitude fewer wall-clock operations than well-mixing MCMC — at the price of biased (usually under-dispersed) uncertainty. Use VI for exploration and hyperparameter sweeps, MCMC for reported intervals.

## Marginal likelihood / model comparison
Evidence for a model needs ∫L(θ)π(θ)dθ: exact when conjugate; bridge sampling or the harmonic-mean identity (with its infinite-variance pathology) otherwise. Never quote a Bayes factor from the harmonic mean estimator without checking stability — it is a known inconsistent estimator.

## The method ladder, by cost and by when to climb

| Method | Cost | Memory | Climb when |
|---|---|---|---|
| Conjugate update | O(1) per observation | O(1) parameters | Likelihood matches prior family — always try first |
| Grid quadrature | O(G*n), G ≈ 10³–10⁴ | O(G) | 1-2 parameters; exact, zero sampling error |
| Importance sampling | O(N*n) | O(N*p) | Light-tailed posterior you can proposal-sample |
| Random-walk Metropolis | O(iter*n*p), ESS = N/τ | O(c*n*p) | Conjugacy failed and geometry is friendly |
| HMC (Stan) | O(iter*L*n*p) gradients | O(c*n*p) | p ≥ 5 with curves; pays per-iteration for small τ |
| ADVI / VI | O(iter*n*p), no sampling | O(p) | Sweeps and initialization — not final intervals |

**The billing metric is (cost per iteration) × τ, never cost per iteration.** If sampler A costs 0.1 ms/iter with τ = 50 and sampler B costs 2 ms/iter with τ = 3, then A burns 5 ms per effective draw while B burns 6 ms — the "10× faster" sampler is the slower one per useful sample. Chains are also embarrassingly parallel: four chains on four cores finish in about the wall-clock of one, so the diagnostics that *require* between-chain disagreement (split-R̂) are free in latency.
