# Architecture: Number Theory Code

## One Layered Library, Four Concerns

1. **Primitive layer** — `gcd`, `modNormalize(a, m)`, `modMul`, `modPow`, `egcd`. Pure functions, no state, canonical output range [0, m). Everything else is built from these; they are also the layer with the overflow rules (see INTERNALS), so they get the assertion budget.
2. **Theory layer** — `modInverse` (from egcd), `isPrime` (trial division + Miller–Rabin), `sieve(n)`, `totient(n)` (needs factorization), `crt(residues, moduli)`. Each function documents its precondition: `modInverse` requires gcd = 1; `crt` requires pairwise-coprime moduli; `totient` requires a factorization strategy.
3. **Application layer** — RSA keygen/sign/verify, Diffie–Hellman, deterministic nonces. Uses only BigInteger for key-sized numbers; never implements its own big-int arithmetic.
4. **Boundary/policy layer** — key sizes, Miller–Rabin round counts, prime-generation RNG, rejection sampling. Policy lives here and nowhere else, so a security review changes exactly one file.

The separation mirrors how the math works: the primitive layer is the ring axioms, the theory layer is the theorems, the application layer is the protocol.

## Representing Residues

- Canonical range: always **[0, m)** at every function boundary. Internally, `((a % m) + m) % m` at entry and exit — cheap insurance against Java's signed `%`.
- Small/moderate m (m < ~3×10⁹): `int`/`long` fine with `multiplyMod`.
- Key-sized (≥ 2048 bits): `BigInteger` only — hand-rolled `long` arithmetic cannot represent n, and mixing the two invites the overflow bug. Compile-time-ish guard: functions that take `long modulus` assert `m > 0` and document the upper bound.

## Sieve as a Separate Product

`boolean[] sieve(long limit)` / segmented variant is a data provider, not a per-call utility: build once (O(N log log N)), then answer `isPrime` queries in O(1). For one-off checks, call Miller–Rabin instead — architectures that let `isPrime` silently build a 10⁸-element sieve on a hot path turn a 20 µs check into an O(N) allocation.

## Determinism and Testability

- Miller–Rabin: use the **fixed 12-base set** for n < 2⁶⁴ (deterministic, reproducible) — random bases in tests produce flaky failures; random bases belong only in the production k-round path where the security parameter is the point.
- Prime generation: inject the RNG (`Supplier<BigInteger>`) so tests can use fixed candidates; production requires a CSPRNG and rejects p ≈ q, smooth p−1/q−1.
- Keygen returns (n, e, d, p, q, φ) in a record for test assertions — private key material exists as data only inside the boundary layer.

## Testing Architecture

- **Oracle:** `BigInteger.modPow` / `BigInteger.probablePrime` cross-check every primitive (10,000 random triples per CI run).
- **Known fixtures:** gcd(1071, 462) = 21; 3⁻¹ mod 352 = 235; 5¹²³ mod 7 = 6; π(10³) = 168, π(10⁴) = 1229; CRT → 23; RSA toy (n = 391, e = 3, d = 235): Enc(50) = 271 and Dec(271) = 50.
- **Property tests:** for random coprime (a, m): `a·a⁻¹ ≡ 1 (mod m)`; for random primes p: a^p ≡ a (mod p); for random (m, n) with gcd = 1: φ(mn) = φ(m)φ(n); Carmichael 561 must be reported composite by Miller–Rabin and (per its definition) prime by the Fermat test — both assertions belong in the suite, documenting the boundary between the two tests.
- **Overflow probes:** modMul at m = Long.MAX_VALUE/2, modPow with 10⁹-bit exponents, sieve to 10⁷ exact count.
