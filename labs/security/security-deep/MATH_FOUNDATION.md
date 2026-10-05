# Math Foundation: security-deep

## Number Theory for Cryptography

### Prime Numbers

Prime numbers are the foundation of RSA and Diffie-Hellman. A prime p has exactly two divisors: 1 and p.

**Key properties:**
- **Fundamental Theorem of Arithmetic**: Every integer > 1 is either prime or a unique product of primes.
- **Prime Number Theorem**: The number of primes less than n is approximately n / ln(n).
- **Primality Testing**: Miller-Rabin test gives probabilistic primality with error probability 4^(-k) for k rounds.

### Modular Arithmetic

All of RSA, DH, and ECC operate in modular arithmetic.

**Definitions:**
- **Congruence**: a ≡ b (mod n) means n divides (a - b)
- **Modular inverse**: a^(-1) (mod n) exists iff gcd(a, n) = 1
- **Euler's totient**: φ(n) = number of integers in [1, n] coprime to n

**Euler's Theorem:** If gcd(a, n) = 1, then a^φ(n) ≡ 1 (mod n)

**Fermat's Little Theorem:** If p is prime and gcd(a, p) = 1, then a^(p-1) ≡ 1 (mod p)

### RSA Mathematics

**Key Generation:**
1. Choose two large primes p, q
2. Compute n = p × q
3. Compute φ(n) = (p-1)(q-1)
4. Choose e such that 1 < e < φ(n) and gcd(e, φ(n)) = 1 (typically e = 65537)
5. Compute d = e^(-1) mod φ(n)

**Encryption:** c = m^e mod n
**Decryption:** m = c^d mod n

**Correctness proof:** c^d = (m^e)^d = m^(ed) = m^(1 + k·φ(n)) ≡ m · (m^φ(n))^k ≡ m · 1^k ≡ m (mod n)

### Diffie-Hellman Mathematics

**Discrete Logarithm Problem (DLP):** Given g, p, and g^x mod p, finding x is computationally hard.

**Protocol:**
1. Agree on prime p and generator g
2. Alice chooses secret a, sends A = g^a mod p
3. Bob chooses secret b, sends B = g^b mod p
4. Shared secret: s = B^a = A^b = g^(ab) mod p

**Security:** An eavesdropper sees g, p, A, B but cannot compute g^(ab) without solving DLP.

### Elliptic Curve Mathematics

**Curve equation:** y² = x³ + ax + b (over a finite field F_p)

**Point addition:** Given points P and Q on the curve, P + Q is defined geometrically:
- Draw line through P and Q
- Find third intersection with curve
- Reflect over x-axis

**Scalar multiplication:** kP = P + P + ... + P (k times) — this is the basis of ECC security.

**ECDLP:** Given P and Q = kP, finding k is computationally hard.

**Key advantage:** 256-bit ECC provides ~128-bit security, equivalent to 3072-bit RSA.

### Information Theory Basics

**Entropy:** H(X) = -Σ p(x) log₂ p(x) — measures uncertainty in a random variable.

**Password entropy:** A password with 8 characters from 94 printable ASCII has log₂(94⁸) ≈ 52.4 bits of entropy.

**Key strength:** AES-256 has 2^256 possible keys — brute force is infeasible (would require more energy than exists in the observable universe).

### Probability in Security

**Birthday paradox:** In a group of 23 people, there's a >50% chance two share a birthday. This applies to hash collisions: a 256-bit hash has a 50% collision probability after ~2^128 hashes.

**False positive rate:** If a scanner has 1% false positive rate and scans 10,000 items, expect ~100 false positives.

**Bayesian detection:** P(Attack|Alert) = P(Alert|Attack) × P(Attack) / P(Alert) — base rate matters enormously.

### Complexity Theory

**P vs NP:** Problems solvable in polynomial time (P) vs problems verifiable in polynomial time (NP). Most cryptographic security relies on problems believed to be outside P.

**NP-Complete:** The hardest problems in NP — if any NP-complete problem is in P, then P = NP.

**One-way functions:** Easy to compute, hard to invert — the foundation of all modern cryptography.

### Statistical Analysis in Security

**Anomaly detection:** Establish baseline behavior (mean μ, standard deviation σ); flag events beyond μ ± 3σ.

**Bayesian networks:** Model probabilistic relationships between security events for threat scoring.

**Log-likelihood:** Used in SIEM correlation rules to rank alerts by probability of being a true positive.
