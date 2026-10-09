# Common Mistakes: Number Theory

## 1. Treating the Modular Inverse Like Division

**2⁻¹ mod 7** is the integer x with 2x ≡ 1 (mod 7) — namely **4**, because 2·4 = 8 ≡ 1. It is *not* 0.5, not 1/2, and not "half." There is no such thing as 2⁻¹ mod 6: gcd(2, 6) = 2 ≠ 1, so no inverse exists. The rule: **a⁻¹ mod m exists iff gcd(a, m) = 1**, and it is computed by the extended Euclidean algorithm (or Fermat's little theorem when m is prime: a⁻¹ ≡ a^(m−2) mod m).

## 2. Java's `%` Is a Remainder, Not a Math Modulo

`-1 % 7` in Java is **−1**, not 6. Positive results require normalization: `((a % m) + m) % m`. Symptoms: a "mod 7" value that goes negative and corrupts a hash/index/array lookup (ArrayIndexOutOfBounds) whenever a subtraction in the loop makes the running total negative — which happens the moment you compute (a − b) mod m without adding m back.

## 3. Applying Fermat/Euler Without the Coprimality Check

- **Fermat:** a^(p−1) ≡ 1 (mod p) only when p is prime **and** gcd(a, p) = 1. The always-true form is a^p ≡ a (mod p) for prime p (any a).
- **Euler:** a^φ(n) ≡ 1 (mod n) only when gcd(a, n) = 1. For n = 8, a = 2: φ(8) = 4 but 2⁴ = 16 ≡ 0 ≢ 1 mod 8.
- **CRT:** the moduli must be **pairwise coprime**. Combining mod 6 and mod 4 (gcd = 2) with the standard formula silently gives a wrong or non-existent solution.

## 4. Overflow Before the Modulo

`pow(a, e, m)` written as a running product in `int`/`long` overflows long before the mod helps: 2⁶⁰ exceeds 2⁶³. Even `(a * b) % m` with a, b < m can overflow `long` when m > ~3×10⁹. Fix: modular multiply via `Math.multiplyMod` (Java 9+), `BigInteger`, or split-multiply (Russian peasant) reduction. Symptom: a "prime" that fails its own primality test at large inputs.

## 5. Confusing φ(p) = p − 1 With φ of a Composite

φ(n) counts integers **coprime** to n, not n−1. φ(p) = p−1 only because p prime. φ(12) = 4 (1, 5, 7, 11), not 11. φ is multiplicative *only for coprime factors*: φ(mn) = φ(m)φ(n) requires gcd(m, n) = 1 — φ(6·2) ≠ φ(6)φ(2) (8 ≠ 4·2? φ(12) = 4 vs φ(6)φ(2) = 2·1 = 2 — unequal, correctly so).

## 6. Forgetting Unique Factorization's Scope

Prime factorization is unique for integers, **not** in general rings: in Z[√−5], 6 = 2·3 = (1+√−5)(1−√−5) with four genuinely different irreducible factors. Algorithms that "assume the prime factorization is canonical" are fine for `long` arithmetic but wrong in Gaussian integers or polynomial rings — a distinction that matters in algebraic number theory and in AES's GF(2⁸), where factorization is over polynomials.

## 7. Off-by-One in the Sieve and in Fermat Indices

Sieve of Eratosthenes: for prime p you may start crossing off at **p²** (smaller multiples already removed by smaller primes), not p·2 — using p·2 is only wasted work, but using `j < n` instead of `j*j < n` as the *outer* bound skips primes √n and beyond. For Fermat tests: a^(n−1) mod n, not a^n; the exponent is n−1 only for prime n.

## 8. Assuming Modular Inverses Are Unique Across Moduli

x ≡ 4 (mod 7) means x ∈ {…, −3, 4, 11, 18, …}: the inverse is unique **as a residue class**, but as an integer there are infinitely many representatives. Code that returns "the inverse" must pick a canonical range (usually [0, m)) — or two implementations (one returning −3, one returning 4) will disagree while both being correct modulo 7.
