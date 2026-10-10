# Performance: Bloom Filter

| Operation | Cost | Notes |
|---|---|---|
| add | O(k) sets (~7) | 2 hashes + k bit sets |
| mightContain | O(k) tests, early exit | absent exits on 1st zero |
| memory | m bits fixed | 12 KB per 10k @ 1% |
| union | O(m/64) word-ORs | 95 851 bits ≈ 1498 longs |

## Cache behavior

k=7 probes scatter across 12KB — fits L1/L2, but each query touches ~7
cache lines worst case. Absent queries usually exit after 1–2 tests
(half the bits are zero at optimum, so P(first probe zero) ≈ 1/2) —
expected ~2 probes for negatives, the welcome asymmetry.

## Sizing guidance

- Size for peak n, not current: saturation degrades silently (p → 1).
  Rebuild (not grow — bits can't be "widened" preserving positions) at
  ~80% of design n.
- k beyond optimum hurts twice: more work per op AND higher FPR via
  saturation. Measure FPR empirically per CODE_DEEP_DIVE snippet 3
  (k=1: 9.9%, 3: 1.9%, 5: 1.1%, 7: 1.0%, 10: 1.3%) rather than assuming
  more hashes = better.
- `long` arithmetic per probe (not int) avoids overflow-corrected
  rehashing; cost is negligible vs the memory accesses.

## vs HashSet

10k strings in HashSet: ~10k nodes × (header + refs + table) ≈ 1MB+.
Filter: 12KB + zero per-element objects, at 1% FPR. The exchange — 100×
less memory for 1% wrong-yeses and no enumeration — is the whole product.
