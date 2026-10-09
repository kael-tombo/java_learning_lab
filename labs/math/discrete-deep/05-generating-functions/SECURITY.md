# Security: Generating Functions in Practice

## Finite Fields Are Not Generating Functions (But They Share the Acronym)

The most important security note in this lab: **GF(2¹²⁸) and GF(2⁸) in cryptography are Galois fields**, not generating functions. AES works in GF(2⁸) = polynomials mod the irreducible x⁸ + x⁴ + x³ + x + 1 (0x11B): each byte is a polynomial, multiplication is polynomial multiply reduced mod that irreducible — giving a field where every nonzero byte has a multiplicative inverse (the basis of AES's MixColumns and S-box inversion). Confusing the two "GF"s is a documentation failure, not a math one, but it hides where the real connection lives: **polynomial algebra over finite fields is where stream ciphers and error detection actually run.**

## Linear Recurrences = Rational GFs = Stream-Cipher Structure

A sequence has a rational generating function iff it satisfies a constant-coefficient linear recurrence — the same object as a **linear feedback shift register (LFSR)**: the recurrence aₙ = q₁aₙ₋₁ + … + qₖaₙ₋ₖ is exactly a k-bit shift register with feedback taps. Two consequences:

- **Berlekamp–Massey** recovers the shortest recurrence (the denominator Q, degree = linear complexity L) from 2L output bits. If a stream cipher's keystream has linear complexity 64, an attacker reconstructs Q from 128 bits and predicts the rest — the keystream dies.
- Security requirement: keystream linear complexity must be large (near the period) and the recurrence must not be *the* structure — hence nonlinear combination/ciphering of LFSR outputs (A5/1, Trivium) rather than one raw LFSR.

## CRCs and Message Authentication: Polynomial Divisions

CRC-k detects any burst error of length ≤ k because the received word's polynomial must be divisible by the generator g(x) — an undetected burst error corresponds to a nonzero e(x) with g(x) | e(x), impossible for deg e < k. Security caveat that follows from the algebra: CRC is *not* a MAC. Since GF(2)[x] arithmetic is linear, an attacker who knows two message/CRC pairs can forge CRC(m ⊕ m′) = CRC(m) ⊕ CRC(m′) — linearity, the property that makes CRC cheap, makes it forgeable. Hence HMAC/GCM tags instead of CRC for integrity against an adversary.

## GHASH: Multiplication in GF(2¹²⁸)

AES-GCM authenticates with GHASH: tag = Σ mᵢ·Hⁱ computed in GF(2¹²⁸) with reduction mod the fixed polynomial x¹²⁸ + x⁷ + x² + x + 1. The known attack surface (forbidden-nonce reuse) is not a GF mistake but a *usage* one: with a repeated nonce the attacker solves for the secret H from one valid tag and forges any message — the field arithmetic is fine; the counting of (nonce, key) pairs was wrong. Design rule: the number of encryptions under one key must stay far below the birthday bound 2^(n/2) for the tag size (≈ 2³² for 96-bit tags in the original analysis), which is the same counting argument as lab 03's collision bounds.

## Counting Attack Spaces With Ordinary GFs

Password policies are counted by coefficient extraction: the number of passwords of length n over an alphabet with subsets is [xⁿ] Π 1/(1 − x^{|Sᵢ|})-style products; restricted compositions (at least one digit, at most two symbols repeated) come from the same products with factors like (x + x² + x³ + …). Passing the count to an entropy estimate (log₂ of the number of words in a passphrase dictionary of size D with w words: w·log₂ D) is the security-relevant use of enumeration — series arithmetic is how you get the count *with* constraints attached.

## Symbolic Protocol Verification Counts Message Sequences

Modeling a protocol's message grammar as a language (built from products = sequences, unions = alternatives, star = repetition) gives its generating function; the coefficient of xⁿ counts distinct transcripts of length n. Dolev–Yao style verifiers explore that space up to a bound — the GF makes explicit why the bound matters: transcripts grow exponentially (a branching factor b gives bⁿ), so exhaustive verification is capped at small n, and any claim "verified up to 10 messages" is a statement about that cutoff, not about all executions.

## Practical Checklist

- Distinguish Galois-field ops (crypto primitives) from GF-series ops (enumeration) in code names: `galois256` vs `ogfCoefficients`.
- Never reuse a stream cipher key/nonce pair — check the usage count against 2^(n/2), not 2ⁿ.
- Never use CRC as an adversarial integrity check; linearity = forgeability.
- Size any enumeration-based security claim (password space, transcript count) by *counting first* (coefficient extraction) before running anything.
