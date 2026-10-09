# How It Works: Estimation Theory

## 1. From likelihood to estimate
Write L(θ) = ∏ f(xᵢ; θ), maximize its log. For the normal, ∂ℓ/∂μ = Σ(xᵢ − μ)/σ² = 0 ⇒ μ̂ = x̄; for the exponential, ∂ℓ/∂λ = n/λ − Σxᵢ = 0 ⇒ λ̂ = n/Σxᵢ = 1/x̄. The score equation "balances the data against the model" — for exponential families the MLE is a function of the sufficient statistics, always.

## 2. Why x̄ is the good estimator
Three theorems, three certificates: (a) it is **unbiased** (E[x̄] = μ); (b) its variance σ²/n **attains the Cramér–Rao bound** I(μ) = n/σ², so no unbiased estimator does better; (c) by Lehmann–Scheffé, any unbiased estimator built from the sufficient statistic Σxᵢ (x̄ being one) is UMVU. Same conclusion, three of statistics' central results.

## 3. How the SE is read off the model
Observed information: for the normal, −∂²ℓ/∂μ² = n/σ², so Var(θ̂) ≈ 1/I = σ²/n and SE = σ/√n. In general: invert the p × p information matrix, take √(diagonal). The sandwich (White 1980) replaces I⁻¹ with I⁻¹·J·I⁻¹ when the model is misspecified — robust to dependence and misspecification at the price of needing more data.

## 4. Likelihood-ratio intervals without new data
The LR set {θ : 2(ℓ(θ̂) − ℓ(θ)) ≤ χ²₁,₀.₉₅} inverts the test (lab 07) — each endpoint is an optimization with θ *fixed* (profile the nuisance parameters). It respects asymmetry and parameter boundaries where Wald's symmetric ±z cannot (a variance interval that would go negative, a correlation pinned near 1).

## 5. The bootstrap: empirical sampling distribution
Resample the data with replacement B times, recompute θ̂ each time: those B values *are* an empirical sample from the estimator's distribution. Percentile quantiles give the CI directly; BCa adds bias and acceleration corrections via jackknife influence values. It needs no formula for Var(θ̂) — only compute — which is exactly why it was computationally impossible before Efron (1979) and modern machines.

## 6. Bias, variance and the decision-theoretic frame
Wald (1950): compare estimators by risk R(θ, δ) = E_θ[L(θ, δ)]. Squared-error risk decomposes to bias² + variance; admissibility asks whether any other estimator has lower risk *everywhere* (James–Stein, 1961: for p ≥ 3, the sample mean of a normal is *inadmissible* — shrinkage beats it uniformly). Estimation theory ends where Bayes decisions (lab 08) begin.

## 7. Wald versus Wilson at a small n — why they diverge

Binomial, k = 6 of n = 20: p̂ = 0.30, SE = √(0.3·0.7/20) = 0.1025, so Wald gives [0.099, 0.501]. Wilson re-centers and re-scales: (p̂ + z²/2n)/(1 + z²/n) ± (z/(1+z²/n))·√(p̂(1−p̂)/n + z²/4n²) = [0.145, 0.519]. Same data, same nominal 95%: Wald's lower endpoint lands at 0.099 because it uses p̂ inside the SE — plug a boundary-hugging p̂ and the SE shrinks with it (self-reinforcing narrowness). Wilson's coverage stays near 95% as p → 0; Wald's collapses. The mechanism is model 9: the two intervals invert *different* tests, and Wald's uses curvature evaluated at the possibly-misleading peak.

## 8. The delta method in one line

If g is smooth and θ̂ has variance σ²/n, then g(θ̂) ≈ N(g(θ), g′(θ)²σ²/n) — variance multiplied by the squared slope. Worked: the SE of a log-rate is g′ · SE = SE/θ̂ (relative error); for m = 4 Poisson counts in T = 1, λ̂ = 4 with SE = 2, so the log-rate SE = 2/4 = 0.5, giving a multiplicative 95% factor e^{±0.98} = [0.38, 2.66] — compare Wald's additive [0.08, 7.92], which includes impossible negative rates at the bottom... it doesn't here, but at m = 1 it does (1 − 1.96 < 0). This is why rates get log intervals and variances get log or profile intervals, never symmetric ±z.

## 9. The score equation is a balance, not a formula

∂ℓ/∂θ = 0 says "the data's surprise, summed over observations, is zero at θ̂." For the normal mean it reduces to Σ(xᵢ − μ) = 0 — the residuals balance — which is *why* x̄ is the MLE and not merely a convenient guess. Every closed-form MLE you will ever use is this balance written out: exponential (n/λ = Σxᵢ → λ̂ = 1/x̄), binomial (k/p = (n−k)/(1−p) → p̂ = k/n), Poisson (k/λ = n → λ̂ = k/n). If you cannot write the balance, you do not yet know why the estimator equals what it equals.
