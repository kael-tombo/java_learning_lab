# Security: Probability Axioms Implementation

## Base rates decide whether alerts mean anything
An intrusion detector with 99% true-positive rate and 1% false-positive rate watching traffic where 0.01% of flows are attacks:

- P(real) = 0.99 × 0.0001 = 0.000099
- P(false alarm) = 0.01 × 0.9999 = 0.009999
- P(real | alarm) = 0.000099 / 0.010098 ≈ 0.0098 → under **1%**

Over 99% of alarms are noise. A SOC that reviews alarms without the prior wastes that ratio; the axioms say the posterior is prior odds times likelihood ratio, always.

## Guessing is a probability budget
- A 128-bit key: P(successful guess) = 2⁻¹²⁸ ≈ 2.94 × 10⁻³⁹ per attempt.
- Password space 36⁸ = 2 821 109 907 456 ≈ 2.82 × 10¹² combinations; at 10⁹ guesses/second (a GPU rig against a fast hash) the whole space averages ~2821 s ≈ 47 minutes.
- A 4-digit PIN (10⁴) falls in 10 µs at that rate — which is why rate limiting changes the sample space, not just the arithmetic.

Doubling key length squares the guessing probability; salted slow hashes (bcrypt, Argon2) shrink the attacker's trials-per-second instead. Both are moves on the same P(success) budget.

## Spam filtering: Naive Bayes
Paul Graham's *A Plan for Spam* (2002) scores a message by the product of per-word likelihood ratios under a naive-Bayes model — an explicit (mis)use of P(A ∩ B) = P(A)P(B). It violates conditional independence in practice yet works because the score only needs correct *ranking*, not calibrated probabilities.

## Risk = probability × impact
Expected annual loss = P(breach) × loss. When P is only bounded (Chebyshev: P(|X − μ| ≥ kσ) ≤ 1/k²), report the bound, not a point estimate. Claiming "1 in a million" without a model of the measure is exactly the error the axioms forbid.

## Review checklist
- [ ] Is the prior stated explicitly, or is only the likelihood quoted?
- [ ] Does any code path treat "rare" as "impossible" (P = 0)?
- [ ] Are token/session probabilities derived from a CSPRNG, not a uniform assumption over time?

## Two rules that follow from the axioms

- Every risk number ships with its prior. "P(breach)" without a base rate is an opinion; the alarm math above shows why — under 1% of alarms are real at 0.01% prevalence even with a strong detector.
- Every threshold is a quantile of a stated distribution, *including the adversary's*: rate limits, lockout counts and anomaly cutoffs are tail probabilities that someone chose, and an attacker who knows the choice paces under it.
