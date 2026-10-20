# Number Theory — Math Foundation

Every figure below comes from a captured run of the CODE_DEEP_DIVE
programs; the Bezout chains were also re-multiplied by hand line by
line.

## 1. Division Algorithm and Its Uniqueness

Claim: for b ≠ 0 there exist unique q, r with a = qb + r and
0 ≤ r < |b|. The run printed all four sign cases:

  17 = 5·3 + 2,  -17 = 5·(-4) + 3,  17 = (-5)·(-3) + 2,  -17 = (-5)·4 + 3

each ending with `identity True | range True`. Uniqueness: if
a = q₁b + r₁ = q₂b + r₂ with both remainders in range, then
(q₁ − q₂)b = r₂ − r₁ is a multiple of |b| whose size is at most
|q₁−q₂|·|b| in absolute value — but |r₂ − r₁| < |b| forces
|r₂ − r₁| = 0 and q₁ = q₂.
Check the sign case 17 = (-5)q + r: raw Python divmod hands back
(-4, -3); the canonical repair shifts to (-3, 2), which the run
verified by re-multiplication.

## 2. Euclid Descent, Then Bezout by Back-Substitution

For (240, 46) the quotients printed were 5, 4, 1, 1, 2 with running
Bezout lines (coefficient pair shown per new remainder):

  10 = 1·240 − 5·46   6 = −4·240 + 21·46
  4 = 5·240 − 26·46   2 = −9·240 + 47·46   0 = 23·240 − 120·46

The final remainder 2 carries the certificate
gcd(240, 46) = 2 = −9·240 + 47·46. Hand check: 47·46 − 9·240 =
2162 − 2160 = 2. The fifth printed line, 0 = 23·240 − 120·46,
certifies that 46 divides 23·240; combined with gcd(46, 240) = 2 it
shows 23 shares a factor with 240 — Bezout's minimal form is what the
algorithm minimizes, and the identity s·a + t·b = r is preserved
forward from the start, so no separate back-substitution pass is
needed.

## 3. Inverse From Bezout, Existence From gcd

Inverting 7 mod 26 asked Bezout for (7, 26): the run's trace self-
corrected an initial zero quotient and landed on
1 = −11·7 + 3·26, so 7⁻¹ ≡ −11 ≡ 15 (mod 26), and indeed
7·15 = 105 = 4·26 + 1. Existence is exactly coprimality: the inverse
of 6 mod 14 does not exist because gcd(6, 14) = 2 — any 6k is even
and can never hit 1 mod 14; Python's pow(6, −1, 14) raises
`base is not invertible for the given modulus`.

## 4. CRT on Sun Tzu's System, Term by Term

x ≡ 2 (mod 3), x ≡ 3 (mod 5), x ≡ 2 (mod 7), with M = 105. Each congruence
contributes a·(M/m)·(M/m)⁻¹ mod m — printed terms 140, 63, 30 — and
233 ≡ 23 (mod 105). Residue check: 23 mod 3 = 2, 23 mod 5 = 3, 23 mod
7 = 2. Uniqueness: a brute sweep of 0..104 found the single solution
[23], because two solutions would differ by a multiple of coprime
product 105 while sharing the same reduced range. The mixed-ratio
mechanism: congruence i fixes x only up to multiples of mᵢ, and the
inverse yᵢ = (M/mᵢ)⁻¹ mod mᵢ is what lets a·Mᵢyᵢ satisfy the target
congruence a mod mᵢ while dying to zero modulo every other modulus.

## 5. Fermat, Euler, and One Carmichael Fool

Prime-modulus Fermat: 2¹⁰ mod 11 = 1 (1024 = 93·11 + 1). Euler shape
with φ(m): 3⁴⁰ mod 100 = 1 since φ(100) = φ(4)·φ(25) = 2·20 = 40.
Composite modulus contrast from the run: 2⁸ mod 15 = 1 ✓ while 2¹⁴ mod 15 = 4
✗ — Fermat's (p−1)-form is not a theorem at composite moduli, Euler's
φ-form still is. The Carmichael number 561 = 3·11·17 defeated Fermat
in the other direction: 2⁵⁶⁰ ≡ 1 (mod 561) passed like a prime, but
λ(561) = lcm(2, 10, 16) = 80 and 2⁸⁰ ≡ 1 too — primality testing on
Fermat alone can be spoofed.

## 6. Totient Census, Computed Two Ways

Brute count of k in {1..n} with gcd(k, n) = 1, against the
factorization formula p^a · (p − 1) per prime block — the program
asserted both agree for n = 1..24:

  1:1 2:1 3:2 4:2 5:4 6:2 7:6 8:4 9:6 10:4 11:10 12:4 13:12 14:6 15:8
  16:8 17:16 18:6 19:18 20:8 21:12 22:10 23:22 24:8

Visible shapes: φ(p) = p − 1 at every prime (3, 5, 7, 11, 13, 17, 19,
23), φ(2^k) = 2^(k−1) (16 → 8, 24 → φ(8)·φ(3) = 4·2), φ(15) = 8 =
φ(3)·φ(5) — multiplicativity sampled in place — and the running sum
Σφ(n) for n ≤ 24 reaches 180.
