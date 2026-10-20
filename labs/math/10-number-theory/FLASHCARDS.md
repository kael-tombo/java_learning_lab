# Number Theory — Flashcards, Run-Backed

Ten cards. Every number came from a captured run or from an exact
hand computation cross-checked in that run — no recollection, no
vibes.

### Card N1
**Ask**: State the division algorithm; what does divmod do when b < 0?
**Say**: a = qb + r with q, r unique and 0 ≤ r < |b|. divmod(17, -5)
returns (-4, -3) under Python's floored convention; canonical is
(-3, 2), reached by adding one to q and |b| to r. The identity
holds in both conventions; only the range law is the contract.

### Card N2
**Ask**: What is the smallest positive value of ax + by over ALL integer pairs?
**Say**: It is gcd(a, b) itself. The run's certificate
2 = −9·240 + 47·46 arrived with every intermediate remainder —
10, 6, 4, 2 — carrying its own Bezout coefficients.

### Card N3
**Ask**: Why does the coefficient slot matter when inverting modulo m?
**Say**: For (26, 7) the identity is 3·26 − 11·7 = 1; the inverse of
7 mod 26 comes from the y-slot: −11 ≡ 15 (mod 26), and
7·15 = 105 = 4·26 + 1. Taking the x-slot instead hands you 3, and
7·3 mod 26 = 21 — not an inverse.

### Card N4
**Ask**: When is a⁻¹ mod m missing, and which error betrays it?
**Say**: Exactly when gcd(a, m) ≠ 1. pow(6, -1, 14) raised
`base is not invertible for the given modulus`, since every 6k is
even and can never be 1 modulo the even modulus 14.

### Card N5
**Ask**: Name the four CRT pieces for Sun Tzu's system and their sum.
**Say**: For x ≡ 2, 3, 2 against 3, 5, 7 with M = 105: pieces 140,
63, 30 sum to 233, reducing to x = 23 (mod 105); residues rechecked
as (2, 3, 2) and a sweep of 0..104 found only [23].

### Card N6
**Ask**: Could the Sun Tzu system hide a second solution in 0..104?
**Say**: No. Any two solutions differ by a multiple of 105, and a
shift by ±105 exits the 105-slot window entirely — so 23 is the
one and only representative, as the brute sweep printed.

### Card N7
**Ask**: Fermat's little theorem — the prime reading and the composite trap.
**Say**: Prime modulus: 2¹⁰ ≡ 1 (mod 11). Composite attempt:
2¹⁴ ≡ 4 (mod 15) — fails; the Euler form with φ(15) = 8 still gives
2⁸ ≡ 1. Fermat's (p−1)-shape is prime-only; Euler's is universal.

### Card N8
**Ask**: How did 561 spoof the Fermat test in the run?
**Say**: 561 = 3·11·17 is composite, yet 2⁵⁶⁰ ≡ 1 (mod 561) and even
2⁸⁰ ≡ 1, since λ(561) = lcm(2, 10, 16) = 80. Carmichael numbers
defeat the pure Fermat primality screen.

### Card N9
**Ask**: Totient census highlights for n ≤ 24.
**Say**: φ(p) = p − 1 at all seven primes (up to 22 at 23);
φ(16) = 8 = 2^(k−1) shape; φ(12) = 4 because only 1, 5, 7, 11 are
coprime to 12; φ(15) = 8 = 2·4 = φ(3)·φ(5) — multiplicativity live.

### Card N10
**Ask**: What exact totals did the census close on?
**Say**: Σφ(n) for n = 1..24 equals 180; brute coprime counts and
the prime-factor formula agreed on all 24 rows under an assert
before the table printed.
