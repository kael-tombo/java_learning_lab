# Security: Random Variables Implementation

## A PRNG is a random variable, and its distribution is the contract
`java.util.Random` is a 48-bit LCG: output must be uniform on [0, 2³²), but the *next* value is a deterministic affine function of the last. An attacker who sees 2 or 3 outputs recovers the internal state (Zi+1 = (a·zi + c) mod 2⁴⁸) and predicts every future token. Session IDs, password-reset links and CSRF tokens must come from `SecureRandom` (SHA1PRNG/DRBG), where each output is modeled as an independent uniform draw.

## Entropy is an expectation over the key space
For a secret X with distribution p, Shannon entropy H(X) = −Σ pₓ log₂ pₓ bits bounds the average number of guesses:
- Fair 128-bit key: H = 128 bits, uniform — expected 2¹²⁷ guesses.
- 8-char password drawn uniformly from [a–z0–9]: log₂(36⁸) = 8·log₂36 ≈ 41.4 bits.
- Real passwords are *not* uniform (the "123456" atom), so H ≪ log₂|space| — measured entropies of common password distributions are a fraction of the nominal bits. Security budgets must use H of the actual distribution, not log of the alphabet size.

## Frequency tests catch a broken random variable
A CSPRNG failing to be uniform shows up immediately: χ² goodness-of-fit over 256 byte values with n = 2⁵⁶ samples should have χ² ≈ 255 ± √(2·255) ≈ 255 ± 22.6 (1σ). NIST SP 800-22 runs exactly these tests; a drifted mean or an over-represented byte is a distribution bug, not a rounding one.

## Timing side channels are distribution leaks
Kocher's (1996) attack on RSA compares the *distribution* of multiplication times for correct vs. incorrect key bytes: each extra byte separates the means by microseconds. Constant-time code exists to make the two distributions identical — variable-time early-exit comparisons (e.g. `MessageDigest.isEqual` vs `==` on strings) reintroduce a distinguishable shift.

## What to review
- [ ] Which RNG produces the token, and is its output modeled as i.i.d. uniform?
- [ ] Is the secret's entropy computed from its real distribution (H) rather than its size?
- [ ] Do any branches depend on secret values, making two outcomes distinguishable by timing?

## Where randomness meets trust

**Seed reuse is a security bug, not a style issue.** Predictable PRNG output has broken real systems: the 2008 Debian OpenSSL disaster (a single seeded value made SSH host keys and session keys predictable), and duplicated PlayStation 3 ECDSA nonces (2010) which leaked private keys. In simulation work the analogous failure is subtler: reusing a seed across "independent" experimental arms makes arms perfectly correlated, invalidating every comparison p-value.

**Sampling bias is an integrity failure.** If the mechanism that *collects* data over-represents some values, the fitted distribution is wrong no matter how large n is. Examples with audit value:
- Web surveys sampled from a panel self-selected into the panel.
- Clinical data from a single hospital, presented as population data.
- Sensor data with clipping: values above the range recorded as the range, fattening or truncating the tail.

**Reporting obligations for a distribution claim:**
1. State the generator and seed (or the sampling frame for real data).
2. State n and the number of independent replications.
3. Report the estimated parameters *with* the standard errors or intervals — a point estimate alone hides the uncertainty an attacker or an auditor needs.
4. If the analysis feeds a decision (credit, triage, pricing), report the error rates on the subgroup level, not only overall.

**Anonymization note:** releasing individual draws from a fitted distribution does not anonymize anything. Re-identification risk depends on the joint distribution of quasi-identifiers, not on the marginal you modeled.
