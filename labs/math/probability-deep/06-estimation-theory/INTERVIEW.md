# Interview: Estimation Theory

### Q1. MLE or method of moments? When do they differ?
**A.** MLE maximizes the likelihood (efficient asymptotically, attains Cramér–Rao in regular families); moments match sample to population moments (closed form, can be badly inefficient or even outside the parameter space). They coincide for binomial p (both = k/n) and normal μ, but for Lognormal(μ, σ²) the moment estimator on raw data has far larger variance than the MLE on log data, and for some models the moment estimate can violate constraints. Default to MLE; fall back to moments when the likelihood has no closed form or as an optimizer starting value.

### Q2. You use σ̂² = Σ(x−x̄)²/n. What's the issue, and when is it correct?
**A.** It's the MLE and is biased: E = (n−1)/n·σ² (10% low at n = 10). For inference — t-tests, SEs — use n−1 so the variance of s² matches theory and x̄ and s² are independent under normality. The 1/n MLE *is* correct where likelihood itself is evaluated (log-likelihood for AIC/BIC, conditional maximum likelihood) — and it is asymptotically negligible. The real sin is mixing the two in one calculation.

### Q3. State the Cramér–Rao bound and one situation it doesn't apply to.
**A.** For a regular family, any unbiased estimator satisfies Var(θ̂) ≥ 1/(n·I(θ)), I(θ) = −E[∂²ℓ/∂θ²]. It fails when the family is irregular: support depends on θ (Uniform(0,θ), Pareto scale), the parameter is on the boundary (variance = 0, mixture weight = 0), or information is singular (p ≥ n). There the bound is undefined and the estimator's rate changes — for Uniform(0,θ) the MLE converges at rate n with an extreme-value limit, not √n with a normal limit.

### Q4. How do you get an interval when Var(θ̂) has no formula?
**A.** Bootstrap: resample B times (B ≥ 1000 for stable quantiles), recompute θ̂ each time, take percentiles — cost O(B·n) for an O(n) statistic; use BCa when the distribution is skewed (it corrects with jackknife influence). Alternatives: profile likelihood ratio intervals (invert χ²₁ tests, respect boundaries), or delta-method transforms for skewed positive parameters (log then exponentiate). Wald symmetric intervals are the last choice when nothing else is available.

### Q5. Your Wald interval under-covers in simulation (91% vs 95%). What do you check?
**A.** In order: (1) **bias** — Wald centers on θ̂; if E[θ̂] ≠ θ at this n, bias eats coverage; (2) **skewness** — sampling distribution skewness ≈ γ₁/√n, big at small n or for variance/rate parameters → use BCa or a transform; (3) **dependence** — SE assumed i.i.d.; compute n_eff or use sandwich/cluster-robust variance; (4) **misspecification** — data not from the assumed family (check QQ/residuals first). Each has a distinct fix: bias → better estimator, skew → BCa/transform, dependence → robust SE, misspec → model.

### Q6. Two estimators: A has bias 0.5 and variance 1; B has bias 0 and variance 3. Which do you report?
**A.** Neither answer without n and the loss function: MSE(A) = 0.25 + 1 = 1.25 < MSE(B) = 3 at every n here, so A wins on squared error — but if the report must be publishable-as-unbiased (some regulators/journals), the constraint forces B. The real interview point: MSE = bias² + variance is computed *at the n you'll run*, and bias may shrink with n while variance does too — state the n, compute both terms, then choose. If the bias doesn't vanish with n (squaring a noisy measurement: E[X²] = μ² + σ² forever), name it in the write-up or correct it.

### Q7. Your likelihood has no closed form and the data are dependent. What is your estimator and your SE?
**A.** Point estimate: maximize the composite/working likelihood anyway — QMLE is consistent if the mean structure is right (White 1982); for dependence use a GEE-style working correlation or fit a state-space model if the dependence is structured. SE: the sandwich I⁻¹·J·I⁻¹, with J from clustered or HAC-robust scores (Newey–West for serial dependence) — never the naive I⁻¹. Bootstrap alternative: block bootstrap (moving blocks of length L ≈ n^{1/3}), not the iid bootstrap, which would erase the dependence you're trying to keep in the resamples. Then say which of the three (cluster, HAC, block) and why — the choice is the answer.

### Q8. How would you decide whether your MLE's CI is trustworthy *before* publishing it?
**A.** Simulation-based calibration, cheap to run: draw R = 1000 datasets at the fitted θ̂ with your actual n, recompute the interval each time, count coverage — expect 95% ± 1.4pp (Monte Carlo error √(0.95·0.05/1000) = 0.69%, so ±1.4pp at 2SE). If coverage is 91%, inspect in order: bias at n (shifts the center), skewness (Wald's symmetry breaks), dependence (SE understated). The check costs minutes and converts "the theory says n is big enough" into evidence at *your* n, with *your* model.

### Q9. What is the practical difference between observed and expected information?
**A.** Observed = −∂²ℓ/∂θ² evaluated at θ̂: data-dependent, can be noisy or singular at small n, but is what a single fit gives you. Expected = −E[∂²ℓ/∂θ²] over the model: smooth, parameter-only, used in Fisher scoring (a stable Newton variant when the observed Hessian is indefinite). They coincide asymptotically (KL expansion: the difference is O(1/√n) in probability). Diagnostically: if observed and expected information differ a lot at your n, the likelihood is locally non-quadratic — meaning the quadratic (Wald) approximation driving your SE is shaky, and LR or bootstrap intervals are the safe report.

### Tips
- Quote one bound and one condition per answer (CRB + its regularity list; sandwich + when i.i.d. fails) — it shows you know where the formula stops being true.
- Have a small-n example ready: k = 6/n = 20 (Wald vs Wilson) or n = 10 (σ̂² bias) — concrete beats abstract.
- Say "asymptotically" before "efficient" every time; interviewers are listening for it.
