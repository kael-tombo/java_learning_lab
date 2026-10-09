# How It Works: Probability Distributions

## 1. A family is a functional form plus parameters
Binomial(n, p): the *shape* is C(n,k)pᵏ(1−p)^{n−k}, fixed by the mechanism of n independent trials; (n, p) carry all the freedom. Data enters only through the parameters — fitting a distribution is the problem of choosing them (method of moments, MLE: labs 06 and 08).

## 2. Discrete: recurrence beats factorials
P(X = k+1)/P(X = k) = (λ/(k+1)) for Poisson, = ((n−k)/(k+1))·(p/(1−p)) for Binomial. One multiply/divide per term, no factorials, no overflow, and the terms decay fast enough that summing stops when the tail is below machine epsilon relative to the sum.

## 3. Continuous: normalize, then integrate
A kernel like e^{−x²} must be divided by its total mass ∫e^{−x²}dx = √π to become N(0, 1/2) with the right constant; every exponential-type density carries a normalizing constant 1/Γ(α)β^α for exactly this reason. The cdf is then the accumulated area, and the pdf is its derivative — the two are never independent facts.

## 4. Standardization does real work
(X − μ)/σ maps any normal to N(0,1), so P(X ≤ x) = Φ((x − μ)/σ) — one table serves every μ, σ. For differences of means, the *variances add* first (σ_D = √(σ₁² + σ₂²)) and only then is standardized: in STEP_BY_STEP's example, D ~ N(20, 164) and P(D > 0) = Φ(1.562) ≈ 0.941.

## 5. Limits turn families into each other
Binomial(n, p) → Poisson(np) as n → ∞, p → 0 with np fixed (P(X = 0) example in COMMON_MISTAKES shows why rate matters). Poisson(λ) → Normal(λ, λ) by the CLT for λ large. Binomial(n, p) → Normal(np, np(1−p)). These are not approximations of convenience: they are the same law seen at different scales, and each has a quantifiable error (Berry–Esseen: ≤ C·ρ/(σ³√n)).

## 6. Convolution is how families compose
Sum of independent Poissons → Poisson(λ₁ + λ₂); sum of independent gammas with the same scale → gamma(α₁ + α₂); weighted sum of normals → normal. Where no closed form exists (sum of uniforms → Irwin–Hall → approaches normal), the CLT or FFT convolution takes over.

## 7. Hazards and survival
h(x) = f(x)/(1 − F(x)) — the instantaneous failure rate. Constant h = λ means exponential (memoryless); increasing h means aging (Weibull with shape > 1); decreasing h means burn-in (shape < 1). The hazard *shape*, not the pdf shape, is what reliability engineering reads off the data.

## 8. Fitting is a different question from sampling

Sampling asks "give me one plausible value"; fitting asks "which parameter made the data I have most likely." They use the same density from opposite sides. Method of moments solves E[X] = x̄ and E[X²] = x̄² + s² for the parameters; MLE maximizes Σ log f(xᵢ; θ). For the exponential both give λ̂ = 1/x̄; for the Poisson both give λ̂ = x̄; for the negative binomial they disagree, and the disagreement is exactly the small-sample bias of the moment estimator — which is why lab 06 prefers MLE and lab 08 puts a prior on top of the same likelihood.

## 9. Mixtures break every "one mechanism" identity

0.5·N(0, 1) + 0.5·N(4, 1) has mean 2 and variance 0.5(1 + 0) + 0.5(1 + 16) − 4 = 5, yet its density *at* 2 is only 0.054 — less than half the density at 1 (0.123) and at 3 (0.123), because 2 sits in the trough between the two components. Consequence: mean = 2 and SD ≈ 2.24 describe a distribution whose typical values avoid the mean entirely. Whenever a fitted mean lands where the data never are, suspect a mixture (two machines, two populations, two regimes) before refining the single-family fit.
