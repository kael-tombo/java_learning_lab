# Security: Combinatorics in Practice

## Counting Is What "Entropy" Means

A password space is a combinatorial object. A 6-digit PIN drawn from 10 digits with repetition allowed has 10⁶ = 1,000,000 possibilities — log₂(10⁶) ≈ 20 bits of entropy, which a rate-limited attacker exhausts trivially. A 12-character password from 94 printable ASCII with repetition allowed has 94¹² ≈ 4.75×10²³ combinations ≈ 78 bits — outside offline reach at current key-search rates but only if the attacker cannot reduce the space (e.g., by guessing "Spring2026!"). Security sizing is a counting exercise: **space size ÷ guesses per second = time**, and every rule (length over complexity, passphrases over PINs) follows from the arithmetic.

A permutation *without* repetition is the trap: a "10-character password with no repeated characters" drawn from 94 symbols has P(94, 10) = 94·93·…·85 ≈ 3.3×10¹⁹ options, while 94¹⁰ ≈ 5.4×10¹⁹ with repetition allowed. The constraint *shrinks* the space by ~40% — it never makes guessing harder. This is the general shape of the mistake: policies that demand "no repeats," "must contain a digit," or "must start with a letter" subtract possibilities while feeling like they add strength. Only length drawn from a large alphabet multiplies the space.

## Birthday Collisions: 2^(n/2), Not 2ⁿ

A hash with n-bit output has 2ⁿ possible values, so a naive guess needs ~2ⁿ tries. But finding *any two inputs with the same hash* needs only ~√(π·2ⁿ/2) ≈ 2^(n/2) trials — the birthday bound. For 64-bit hashes that is ~2³² ≈ 4.3×10⁹ evaluations: brute-force-resistant as a preimage problem, feasible as a collision search. This is why SHA-1's 160-bit output still needed collision defenses (SHAttered, 2017) far earlier than preimage attacks would suggest, and why security designs use ≥ 256-bit collision resistance for unkeyed hashing. The count, not the code, is the spec.

## Key Space Sizes Are Combinatorial Claims

- AES-128 key space: 2¹²⁸ keys; exhaustive search at 10⁹ keys/second takes ~1.09×10²² years (2¹²⁸ / 10⁹ ≈ 3.4×10²⁹ seconds).
- ECC over 256-bit curves: the best known attack (Pollard's rho) is O(√q) = 2¹²⁸ group operations — the group's structure *halves the exponent*, and only counting the group's order tells you that.
- A 56-bit DES key (2⁵⁶ ≈ 7.2×10¹⁶) was broken in 1999 by brute force; the difference between 56 and 128 bits is 10¹⁹×, i.e., the whole game is exponent arithmetic.

Any claim "this algorithm is secure" bottoms out in a counting claim: how many candidates must an adversary try, and how fast can they try them?

## Combinatorial Explosion as a Denial-of-Service Surface

Attackers weaponize your counting assumptions: requesting "all subsets of these 30 options" forces your server through 2³⁰ ≈ 10⁹ outputs; a batch API that generates all k-permutations of user-supplied tokens is O(P(n,k)) work attacker-chosen. Mitigations are combinatorial caps: hard limits on n and k, response-size budgets, streaming with backpressure, and rejecting queries whose *counted* output size (computed in O(1) or O(k) with the binomial formula) exceeds a threshold *before* any generation starts. Never start enumerating and hope the client disconnects.

## Rate Limiting and the Guessing Budget

Lockout policies are budgets over the password space: if a 6-digit PIN has 10⁶ entries and you allow 10⁵ attempts/day/account without lockout, the space is exhausted in 10 days. Counting also shows why per-account lockouts enable denial-of-service (locking a victim out is cheaper than guessing) — hence exponential backoff and CAPTCHA rather than hard locks.

## Probability of Detection

If an intrusion is detected per event with probability p and an attacker runs t trials, the chance of going undetected is (1−p)ᵗ → 0 exponentially. Choosing p and t is again pure counting: ln(undetected)/ln(1−p) ≈ −t for small p. A detection rate of 0.1% over 10,000 attempts leaves ≈ e⁻¹⁰ ≈ 4.5×10⁻⁵ chance of escaping notice.
