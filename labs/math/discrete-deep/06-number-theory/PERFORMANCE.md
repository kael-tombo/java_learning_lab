# Performance: Number Theory Algorithms

## The Core Operations (exact complexities)

| Operation | Time | Notes |
|---|---|---|
| gcd(a, b) (Euclid) | O(log min(a, b)) | worst case: consecutive Fibonaccis, Θ(log φ min(a,b)) steps |
| modInverse via extgcd | O(log m) | same loop + Bézout bookkeeping |
| modPow(a, e, m) | O(log e) modular multiplications | with big-int mult: O(M(d)·log e), d = digits of m |
| Trial division primality | O(√n) | fine to n ≈ 10¹² |
| Sieve of Eratosthenes to N | O(N log log N) | memory O(N) bits (or O(√N) segmented) |

Sieve note: **O(N log log N)** time (the harmonic sum over primes ≤ √N), effectively linear in practice; memory O(N) — a 10⁸-bit sieve is 100 MB as Java `boolean[]`, 12.5 MB as a true bitset.

## When Each Primality Strategy Wins

- n < 10¹²: trial division by primes ≤ 10⁶ — O(√n) ≈ 10⁶ operations, trivially fast, deterministic.
- n < 2⁶⁴: Miller–Rabin with the 12 proven bases — deterministic, each round is one modPow: O(12·log³ n) ≈ a few thousand word operations.
- Cryptographic sizes (3072-bit n): Miller–Rabin with k = 40–64 random rounds, error ≤ 4^(−k) ≈ 2^(−80) worst case (adversarial bound; for random bases the true error is ~4^(−k) only in the worst case — practical error is lower but designs assume the bound).
- AKS: O(log^6 n) polynomial — theoretically the answer, practically slower than Miller–Rabin by orders of magnitude; never chosen for performance.

## Factorization: Where Performance Collapses

| Method | Complexity | Practical range |
|---|---|---|
| Trial division | O(√n) | to n ≈ 10¹² (or small factors of anything) |
| Pollard's rho (Brent) | expected O(n^(1/4)) per factor | factors up to ~50–60 bits instantly; 100-bit factors in seconds |
| Quadratic sieve | sub-exp, exp(√(ln n ln ln n)) | to ~100 digits |
| General number field sieve | exp((64/9)^(1/3)(ln n)^(1/3)(ln ln n)^(2/3)) | 829-digit record (2020, RSA-250); 2048-bit out of reach |

The gap between O(√n) factoring and O(log³ n) primality testing is the entire economic basis of public-key cryptography: *checking* a candidate prime is cheap, *splitting* a composite is expensive.

## Modular Exponentiation Cost in Practice

For RSA-2048, e = 65537 (2¹⁶ + 1): modPow with e takes 17 squarings + 1 multiply — versus e = 3 taking 2 squarings + 1. That is why 65537 is standard: a tiny exponent for **public** operations (fast) while decryption uses d (huge exponent, ~2048 bits, ~3072 squarings) — asymmetry in exponent size, not in key size, gives the speed split. CRT-RSA (precompute d mod p−1 and d mod q−1, do two mod-p and mod-q exponentiations) cuts decryption work roughly 4× (Chinese Remainder Theorem applied to the exponentiation itself).

## Sieve Choices

- Naive trial division of every n ≤ 10⁷ for primes: 10⁷ · √10⁷ ≈ 3×10¹⁰ operations — infeasible.
- Sieve to 10⁷: ~10⁷·log log 10⁷ ≈ 10⁷·~3 ≈ 3×10⁷ operations — **1000× less**, and it also gives divisibility info.
- Segmented sieve to 10¹²: O(√10¹²) = 10⁶ memory slots for the base primes, block-wise scanning — memory-bounded instead of impossible (a plain 10¹²-bit array is 125 GB).

## Fixed-Modulus Hot Loops

When the same modulus is reused (RSA, hash fields): precompute Barrett reciprocal (⌊2^k/m⌋) or use Montgomery form once, turning each reduction from a division (tens of cycles) into 2–3 multiplies. This constant-factor work is why cryptographic libraries implement four multiplication strategies rather than one — the asymptotics are identical; the cycles are not.
