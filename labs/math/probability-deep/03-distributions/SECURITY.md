# Security: Probability Distributions

## Attack arrivals are Poisson — until they aren't
The classic intrusion model is a homogeneous Poisson process: λ attempts/hour ⇒ P(N = k in an hour) = e^{−λ}λᵏ/k!, independent increments, exponential inter-arrival times (memoryless). With λ = 0.1/hour: P(N ≥ 3) = 1 − e^{−0.1}(1 + 0.1 + 0.005) = 1 − 0.999845 = 0.000155 — about 1 chance in 6 400 hours under background noise.

**Why the model matters:** automated credential-stuffing is *not* Poisson — it is bursty and adaptive. Rate limiters sized on Poisson tail probabilities (fail2ban thresholds of 5 tries/60s) work precisely because the attacker's distribution *differs* from the background's; an attacker who paces at the background rate's quantiles evades distribution-based detection entirely.

## Password entropy follows known distributions
A 4-digit PIN is Uniform over 10⁴ = 10 000 values: expected guesses 5 000 at uniform sampling. Real passwords are Zipf-like (a few strings carry most of the mass), so guessing order by frequency table (rockyou) reaches a given success probability in orders of magnitude fewer tries than uniform — same nominal space, radically different distribution.

## File and payload sizes: lognormal, not normal
Executable and request payload sizes fit lognormal/Pareto far better than Gaussians (all positive, heavy right tail). A WAF threshold set at mean + 3σ of a lognormal fit *understates* the tail: for lognormal(μ, σ = 1.5), P(X > e^{μ+3σ}) is dominated by the exponential tail, and the "3σ" intuition (0.13% for a normal) badly undercounts. Size-based blocking rules must be quantiles of the fitted family.

## Exponential distribution = constant hazard in retries
Retry/backoff times modeled as Exp(λ) imply the security-relevant property that a long-silent attacker is not more trustworthy. Exponential backoff with jitter is modeled as exponential precisely because a fixed-interval retry pattern is a *deterministic* distribution an adversary can synchronize with; jitter keeps the aggregate distribution near exponential while destroying the timing signal.

## What to check
- [ ] Is the assumed family justified by a goodness-of-fit test on observed data (χ² / KS), not by habit?
- [ ] Are threshold decisions made at *quantiles of the fitted tail*, not at mean + kσ for a skewed family?
- [ ] For detection: which distribution does the attacker's traffic need to resemble to blend in?

## Where distributions carry risk

**Pseudorandomness is not randomness.** Simulation seeds feed PRNGs (PCG64, Mersenne Twister). If an adversary can learn the seed or the first outputs, they can predict every future "random" draw: this is how MT19937-untwisting attacks reconstruct internal state from 624 outputs, and why `random.random()` must never be used for session tokens. Simulation code and key-generation code must use different generators and different sources of entropy.

**Model choice affects who is misclassified.** A normal assumption for a heavy-tailed cost distribution underestimates extreme claims; an exponential assumption for service times hides the tail that dominates customer experience. The harm lands on whichever group occupies the tail — report which family you fit and what its 99th percentile implies, not just the mean.

**Count-data disclosure.** Publishing Poisson rates for small subpopulations (a clinic's rare-diagnosis counts by zip code) can re-identify individuals. Aggregate cells with expected counts below ~5–10 before release (the same threshold that χ² testing uses, for a different reason).

**Audit questions:** Which family, fitted how (MLE or Bayesian), with what goodness-of-fit evidence? Does the fitted 99.9th percentile drive any safety or financial decision? Was the PRNG seed logged and reproducible, and is it from a CSPRNG where the output is externally visible?
