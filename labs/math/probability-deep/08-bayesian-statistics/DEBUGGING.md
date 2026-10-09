# Debugging: Bayesian Statistics

### Symptom: posterior density integrates to 1.7 (or 0.003)
The normalizing constant was dropped or computed wrong. If you evaluated on a grid, integrate the *unnormalized* density and divide by the total: `w[i] /= Σw[i]·dθ`. If you are sampling, the draws are from the shape regardless of the constant — but any *marginal likelihood* or Bayes factor you compute from unnormalized values is garbage.

### Symptom: chains disagree (split-R̂ ≫ 1.01)
Modes: (1) **different modes per chain** — the classic multimodal posterior (mixture weights, label switching); no amount of iterations fixes it, reparameterize or use more dispersed initialization; (2) **poor mixing** — increase adaptation/step size or switch to HMC; (3) **non-identifiability** — flat ridges (α and β trading off) make the posterior improper along a direction. R̂ detects all three; single chains never do.

### Symptom: ESS ≈ 200 from 200 000 draws
Autocorrelation time τ ≈ 100: the random walk is far too slow (step size not adapted, or a heavy-tailed posterior with occasional long excursions). Fixes: adapt the proposal scale to target ~20–25% acceptance for random-walk Metropolis, reparameterize to a geometry HMC can follow (non-centered parameterization for hierarchical models), or thin only for storage — thinning does not create information.

### Symptom: posterior is dominated by the prior and you didn't expect it
Prior strength: Beta(100, 100) contributes 200 pseudo-observations; 20 real flips barely move it. Print the prior's effective sample size (α + β for Beta) next to n. Also check the likelihood is actually being evaluated — a bug returning a constant makes posterior = prior silently.

### Symptom: NaN in the log-posterior
log 0 from a likelihood at θ on the boundary (e.g. p = 1 with a tail observation) or underflow from multiplying densities. Always compute **log**-posterior = Σ log-likelihood + log-prior; guard the support (reject proposals outside it rather than evaluating log(−∞)).

### Symptom: uniform prior produces an improper posterior
π(θ) = 1 on (0, ∞) with an Exponential likelihood: ∫ L(θ)dθ can diverge, so the posterior isn't a distribution and no MCMC can exist (the chain drifts forever). Check integrability analytically for simple models; numerically, watch whether the sample variance keeps growing with iterations — that is a signature of impropriety, not slow mixing.

### Symptom: MCMC and conjugate answers disagree
For Beta–Binomial, compare the sampled posterior mean (ESS-corrected MC error) to 11/14 = 0.7857: if the discrepancy exceeds ~2·SE_MC, the sampler or the likelihood differs from the model you think you specified (wrong prior, dropped Jacobian from a transformation, or data double-counted). The conjugate path is the oracle for every MCMC path.

### Symptom: HMC reports divergent transitions
The integrator could not resolve the geometry — typically a funnel (hierarchical σ), a hard boundary, or parameters on wildly different scales (one at 10⁻³, one at 10⁵). Fix in order: non-centered parameterization (z ~ N(0,1), θ = μ + σ·z) to remove the funnel, rescale inputs to O(1), then raise target_accept (0.8 → 0.95) for smaller leapfrog steps. Divergences are not cosmetic: mass is missed exactly where the funnel narrows, so summaries stay biased even at split-R̂ = 1.00.

### Symptom: mixture model's labels flip between chains
Label switching: the posterior has k! symmetric modes (component 1 in chain A ↔ component 2 in chain B), so R̂ ≫ 1 while each chain is internally perfect. No tuning fixes a symmetry by construction — identify the components (order the means μ₁ < μ₂ < …, or anchor to a well-measured component) or relabel post hoc (pivot algorithm / Hungarian matching on a reference component).

### Symptom: prior predictive draws are orders of magnitude off
A prior put on the wrong scale (Exponential(1) on a quantity measured in milliseconds) produces prior-predictive draws nobody would believe — and the posterior hides the mistake by contracting onto the data anyway. Simulate *before* fitting: draw θ ~ π, then × ~ P(·|θ), and check the 95% prior-predictive band brackets the observable's plausible range. One loop; catches scale bugs no convergence diagnostic can see.
