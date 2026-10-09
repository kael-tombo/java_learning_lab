# Internals: Number Theory Implementations

## Binary Exponentiation (modPow)

`pow(a, e, m)` by square-and-multiply: process e's bits from LSB to square the accumulator each step and multiply in when the bit is set — **O(log e) modular multiplications** (about 1.5·log₂e on average, since half the bits are set). Each step reduces mod m so intermediates stay < m². This is what `BigInteger.modPow` does, with Karatsuba/Toom-Cook/FFT multiplication underneath for large operands — total O(M(log e) · log e) for schoolbook multiplications M(d) = O(d²).

## Modular Multiplication: Three Implementations

1. `long c = (a * b) % m` — correct only while a·b < 2⁶³ (m < ~3×10⁹ for safety).
2. `Math.multiplyMod(a, b, m)` (Java 9+) — `BigInteger`-free exact reduction; internally uses either direct multiplication or a decomposed reduction depending on operand size.
3. **Russian-peasant (double-and-add) reduction**: repeatedly halve b, double a mod m — O(log b) additions, no overflow, no BigInteger. This is the embedded/competitive default when m can approach 2⁶³.

**Montgomery reduction** (used inside fixed-modulus hot loops, e.g., RSA with a constant n): requires m odd, transforms multiplication into a residue-class representation where reduction costs ~3 extra word ops instead of a division — asymptotically the same O(1) per multiply but with a much smaller constant. **Barrett reduction** avoids the oddness requirement by precomputing ⌊2^k/m⌋ for a fixed m, giving one multiply-based reciprocal instead of division.

## Extended Euclidean Algorithm

Loop invariant: `rᵢ = sᵢ·a + tᵢ·b`, decreasing remainders. Runs in O(log min(a, b)) steps (worst case consecutive Fibonacci numbers — the classical bound), storing only the previous triple. Returns gcd plus Bézout coefficients. `modInverse(a, m)` = `s mod m` from extgcd(a, m), valid exactly when gcd = 1. Same loop powers the **binary GCD** alternative (subtract/shift instead of division: also O(log) but division-free — slower in practice than hardware division on modern CPUs).

## Sieve of Eratosthenes: Complexity and Memory

Crossing off multiples of p ≤ √n: Σ_{p ≤ √n} n/p ≈ n·ln ln n operations → **O(n log log n)** time (measurably near O(n)); memory O(n) bits (boolean array: n = 10⁷ → 10 MB in Java's `boolean[]` = 1 byte each, or 1.25 MB as a real bitset). **Segmented sieve**: process blocks of size B ≈ √n (or a cache-sized block), keeping only the block plus primes ≤ √n — O(√n) memory with the same O(n log log n) time, the standard way to sieve to 10¹².

The timing detail that matters: mark starting at **p²** with stride p (`for (long j = p * p; j <= n; j += p) sieve[j] = false;`) — smaller multiples were already struck by smaller primes. Starting at 2p is still correct but wastes roughly half the passes.

## Primality Testing Internals

- **Trial division**: O(√n) — only for n up to ~10¹² or as a pre-filter.
- **Miller–Rabin**: each round is one modPow (O(log³ n) with schoolbook multiplication) plus O(log n) squarings; k rounds → O(k·log³ n), error ≤ 4^(−k) per round (adversarial worst case). Deterministic for n < 2⁶⁴ with 12 fixed bases.
- **AKS (2002)**: deterministic polynomial, original O(log^12 n) improved to O(log^6 n) — theoretically decisive, practically unused (Miller–Rabin + a deterministic Lucas/extra round is faster in the ranges that matter).
- **Lucas–Lehmer**: only for Mersenne numbers 2^p − 1, O(p²) or O(p log p) with FFT — the test behind GIMPS primes.

## Factoring Internals (Why RSA Cares)

- **Trial division**: O(√n); removes small factors first (primes 2, 3, 5… up to 10⁶ instantly).
- **Pollard's rho** (Brent's variant): expected O(n^(1/4)) = O(√p) for smallest prime factor p — finds a 40-bit factor of a 1024-bit n in moments, which is why RSA primes must be equally large.
- **Quadratic sieve / general number field sieve**: sub-exponential exp((64/9)^(1/3)(ln n)^(1/3)(ln ln n)^(2/3)) — the reason 2048-bit RSA (n ≈ 617 digits) is the current floor.
