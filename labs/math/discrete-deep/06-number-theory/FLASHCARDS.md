# Number Theory — Flashcards (Verified Numbers)

Values on these cards were printed by the captured runs in CODE_DEEP_DIVE.md.

### Card 1
**Front**: Bezout's identity, run-certified instance?
**Back**: gcd(240, 46) = 2 with 240·(−9) + 46·47 = 2 (equals-g True).
Also (57, 29): 57·(−1) + 29·2 = 1; (101, 13): 101·4 − 13·31 = 1.

### Card 2
**Front**: The Euclid descent steps on (240, 46)?
**Back**: 240 = 5·46 + 10, then 46 = 4·10 + 6 — remainders shrink;
back-substitution rebuilds (x, y) = (−9, 47).

### Card 3
**Front**: When does a mod m have an inverse?
**Back**: Exactly when gcd(a, m) = 1. Run: 6 mod 15 has none
(gcd 3 ≠ 1), printed before any computation is attempted.

### Card 4
**Front**: 17⁻¹ mod 43, with certificate?
**Back**: 38, since 17·38 = 646 = 15·43 + 1 (run-printed line).
Similarly 7⁻¹ mod 26 = 15 (105 = 4·26 + 1).

### Card 5
**Front**: An involutive inverse?
**Back**: 11⁻¹ mod 15 = 11: 11·11 = 121 = 8·15 + 1. Self-inverse
elements exist whenever a² ≡ 1, i.e. a ≡ ±1 or the modulus splits
a² − 1 nontrivially.

### Card 6
**Front**: CRT construction terms?
**Back**: x = Σ aᵢ·(M/mᵢ)·((M/mᵢ)⁻¹ mod mᵢ). The triple (2, 3, 2)
over (3, 5, 7) printed terms 140, 63, 30, raw 233 → 23 mod 105.

### Card 7
**Front**: CRT uniqueness range?
**Back**: M = ∏mᵢ = 105 here: both 23 and 23 + 105 = 128 fit all
three congruences (printed checks), and no larger gap exists below
the product.

### Card 8
**Front**: Consistency gate for non-coprime moduli?
**Back**: Solvable iff gcd(m₁, m₂) divides a₁ − a₂. Run:
difference 8 % 4 = 0 → True for (4 mod 8, 12 mod 12); difference
1 % 4 = 1 → no solution for (4 mod 8, 5 mod 12).

### Card 9
**Front**: Fermat, with typed integers?
**Back**: 2⁶ = 64 ≡ 1 (mod 7); 2¹⁰ = 1024 ≡ 1 (mod 11); 3¹⁰ ≡ 1
(mod 11); 5¹² ≡ 1 (mod 13) — all p prime, all run-printed.

### Card 10
**Front**: Fermat's counter-case?
**Back**: 2³ mod 4 = 0 (printed): composite modulus 4 carries zero
divisors, so lowering p−1 to 3 loses the law — primality is load
bearing.

### Card 11
**Front**: φ(36) two ways?
**Back**: Census 12, formula 12 (equal True); factorization
36 = 2²·3² gives (4 − 2)·(9 − 3) = 12. φ(15) = 8, φ(100) = 40 by the
same double-run.

### Card 12
**Front**: Euler's theorem instances checked?
**Back**: 7⁸ ≡ 1 (mod 15), 11¹² ≡ 1 (mod 36), 3⁴⁰ ≡ 1 (mod 100),
each printed with its gcd = 1 badge — a^(φ(n)) ≡ 1 whenever the base
is coprime to n.
