# Math Foundation — Bit Sort & Search

Word-RAM complexity, the SWAR accounting, bitset set algebra, and the Morton-code locality analysis.

---

## 1. Word-RAM model

Assumptions: a machine word holds `w` bits (`w = 64`); an add, shift, or AND on a word costs `Θ(1)`; multiplication costs `Θ(1)` for word-sized operands.

Under this model:

| Operation | Word-RAM cost |
|-----------|--------------|
| Add, subtract, AND, OR, XOR, NOT | `Θ(1)` |
| Shift by any amount < `w` | `Θ(1)` |
| Compare | `Θ(1)` |
| Population count | `Θ(1)` if the model includes `POPCNT` (modern), else `Θ(log w)` |
| Multiply | `Θ(1)` |
| Divide / modulo | `Θ(1)` (or `Θ(log w)` in a bit model) |

**This is exactly why bit tricks work.** In the standard RAM model (unit-cost arithmetic on `Θ(log n)`-bit words), a bit operation is `Θ(log w)`. In the word-RAM model it is `Θ(1)`.

---

## 2. Bitset set algebra

Represent a set of `n` bits as `⌈n/w⌉` words.

| Operation | Bit-array cost | `HashSet` cost | Speedup |
|-----------|----------------|----------------|---------|
| `test(i)` | `Θ(1)` | `Θ(1)` expected | 1× |
| `add(i)` | `Θ(1)` | `Θ(1)` expected | 1× |
| `A ∩ B` | `Θ(n/w)` | `Θ(min(|A|,|B|))` | **`w = 64×`** |
| `A ∪ B` | `Θ(n/w)` | `Θ(|A|+|B|)` | up to `64×` |
| `A \ B` | `Θ(n/w)` | `Θ(|B|)` | up to `64×` |
| `|A|` | `Θ(n/w)` | `Θ(1)` (`size()`) | 64× **slower** |
| `contains` | `Θ(1)` | `Θ(1)` | 1× |
| `remove(i)` | `Θ(1)` | `Θ(1)` | 1× |
| iterate elements | `Θ(n/w + popcount)` | `Θ(|A|)` | `~64×` for dense |
| iterate sparse | `Θ(n/w + |A|)` | `Θ(|A|)` | **`n/(w·|A|)`× slower** |

**The crossover.** For a sparse set with `|A| = n/1000`, iterating the bitset costs `n/64 + n/1000 ≈ 0.0166n` vs `HashSet`'s `0.001n` — the bitset is **16× slower**. The bitset wins only when `|A| ≳ n/64`.

**Memory:** `n/8` bytes vs ~48 bytes/entry ⇒ **~384× smaller** at full density. This is the entire basis of Bloom filters, cuckoo hashing, and GPU bitset primitives.

### Find-first-set-bit

```java
long[] w;  // bitset
int firstSet(long[] w) {
    for (int i = 0; i < w.length; i++) {
        if (w[i] != 0) return i * 64 + Long.numberOfTrailingZeros(w[i]);
    }
    return -1;
}
```

- Worst case: `Θ(n/w)` — the set is in the last word.
- Expected for a uniformly random position: `Θ(n/(2w)) = Θ(n/128)`.
- **Improvement**: keep a 64-bit "summary" word where bit `i` is set iff `w[i] != 0`. Then `TZCNT` on the summary gives the first non-empty word in `Θ(1)`. For `n = 10⁹` bits, this is a **2-level bitmap** and reduces the worst case to `Θ(1)`.

### SWAR popcount (the classic 12-op version)

Each step halves the data while accumulating:

| Step | Operation | Data shrinks to | Ops |
|------|-----------|-----------------|-----|
| 0 | `c = x - ((x >>> 1) & 0x5555…)` | pairs | 3 |
| 1 | `c = (c & 0x3333…) + ((c >>> 2) & 0x3333…)` | nibbles | 4 |
| 2 | `c = (c + (c >>> 4)) & 0x0f0f…` | bytes | 3 |
| 3 | `(c * 0x0101…) >>> 56` | total | 2 |

**12 ops per 64-bit word = 0.1875 ops/bit**, versus `POPCNT`'s **1 op per 64 bits = 0.0156 ops/bit**. **SWAR is 12× worse on hardware that has `POPCNT`** (all x86-64 since Nehalem, and ARMv7+ with `-march=armv7-a+popcnt`).

It remains relevant for:
- **Bulk** operations `POPCNT` cannot do (e.g. `x = (x >>> 1) + (x >>> 2) + (x >>> 4); x += x >>> 8; …` then a byte-wise prefix — a full byte-wise popcount of an array in 2 passes).
- Platforms without the instruction.

### Bit-parallel comparison/sorting

A sorting network on packed `w`-bit lanes performs `w` comparisons per word op:

```
Comparisons per word-op:  w/2  (compare-exchange on adjacent lanes)
```

So sorting `n` keys with a `Θ(n log² n)`-comparison network costs `Θ(n log² n · 2/w)` word-ops. For `n = 10⁶`, `w = 64`, a Batcher network: `Θ(n log² n / 32)` word-ops ≈ `6.4·10⁸`. **Still slower than `Arrays.sort`** — bit-parallel *sorting networks* are a theoretical result, not a practical win at these sizes. They win for **sorting a huge number of small fixed-width keys in one pass on a GPU/SIMD unit** (see `05-matrix-algorithms` and `06-parallel-algorithms`).

---

## 3. Bitwise partition sort: counting the work

### Depth and per-level work

Keys are `w`-bit. MSD bit sort partitions on bits `w−1, w−2, …, 0`.

- Depth: `w` levels.
- At level `b`, the total number of elements across all active nodes is `≤ n` (each element is in exactly one active node).
- Per level: `Θ(n)` comparisons-free bit tests plus swaps.

```
T(n, w)  =  w · Θ(n)  =  Θ(nw)
```

### Refined accounting: only `log₂ n` levels do real work

For `n` random `w`-bit keys, after the first `log₂ n` bits the buckets have size ≈ 1. So the *useful* depth is `log₂ n`, and the remaining `w − log₂ n` levels are visited only by singleton buckets (cost `Θ(1)` each via the cutoff).

```
T  =  min(n, w) levels · Θ(n)  for the deep levels, plus Θ(n) for the shallow tail
```

For `n = 10⁶` and `w = 32`: 20 deep levels × `Θ(n)` = `20n`, then 12 levels of trivial work.

**So bitwise partition sort is `Θ(n · min(log₂ n, w))` = `Θ(n log n)` in practice** — the same as quicksort — but with **no comparisons and no unpredictable branches**. That is the entire selling point.

### Branchless vs branchy cost model

Modern CPUs speculatively predict branches:

| | branchy | branchless |
|---|---|---|
| Ops per element | ~3 (`load`, `test`, `branch`) + swap | ~8 ALU ops |
| Misprediction rate | ~50% at a random partition | 0 |
| Cost per misprediction | ~15–20 cycles | — |
| Expected cycles/element | `3 + 0.5 · 17 ≈ 11.5` | `8 · 1 (ILP ≈ 2-3 ops/cycle) ≈ 3` |

**Branchless is ~3–4× better in cycle count** even though it executes 2.7× more instructions. This is the canonical example of *cycles ≠ instructions*.

---

## 4. Bit trie analysis

### Node count

A trie over `n` random `w`-bit keys:

- Level `d` has at most `min(2^d, n)` nodes.
- Total nodes `≈ Σ_{d=0}^{w} min(2^d, n)`.

For `n = 2^k`, the first `k` levels contribute `2^k - 1 ≈ n`, and each of the remaining `w − k` levels contributes `≈ n` (each key on its own chain). So:

```
nodes  ≈  n · (w − log₂ n) + 2n        (approximately)
```

| `w` | `n` | nodes | bytes (2 ints each) |
|-----|-----|-------|---------------------|
| 32 | 10³ | ~28 000 | 224 KB |
| 32 | 10⁶ | ~13·10⁶ | **104 MB** |
| 64 | 10⁶ | ~45·10⁶ | **360 MB** |
| 64 | 10⁸ | ~5.1·10⁹ | **41 GB** — infeasible |

**This is why you must use a compressed (Patricia / radix) trie**, which stores only branching nodes:

```
Patricia trie nodes = number of branching points ≤ 2n − 1
```

**`Θ(n)` instead of `Θ(n(w − log n))`.** Memory for `n = 10⁶`: 2n nodes × 16 bytes = 32 MB. Now `HashMap`-competitive *and* with ordered operations.

### Search complexity

| Operation | Plain trie | Patricia trie |
|-----------|-----------|---------------|
| `find` | `Θ(w)` = 32 | `Θ(log n)` (traverse branching nodes only) |
| `ceiling` / `floor` | `Θ(w)` | `Θ(log n)` |
| ordered iteration | `Θ(1)` per element (DFS) | `Θ(1)` per element |
| insert / delete | `Θ(w)` | `Θ(log n)` |

**Comparison with `HashMap`:**

| | `HashMap<Integer,V>` | Patricia trie |
|---|---|---|
| `get` | `Θ(1)` expected, **1 hash (multiply) + 1 probe** | `Θ(log n)` array reads, **no hash** |
| `get` constant factor | higher | lower for small `n` |
| `ceiling(x)` | **not supported** (`Θ(n)` scan) | `Θ(log n)` |
| ordered iteration | **not supported** | `Θ(1)` amortised per element |
| memory | ~48 B/entry | ~32–64 B/node × `2n` |

**The honest conclusion:** for `get` alone, `HashMap` wins. For *any* range or ordered query, the trie is the only structure in the table that answers in `Θ(log n)`.

---

## 5. Morton code locality

### Definition

```
morton2(x, y)  =  spread(x) | (spread(y) << 1)
```

`spread` doubles the bit width each step. For 16-bit `x`, `y` and a 32-bit code:

| step | mask | ops |
|------|------|-----|
| 1 | `0x0000ffff` | 3 |
| 2 | `0x00ff00ff` | 3 |
| 3 | `0x0f0f0f0f` | 3 |
| 4 | `0x33333333` | 3 |
| 5 | `0x55555555` | 3 |

**`Θ(1)` per coordinate, 15 ops for a 2-D encode.** Or `Θ(log w)` = 5 doubling steps.

### Locality metric

Define the **jump ratio** = (number of codes between two spatially adjacent points) / (average gap).

- **Random order:** average gap `n` — adjacent points are `n/2` apart on average.
- **Morton/Z-order:** average gap `Θ(n)` still (Z has long jumps), but *most* adjacent pairs are close, with a heavy tail.
- **Hilbert curve:** average gap `Θ(1)` with bounded worst case `Θ(√n)` — **continuous**, no jumps.

Known result: the **average jump length of the Z-order curve is `Θ(√n)`** for an `n`-point grid; Hilbert's is `Θ(log √n) = Θ(log n)`. So **Hilbert is asymptotically better for range queries**, at the cost of no closed-form inverse (you cannot compute `d(hilbertToXY(k))` in `Θ(1)`; it needs an inverse table or `Θ(log n)` bit interleaving).

### Range query cost

A rectangle query on Morton codes:
- Pre-filter: one binary search for the code range ⇒ `Θ(log n)`.
- Verify: scan the candidates, test each against the rectangle.

If the code range contains `F` points of which `T` are true positives, cost is `Θ(log n + F)`. With Morton, `F/T` (the **false-positive ratio**) is typically 1.3–3× for reasonable rectangles; with Hilbert, ~1.05×. **This ratio, not the query time, is what determines whether Morton is usable.**

### GPU vertex cache (the measurable win)

Vertices reordered by Morton code of screen-space position reduce vertex-cache misses because vertices fetched in one screen region cluster in memory.

| Metric | No reorder | Morton reorder |
|--------|-----------|---------------|
| Vertex cache miss rate | baseline | **2–5× lower** |
| Rasterisation throughput | baseline | **2–5× higher** |
| Cost | 0 | `Θ(n)` Morton encode + `Θ(n log n)` sort (amortised over frames) |

This is a real, shipping optimisation in every serious GPU renderer (DirectX's `GenerateMipMaps`, Vulkan best-practice guides, NVIDIA's GPU Gems 3 ch. 20).

---

## 6. Submask enumeration complexity

`for (int s = k; ; s = (s - 1) & k)` enumerates all `2^popcount(k)` submasks.

| Quantity | Value |
|----------|-------|
| Iterations | `2^popcount(k)` |
| Per iteration | `Θ(1)` (two ALU ops) |
| Total | `Θ(2^popcount(k))` |
| `k = 2²⁰ − 1` (20 items) | `2²⁰ = 1 048 576` iterations — practical |
| `k = 2²⁶ − 1` (26 items) | `6.7·10⁷` — borderline |
| `k = 2³² − 1` | `4.3·10⁹` — infeasible |

**Held–Karp TSP DP:** `Θ(2ⁿ · n²)` time, `Θ(2ⁿ · n)` memory. For `n = 20`: `2⁰²·400 = 4.2·10⁸` time and `2⁰²·20 = 2.1·10⁷` memory — feasible. This is the **only** exact exponential algorithm that is competitive, and it is why the lab suite has `32-exact-exponential`.

**The terminator is the bug:** `for (int s = k; ; s = (s-1) & k)` loops forever after `s` reaches 0, because `(0−1) & k = k`. You must `break` when `s == 0`, or use the variant that processes `k` first and breaks on 0.

---

## 7. Complexity comparison table

| Task | Comparison-based | Digit-based | Bit-parallel |
|------|-----------------|-------------|--------------|
| Sort `n` `w`-bit ints | `Θ(n log n)` comparisons | `Θ(w·n)` (bitwise MSD) | `Θ(n log²n · 2/w)` (network) |
| Membership, `n` keys | `Θ(log n)` BST, `Θ(1)` hash | — | `Θ(w)` trie |
| Range query | `Θ(log n + F)` | — | `Θ(log n + F)` (Patricia) |
| Set intersection | `Θ(min(|A|,|B|))` | — | **`Θ(max(|A|,|B|)/w)`** |
| Select k-th | `Θ(n)` expected | — | `Θ(w)` per level |
| Popcount of `n` bits | `Θ(n)` bit-by-bit | — | **`Θ(n/w)`** |

---

## 8. Quick reference

| Quantity | Value |
|----------|-------|
| Word size | `w = 64` |
| Bitset set algebra | `Θ(n/w)` = 64× faster than a hash set when dense |
| Bitset memory | `n/8` bytes — 384× smaller than `HashSet` |
| Bitset sparse crossover | wins only when `|A| ≳ n/64` |
| SWAR popcount | 12 ops/word = 0.1875 ops/bit |
| `POPCNT` popcount | 1 op/word = 0.0156 ops/bit — **12× better** |
| Branchless vs branchy partition | ~3× fewer **cycles** (not instructions) |
| Bitwise partition sort | `Θ(n · min(log₂ n, w))` |
| Plain trie nodes | `≈ n(w − log₂ n) + 2n` |
| Patricia trie nodes | `≤ 2n − 1` |
| Patricia trie `find` / `ceiling` | `Θ(log n)` |
| Morton encode (2-D, 16-bit) | `Θ(1)` = 15 ops |
| Morton average jump | `Θ(√n)` |
| Hilbert average jump | `Θ(log n)` — better locality, no `Θ(1)` inverse |
| Submask enumeration | `Θ(2^popcount(k))`, `Θ(1)` per step |
| Held–Karp TSP | `Θ(2ⁿ·n²)` time, `Θ(2ⁿ·n)` memory |
| GPU vertex reorder win | 2–5× rasterisation throughput |