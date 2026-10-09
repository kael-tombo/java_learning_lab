# Internals: How Sets Are Implemented

## HashSet = HashMap with a Placeholder Value

`java.util.HashSet` is a thin wrapper over `HashMap<K, Object>`; every "element" is a map key mapped to a shared `PRESENT` sentinel. The whole lookup path is the map's:

1. `hashCode()` is spread: `h ^ (h >>> 16)` so high bits reach low bucket indices.
2. Bucket index is `(n - 1) & hash` with n = table length (a power of two).
3. If the bucket holds a tree node (bin length ≥ 8 and table size ≥ 64), a red-black tree gives O(log n) lookup; otherwise a linked list gives O(n_bin).
4. On match, `equals()` confirms identity.

Average O(1) add/contains; worst case O(n) if every key collides (the red-black fallback exists precisely to bound that).

## Load Factor and Resize

The default load factor is 0.75. When size exceeds `0.75 × capacity`, the table doubles and all entries rehash — an amortized O(1) operation per insert, but O(n) for a single resize. Capacity is rounded up to a power of two, so `new HashSet<>(expectedSize)` with `expectedSize / 0.75` avoids repeated doublings.

## TreeSet: Order Instead of Hashing

`TreeSet` backs a `NavigableSet` on a red-black tree: add/contains/remove are O(log n), and iteration is in ascending order of the comparator. It requires a total order — a comparator inconsistent with `equals` (e.g., ordering strings by length only) makes distinct-but-compare-equal elements silently collapse into one entry, a classic data-loss bug.

`LinkedHashSet` keeps a doubly linked list across buckets: O(1) membership with predictable insertion-order iteration, at the cost of extra pointers per entry.

## BitSet: Sets as Bit Vectors

A `BitSet` stores a `long[]` of words. Membership test of element i is `(bits[i >> 6] >>> (i & 63)) & 1L` — O(1). Union is a word-wise OR: for a universe of size n it costs Θ(⌈n/64⌉) machine words, i.e., about n/64 operations instead of n hash lookups. This is the gap between a bitset union (linear in the word count, cache-friendly) and a `HashSet` union (hash each element, allocate nodes).

## Immutable and Persistent Sets

`Set.of(...)` (Java 9+) builds an immutable compact hash-based set with no per-entry nodes; it rejects duplicates at construction with `IllegalArgumentException`. Persistent sets (as in Clojure) use hash array mapped tries to share structure across versions — copy is O(1) amortized because unchanged subtrees are reused.

## What the Contract Guarantees

- `Set` forbids duplicate elements: `add` returns false when x is already present.
- `HashSet` iteration order is unspecified and can change after a resize.
- `TreeSet` iteration order follows the comparator, not insertion.
- Nulls: `HashSet` allows one null key; `TreeSet` allows null only if the comparator handles it (natural ordering throws `NullPointerException`).
