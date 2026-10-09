# Visual Guide: Number Theory

## 1. The Clock Faces (Residue Classes mod 6)

```
mod 12:    0  1  2  3  4  5  6  7  8  9 10 11
real:     12 13 14 15 16 17 18 19 20 21 22 23   ← all land on the same spokes

mod 6 units (invertible residues):  {1, 5}  = {x : gcd(x,6)=1}     φ(6) = 2
mod 7 units: {1,2,3,4,5,6}  (7 prime → all)   φ(7) = 6
```

Multiplication by a unit permutes the spokes; multiplication by a non-unit (×2 mod 6) collapses spokes: 2·0=0, 2·1=2, 2·2=4, 2·3=0 — collisions, hence no inverse.

## 2. Sieve Visualization to 50 (strike = x)

```
 2  3  4x 5  6x 7  8x 9x 10x 11 12x 13 14x 15x 16x 17 18x 19 20x
21x 22x 23 24x 25x 26x 27x 28x 29 30x 31 32x 33x 34x 35x 36x 37 38x
39x 40x 41 42x 43 44x 45x 46x 47 48x 49x 50x

primes ≤ 50: 2,3,5,7,11,13,17,19,23,29,31,37,41,43,47  → 15 primes
```

Passes actually run: p = 2 (from 4), p = 3 (from 9), p = 5 (from 25), p = 7 (from 49). Everything else was already struck — the Θ(N log log N) total.

## 3. Euclid's Algorithm as Shrinking Pairs

```
(1071, 462) → (462, 147) → (147, 21) → (21, 0)  STOP: gcd = 21
   1071−2·462=147   462−3·147=21    147−7·21=0
```

Each arrow replaces the pair (a, b) with (b, a mod b) — the second entry always shrinks. Worst case (Fibonacci): (Fₙ₊₁, Fₙ) takes n steps, yet n ≈ log_φ(min) — still logarithmic.

## 4. CRT as a Product of Small Clocks

```
   x mod 105   ←—————→   (x mod 3, x mod 5, x mod 7)     one big clock → three small clocks
   23  ↔  (2, 3, 2)      128 ↔  (2, 3, 2)   because 128 = 23 + 105 → same triplet, one period later
```

The arrows are bijections when the moduli are pairwise coprime — the two pictures are the *same* number seen in two coordinate systems (3×5×7 = 105 grid coordinates).

## 5. The Totient as a Counting Picture

```
   n = 12:  1  2  3  4  5  6  7  8  9 10 11 12
   gcd=1?:  ✓  ✗  ✗  ✗  ✓  ✗  ✓  ✗  ✗  ✗  ✓  ✗      φ(12) = 4   {1,5,7,11}
   n = p (prime): all ✓ → φ(p) = p − 1
   formula: φ(n) = n · Π_{p|n} (1 − 1/p)   → φ(12) = 12·(1−1/2)(1−1/3) = 4 ✓
```

Each factor (1 − 1/p) is "cross out every p-th number" — the product is the inclusion–exclusion sieve from lab 03 applied to divisibility.

## 6. Fermat's Little Theorem as a Permutation Cycle

```
   multiply-by-3 mod 7 (a = 3, p = 7):  1 → 3 → 2 → 6 → 4 → 5 → 1
      one 6-cycle; 6 = p−1 steps return to 1 → 3⁶ ≡ 1, 3⁷ ≡ 3
   multiply-by-2 mod 8 (a = 2, n = 8, NOT coprime):  1 → 2 → 4 → 0 → 0 → …
      dies at 0 — no cycle through 1, no inverse
```

Euler's theorem is the same picture in a group of size φ(n): repeated multiplication by a unit cycles and must return to 1 after a divisor of φ(n) steps (the element's *order*).

## 7. RSA's Two Keys on One Diagram

```
   choose p, q ──► n = pq, φ = (p−1)(q−1)
        │                    │
        │ (secret)           │ (secret, derived)
        ▼                    ▼
   encrypt: c = m^e mod n   decrypt: m = c^d mod n,  d ≡ e⁻¹ (mod φ)

   m ──e──► c ──d──► m      because m^(ed) = m^(kφ+1) ≡ m   (Euler + CRT)
```

Everything is exponentiation *mod n* — there is no division anywhere; the "undo" is exponentiation by the inverse exponent, which exists only because the units group has known order φ.
