# Estimation Theory — Math Foundation

Every number is a run output (transcripts in CODE_DEEP_DIVE.md) or an
exact-arithmetic consequence of two such outputs. No hand-derived
figures.

## 1. Loss Chooses the Location — Three-Point Sample, Excavated
Sample x = (1, 2, 4). Observed: mean 7/3, median 2. On a grid of
steps 1/12, the squared-loss risk E-like average (Σ(x_i − a)^2)/3 was
minimized at a = 7/3 with minimum 14/9; the printed neighbors agree
precisely: risk at 9/4 equals 25/16 and at 29/12 equals 25/16. The
absolute-loss risk: 1 at the median 2, 10/9 at the mean 7/3 — the mean
pays 10% more under absolute loss, executed as a fraction.

## 2. The Squared-Loss Center Is the Mean — Verified Around the Min
The grid test surrounds the winner from both sides: a step below
(9/4) and a step above (29/12) share the identical risk 25/16, while
the argmin sits strictly lower at 14/9. As fractions:
deviations from 7/3 are −4/3, −1/3, 5/3, and
(Σ deviation^2)/3 = (16/9 + 1/9 + 25/9)/3 = 42/27 = 14/9 — the minimum
line decomposed term by term.

## 3. Bernoulli MLE and Its Exact Moments
Ten flips, seven heads: MLE p_hat = 7/10 (the run prints it as a
Fraction). At the truth p = 1/2: E[p_hat] = 1/2, so Bias = 0 — the run
verified the zero — and Var(p_hat) = pq/n = (1/4)/10 = 1/40 exactly,
so MSE = Var + 0^2 = 1/40 = 0.025. The decomposition of MSE is a
formula here: one member was computed, the other measured zero.

## 4. Uniform(0, θ) — The Biased MLE and Its Cure
True θ = 12; sample (3, 8, 9); MLE = max = 9. Theory: E[max of n] =
(n/(n+1))·θ — at n = 3: (3/4)·12 = 9, matching the run's expected-max
line exactly, so Bias = 9 − 12 = −3 (execute run printed: bias −3).
Scaling cure: (n+1)/n · max = (4/3)·9 = 12 = θ restores unbiasedness
(symbolically E[(4/3) max] = (4/3)(3/4)θ = θ). Seeded simulation over
200000 replications: observed E[max] = 8.997715881500072 against
theory 9 — agreement under 0.03% with the exact prediction.

## 5. Poisson Rate — The Mean Is the Answer
Data (1, 1, 3, 4, 1): sum 10 over five points; the run printed
sum/n = 2 and the derivative-of-log-likelihood confirms the mean as
the critical point: d/dλ [−nλ + (Σx) log λ] = −n + Σx/λ = 0 gives λ =
Σx/n = 10/5 = 2 exactly. The maximum: log-likelihood concavity in λ
(since (Σx) log λ is concave) makes the critical point the argmax,
no second-derivative theater needed.

## 6. Estimation Vocabulary From the Numbers
The three-point sample carries the whole menagerie: 7/3 (mean,
squared-loss choice), 2 (median, absolute-loss choice, max-MLE under
the uniform reading), 1/40 (exact MSE of a proportion estimate), −3
(bias of a max estimate), 0.03% (simulated-vs-exact agreement for the
scaled estimator at 200000 replications). Each figure traces to a
printed line.
