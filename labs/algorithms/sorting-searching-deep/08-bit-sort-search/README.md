# 08 — Bit Sort & Search

<div align="center">

**Bitset Sorting · XOR Selection · Trie via Bit Masks · Morton/Z-Order · Bitwise Search Primitives · PDEP/PEXT**

</div>

---

## Learning Objectives

- Recognise when bit parallelism beats a comparison sort: `Θ(n · w / log w)` instead of `Θ(n log n)`
- Implement radix-style bitwise partition sort (MSD/LSD on raw bit patterns)
- Implement the constant-time selection trick: `k XOR (k−1)` for "clear the lowest set bit"
- Build a `w`-bit trie over `w`-bit words and search it in `O(w)` *without* hash lookups
- Understand Morton (Z-order) codes, why locality improves, and when spatial queries need them
- Use the modern primitives: `bitCount`, `bitTrailingZeros`, `bitLeadingZeros`, `reverse`, `reverseBytes`, `numberOfLeadingZeros`
- Recognise the traps: sign extension, shifts ≥ word size, `>>` vs `>>>`, overflow in masks

## Prerequisites

- `04-linear-sorts` (radix sort)
- Two's-complement representation and unsigned/signed comparison
- `Integer.numberOfTrailingZeros` and friends

## Estimated Time

- **Theory**: 85 minutes
- **Practice**: 120 minutes
- **Exercises**: 60 minutes
- **Total**: 4–5 hours

## Key Concepts

| Concept | Description |
|---------|-------------|
| Word-parallelism | One machine word holds `w/64` 64-bit lanes; a single operation updates all of them |
| Bitwise partition | Split by one bit at a time — no comparisons, no branches |
| `k XOR (k-1)` | Clears the lowest set bit — `O(1)` "next permutation of bits" |
| `k & (k-1)` | Tests whether `k` has more than one set bit |
| Bit trie | `w`-level binary tree over bit prefixes; `O(w)` search with **no hashing** |
| Morton / Z-order code | Interleave bit fields so numerically-close codes are spatially close |
| `Integer.bitCount` | Population count — `O(1)` via a CPU instruction (`POPCNT`) |
| PDEP / PEXT | Parallel bit deposit/extract — hardware bit-field scatter/gather |
| Radix-partition sort | MSD quicksort-like partition on bit positions, with `Θ(w)` depth |
| Signed vs unsigned | Java's `compare`/`compareUnsigned`; every bit trick must specify one |
| `Long.numberOfLeadingZeros` | Intrinsic `LZCNT`/`BSR` — `O(1)`, the basis of most bit searches |

## Complexity Snapshot

| Operation | Cost | Note |
|-----------|------|------|
| `Integer.bitCount(x)` | `Θ(1)` | one `POPCNT` instruction |
| `Integer.numberOfTrailingZeros(x)` | `Θ(1)` | one `TZCNT` instruction |
| `Integer.numberOfLeadingZeros(x)` | `Θ(1)` | one `LZCNT`/`BSR` |
| `Long.reverseBytes(x)` | `Θ(1)` | one instruction (`BSWAP`) |
| `k & (k-1)` / `k ^ (k-1)` | `Θ(1)` | clear the lowest set bit |
| Popcount of an `n`-bit vector (software) | `Θ(n/w)` | SWAR: 8 ops per 64-bit word |
| Bitwise partition sort (LSD, `w` bits) | `Θ(w · n)` | 32 or 64 passes for `int`/`long` |
| Bitwise partition sort (MSD) | `Θ(n · w)` worst | with `Θ(n)` typical |
| Bitset sorting (`w`-bit keys, radix `2^k`) | `Θ(d(n + 2^k))` | = radix sort |
| Trie search | `Θ(w)` | one `bit()` call per level — **no hash** |
| Morton code | `Θ(1)` per key | with magic-number bit spreading |
| PDEP / PEXT | `Θ(1)` | BMI2 PDEP/PEXT; not exposed by the JDK API directly |

## Algorithms Covered

### Bitwise partition sort (MSD on raw bits)
```
sort(a, lo, hi, bit):
    if bit < 0 or hi - lo <= SMALL: insertionSort(a, lo, hi); return
    i = lo; 
    for j = lo..hi-1: if bit(a[j], bit) == 0: swap(a, i++, j)   // branchless variant below
    sort(a, lo, i, bit - 1); sort(a, i, hi, bit - 1)
```
`Θ(n · w)` worst, `Θ(n · log n)` typical behaviour when values are well spread. **The real reason to use it: no comparisons, so it is deterministic and branchless**, which on modern CPUs beats branchy comparison code.

**Branchless partition** (the production form):
```java
// mask = all ones if the bit is 0, all zeros otherwise -- via comparison
long mask = -(((a[j] >>> bit) & 1));   // hmm: need a 0/-1 mask, see below
// standard trick:  long t = ((a[j] >>> bit) & 1) * 0xFFFF...FFL;
```
This removes the unpredictable branch that dominates naive partitioning.

### `k ^ (k - 1)` — the bit trick that powers many others
```
k       = 0b10110  (22)
k - 1   = 0b10101  (21)
k ^ k-1 = 0b00011  (3)     -> the lowest set bit, isolated
k & (k-1) = 0b10100 (20)   -> k with the lowest set bit cleared
```
Uses:
- Isolate the lowest set bit: `k & -k`.
- Test power of two: `k > 0 && (k & (k-1)) == 0`.
- Iterate set bits: `for (long x = k; x != 0; x &= x - 1)` visits each set bit once, `O(popcount(k))`.
- Next permutation of a bitmask, submask enumeration: `for (int s = k; ; s = (s - 1) & k) { …; if (s == 0) break; }`.

### Bit trie over machine words
A `w`-bit trie over `w`-bit keys has depth `w` (32 or 64). Each level reads one bit:
```java
int child(int node, int bit) { return node[bit]; }
```
**`O(w)` search with a single array index per level and zero hashing.** For `w = 32` and a hot path, this beats `HashMap` on `int` keys — the hash computation is the thing you eliminate.

**Key order property:** trie traversal is *unsigned* lexicographic on the bit string. That is exactly `Long.compareUnsigned`. If you want signed order, XOR the key with `Long.MIN_VALUE` first.

### Morton (Z-order) codes
Interleave the bits of coordinate fields so that nearby `(x, y)` values have nearby codes:
```
morton(x, y) = spread(x) | (spread(y) << 1)
```
- **Benefit:** spatial locality — nearby points are nearby in code order, so a range query on codes is a range query on space.
- **Cost:** one-time `Θ(w log w)` (or `Θ(1)` with magic numbers) to encode; the code order is *not* the same as lexicographic `(x, y)` order.
- **Use:** Hilbert curves for even better locality; Morton codes in GPU vertex cache optimisation, spatial databases (H3, some Z-order indexes), and GPU rasterisation (dead-code elimination by tile masks).

### Modern JDK primitives (JDK 9+)
```java
Integer.bitCount(x)                        // POPCNT
Integer.numberOfTrailingZeros(x)           // TZCNT  (0 for x == 0)
Integer.numberOfLeadingZeros(x)            // LZCNT  (32 for x == 0)
Long.bitCount / numberOfTrailingZeros / numberOfLeadingZeros
Integer.reverse(x)                         // bit-reversal in the WORD
Long.reverseBytes(x)                       // BSWAP
Integer.highestOneBit(x) / lowestOneBit(x)
Integer.rotateLeft / rotateRight
```
All `Θ(1)` intrinsics on x86-64 (`POPCNT`, `TZCNT`, `LZCNT`, `BSWAP`, `ROL`). **Always prefer these over hand-rolled De Bruijn multiplication or binary-search hacks.**

## Files

| File | Purpose |
|------|---------|
| `src/main/java/com/alglab/bitops/` | Bit-trick toolkit, trie, Morton, SWAR popcount |
| `src/test/java/com/alglab/bitops/` | Cross-validation vs naive/reference |
| `SOLUTION/` | Worked solutions |
| `TESTS/` | Boundary-value suites (0, MIN_VALUE, MAX_VALUE) |
| `BENCHMARK/` | Branchless vs branchy partition, trie vs HashMap |
| `MINI_PROJECT/` | Bit-trie visualiser + Morton curve renderer |
| `REAL_WORLD_PROJECT/` | Bloom-filter/cuckoo-hash accelerator in the style of labs 36 |
| `CHALLENGE/` | SIMD via `Vector` API, PDEP/PEXT via `Unsafe` |
| `DIAGRAMS/` | Bit-level diagrams, Morton curve plots |