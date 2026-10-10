# Math Foundation: False-Positive Rate

## Derivation of p = (1 − e^(−kn/m))^k

1. One hash sets a given bit with probability 1/m. kn hashes total (n
   elements × k).
2. P(bit still 0) = (1 − 1/m)^(kn). With (1 − 1/m)^m → e^(−1):
   ≈ e^(−kn/m).
3. P(bit set) ≈ 1 − e^(−kn/m). A false positive needs all k probed bits
   set (treated independent): **p = (1 − e^(−kn/m))^k**.

## Optimal k = (m/n)·ln 2

Minimize p over k: d/dk [k·ln(1 − e^(−kn/m))] = 0 → e^(−kn/m) = 1/2 →
k = (m/n)·ln 2. At this k half the bits are set, and p = (1/2)^k.

## Optimal m = −n·ln p / (ln 2)²

From p = (1/2)^k and k = (m/n)·ln 2: ln p = −(m/n)·(ln 2)² →
m = −n·ln p/(ln 2)². Canonical: n=10000, p=0.01:
m = −10000·(−4.605)/0.4805 ≈ 95 851 bits ≈ 11.7 KB; k = 9.585·0.693 ≈ 6.64
→ 7.

## Worked ladder (each 10× less p costs ~4.8 bits/element)

| p | m/n (bits/elem) | k |
|---|---|---|
| 1% | 9.6 | 7 |
| 0.1% | 14.4 | 10 |
| 0.01% | 19.2 | 13 |

## Double-hashing note (Kirsch–Mitzenmacher 2006)

`g_i = h1 + i·h2` preserves asymptotic p with 2 hashes instead of k —
the derivation assumes uniform independent probes, which the (h1,h2)
construction approximates when the finalizer avalanches and h2 is odd.
