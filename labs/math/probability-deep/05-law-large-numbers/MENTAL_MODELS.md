# Mental Models: Law of Large Numbers and CLT

## 1. Two Different Random Variables
X̄ₙ is not "the data" — it is a *new* random variable with its own distribution, centered at μ and squeezed by √n. The LLN says its center is honest; the CLT says its shape is Gaussian. Almost every misunderstanding of the LLN comes from conflating X̄ₙ with Xₙ.

## 2. The √n Ruler
Information accumulates as √n: error bars shrink by 1/√n, so ten times the data buys 3.16× the precision. This is why pollsters need ~1000 for ±3%, and why going from ±3% to ±1% costs 9× more respondents, not 3×.

## 3. Averages are Lossy Filters
The sum X₁ + … + X_n forgets arrangement — 600 heads then 600 tails has the same mean as alternating. The LLN operates on that lossy summary, which is why it cannot and does not constrain runs, streaks or the next flip.

## 4. CLT as Standardized Centering
(X̄ − μ)/(σ/√n) = "how many SEs is my average from the truth?" — that quantity goes to N(0,1) regardless of the original shape (uniform, exponential, bimodal). One reference curve then answers every confidence-interval question, provided the summands are independent and no single term dominates.

## 5. Stable Laws Are the Real Limit Theory
Lévy (1925): sums of i.i.d. variables converge (after affine normalization) only to stable laws. The Gaussian (α = 2) exists *because* variance is finite; with α < 2 variance is infinite and the sample mean's spread shrinks only as n^{1/α − 1} — for α = 1.2 that is n^{−0.167}, so 100× more data divides the spread by just 2.15 instead of the Gaussian's 10. Averaging is then a bad estimator: trimmed means or the median take over, and extreme values, not means, carry the information.

## 6. Dependence Compresses Your Data
n measurements with lag-k correlation ρₖ contain about n/(1 + 2Σρₖ) independent ones. An AR(1) series with ρ = 0.9 has n_eff ≈ n/19 — 19 correlated readings buy you one. Every apparent "more data ⇒ tighter" claim must be discounted by this factor.

## 7. Convergence Modes Are Nested Promises

Almost sure ⇒ in probability ⇒ in distribution, and no arrow reverses. Each mode is weaker but cheaper: the SLLN (a.s.) needs E|X| < ∞ and speaks about the whole infinite sequence — one event with probability 1; the WLLN (in probability) only says P(|X̄ₙ − μ| > ε) → 0, holding at each n; convergence in distribution constrains only the shape of X̄ₙ's law and says nothing about where it centers. When someone says "the mean converges," ask which arrow they mean — planning a stopping rule needs the weak form, justifying a long-run frequency needs the strong one.

## 8. The Error Budget: Only the Random Half Shrinks

Total error = systematic (bias, discretization, wrong model) + random (≈ 1.96·σ/√n). The LLN/CLT govern *only* the second term. Averaging a biased estimator 10⁶ times gives a razor-thin interval around the wrong value — the simulation equivalent of measuring the wrong quantity precisely. Budget rule: before buying n, ask what the bias floor is; if bias > your target error, no amount of n reaches it, and the fix is in the model (better integrator, de-biased estimator, finer mesh), not the sample size.

## 9. Effective Sample Size Is Data's Freedom, Not Its Count

n_eff = n/(1 + 2Σρₖ) rephrases the data's usable content in units of independent observations. ρ > 0 (clustering, caching, MCMC) makes 19 correlated readings worth 1; ρ < 0 (antithetic variates, systematic sampling) makes n_eff *exceed* n — variance reduction by construction, not magic. Every precision claim should be quoted as "n = 3000 (n_eff ≈ 162)": the parenthesized number is the one the error bar came from.
