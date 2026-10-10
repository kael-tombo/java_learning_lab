# Architecture: Bloom Filter

## Components

- `long[] bits` (m bits, m = 95 851 canonical) — all zero at construction.
  Fixed size: never grows.
- Hash pipeline: raw `hashCode` → 64-bit mix finalizer (xor-shift/multiply
  avalanche) → split into `h1` (low 32) / `h2` (high 32, forced odd).
- `k` probe positions per key: `g_i = (h1 + i·h2) mod m`, i = 0..k−1,
  computed in `long` to avoid int overflow.
- Parameters derived together: m from (n, p), k from (m, n). Same triple
  (m, k, hash) required on both sides of a union.

## Data flow: add(x)

1. Finalize hash → (h1, h2 odd). 2. For i in 0..k−1: set bit
   `(h1 + i·h2) mod m`. O(k) sets, k ≈ 7 typical.

## Data flow: mightContain(x)

1. Same k positions. 2. All set → "possibly present" (true or false
   positive). Any zero → "definitely absent" (never wrong). O(k) tests
   with early exit on first zero.

## Data flow: union(a, b)

Bitwise OR of the `long[]` words — O(m/word). Valid iff m, k, and hash
functions identical; result = filter of the set union. Intersection via
AND is NOT closable (overestimates differently, size unknown).

## Boundaries

- No delete (use counting variant: 4-bit counters, saturating at 15), no
  iteration, no size query — elements aren't stored.
- Oversaturation degrades p → 1 continuously without error; the "no false
  negatives" guarantee assumes load ≤ designed n.
