# Estimation Theory — Quiz (15 Questions with Worked Answers)

Point estimators, bias–variance, MLE, Fisher information, and the Cramér–Rao bound — with the traps each result sets.

---

## Q1 — Unbiased does not mean low variance
**Q.** Two estimators for θ: an unbiased one with huge variance, a biased one with tiny variance. Which has lower MSE?

**A.** MSE = Bias² + Var. An unbiased estimator with variance 100 has MSE 100; a biased one with bias 0.1 and variance 0.01 has MSE 0.0101. The biased estimator wins. "Unbiased" is a property of the *average* over the sampling distribution, not a guarantee of a good single estimate. In small samples, biased estimators (or shrinkage estimators) systematically have lower MSE — the James–Stein phenomenon is the dramatic form of this.

---

## Q2 — MLE is consistent, asymptotically normal, efficient
**Q.** State the three standard asymptotic properties of the MLE and the condition each needs.

**A.** Under regularity conditions (support independent of θ, identifiable, differentientiable in θ, Fisher information finite and positive): (1) consistency — θ̂_n → θ a.s.; (2) asymptotic normality — √n(θ̂_n - θ) ⇒ N(0, I(θ)⁻¹); (3) asymptotic efficiency — its asymptotic variance I(θ)⁻¹ equals the Cramér–Rao lower bound. These are asymptotic statements: for finite n the MLE can be biased (e.g. the variance MLE with denominator n is biased; n-1 debiases it), can be inconsistent in misspecified models (then it converges to the KL-closest parameter), and can be dominated by another estimator.

---

## Q3 — Cramér–Rao lower bound
**Q.** State the CR bound and when an estimator achieves it.

**A.** For any unbiased estimator T of g(θ), Var(T) ≥ (g'(θ))² / I_n(θ), where I_n(θ) is the Fisher information of the sample. Equality holds iff the score is a linear function of the estimator: ∂/∂θ log L = a(θ)(T - g(θ)) — i.e. the family admits T as a sufficient statistic of a particular linear form. This exponential-family condition is the "efficient estimator exists" characterisation. For the normal mean with known variance, the sample mean achieves the bound; for the variance, the biased denominator-n MLE achieves it.

---

## Q4 — Fisher information
**Q.** Define Fisher information and show it is additive for i.i.d. samples.

**A.** I(θ) = E[(∂/∂θ log f(X;θ))²] = -E[∂²/∂θ² log f(X;θ)] (the two forms agree under regularity). For an i.i.d. sample of n, the log-likelihood is a sum, the score is a sum of independent mean-zero terms, so Var(score) = n·Var(single score) — I_n(θ) = n·I(θ). Fisher information is the *signal* in the sample: it is the curvature of the log-likelihood at the true parameter, and it directly sets the CR bound"s denominator. Double the sample, double the information, halves the variance of the best unbiased estimator.

---

## Q5 — Method of moments vs MLE
**Q.** When do they agree, and which is more efficient in general?

**A.** Method of moments (MoM) matches sample moments to population moments; MLE maximises the likelihood. They agree for the normal (MoM for μ, σ² equals the MLE) and for the exponential family in natural parameters (matching the sufficient statistics *is* the MLE equation). In general they differ, and the MLE is asymptotically efficient while MoM is only consistent. Example: uniform(0,θ) — MoM gives θ̂ = 2·X̄, MLE gives θ̂ = max X_i. The MLE has variance θ²/((n+1)(n+2))·(... ) ≈ θ²/n²... precisely Var(max) = nθ²/((n+1)²(n+2)), much smaller than MoM's 2σ·... — the MLE wins because it uses every order statistic implicitly, MoM uses only the mean.

---

## Q6 — Bias–variance for the sample mean
**Q.** Is the sample mean unbiased for μ, and what is its variance?

**A.** X̄ = (1/n)ΣX_i. E[X̄] = (1/n)ΣE[X_i] = μ regardless of distribution — unbiased. Var(X̄) = σ²/n by independence. MSE(X̄) = σ²/n, which is the variance since bias is 0. This is the cleanest case: unbiasedness is exact, the variance shrinks as 1/n, and the CLT gives the shape of the error. Note that "unbiased" is about the *average over the sampling distribution*, not about any single sample.

---

## Q7 — Sufficient statistics preserve information
**Q.** What is a sufficient statistic, and why does the MLE depend on the data only through it?

**A.** T is sufficient for θ if the conditional distribution of X given T does not depend on θ: P(X=x | T=t) is θ-free. By the factorisation theorem, T is sufficient iff the likelihood factors as L(θ;x) = g(T(x),θ)·h(x). The MLE depends on x only through T(x) because log L = log g(T(x),θ) + log h(x), and only the first term involves θ. So the sufficient statistic is the minimal reduction of the data that loses no information about θ — the sample mean for the normal, max for uniform(0,θ), and for the exponential family the whole vector of sufficient statistics.

---

## Q8 — Confidence intervals from the MLE
**Q.** How do you build an approximate 95% CI for θ from the MLE?

**A.** Asymptotic normality gives √n(θ̂-θ) ⇒ N(0, I(θ)⁻¹), so θ̂ ≈ N(θ, (nI(θ))⁻¹). A Wald interval is θ̂ ± 1.96·SE, SE = 1/√(n·I(θ̂)) (plug-in estimate of I at θ̂). It is only asymptotically valid — for small n, skewed likelihoods (Poisson with small counts, proportions near 0 or 1), or curved parameter spaces, the Wald interval can fall outside the parameter space or have poor coverage. The likelihood-ratio interval {θ : 2(ℓ(θ̂)-ℓ(θ)) ≤ χ²₁(0.95)} is more accurate for moderate n because it respects the asymmetry of the likelihood.

---

## Q9 — Regular vs irregular estimators
**Q.** Why does the normal-MLE theory fail for uniform(0,θ)?

**A.** The support [0,θ] depends on θ, violating the regularity condition that the support is θ-free. The log-likelihood ℓ(θ) = -n log θ·1{θ ≥ max X_i} is discontinuous at θ = max X_i, with no derivative there. So the MLE θ̂ = max X_i converges to θ at rate 1/n (not 1/√n), and its limiting distribution is (n(θ-θ̂))/θ ⇒ Exp(1) — not normal. The CR bound does not apply; the variance of θ̂ is θ²/((n+1)²·(n+2))·... specifically Var = nθ²/((n+1)²(n+2)) ≈ θ²/n², an order of magnitude smaller than regular estimators. The lesson: regularity conditions are not boilerplate; they *are* the theorem.

---

## Q10 — Bayes vs frequentist: the role of the prior
**Q.** How does a Bayesian point estimator differ from the MLE?

**A.** The MLE maximises the likelihood L(θ; x). The Bayesian posterior is p(θ|x) ∝ L(θ;x)·π(θ), and a point estimate is a functional of the posterior — the posterior mean (minimises squared loss), posterior median (absolute loss), or MAP (0-1 loss, maximises L·π). The MAP equals the MLE when π is flat; it adds regularisation when π has curvature. So Bayesian estimation is not a different philosophy of probability so much as a different loss choice over the posterior that also defaults to the MLE under a flat prior.

---

## Q11 — Plug-in bias of nonlinear functionals
**Q.** Bias of θ̂² where θ̂ is unbiased for θ?

**A.** E[θ̂²] = Var(θ̂) + (Eθ̂)² = Var(θ̂) + θ² — so θ̂² overestimates θ² by Var(θ̂). The plug-in estimator is biased upward by the variance. The delta method linearises: g(θ̂) ≈ g(θ) + g'(θ)(θ̂-θ), giving bias ≈ ½g''(θ)Var(θ̂). For g(θ)=θ², g''=2, so bias ≈ Var(θ̂) — matching the exact calculation. This is the general reason plug-in estimators of nonlinear functionals are biased: the curvature of g converts estimation error into systematic error.

---

## Q12 — Sample variance unbiased?
**Q.** Is s² = (1/(n-1))Σ(X_i-X̄)² unbiased for σ²? What about the version with 1/n?

**A.** E[Σ(X_i-X̄)²] = (n-1)σ² — this follows from Σ(X_i-μ)² = Σ(X_i-X̄)² + n(X̄-μ)² and taking expectations, using E[n(X̄-μ)²] = n·σ²/n = σ². So dividing by n-1 debiases s²; dividing by n gives (n-1)/n·σ², biased downward by a factor (n-1)/n. The 1/n version is the MLE, the 1/(n-1) version is unbiased. Both are consistent; for large n the difference is negligible. So "s² is unbiased" is true only for the n-1 denominator — the naive n denominator quietly shrinks the estimate.

---

## Q13 — Consistency is asymptotic unbiasedness + vanishing variance
**Q.** Every unbiased estimator is consistent — true or false?

**A.** False. Consider X_i ~ N(0,1): T_n = X_1 for all n is unbiased for 0 but Var(T_n) = 1, so T_n does not converge to 0 — it is not consistent. Consistency requires the error to vanish: T_n → θ in probability. Unbiasedness fixes the *mean*, not the *concentration*. The clean sufficient condition: unbiased + Var(T_n) → 0 ⇒ consistent (by Chebyshev). The sample mean has both, so it is consistent; the first observation has only the first, so it is not.

---

## Q14 — Fisher information for a location family
**Q.** For X ~ N(μ, σ²), what is the Fisher information for μ?

**A.** log f = -½log(2πσ²) - (x-μ)²/(2σ²). ∂/∂μ log f = (x-μ)/σ². I(μ) = E[(X-μ)²]/σ⁴ = σ²/σ⁴ = 1/σ². So the information about the mean is 1/σ² — the noisier the observation, the less information each one carries. For n i.i.d. observations, I_n(μ) = n/σ², so the CR bound on Var(μ̂) is σ²/n — exactly the variance of X̄, which therefore achieves the bound. This is why the sample mean is the UMVUE for the normal mean.

---

## Q15 — Likelihood-ratio ordering of estimators
**Q.** How does the Wilks theorem shape confidence regions?

**A.** For a k-dimensional parameter, Wilks' theorem says 2(ℓ(θ̂) - ℓ(θ)) ⇒ χ²_k under the null. So the confidence region {θ : 2(ℓ(θ̂)-ℓ(θ)) ≤ χ²_k(1-α)} has asymptotic coverage 1-α. For k=1 this is θ̂ ± z_{α/2}·SE in the symmetric case; for asymmetric likelihoods it correctly captures the shape, unlike the symmetric Wald interval. Wilks is the theoretical justification for using the likelihood-ratio test and interval whenever the regularity conditions hold — and its failure for boundary parameters (e.g. testing variance = 0) is a standard trap.

---

