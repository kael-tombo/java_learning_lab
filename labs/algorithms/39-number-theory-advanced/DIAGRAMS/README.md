# Diagrams — Lab 39: Advanced Number Theory

Diagrams for the algorithmic number theory in this lab: **sieve of Eratosthenes and its segmented form**, **the wheel sieve**, **Miller–Rabin**, **Pollard's rho**, **the discrete-log ladder (BSGS/Pohlig–Hellman)**, and **Chinese Remainder Theorem recombination**.

All diagrams are terminal-renderable ASCII so they survive a diff. Each entry names the section of `../THEORY.md` it illustrates and gives a construction recipe for a rendered version.

---

## Diagram inventory

| # | File / construct | Purpose | Format |
|---|-----------------|---------|--------|
| N1 | `sieve-of-eratosthenes.md` | Composites struck out, step by step | ASCII grid |
| N2 | `segmented-sieve.md` | The `[L, R]` window with per-prime base multiples | ASCII |
| N3 | `wheel-sieve-6.md` | Residue classes `1, 5 mod 6` and the `8×8` visual grid | ASCII |
| N4 | `factor-power-ladder.md` | `p`, `p²`, `p³`, … multiplicities in a sieve | ASCII bars |
| N5 | `miller-rabin-witness.md` | `n − 1 = d·2^s`, the `s` squarings, and a witness witness | ASCII trace |
| N6 | `pollard-rho-cycle.md` | Floyd's `x, y = f(f(y))` cycle detection by `x == y` | ASCII sequence |
| N7 | `bsgs-lattice.md` | The `m × m` table / baby-step giant-step picture | ASCII grid |
| N8 | `pohlig-hellman-decomposition.md` | Factoring `|G|` to smooth the group order | ASCII tree |
| N9 | `crt-reconstruction.md` | `x ≡ aᵢ (mod mᵢ)` and the incremental `x = x₀ + k·M` walk | ASCII walk |
| N10 | `number-theory-in-systems.md` | Where this lab's algorithms appear: key generation, hashing, checksums, scheduling | ASCII architecture |

---

## The picture that carries the whole lab (N1)

```
Sieve of Eratosthenes up to 50. Start: every cell is a candidate prime.

  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19
  x  x  P  P  x  P  x  P  x  x  x  P   x  P   x  x  x  P   x  P
     ^ struck for the trivial reasons: 0 and 1 are not prime

  p = 2  -> strike  4, 6, 8,10,12,14,16,18
  p = 3  -> strike  9,12,15,18        (start at p*p = 9, not p)
  p = 5  -> strike 25                (start at 25)
  p = 7  -> strike 49                (start at 49 = 7*7, and 7*7 > 50 next)

  survivors: 2 3 5 7 11 13 17 19 23 29 31 37 41 43 47   (pi(50) = 15)

KEY INVARIANT: we start striking at p*p, so every composite c is struck
by its SMALLEST prime factor p <= sqrt(c), and p*p <= c  =>  c is
always struck exactly once, at the step where p <= sqrt(c).

That single observation is why the sieve is O(n log log n) and not O(n sqrt n):
   sum over p <= sqrt(n) of  n/p   =   n * (ln ln sqrt(n) + M)
                                =   Theta(n log log n)
```

**Diagram the invariant, not just the numbers.** The "why start at `p²`" argument is what students miss, and it is the entire complexity proof.

---

## Recommended diagram exercises

1. Draw N1 fully with all strike-outs, then re-run it counting strikes per prime. The count for `p` should be `⌊n/p⌋ − p + 1`. Sum it and verify `Θ(n log log n)` numerically.
2. Draw N2: a window `[10^9, 10^9 + 20]` and the base multiples `p·⌈L/p⌉` for every prime `p ≤ √(10^9 + 20) ≈ 31623`. Verify that marking a multiple never touches a prime in the window — **this is the off-by-one that silently produces wrong primes** (you must skip `p` itself).
3. Draw N3 for the 6-wheel (`1, 5 mod 6`) and for the 30-wheel (`1,7,11,13,17,19,23,29 mod 30`). Show the density reduction `1/φ(k)`.
4. Draw N5 for `n = 2·3·5·7·11·13·17·19·23·29·31·37 = 7420738134810 + 1` style inputs, including **a composite that passes a small number of bases** (there are known strong pseudoprimes for each base count — find one for 2, 3, 5).
5. Draw N6 and show the `x == y` collision point, then the `x == y` recovery of the factor `|x − y|`. Then find a `p` where `ρ(p^0.5) = O(1)` by running the trace and count iterations.
6. Draw N7 for the discrete log of `g^x ≡ h (mod p)` with `x` known to be in `[0, m²)`. Show how a `√p`-sized baby-step table finds `x` in `O(√p)`. Then draw N8: if `p − 1 = 2^s · q` with `q` smooth, the DL problem collapses to `O(√q)`.
7. Draw N9: solve `x ≡ 3 (mod 5)`, `x ≡ 7 (mod 11)`, `x ≡ 2 (mod 13)` incrementally and verify the combined solution modulo `715`.

---

## Related files

- `../THEORY.md` — sieve mechanisms and the `p²` argument, Miller–Rabin's threshold (`2³²` with bases `{2,3,5,7,11,13,17}`), Pollard's rho and the birthday paradox, BSGS/Pohlig–Hellman, CRT and its non-coprime variant.
- `../MATH_FOUNDATION.md` — `Σ 1/p = ln ln n + M` (Mertens), `√p` factoring and `p^1/4` for Pollard, `O(√n)` for BSGS, and the `log` reductions from smooth orders.
- `../BENCHMARK/` — where the ASCII renderers live; the sieve counts in N1 and N4 are reproducible there.