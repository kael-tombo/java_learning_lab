# Debugging: Number Theory Code

## Symptom: Negative or Out-of-Range Results After Modular Arithmetic

Diagnosis: Java's `%` keeps the dividend's sign. Any expression of the form (a − b) mod m computed as `(a - b) % m` goes negative when a < b.

```java
long mod(long a, long m) { return ((a % m) + m) % m; }   // canonical [0, m)
```

Assert postconditions in every modular function: `0 <= result && result < m`. That single invariant catches the whole class of bugs (negative hash indices, wrong CRT components, `pow` returning negative).

## Symptom: Correct for Small Inputs, Wrong Above ~10⁹

Overflow. Test at the boundary: for m near 10⁹, `(a*b) % m` in `long` is fine (10¹⁸ < 9.2×10¹⁸) but two `int` values or a larger m break it; for m near 10¹⁸ you need `Math.multiplyMod(a, b, m)` or `BigInteger`. Write the test first: `modMul(Long.MAX_VALUE/2, Long.MAX_VALUE/2, Long.MAX_VALUE/2)` must not return a negative number. Same check for modular exponentiation: `pow(3, 1_000_000_007, …)` — a naive loop multiplying without reducing at every step dies immediately.

## Symptom: Primality Test Says "Prime" for 561, 1105, 1729

You implemented the **Fermat test**: check a^(n−1) ≡ 1 (mod n). Carmichael numbers (561 = 3·11·17, 1105 = 5·13·17, 1729 = 7·13·19) pass for every base coprime to n. Fix: use Miller–Rabin — write n−1 = 2^s·d, compute the witness sequence x₀ = a^d, x_{i+1} = xᵢ²; n is composite if any xᵢ ≡ −1 (mod n) never appears before hitting 1. For n < 2⁶⁴ the deterministic base set {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37} is proven sufficient — use it instead of random bases for reproducibility.

## Symptom: gcd/Inverse Returns Wrong Sign or Wrong Value

Extended Euclid postcondition: `s·a + t·b == gcd(a, b)` — assert it every time. The inverse of a mod m is `s mod m` normalized into [0, m); forgetting the normalization returns negative s (e.g., s = −117 → the correct inverse is 235 mod 352, not −117). Also handle degenerate inputs: gcd(0, n) = n, inverse of 1 mod m = 1, and a = 0 has no inverse (gcd(0, m) = m ≠ 1 unless m = 1).

## Symptom: Sieve Skips or Crashes

- Crash: `boolean[] sieve = new boolean[n]` indexed by n itself → use n+1 if you test up to and including n.
- Skipped primes: outer loop must run `for (long p = 2; p * p <= n; p++)` — writing `p <= Math.sqrt(n)` with a double sqrt can stop one iteration early on huge n (floating rounding).
- Wrong starts: mark multiples from p·p; starting at 2p is only slower (O(n log n) instead of the sieve's O(n log log n) total), not wrong.
- Verify: count of primes below 10³ = 168, below 10⁴ = 1229, below 10⁶ = 78,498 — assert these known values as fixtures.

## Symptom: CRT Combination Produces a Value That Fails One Congruence

Check pairwise coprimality first (gcd of every pair must be 1); then verify each congruence before returning — a 3-line assertion that would have caught the mixed-modulus case. Also verify the M = Π mᵢ computation doesn't overflow: moduli 3, 5, 7 → M = 105 fine; six 32-bit moduli → M exceeds 192 bits, use `BigInteger`.

## Symptom: pow With a Negative Exponent

modular exponents must be nonnegative: reduce e mod φ(m) **only if** gcd(a, m) = 1 (else the reduction is invalid — see COMMON_MISTAKES §3). If a caller passes e < 0, compute the inverse first (requires gcd(a, m) = 1) then use e mod φ(m) with φ(m) computed from the factorization — or reject the input loudly.

## Test Oracle

For n < 10⁶, primality is checked against a trusted sieve; for gcd/inverse, assert `a·a⁻¹ ≡ 1 (mod m)` on random coprime pairs (10,000 cases); for modular pow, cross-check `pow(a, e, m)` against `BigInteger.modPow(a, e, m)` — `BigInteger` is the oracle for every other implementation in this lab.
