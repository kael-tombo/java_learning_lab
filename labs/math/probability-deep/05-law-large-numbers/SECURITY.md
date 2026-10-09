# Security: Law of Large Numbers and CLT

## Rate limiting is an LLN statement
A rate limiter asserting "≤ 5 login attempts/minute per account" assumes the background rate concentrates. Background users follow Poisson with λ ≈ 0.5/min: P(N ≤ 4) = 0.606531 + 0.303265 + 0.075816 + 0.012636 + 0.001580 = 0.999828, so P(N ≥ 5) = **0.000172** — about 1 in 5 800 account-minutes of false lockout. The false-positive rate follows the *tail* of the background distribution, not its mean, so the threshold must come from the Poisson quantile of λ rather than from "average users try twice."

The CLT also says: requests averaged over 60 s concentrate at σ/√60 — an attacker pacing *below* the moving average is invisible to mean-based detectors, which is why burst/peak detectors complement LLN-based ones.

## Monte Carlo is how rare attack probabilities get estimated
Probability a 64-bit random nonce collides after m draws: birthday bound ≈ m²/2⁶⁵. Estimating such tiny probabilities by direct simulation is impossible (would need ~10¹⁹ trials for even a handful of hits), while the analytic result is immediate. Use LLN-style simulation only for events with p ≳ 10⁻⁴ (10⁴–10⁶ trials), and analytic bounds (union bound, birthday) below that.

## Averaging hides tails — the failure that costs money
VaR and "95% uptime" are quantiles, and averaging (the LLN's currency) is blind to them: 10⁴ requests with mean latency 100 ms can still contain 50 requests at 8 s. Security-relevant service guarantees (timeouts, credential-attempt budgets) must be checked on the *tail* — the CLT describes the mean, not the maximum; extremes follow extreme-value laws (lab 03).

## Entropy estimation converges, slowly
Estimating H from n samples has error ~ O(|alphabet|/n) plug-in bias (Miller–Madow: bias ≈ (m−1)/(2n) nats for m symbols). For a 26-symbol alphabet and n = 1000, bias ≈ 25/2000 = 0.0125 nats ≈ 0.018 bits — small; for n = 100 it is 0.125 nats ≈ 0.18 bits, i.e. you can *overestimate* a password scheme's entropy by a fifth. Convergence in probability does not mean "accurate at small n."

## Review checklist
- [ ] Was the threshold derived from the tail quantile of the measured distribution, or from its mean?
- [ ] Are the data independent enough for σ²/√n, or does autocorrelation shrink n_eff?
- [ ] Is the event's probability estimable by simulation (p ≳ 10⁻⁴), or does it need an analytic bound?

## Timing side channels are a CLT experiment an attacker runs for free

A leak of δ = 1 µs per request against background noise σ = 10 µs becomes detectable in n ≥ (1.96σ/δ)² = **385** requests — well inside any rate limit. That arithmetic is the whole threat model: defences that "average out" noise (constant-time *look* implementations, random delays) fail because the attacker controls n, and 1/√n convergence works against you. Countermeasures are structural — constant-time comparison, no data-dependent branches — not "add jitter and re-measure."

## Baseline monitors inherit the LLN's slow start

A WAF learning normal traffic from n = 100 minutes of Poisson(60)/min counts has SE = √60/10 = 0.775, so its 95% band is ±1.52 counts (±2.53% of λ). Four times as much history (n = 400) only halves it to ±0.76 (±1.27%). Two operational consequences: (1) a fresh deployment's threshold is wide — attacks sized below it are invisible for the whole warm-up; (2) raising precision means hours, not minutes, of clean history — plan the warm-up window explicitly instead of shipping a monitor whose baseline is 100 noisy samples.

## Review checklist

- [ ] Which statistics are averaged before a decision, and what is each one's n_eff (dependence) and bias floor (model)?
- [ ] For learned baselines: how many observations before the band is narrow enough to catch the threat you care about?
- [ ] For any published rate (false-positive %): is it measured on held-out replications with a stated Monte Carlo error, or asserted from theory?
