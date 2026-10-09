# Internals: Bayesian Statistics

## Log-posterior as the single objective
Everything downstream — MH acceptance, HMC gradients, VI optimization — consumes one function:
```
logPosterior(θ) = Σᵢ logLikelihood(xᵢ | θ) + logPrior(θ)   // (+ log-Jacobian if transformed)
```
It returns −∞ outside the support instead of NaN, and is always computed in log space (products of densities underflow immediately at n ≈ 1000).

## Conjugate path (exact, no sampler)
```
BetaBinomial:  posterior = Beta(α + Σk, β + n − Σk)
GammaPoisson:  posterior = Gamma(α + Σx, β + n)
NormalNormalKnownVar:  precision τ' = τ₀ + n/σ²,  mean' = (τ₀μ₀ + n·x̄/σ²)/τ'
```
Each is a constructor call — O(1) — and doubles as the *oracle* that MCMC results are checked against in tests.

## Samplers behind one interface
```
interface Sampler { Chain sample(LogDensity f, Init init, int draws); }
```
- **Metropolis–RW**: propose, accept with min(1, exp(f(θ') − f(θ))); adaptive scale during warmup to hit ~0.234 (random-walk target in moderate dimension).
- **Gibbs**: draws from full conditionals — used only when every conditional is conjugate; each sweep is O(p) conditional draws.
- **HMC**: L leapfrog steps with gradient (autodiff), accept/reject on Hamiltonian; mass matrix estimated during warmup to decorrelate parameters. Cost per iteration O(L·n·p) for gradient, but τ drops by orders of magnitude versus random walk.

## Diagnostics computed from raw draws
- **Split-R̂**: split each chain in half, compare within/between variance of all segments — requires ≥ 4 chains; threshold < 1.01.
- **ESS**: via autocorrelation sums with Geyer initial-positive-sequence truncation: ESS = N/τ, τ = 1 + 2Σρₖ.
- **MCSE**: standard error of a posterior-mean estimate = sd/√ESS — the number that tells you whether 0.786 vs 0.791 is signal or simulation noise.

## Storage layout
Draws are `double[chains][draws][parameters]` (primitives, not boxed), warmup discarded by index. Summary statistics (mean, sd, quantiles) stream over the arrays without materializing sorted copies except for quantile queries (quickselect on one parameter at a time).

## Layering
`model (logLik + logPrior) → sampler → chain draws → diagnostics → summaries/credible intervals`. Diagnostics read *only* draws, so the same R̂/ESS code audits conjugate, MH, Gibbs and HMC output — and DEBUGGING's failure modes are all visible at one layer.
