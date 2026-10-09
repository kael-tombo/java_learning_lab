# Common Mistakes: Law of Large Numbers and CLT

### 1. Confusing convergence of the average with convergence of the draw
X̄ₙ → μ but Xₙ does not converge to anything — each new observation is still drawn from the full distribution. "The coin owes me heads" (gambler's fallacy) confuses the two: after 600 flips the *average* is near 0.5, while flip 601 is still 50/50.

### 2. Wrong scaling of the standard error
SE(X̄) = σ/√n, not σ/n. n = 100 with σ = 10 gives SE = 1, not 0.1. Consequently halving the error bar requires *quadrupling* n — every "we need 2× more data for 2× more precision" plan over-promises by treating precision as linear in n.

### 3. Applying the CLT where the variance doesn't exist
St. Petersburg (1738) has infinite expectation; Pareto with α ≤ 2 has infinite variance. Then X̄ does not converge to a normal — the stable limit (Lévy 1925) with α = 1.5 has heavier tails than any normal, and sample means jump discontinuously as n grows. Fit the tail first (lab 03), then choose the limit theorem.

### 4. Reading the CLT as a statement about your raw data
The CLT says (X̄ − μ)/(σ/√n) → N(0,1) — it says nothing about X itself being normal, and nothing about maxima (extreme-value theory applies there). Normally distributed *sums* built from uniform, exponential or even bimodal components are exactly the claim; "our latencies are normal because CLT" is a non-sequitur.

### 5. Treating dependent data as i.i.d.
Averaging autocorrelated measurements: Var(X̄) = (σ²/n)(1 + 2Σₖ ρₖ), which can be many times σ²/n when ρₖ > 0. The effective sample size is n_eff = n/(1 + 2Σρₖ); using n instead understates the SE and produces over-confident intervals. This is the same error as treating MCMC draws (lab 08) as independent.

### 6. Expecting monotone or fast convergence
The weak law gives convergence in probability with no rate; the strong law (Kolmogorov 1930) gives almost sure convergence with *no usable bound at all* (by the law of the iterated logarithm, the deviation is of order √(n log log n)/n infinitely often). A short simulation showing the mean wandering is not evidence against the theorem — and one showing it settling is not proof of it.

### 7. Confusing weak and strong convergence statements
WLLN: X̄ₙ →μ in probability — P(|X̄ₙ − μ| > ε) → 0. SLLN: P(lim X̄ₙ = μ) = 1 — a statement about the whole sequence on one event. Sample proportions satisfying "95% of intervals within ε" is a *confidence* statement, not the SLLN; the distinction matters when n is random (sequential stopping).

### 8. Chebyshev used as if it were an approximation
Chebyshev's P(|X̄ − μ| ≥ kσ/√n) ≤ 1/k² is a worst-case bound with no normality assumption — valid but often loose by 2–3 orders of magnitude (STEP_BY_STEP: 0.081 bound vs 0.00044 actual for k ≈ 3.5). It is a guarantee, not an estimate; do not report it as "the probability."

## Self-check: do these answers hold up?

1. *"1000 flips gave 52% heads — the coin is biased, p < 0.05."* — z = 0.02/√(0.25/1000) = 1.265, two-sided p = 0.206. At n = 1000 the CLT says this deviation is ordinary; a biased conclusion here is the *power* error (lab 07), not a CLT error — 80% power for that 2-point bias needs n ≥ (1.96 + 0.84)²·0.25/0.02² ≈ 4900 — about 5× this run.
2. *"±2% precision, so we need about twice the respondents of a ±4% poll."* — n scales as 1/e²: n ≥ 1.96²·0.25/0.02² = 2401 (vs 601 for ±4%). Half the error, four times the cost — plans built on linear scaling come in 4× short.
3. *"The server logs are n = 3000 measurements, so SE = σ/√3000."* — Only if independent. With lag-1 correlation ρ = 0.5 in an AR(1) stream, n_eff = n(1−ρ)/(1+ρ) = n/3: your real SE is √3 ≈ 1.7× the reported one, and the report is over-confident by that factor.
4. *"The simulation mean settled at run 20 000, so convergence is slow."* — Convergence in probability is about ensembles, not one path: the fluctuation of a single path is governed by the law of the iterated logarithm, which *never* stops wandering. Judge convergence across replications (SE of the replication mean), never along one trajectory.
