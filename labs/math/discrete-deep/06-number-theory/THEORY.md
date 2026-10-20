# Number Theory — Theory

## 1. Bezout: The Division Algorithm Pays Its Ledger

For all a, b > 0, d = gcd(a, b) is the smallest positive element of
{ax + by : x, y ∈ Z}, and every such combination is a multiple of d.
Machine-witnessed: (240, 46) → d = 2 with 240·(−9) + 46·47 = 2;
(57, 29) → d = 1 with 57·(−1) + 29·2 = 1; (101, 13) → d = 1 with
101·4 − 13·31 = 1. The descent 240 = 5·46 + 10, 46 = 4·10 + 6 is how the
program ran: each remainder replaces the pair, and the recursion
rewrites upward. Equality d = 1 is the certificate that the pair is
coprime — which is exactly what inverses need.

## 2. Modular Inverse via Extended Euclid

a has an inverse mod m iff gcd(a, m) = 1, because ax ≡ 1 (mod m) is
ax + my = 1 for some y. Run values: 17⁻¹ mod 43 = 38 (17·38 = 646 =
15·43 + 1); 7⁻¹ mod 26 = 15 (105 = 4·26 + 1); 11⁻¹ mod 15 = 11, an
involution (121 = 8·15 + 1). Counter-case printed in the same run:
6 has NO inverse mod 15, gcd 3 ≠ 1 — the failure is a divisibility
fact, not a search fatigue.

## 3. CRT: One X, Three Masks

With pairwise-coprime moduli m₁..mₖ and residues aᵢ, the system
x ≡ aᵢ (mod mᵢ) has a unique solution mod M = ∏mᵢ, constructed as
x = Σ aᵢ·(M/mᵢ)·((M/mᵢ)⁻¹ mod mᵢ). Fully worked triple: (2 mod 3,
3 mod 5, 2 mod 7) carried terms 140, 63, 30 summing to 233, which
lands at 23 mod 105 (run-printed raw sum and checks 23 mod 3 = 2,
mod 5 = 3, mod 7 = 2). The two-modulus warmup gave 38 → 8 mod 15.
Why uniqueness: if x and y both fit, M | (x−y), and M is the exact
period — 128 = 23 + 105 satisfies all three checks identically.

## 4. CRT With Non-Coprime Moduli: The Consistency Gate

x ≡ 4 (mod 8) meets x ≡ a₂ (mod 12) iff the difference a₁ − a₂ is
divisible by d = gcd(8, 12) = 4. Run pair (4, 12): difference 8, and
8 % 4 = 0, so solvable True — while (4 mod 8, 5 mod 12) gives
difference 1, 1 % 4 = 1, printed as no solution. One gate misread and
the whole system is unsatisfiable regardless of construction.

## 5. Fermat's Little Theorem with Exact Integers

For prime p, a^(p−1) ≡ 1 (mod p) whenever gcd(a,p) = 1. Typed values
in the run: 2⁶ = 64, and 64 mod 7 = 1; 2¹⁰ = 1024, 1024 mod 11 = 1;
3¹⁰ ≡ 1 (mod 11); 5¹² ≡ 1 (mod 13). The counter-cases matter: 2³ mod
4 printed 0, showing the theorem requires p prime — mod exponent
arithmetic collapses as soon as the modulus factors.

## 6. Euler's φ and Its Formula

φ(n) counts 1..n with gcd(k,n) = 1 and obeys n = ∏ (pᵉ − p^{e−1}) over
the factorization, multiplicatively. Census ∥ formula printed both
ways: φ(15) = 8, φ(36) = 12, φ(100) = 40 (with 36 = 2²·3² giving
(4−2)(9−3) = 12 on the run). Then Euler: 7⁸ ≡ 1 (mod 15),
11¹² ≡ 1 (mod 36), 3⁴⁰ ≡ 1 (mod 100) — all gcd 1, all verified.

## 7. The Programs

Rule 2 assembles the CRT triple from the printed Mi/inverse terms,
plus two incompatible pairs, and enters Fermat's typed powers with the
phi double-derivation and Euler's theorem across three moduli. Each
prints its own division steps so the ledger is auditable.
