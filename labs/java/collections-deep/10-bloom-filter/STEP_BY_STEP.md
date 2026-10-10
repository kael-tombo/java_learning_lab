# Step by Step: Bits by Hand

Toy filter: m = 16 bits, k = 2. Positions precomputed (pretend finalized).

1. Empty: `................` (16 zeros). Query anything → zero bit → absent.
2. `add(apple)` → {3, 9}: `...█.....█......`
3. `add(pear)` → {9, 14}: `...█.....█....█` (bit 9 shared, stays set).
4. `mightContain(apple)` → 3 ✓, 9 ✓ → possibly present (true positive).
5. `mightContain(fig)` → {9, 14} → both set → FALSE positive. Bits owned
   by others; the filter cannot tell. This is the 1% you budgeted.
6. `mightContain(melon)` → {5, 11} → 5 is zero → definitely absent.
   Short-circuit: check 5 first, skip 11 (early exit).
7. Attempt `remove(apple)` by clearing 3, 9 → bit 9 was pear's too: now
   `mightContain(pear)` misses → FALSE NEGATIVE, the unforgivable error.
   Deletion is banned; this drill is why.
8. Union drill: filter A bits `{3,9}`, B bits `{9,14}` → OR = `{3,9,14}`
   = exactly the bits `add(apple)+add(pear)` would set. Mergeable ✓.
9. Saturation drill: add 50 more keys to m=16 → most bits set → every
   query returns "possibly" → p → 1. No exception; the math degrades, it
   doesn't throw. Size for your load or accept the noise.
## Bonus trace: sizing from requirements

Requirement: 1M URLs, FPR ≤ 0.1% (fallback fetch costs 50ms; budget says
0.1% × traffic × 50ms is affordable, 1% is not):

1. m = −n·ln p/(ln 2)² = −10⁶·(−6.908)/0.4805 ≈ 14.38M bits ≈ 1.8 MB.
2. k = (m/n)·ln 2 = 14.38 × 0.693 ≈ 9.97 → 10.
3. Sanity: p = (1/2)^10 ≈ 0.098% ✓. Set-bit fraction at load ≈ 1/2 ✓.
4. Memory check: 1.8MB for 1M URLs vs ~100MB+ as a HashSet — the gate pays
   for itself if it skips even a small fraction of 50ms fetches.

Recompute for p = 1%: m ≈ 9.6M bits (1.2MB), k = 7 — the decade ladder in
one comparison (each extra nine ≈ +0.6MB here).
