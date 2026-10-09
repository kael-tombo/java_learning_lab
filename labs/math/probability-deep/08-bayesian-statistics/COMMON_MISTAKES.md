# Common Mistakes: Bayesian Statistics

### 1. Confusing P(A|B) with P(B|A) — and forgetting the base rate
The medical test again: 1% prevalence, 99% sensitivity, 95% specificity → P(D | +) = 0.0099/0.0594 = **16.7%**, not 99%. Bayesian updating makes the prior do real work; skipping P(+) in the denominator is the same error as lab 01, now wearing Bayesian clothes.

### 2. Using the likelihood ratio twice
Fitting a prior *from the data* (empirical Bayes: β from the same sample) and then multiplying that prior by the same data's likelihood double-counts one observation — the posterior is overconfident by roughly a factor of 2 in information. Proper fix: hierarchical modeling (put hyperpriors on β) or leave-one-out cross-validation.

### 3. Reporting the unnormalized posterior as if it were a probability
p(θ|D) ∝ L(θ)π(θ) — the proportionality constant is the marginal likelihood P(D) = ∫L(θ)π(θ)dθ, and without it you have no posterior *probabilities*, no model comparison, and possibly no proper distribution (∫posterior ≠ 1). Normalize numerically (grid/quadrature) or sample properly.

### 4. Confusing credible intervals with confidence intervals
A 95% credible interval is a set with 95% posterior probability of containing θ *given the model and prior*. A 95% CI has 95% coverage over repeated samples and says nothing about this θ. They share the notation "95%" and none of the semantics; stating "there is a 95% probability θ ∈ (a, b)" is Bayesian and requires the posterior you actually computed.

### 5. Priors that are uniform in the wrong parameterization
"θ ~ Uniform(0,1)" on a rate λ means something different from "log λ ~ Uniform(−10, 0)": a prior flat in one parameter is strongly informative in another. Jeffreys's response (1939) was reference priors invariant to reparameterization — for a binomial p, π(p) ∝ 1/√(p(1−p)); for a scale σ, π(σ) ∝ 1/σ.

### 6. Ignoring the prior's influence when data are scarce
With 10 flips, Beta(2,2) posterior mean 11/14 = 0.786 vs a Beta(1,1) prior giving 10/12 = 0.833 vs Beta(0.5,0.5) giving 10/11 = 0.909. Report a prior-sensitivity analysis: if conclusions move materially, the data don't speak loudly enough to hide your prior choice.

### 7. Trusting MCMC without diagnostics
Correlated draws make 100 000 iterations behave like ~2 000 independent samples (ESS). Requirements before reading a posterior: split-R̂ < 1.01 across ≥ 4 chains (Vehtari et al. 2021), ESS > 400 for the quantities you report, and no trend/multimodality in trace plots. A single chain that "looks fine" is the classic failure.

### 8. Reading Bayes factors like p-values
BF₁₀ = 12 is evidence *for* H₁ in the odds sense (posterior odds = prior odds × BF) — it must be combined with prior model odds, and it is sensitive to the prior on θ under H₁ (the Jeffreys–Lindley paradox: with diffuse priors, moderate data favor H₀). Do not map BF onto the α = 0.05 scale.

### 9. Treating the highest-density interval as parameterization-invariant
An HDI on σ, pushed through the monotone map σ → log σ, is *not* the HDI on log σ — highest-density sets do not commute with reparameterization, while equal-tail quantiles do. For skewed posteriors (variances, rates, anything on a positive axis) the two intervals differ visibly. Pick one by policy, label it in the report, and never carry an HDI across a parameter change as if it were the same set.

### 10. Reading P(θ > 0 | D) = 0.97 as "97% confident the effect is real"
That number prices *parameter* uncertainty conditional on the model M; it says nothing about whether M belongs in the conversation. If the data came from over-dispersion, selection, or a missing covariate, the posterior concentrates on the best wrong answer with probability approaching 1. Model criticism (posterior predictive checks) and model averaging (BF/LOO) are how the model index gets priced — the interval alone never will.

**Rule of thumb**: if swapping equal-tail for HDI moves your conclusion, the posterior's *shape* is the finding — show the density, not the bracket.
