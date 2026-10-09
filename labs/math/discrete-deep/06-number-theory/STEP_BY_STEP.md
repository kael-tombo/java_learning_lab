# Step-by-Step: Number Theory by Hand

## 1. Euclid's Algorithm: gcd(1071, 462)

Divide, keep the remainder, repeat — the pair shrinks every step:

```
1071 = 2 × 462 + 147
 462 = 3 × 147 +  21
 147 = 7 ×  21 +   0     ← remainder 0: stop
```

**gcd = 21.** Verify: 1071 = 21·51 ✓, 462 = 21·22 ✓, and no larger divisor divides both (51 and 22 share no factor).

## 2. Extended Euclid: Bézout Coefficients and an Inverse

Back-substitute to write 21 as a combination of 1071 and 462:

```
21 = 462 − 3 × 147
   = 462 − 3 × (1071 − 2 × 462) = 7 × 462 − 3 × 1071
```

Check: 7·462 − 3·1071 = 3234 − 3213 = 21 ✓.

**Inverse application:** find 3⁻¹ mod 352. Steps: 352 = 117·3 + 1 → 1 = 352 − 117·3 → −117·3 ≡ 1 (mod 352) → inverse = −117 + 352 = **235**. Verify: 3·235 = 705 = 2·352 + 1 ≡ 1 ✓.

Contrast: inverse of 6 mod 9? gcd(6, 9) = 3 ≠ 1 → **no inverse exists**. Test quickly: multiples of 6 mod 9 cycle 6, 3, 0, 6, … — 1 never appears.

## 3. Modular Exponentiation Two Ways: 5¹²³ mod 7

**Method A — Fermat's little theorem (p = 7 prime, gcd(5, 7) = 1):**

```
5⁶ ≡ 1 (mod 7);  123 = 6 × 20 + 3
5¹²³ = (5⁶)²⁰ × 5³ ≡ 125 = 17 × 7 + 6  →  ≡ 6
```

**Method B — square-and-multiply (no theorem needed):**

123 = 64 + 32 + 16 + 8 + 2 + 1 (binary 1111011).

```
5¹≡5   5²≡25≡4   5⁴≡4²≡2   5⁸≡4   5¹⁶≡2   5³²≡4   5⁶⁴≡2      (square each time, mod 7)
```

Product of the needed powers: 5⁶⁴·5³²·5¹⁶·5⁸·5²·5¹ ≡ 2·4·2·4·4·5 = (2·4)(2·4)(4·5) = 8·8·20 ≡ 1·1·6 = **6** ✓ — both methods agree, and B is exactly what `modPow` executes (7 squarings + 3 multiplies vs 1 exponent reduction).

## 4. Chinese Remainder Theorem by Hand

Solve x ≡ 2 (mod 3), x ≡ 3 (mod 5), x ≡ 2 (mod 7).

```
M = 3·5·7 = 105
N₁ = 35 (M/3): 35 ≡ 2 (mod 3), 2⁻¹ ≡ 2 (mod 3)  → term₁ = 2·35·2 = 140
N₂ = 21 (M/5): 21 ≡ 1 (mod 5), 1⁻¹ ≡ 1          → term₂ = 3·21·1 = 63
N₃ = 15 (M/7): 15 ≡ 1 (mod 7), 1⁻¹ ≡ 1          → term₃ = 2·15·1 = 30
x = (140 + 63 + 30) mod 105 = 233 mod 105 = 23
```

**x = 23.** Verify each: 23 mod 3 = 2 ✓, 23 mod 5 = 3 ✓, 23 mod 7 = 2 ✓. (This is the answer to Sun Zi's c. 3rd-century puzzle.)

## 5. Sieve Trace to 30

```
start: 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30
strike multiples of 2 from 4:    4,6,8,10,12,14,16,18,20,22,24,26,28,30
strike multiples of 3 from 9:            9,   15,      21,   27
strike multiples of 5 from 25:                        25
(stop: 7² = 49 > 30)
survivors: 2, 3, 5, 7, 11, 13, 17, 19, 23, 29  → π(30) = 10 ✓
```

Note starting at p² (9, 25) — 6 and 12 were already gone when p = 2 and p = 3 handled their factors.

## 6. Fermat "Primality" Failure: 561

561 = 3·11·17 (composite). Test a = 2: 2⁵⁶⁰ mod 561 — the Fermat test **passes** (561 is the smallest Carmichael number: a⁵⁶⁰ ≡ 1 for all a coprime to 561). So "a^(n−1) ≡ 1 for a few bases" is not a proof of primality. Miller–Rabin on 561: n−1 = 560 = 2⁴·35; compute 2³⁵ mod 561 = 263; square: 263² = 69169 mod 561 = 166; square: 166² = 27556 mod 561 = 67; square: 67² = 4489 mod 561 = 1 — but **−1 ≡ 560 never appeared** in the sequence → composite. The strong-liar condition is what Fermat lacks.
