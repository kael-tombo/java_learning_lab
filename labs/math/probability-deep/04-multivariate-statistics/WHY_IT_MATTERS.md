# Why It Matters: Multivariate Statistics

## Every "controlling for" is a multivariate claim
A regression with k covariates, an ANOVA with interactions, a matched case-control study — all are partial-regression computations from a joint covariance structure. Reporting a marginal association (smoking vs. disease, unadjusted) alongside the adjusted one is standard practice precisely because Yule/Simpson effects are common: the marginal and partial coefficients can differ in *sign*.

## Risk, returns, and Σ
Portfolio variance is wᵀΣw, not Σwᵢ²σᵢ². With two assets of equal variance σ² at ρ = 0.6 and equal weights, the true variance is 0.25σ² + 0.25σ² + 2(0.25)ρσ² = 0.5σ²(1+ρ) = 0.8σ²; assuming ρ = 0 predicts 0.5σ² — understating variance by 37.5% (reported σ 0.707 vs true 0.894, i.e. 21% too low). Diversification still helps (0.8σ² < σ² of one asset) *only* because ρ < 1. Every risk model — and every 2008-era CDO failure, where Σ was estimated from a short calm history — is a bet on this matrix.

## Dimensionality decides whether estimation is possible
Sample covariance has p(p+1)/2 free parameters; with p = 10 000 features and n = 500 samples, the covariance is unestimable without shrinkage/PCA. Genomics, NLP and sensor fusion all hit this wall first — which is why Ledoit–Wolf shrinkage (2004), sparse Σ estimation and PCA-before-modeling are load-bearing techniques, not conveniences.

## Anomaly detection, biometrics, quality
- Multivariate SPC (Hotelling's T² chart) catches a shift that moves two correlated measurements *jointly* while each stays inside its own control limits.
- Keystroke/mouse-behavior authentication and face recognition both reduce to distance in a whitened, low-dimensional space.
- Fraud rings show up as clusters in joint feature space that marginals never reveal.

## Where it hands off
Lab 05 needs the CLT *for* X̄ (a vector, hence Σ/n scaling); lab 06's MLE of μ, Σ assumes the multivariate normal; lab 07's χ² contingency test is a multinomial covariance constraint; lab 08's Dirichlet is the conjugate prior for a multinomial. Multivariate structure is the substrate under all four.

## Concrete decisions that change when Σ is included

**Portfolio allocation.** Two assets, σ = 0.2 each, ρ = 0.6, equal weights: true variance = 0.5σ²(1 + ρ) = 0.032, σ_p = 0.179. Ignoring correlation predicts σ_p = 0.141 — a 21% underestimate of risk that sizes the reserve too small. With ρ = 0.95 (crisis regime), σ_p = 0.197: the same allocation code with a stale Σ is a different risk position.

**Diagnosis combining several markers.** Two biomarkers with r = 0.7 that each "add information": the joint score's effective dimension is close to one — measuring both costs double for near-zero gain; with r = −0.2 they are genuinely complementary. Which panels to run is a question about Σ, not about either marker's individual AUC.

**Sensor placement and monitoring.** If two sensors' readings share 95% of variance, monitoring both adds one alarm channel, not two — but it doubles the chance that a *single* common-mode fault trips both, which changes how redundancy should be designed (independent failure modes, not just duplicated coverage).

**Feature screening before modeling.** In n = 500, p = 10 000 settings, the choice between "drop correlated duplicates" and "shrink Σ" changes both runtime (p³ vs k³ eigendecomposition) and interpretability — it is decided by the spectrum (effective rank), which you should compute before any model choice.

## Reading checklist for any multivariate result

- What n and p, and what was n/p? (Below ~0.1, treat every inverse with suspicion.)
- Which Σ — sample, shrunk (δ?), or robust — and what condition number?
- Is the headline claim about *marginal* or *partial* association, and does the paper say which?
- For PCA results: Σ or correlation matrix, how many components, and what does "variance explained" not imply about prediction?
