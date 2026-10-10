# Internals: Lab Filter vs Guava

## Your filter (this lab)

- `long[] words` bit array; `setBit`/`getBit` via `(word << 6)` indexing.
- Hash: `hashCode` → SplitMix64-style finalizer (xor-shift + multiply
  avalanche — required because `String.hashCode`'s 31-multiplier has weak
  low bits) → h1/h2 split, `h2 | 1`.
- Positions in `long`: `((h1 & 0xFFFFFFFFL) + i * (h2 & 0xFFFFFFFFL)) % m`
  — int arithmetic would overflow the multiply; the mask-then-widen keeps
  values non-negative without `Math.abs` (which breaks on MIN_VALUE).
- Parameters: `m = −n·ln p/(ln 2)²`, `k = round((m/n)·ln 2)`; canonical
  n=10000, p=0.01 → m=95851, k=7.

## Guava's BloomFilter (reference cousin)

`com.google.common.hash.BloomFilter` — same double-hashing skeleton
(`h1 + i·h2`), `long`-based bit array, funnel-driven hashing instead of
`hashCode`, serialization of (m, k, hash strategy) so unions check
compatibility. Study its `put`/`mightContain` for the production-hardened
shape of your lab code (explicit compatibility checks before `putAll`).

## What the JDK has instead

Nothing probabilistic in `java.util` — the JDK answers membership with
`HashSet` (exact, ~32+ bytes/element). The lab's 12KB-for-10k-strings
figure is the entire argument for reaching outside the JDK (or Guava).

## Alternatives on the same shelf

Counting Bloom (4-bit counters, ±1, saturating), Cuckoo filter (Fan et
al. 2014: fingerprints in cuckoo table, deletion OK, fails past ~95%
load), XOR filter (immutable, build-once/query-fast static sets).
