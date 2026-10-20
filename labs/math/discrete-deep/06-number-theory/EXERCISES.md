# Exercises — Number Theory

Five problems with worked solutions; numbers quoted from the captured
runs in CODE_DEEP_DIVE.md.

## Problem 1. Bezout by Hand and Machine

Find gcd(240, 46) together with integers x, y with 240x + 46y = gcd.

**Solution**: g = 2, x = −9, y = 47 (run-printed, equals-g True).
Verification by substitution: 240·(−9) = −2160; 46·47 = 2162;
−2160 + 2162 = 2. The descent ran 240 = 5·46 + 10, then 46 = 4·10 + 6,
then 6, then back up.

## Problem 2. Invert 17 Mod 43 — and a Non-Invertible

Compute 17⁻¹ mod 43 by extended Euclid; explain why 6 mod 15 fails.

**Solution**: 17⁻¹ ≡ 38 (mod 43): run's certificate 17·38 = 646 =
15·43 + 1. Euclid on (43, 17) returns x = 38 after reduction. Failure
case printed in the same run: ext_gcd(6, 15) reads g = 3 ≠ 1, and
ax ≡ 1 (mod m) would force ax + my = 1, impossible since 3 | LHS.

## Problem 3. Build 23 Mod 105 From Printed Tiles

Given x ≡ 2 (mod 3), x ≡ 3 (mod 5), x ≡ 2 (mod 7), reconstruct x by
the CRT formula and verify against the modular checks.

**Solution**: Printed terms 140, 63, 30 (raw sum 233) → x = 23
(mod 105). Each term supplied: M/m = 35 with (35 mod 3 = 2)⁻¹ = 2 →
2·35·2 = 140; school arithmetic against the run checks
23 mod 3 = 2, mod 5 = 3, mod 7 = 2. Uniqueness range: 128 = 23 + 105
repeats all three residues (printed).

## Problem 4. The Consistency Gate

Which of these systems is solvable: {x ≡ 4 (mod 8), x ≡ 12 (mod 12)}
or {x ≡ 4 (mod 8), x ≡ 5 (mod 12)}?

**Solution**: First: gcd(8, 12) = 4 divides the difference
12 − 4 = 8, so solvable True (printed). Second: difference 1 is not
divisible by 4, printed no solution. Rule: the gate |a₁ − a₂| ≡ 0
(mod gcd) must be read before any inverse assembly — otherwise a
nonexistent solution gets computed silently.

## Problem 5. Fermat's Typed Exponents and Euler's φ

(a) Verify a^(p−1) ≡ 1 for three typed powers. (b) Show the modulus-
4 counter-case. (c) Compute φ(36) two ways and run Euler's theorem.

**Solution**: (a) 2⁶ = 64, and 64 mod 7 = 1; 2¹⁰ = 1024, mod 11 = 1;
3¹⁰ ≡ 1 (mod 11); 5¹² ≡ 1 (mod 13) — all printed. (b) 2³ mod 4 = 0,
printed, because 4 is composite. (c) Census 12 and formula
(4−2)(9−3) = 12, equal True; then 11¹² ≡ 1 (mod 36) (gcd 11, 36 = 1,
printed). Same census/formula pair at 15 (8) and 100 (40).
