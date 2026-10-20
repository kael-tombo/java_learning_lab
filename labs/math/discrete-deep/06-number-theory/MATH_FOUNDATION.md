# Number Theory — Math Foundation

Values below are pasted from the captured runs of CODE_DEEP_DIVE.md;
each division step is printed in the runs, so every line is checkable.

## 1. Bezout, Machine-Fetched

ext_gcd(240, 46) = (2, −9, 47): the run printed the substitution
240·(−9) + 46·47 = 2 with equals-g True. ext_gcd(57, 29) = (1, −1, 2):
57·(−1) + 29·2 = 1. ext_gcd(101, 13) = (1, 4, −31):
404 − 403 = 1. The descent rows printed: 240 = 5·46 + 10 and
46 = 4·10 + 6, so the recursion consumes remainders (10, then 6, ...)
and the back-substitution rebuilds (x, y).

## 2. Inverses as Multiply-to-1 Certificates

Observed: 17⁻¹ mod 43 = 38, printed with the certificate
17·38 = 646 = 15·43 + 1. 7⁻¹ mod 26 = 15: 7·15 = 105 = 4·26 + 1.
11⁻¹ mod 15 = 11: 11·11 = 121 = 8·15 + 1 — self-inverse. Rejected in
the same run: 6 mod 15 has no inverse because ext_gcd(6, 15) reads
g = 3 ≠ 1 — inverses exist exactly on the coprime set.

## 3. CRT Pairwise and Triple, Terms Printed

Two-face: residues (2 mod 3, 3 mod 5). Printed terms: for m = 3,
Mi = 5 with (5 mod 3 = 2)⁻¹ = 2, contributing 2·5·2 = 20; for m = 5,
Mi = 3, (3 mod 5 = 3)⁻¹ mod 5 = 2, contributing 3·3·2 = 18. Raw sum
38 → x = 8 mod 15; checks 8 mod 3 = 2 and 8 mod 5 = 3 both printed.
Triple: (2 mod 3, 3 mod 5, 2 mod 7) printed terms 140, 63, 30 — raw
sum 233 — settling at x = 23 mod 105, with checks 2, 3, 2 across
moduli 3, 5, 7. Period wrinkle printed: 128 = 23 + 105 satisfies all
three congruences identically — modulus 105 IS the uniqueness range.

## 4. The Consistency Gate on Non-Coprime Moduli

x ≡ 4 (mod 8), x ≡ 12 (mod 12): difference 8, 8 % 4 = 0, solvable
True (residues can be reconciled because d | a₁ − a₂). x ≡ 4
(mod 8), x ≡ 5 (mod 12): difference 1, 1 % 4 = 1, printed no
solution. The gate is |a₁ − a₂| ≡ 0 (mod gcd(m₁, m₂)), read before
any term assembly.

## 5. Fermat's Typed Powers

Run-verified: 2⁶ = 64 and 64 mod 7 = 1; 2¹⁰ = 1024, mod 11 = 1;
3¹⁰ ≡ 1 (mod 11); 5¹² ≡ 1 (mod 13) — every row a prime modulus p and
exponent p − 1. The failure row: 2³ mod 4 = 0, printed explicitly —
p must be prime, since a composite modulus carries zero divisors that
eat the exponent.

## 6. φ by Census and by Formula

Census ∥ formula on three moduli: φ(15) = 8 = 8 (equal True);
φ(36) = 12 = 12; φ(100) = 40 = 40. Formula working shown:
36 = 2²·3² → (4 − 2)·(9 − 3) = 12. Euler then checks:
7⁸ ≡ 1 (mod 15), 11¹² ≡ 1 (mod 36), 3⁴⁰ ≡ 1 (mod 100), each printed
with its gcd = 1 badge.
