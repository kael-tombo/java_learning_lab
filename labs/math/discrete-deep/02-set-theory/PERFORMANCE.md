# Performance: Set Theory Operations

## Costs of the Standard Implementations (Java)

| Structure | add / contains / remove | iteration order | memory per element |
|---|---|---|---|
| `HashSet` | O(1) amortized average, O(n) worst | unspecified | node + hash ≈ 32–48 bytes |
| `TreeSet` | O(log n) | sorted by comparator | tree node ≈ 40 bytes |
| `LinkedHashSet` | O(1) average | insertion order | node + two pointers |
| `BitSet` (universe ≤ 2^k) | O(1) test, O(1) set | ascending element index | 1 bit per universe slot |

Numbers are from data-structure analysis (hashing, red-black trees), not measured benchmarks.

## Choosing by Operation Mix

- Many membership probes against a growing collection → `HashSet`: n probes cost O(n) total instead of O(n log n) for a `TreeSet`.
- Range queries ("all elements in [lo, hi]") → `TreeSet.subSet` is O(log n + k) for k reported elements; a `HashSet` cannot answer without scanning O(n).
- Dense small universe (flags, primes below 10^6) → `BitSet`: a 10^6-element universe costs 1,000,000 bits ≈ 125 KB, versus ~30 MB for a `HashSet<Integer>` of the same density (boxing alone is 16 bytes/value).

## Union / Intersection / Difference Complexity

- `HashSet.addAll(b)`: Θ(|b|) hashing work plus node allocation; result build is Θ(|a| + |b|) in the worst case.
- `BitSet.or(other)`: Θ(⌈n/64⌉) word operations with no allocation per element — roughly a 64× reduction in per-element work at the machine-word level, plus cache locality.
- Checking disjointness short-circuits: iterate the smaller set, `contains` in the larger — O(min(|a|,|b|)) expected, vs O(|a|·|b|) with two lists.

## Power Set Generation

Enumerating P(A) by integer mask runs in O(n·2^n): there are 2^n subsets and building each from its mask costs Θ(n) (or Θ(1) amortized with Gray-code increments that flip one bit at a time). There is no O(2^n) algorithm with explicit element-by-element construction; this exponential is inherent to output size. Do not attempt P(A) for n > 25 in memory (2^25 = 33,554,432 subsets).

## Set Equality and Hashing Pitfalls (Cost Side)

`a.equals(b)` for two `HashSet`s is Θ(|a| + |b|) at best (contains checks) — and `hashCode` must therefore be Θ(n). Aggregating huge set hashes per frame (e.g., hashing a whole set inside a loop) turns an O(1) check into an O(n) hot spot; cache the hash or compare sizes first (`size()` mismatch → unequal in O(1)).

## When a "Set" Should Be a Sort

Deduplicating n items via `TreeSet` costs O(n log n); via `HashSet` it costs O(n) average but pays hashing and memory. If the data is already being sorted anyway (comparison sort, merge joins), fold dedup into the sort and you get order + uniqueness for the same O(n log n) you were spending regardless.
