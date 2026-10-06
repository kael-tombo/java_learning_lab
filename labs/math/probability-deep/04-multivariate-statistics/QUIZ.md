# Multivariate Statistics — Quiz (15 Questions with Worked Answers)

Multivariate distributions, correlation, covariance matrices, PCA, and the conditioning traps that survive into every data pipeline.

---

## Q1 — The covariance matrix is PSD
**Q.** State the covariance matrix and prove it is positive semi-definite.

**A.** For X ∈ ℝ^d with mean μ, Σ = E[(X-μ)(X-μ)ᵀ]. For any v ∈ ℝ^d, vᵀΣv = E[(vᵀ(X-μ))²] ≥ 0 — it is the expected value of a squared real quantity. So all eigenvalues are non-negative. This is why covariance matrices can be diagonalised by an orthogonal matrix (the PCA basis), and why a "variance" along any direction v is automatically non-negative.

---

## Q2 — Zero correlation does not imply independence
**Q.** Give a counter-example to: Cov(X,Y) = 0 ⇒ X ⟂ Y.

**A.** X ~ Uniform(-1,1), Y = X². Cov(X,Y) = E[X³] - E[X]E[X²] = 0 - 0 = 0 (X³ is odd, and E[s³] over a symmetric distribution is 0). Yet Y is a deterministic function of X — maximally dependent. The converse holds (independence ⇒ Cov = 0), so zero covariance is a *necessary* but not sufficient condition for independence. The exception that proves the rule: jointly Gaussian variables, where zero covariance implies independence.

---

## Q3 — Conditional expectation as projection
**Q.** State the L²-projection characterisation of E[Y|X] and why it minimises MSE.

**A.** E[Y|X] is the unique function of X that is orthogonal to every other function of X: E[(Y - E[Y|X])·g(X)] = 0 for all g. Hence for any predictor Ŷ = h(X), E[(Y-h(X))²] = E[(Y-E[Y|X])²] + E[(E[Y|X]-h(X))²] ≥ E[(Y-E[Y|X])²] — the error splits into the irreducible part plus a non-negative term vanishing only when h = E[Y|X] a.s. So E[Y|X] is the minimum-MSE predictor, and the best *linear* predictor is its linear approximation — which is exact iff (X,Y) are jointly Gaussian.

---

## Q4 — PCA: variance maximisation = eigenproblem
**Q.** Derive the direction of maximum variance of a centred data matrix.

**A.** For unit v, the projected variance is vᵀΣv. Maximise subject to ‖v‖=1: the Lagrangian gives ∇(vᵀΣv - λ(vᵀv-1)) = 2Σv - 2λv = 0, so Σv = λv — a critical point is an eigenvector, and the max is the largest eigenvalue with its eigenvector. The second PC is the same problem restricted to be orthogonal to the first, yielding the next eigenvector, and so on. PCA is exactly the eigendecomposition of Σ, and the explained-variance fraction of PC k is λ_k/Σλ_i.

---

## Q5 — Why scale features before PCA
**Q.** Two features measured in metres and millimetres — what breaks if you do not standardise?

**A.** PCA finds directions of *maximal variance*, and variance scales quadratically with the unit: a feature measured in millimetres has variance ≈ 10⁶× the same feature in metres. The first PC will align almost exactly with the millimetre feature regardless of its real importance. Standardising (subtract mean, divide by std) equalises the marginal variances so PCA compares directions rather than units. This is a modelling choice, not a mathematical necessity — sometimes the units carry real information.

---

## Q6 — Correlation is unit-free; covariance is not
**Q.** Compute Corr(X,Y) and show it is invariant under affine rescaling.

**A.** ρ(X,Y) = Cov(X,Y)/(σ_X σ_Y). Under X ↦ aX+b, Y ↦ cY+d: Cov becomes ac·Cov, σ_X σ_Y becomes |ac|·σ_Xσ_Y, so ρ ↦ (ac/|ac|)·ρ = sign(ac)·ρ. The magnitude is preserved, only the sign can flip when exactly one scaling is negative. Correlation is the cosine of the angle between the centred, standardised vectors — a pure shape measure of linear dependence.

---

## Q7 — Mahalanobis distance and whitening
**Q.** Define Mahalanobis distance and show it is unit-invariant; relate it to PCA whitening.

**A.** d_M(x,y) = √((x-y)ᵀ Σ⁻¹ (x-y)). Under any affine change of coordinates it is invariant (Σ transforms congruently, so Σ⁻¹ absorbs the linear factor). If you whiten the data, z = W(x-μ) with Σ_z = WWᵀ = I (e.g. W = Σ^{-1/2} from the eigendecomposition Σ = QΛQᵀ, W = Λ^{-1/2}Qᵀ), then d_M becomes the ordinary Euclidean distance in z-space. PCA-whitening rescales each PC to unit variance; ZCA-whitening rotates back to the original axes. Both are the same idea seen from different angles.

---

## Q8 — Simpson's paradox
**Q.** Give a numerical counter-example to: "A has a better success rate than B overall, so A is better in every stratum."

**A.** Stratum 1: A 8/10 (80%), B 18/20 (90%). Stratum 2: A 45/50 (90%), B 2/4 (50%). Overall: A 53/60 (88.3%), B 20/24 (83.3%). B wins both strata, yet A wins overall because A treats mostly stratum 2 (easy) cases. Simpson's paradox: aggregation reverses the within-stratum comparison whenever the stratum sizes differ and the strata have different base rates. The fix is to report the conditional (per-stratum) rates, not the marginal one — and to ask, for every marginal comparison, what the lurking stratifier is.

---

## Q9 — Conditioning vs marginalisation
**Q.** State the law of total expectation and a common misapplication.

**A.** E[Y] = E[E[Y|X]] — the marginal expectation is the average of the conditional expectations over the distribution of X. Misapplication: conditioning on an event and then *averaging without the right weights*. E.g. P(A) = Σ_x P(A|X=x)P(X=x), not (1/n)Σ P(A|X=x). The classic Simpson-paradox-adjacent error is averaging conditional probabilities over strata of unequal size. Weights matter: the stratum distribution is part of the statement.

---

## Q10 — The Gaussian is determined by two moments
**Q.** Why is a multivariate Gaussian fully specified by μ and Σ, and what breaks otherwise?

**A.** For a Gaussian, the log-density is a negative quadratic in (x-μ): log p(x) = -½(x-μ)ᵀΣ⁻¹(x-μ) + const — the exponent is fixed by μ and Σ. Any other family is not so determined: two different distributions can share the same mean and covariance (e.g. a Gaussian and a mixture tweaked to match two moments). This is why "PCA is just a Gaussian model" is wrong unless the data is actually Gaussian — PCA uses only the first two moments, so it is the *best linear* summary, but not the full distribution.

---

## Q11 — Shrinkage of the covariance estimate
**Q.** In the small-n large-d regime, why is the sample covariance Σ̂ unstable, and what is the fix?

**A.** The sample covariance Σ̂ has rank at most n-1 and, when d is comparable to n, its smallest eigenvalues collapse toward 0 while the largest inflate — the condition number blows up. Inverting Σ̂ (for Mahalanobis, for whitening, for discriminant directions) then amplifies noise. The fix is shrinkage: use Σ_shrink = (1-λ)Σ̂ + λ·T for a well-conditioned target T (often the diagonal of Σ̂, or σ²I). Ledoit–Wolf give the optimal λ in closed form. The same instability is why high-d Gaussian graphical models need regularisation.

---

## Q12 — Canonical correlation analysis
**Q.** Define CCA and what it optimises.

**A.** Given two sets of variables X ∈ ℝ^p, Y ∈ ℝ^q, CCA finds linear projections a, b maximising Corr(aᵀX, bᵀY). Successive pairs are restricted to be uncorrelated with the earlier ones. The solution reduces to a generalised eigenproblem on the covariance blocks: Cov(X,Y)Cov(Y)⁻¹Cov(Y,X) vs Cov(X). CCA is the two-view generalisation of PCA — instead of maximum variance of one variable set, it finds the maximal *shared* linear structure between two sets. Its sample version needs the same shrinkage caution as Σ̂.

---

## Q13 — Why the inverse covariance is the graph
**Q.** In a Gaussian graphical model, what does a zero entry of Σ⁻¹ mean?

**A.** For a jointly Gaussian vector, Cov(X_i, X_j | rest) ∝ -(Σ⁻¹)_{ij}. So (Σ⁻¹)_{ij} = 0 iff X_i ⟂ X_j | rest — i.e. no *direct* edge between them in the conditional-independence graph. The marginal covariance Σ has many non-zero entries along longer paths; the precision matrix Σ⁻¹ isolates direct links. This is the basis of many network-inference methods, and it is why the precision matrix — not the covariance — is the object to estimate when p is large.

---

## Q14 — The curse of dimensionality in one line
**Q.** Why does nearest-neighbour degrade in high dimensions?

**A.** As d grows, the distance to the nearest neighbour and the distance to the farthest neighbour both concentrate: by the LLN, ‖x - x_i‖² ≈ d·(per-coordinate variance) for almost all points, so every pair is about equally far. The contrast that NN relies on — (max-min)/min of distances — collapses to 0. Distance-based methods need exponential sample size to maintain constant contrast. This is the informal statement of the curse of dimensionality, and why high-d data pipelines reduce dimension (PCA, feature selection) before nearest-neighbour or clustering.

---

## Q15 — Bartlett"s test of sphericity
**Q.** What does Bartlett's test test, and when is the conclusion "the covariance is not isotropic"?

**A.** Bartlett's test asks whether Σ is proportional to the identity — H₀: Σ = σ²I. It uses the likelihood-ratio statistic from the sample Σ̂; under H₀ it is approximately chi-squared with d(d-1)/2 dof. A small p-value rejects isotropy, i.e. the variances/correlations are not all equivalent. The practical use is a sanity check before PCA: if you cannot reject Σ = σ²I, the PCs carry no structure beyond equal noise, and the whole analysis is fitting noise. The test is sensitive, so a large sample "rejects" trivially — always report the effect size (the eigenvalue spread) alongside the p-value.

---

