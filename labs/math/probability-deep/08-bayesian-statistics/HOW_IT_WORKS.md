# How It Works: Bayesian Statistics

## 1. The rule, mechanically
posterior ∝ likelihood × prior. Concretely for the coin: prior Beta(2,2) has kernel θ¹(1−θ)¹; data (9,1) contributes θ⁹(1−θ)¹; multiply → θ¹⁰(1−θ)² → normalize → Beta(11,3). The "normalization" step is where the marginal likelihood P(D) = 1/B(2,2)·B(11,3)·[...] hides; you may drop it for *sampling* (shape is enough) but not for model comparison.

## 2. Why conjugacy makes updating arithmetic
The Beta family is closed under the binomial likelihood because the likelihood's kernel (θ^k(1−θ)^{n−k}) lives in the *same exponential family* as the prior (θ^{α−1}(1−θ)^{β−1}); multiplying just adds exponents. Sufficient statistics (k, n−k) carry all the likelihood's content, so each new observation is a counter increment — which is why a conjugate posterior update is O(1) and a conjugate prior predictive is exact.

## 3. Posterior as prior-weighted average
Beta–Binomial mean: (α + k)/(α + β + n) = [α/(α+β)]·[w] + [k/n]·[1 − w] with w = (α+β)/(α+β+n). Prior strength *is* the weight. This identity is the practical sensitivity analysis: report n and α+β side by side and any reader can see who is winning.

## 4. When conjugacy fails: integrate or sample
General θ: compute ∫L(θ)π(θ)dθ on a grid (1-D, fast), or draw from the posterior with MCMC. Random-walk Metropolis: propose θ′, accept with probability min(1, posterior(θ′)/posterior(θ)). The chain's stationary distribution *is* the posterior — because the acceptance rule enforces detailed balance — so the histogram of accepted states is the answer. HMC replaces the random walk with physics (gradient-driven trajectories), exploring high-dimensional posteriors with far lower autocorrelation.

## 5. Model comparison without p-values
BF₁₀ = P(D | M₁)/P(D | M₀) — evidence ratio, integrated over each model's prior. Posterior model odds = prior odds × BF. Unlike a p-value, it can favor H₀ (Jeffreys–Lindley: with a very diffuse prior on θ, the evidence is diluted across implausible values, penalizing the flexible model automatically — Bayesian Occam's razor).

## 6. Prediction
Posterior predictive: P(x̃ | D) = ∫ P(x̃ | θ) π(θ | D) dθ — sample θ from the posterior, simulate x̃. For the coin: after 9H/1T with Beta(11,3), next-flip probability is the posterior *mean* 11/14 = 0.786 (averaging over uncertainty), not the MLE 0.9 — the difference is exactly what "full uncertainty propagated" buys.

## 7. Worked: normal-normal, numbers attached

Prior μ ~ N(100, 10²); data n = 25 measurements, x̄ = 105, known σ = 10. Precisions add: 1/100 + 25/100 = 0.26, so posterior σ = 1/√0.26 = 1.96 — the data are 25× as precise as the prior, cutting uncertainty from 10 to under 2. Posterior mean = (100/100 + 105 × 0.25)/0.26 = 104.81: a precision-weighted average (prior weight 0.01, data weight 0.25) sitting 96% of the way from prior mean to data mean.

## 8. Worked: the prior predictive, before any data

Draw θ ~ Beta(2,2), then k | θ ~ Binomial(10, θ). P(k = 10) = ∫θ¹⁰·6θ(1−θ)dθ = 6·B(12,3) = 1/182 = 0.55% — ten straight heads is surprising but permitted under this prior. If your real data are 10/10 and that number feels wrong, you have just located the prior-sensitivity conversation you owe your readers, and it is cheaper to have it now than after the posterior is on a slide.

## 9. Thompson sampling in one paragraph

Keep a posterior per arm; each round draw θ̃_b from every arm's posterior and play argmax_b θ̃_b. The draw comes from the posterior, so arm b is played with probability exactly P(b is optimal | data) — exploration and exploitation are the same act. As one arm's probability of optimality collapses its pulls collapse with it, which is why this 1933 idea (Thompson, *Biometrika* 25) is the update loop running in ad ranking and adaptive trial allocation today.

## 10. The one-loop summary

prior → likelihood × prior → normalize (or sample) → diagnose (R̂, ESS) → summarize (interval, P(θ > c)) → predict (posterior predictive) → criticize (does the predictive cover the data?). The order is load-bearing: no summary from an undiagnosed chain, no decision from an unchecked model — each step can invalidate the next, and skipping one only moves the failure downstream.
