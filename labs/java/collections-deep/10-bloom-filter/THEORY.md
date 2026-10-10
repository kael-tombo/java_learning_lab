# Bloom Filter Deep Dive — Theoretical Foundation

## Core Concept

A Bloom filter answers "is x in the set?" with **no false negatives and a
tunable false-positive rate**, using ~10 bits per element instead of storing
the elements at all. Structure: an `m`-bit array (all zero) plus `k`
independent hash functions. To add x, set bits `h₁(x) … hₖ(x)`. To query x,
answer "possibly present" iff all `k` bits are set — a single zero bit is
proof of absence.

There is no `java.util` Bloom filter (Guava has one; the JDK doesn't), so this
lab builds it from scratch — which is also how you learn why the parameters
interact the way they do.

## The False-Positive Formula (derived, not quoted)

After inserting n elements with k hashes into m bits:

1. P(a given bit is still 0) = `(1 − 1/m)^(kn) ≈ e^(−kn/m)`.
2. A false positive needs all k probed bits set:
   **p = (1 − e^(−kn/m))^k**.

For the canonical sizing (n = 10 000 elements at p = 1%):

| k | measured FPR class | formula value |
|---|-------------------|---------------|
| 1 | ~9.9% | 0.0991 |
| 3 | ~1.9% | 0.0194 |
| 5 | ~1.1% | 0.0111 |
| 7 | ~1.0% | 0.0100 |
| 10 | ~1.3% | 0.0130 |

Too few hashes → each query checks too few bits (easy to get lucky). Too many
→ the array saturates and every query finds its bits set. The minimum sits at
the optimum below (all values recomputed for this doc — see CODE_DEEP_DIVE
snippet 3, which measures them empirically).

## Optimal Parameters (both derived by minimizing p)

- **Hashes**: `k = (m/n)·ln 2`. At m/n ≈ 9.6 bits per element, k ≈ 6.64 → 7.
- **Size**: `m = −n·ln p / (ln 2)²`. For n = 10 000, p = 0.01: m ≈ 95 851
  bits ≈ **12 KB**. Ten thousand strings in 12 kilobytes with 99% query
  accuracy — that's the entire appeal.
- At optimal k, exactly half the bits are set (`e^(−kn/m) = 1/2`), and
  `p = (1/2)^k = 0.5^6.64 ≈ 0.01`. The filter is a half-full bit array; the
  information-theoretic reading is that each element costs `k = −log₂ p`
  bits of evidence.

Rule of thumb: **~10 bits per element per 1% FPR decade** (1% → 9.6 bits,
0.1% → 14.4 bits, each extra decimal digit costs ~4.8 bits/element).

## Double Hashing: k Functions from 2 (Kirsch–Mitzenmacher)

Computing k independent hashes is wasteful. The standard construction needs
only two:

```java
g_i(x) = h1(x) + i * h2(x)  (mod m),   i = 0 .. k-1
```

Kirsch and Mitzenmacher (2006) showed this preserves the asymptotic false-
positive rate — no need for k hash evaluations. The implementation splits one
64-bit mix (e.g. SplitMix64-style finalizer over `hashCode`) into two 32-bit
halves. Constraint: `h2` must be odd (else the probe sequence has period < m
and never visits half the array); force `h2 | 1`.

## What a Bloom Filter Cannot Do

- **No deletion** — clearing bits could unset a bit shared with another
  element, creating false negatives. (Counting Bloom filters replace bits
  with 4-bit counters: +1 on add, −1 on remove, query `counter > 0`. Costs
  4× memory, counters can overflow/underflow if misused.)
- **No enumeration** — the elements aren't stored; you can't iterate or count
  (`size` is unknowable from the bits alone).
- **No false-negative freedom under saturation** — the guarantee "no false
  negatives" assumes the filter was sized for its load. Insert 10× the
  designed n and p → ~1: the math degrades continuously, it doesn't throw.
- **Hash quality is load-bearing** — `String.hashCode()` (31-multiplier,
  weak low bits) directly as `h1`/`h2` correlates the probes. Always run the
  raw hash through a finalizer (xor-shift/multiply avalanche) first.

## Complexity

| Operation | Cost | Notes |
|-----------|------|-------|
| add | O(k) bit sets | k ≈ 7 typical |
| query (mightContain) | O(k) bit tests | early exit on first zero |
| memory | m bits, fixed at construction | never grows |
| union | O(m/word) OR | same (m, k, hash) required |
| intersection | NOT closable | AND of filters overestimates differently; size unknown |

Union deserves emphasis: OR-ing two filters with identical parameters yields
the filter of the union — the only composable sketch in the collections
family. This is why distributed systems (Cassandra, Bigtable/HBase, Chrome
Safe Browsing) ship them: each node builds locally, the coordinator ORs.

## Counting Variant and Alternatives

- **Counting Bloom filter**: 4-bit counters per cell; supports remove;
  overflow at 15 must be guarded (saturating add) or it wraps into false
  negatives.
- **Cuckoo filter** (Fan et al., 2014): stores fingerprints in a cuckoo hash
  table; supports deletion, slightly better space for p < 3%, but fails past
  load ~95% and needs fingerprint size tuned to p.
- **Quotient filter / XOR filter**: static-set successors with better cache
  behavior (XOR filters are immutable — build once, query fast).

Pick Bloom when: set membership only, additions only, tiny memory, and a 1%
error budget is fine. Reach for the alternatives when deletion or enumeration
enters the requirements.

## Key Invariants

1. A zero bit at any of x's k positions ⟺ x was never added (no false
   negatives) — the only hard guarantee.
2. At optimal k, fraction of set bits ≈ 1/2 after n insertions.
3. `p = (1 − e^(−kn/m))^k` predicts measured FPR within sampling noise when
   hashes are uniform — non-uniform hashes break the formula before they
   break the code.
4. Filters are mergeable by OR **iff** (m, k, hash functions) are identical.
