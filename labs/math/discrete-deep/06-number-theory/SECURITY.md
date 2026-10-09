# Security: Number Theory in Practice

## RSA Key Generation, Start to Finish (Small Primes)

**Step 1 — Choose two primes.** p = 17, q = 23 (in production: two random primes of 1536+ bits each, found by random search + Miller–Rabin).

**Step 2 — Modulus.** n = p·q = 391. Public and private key material both live in Z/391Z.

**Step 3 — Euler totient.** φ(n) = (p−1)(q−1) = 16·22 = 352. *This is the number you can compute knowing p, q — and cannot compute (equivalently: cannot factor n) without them.* That asymmetry is the entire security assumption.

**Step 4 — Public exponent.** e = 3: need gcd(3, 352) = 1 (352 = 3·117 + 1 ✓). Production uses e = 65537 = 2¹⁶+1 for speed (17 squarings in modPow).

**Step 5 — Private exponent.** d ≡ e⁻¹ (mod 352) via extended Euclid: 352 = 117·3 + 1 → 1 = 352 − 117·3 → **d = −117 ≡ 235 (mod 352)**. Check: 3·235 = 705 = 2·352 + 1 ✓.

**Public key (n, e) = (391, 3); private key (n, d) = (391, 235).**

**Step 6 — Encrypt** m = 50 (require m < n): c = m^e mod n = 50³ mod 391 = 125,000 mod 391. 391·319 = 124,729 → **c = 271**.

**Step 7 — Decrypt** m = c^d mod n = 271^235 mod 391. Why this returns 50: ed = 705 = 2·352 + 1 = 2φ(n) + 1, so for gcd(m, n) = 1, c^d = m^(ed) = m^(2φ+1) = m·(m^φ)² ≡ m·1² = m (mod 391) by Euler's theorem. (With gcd(m, n) ≠ 1 — e.g., m = 17 sharing a factor with 391 — Euler doesn't apply, but Fermat's little theorem on the shared prime p or q still forces m^(ed) ≡ m mod p and mod q, hence mod n by CRT. Verify: 17³ = 4913 = 12·391 + 221 → ciphertext 221.)

**Why decryption with the private key works and a naive modular division doesn't:** there is no way to "take the e-th root mod n" — 271^(1/3) is meaningless in Z/391Z. The inverse exponent d *exists as a thing* precisely because the group of units has order φ(n) known to the keyholder.

## Why Primality Testing Is a Security Requirement

- If p or q is **composite**, φ(n) ≠ (p−1)(q−1), so the computed d does not satisfy e·d ≡ 1 (mod φ(n)) — **decryption fails or is inconsistent**, and worse, n may have small factors that make factoring trivial (Pollard rho finds a 40-bit factor of n in milliseconds).
- **False primality = weakened key.** A compositeness-prone test (plain Fermat) can be fooled by Carmichael numbers (561, 1729…), so generators use Miller–Rabin with ≥ 40 rounds: error ≤ 4^(−40) ≈ 2^(−80) — the parameter choice, not the algorithm, sets the security level.
- **Key size follows factoring cost.** GNFS on a d-bit n: sub-exponential in d, so 1024-bit factoring is within reach of nation-states (motivating deprecation), 2048-bit remains the baseline, 3072-bit for long-term. The count (how many operations to factor) *is* the policy.
- **Prime generation must be random.** Primes are dense enough (1/ln n of numbers near n are prime: at 1024 bits, ~1/710 candidates pass) that searching random odd candidates + Miller–Rabin works in milliseconds — but a *predictable* RNG producing p and q collapses the scheme regardless of modulus size (the Dual_EC_DRBG backdoor class of failures).

## Where Else Number Theory Carries Security

- **Diffie–Hellman**: shares g^a mod p; security = discrete log in a prime-order subgroup — same "easy forward, hard backward exponent" structure as RSA, but for a *different* hard problem (so a break of factoring doesn't break DH).
- **Elliptic curves (ECDSA, X25519)**: the group is points on a curve instead of residues; 256-bit curve order gives ~128-bit security because the best attack (Pollard rho) is O(√q) — the sqrt-halves-the-exponent counting from lab 03 again.
- **Ed25519 / deterministic nonces**: a reused or biased nonce k leaks d from two signatures (k = (z₁ − z₂)/(s₁ − s₂) style algebra) — a single modular-arithmetic slip in nonce generation is a full private-key disclosure.
- **Checksums ≠ integrity**: mod-based checksums (Luhn, CRC) are linear/algebraic and forgeable by design — authentication needs HMAC or signatures, i.e., *hard* one-way number-theoretic functions, not easy modular ones.

## Practical Checklist

- Generate p, q randomly; test with Miller–Rabin (k ≥ 40); reject if p ≈ q or p−1/q−1 have small factors (Pollard p−1 smoothness).
- Use e = 65537; pad messages (OAEP) — raw RSA (textbook m^e) is malleable: Enc(m₁·m₂) = Enc(m₁)·Enc(m₂), so deterministic unpadded RSA leaks multiplicative relations.
- Enforce m < n (otherwise ciphertext wraps and leaks), and always reduce into [0, n) (the negative-remainder bug in COMMON_MISTAKES is an oracle when it changes error behavior).
