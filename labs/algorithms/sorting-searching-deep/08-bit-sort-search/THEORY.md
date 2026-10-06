# Theory — Bit Sort & Search

Bit-level algorithms trade *instruction count* for *bit parallelism*. A 64-bit word holds 64 boolean values; an operation on it updates all 64 at once. Combined with the fact that CPU instructions like `POPCNT`, `TZCNT`, `BSWAP` are single-cycle, this beats loop-based code on primitives by 5–50×.

---

## 1. The three regimes for sorting/searching

| Regime | Method | Information per op | Cost |
|--------|--------|--------------------|------|
| **Comparison** | `Arrays.sort(int[])` | 1 bit | `Θ(n log n)` comparisons |
| **Digit** (radix) | radix sort | `log₂ B` bits | `Θ(d(n + B))` |
| **Bit-parallel** | SWAR / bitset / branchless partition | up to `w` bits | `Θ(n · w / log w)` word ops |

The third regime is the interesting one: sorting `n` `w`-bit integers with a **sorting network on packed words** can achieve `Θ(n · w/log w)` word-operations, i.e. `Θ(n log n / 64)` 64-bit operations. In practice this only pays off for very large `n` and simple keys, but it is the theoretical floor for sorting on a word-RAM with a unit-cost `w`-bit word.

---

## 2. Bitwise partition sort

### Mechanism (MSD on raw bit patterns)

```java
static void bitSort(long[] a, int lo, int hi, int bit) {
    if (bit < 0 || hi - lo <= SMALL) { insertionSort(a, lo, hi); return; }
    int m = lo;
    for (int j = lo; j < hi; j++)
        if (((a[j] >>> bit) & 1) == 0) { swap(a, m, j); m++; }
    bitSort(a, lo, m, bit - 1);
    bitSort(a, m, hi, bit - 1);
}
```

**Invariant:** after the partition on bit `b`, `a[lo..m-1]` has bit `b` clear and `a[m..hi)` has it set. Recursing on bit `b−1` within each group produces the sorted order (unsigned, MSB-first).

**Complexity:** `Θ(n · w)` worst (32 or 64 levels), `Θ(n · log n)` on well-spread data. Depth `w`, so recursion must be **tail-recursive or iterative** — a naive recursive version with `w = 64` is fine (64 frames), but a `byte[]` version with `w = 8` and unbalanced splits can recurse deeply. Use the smaller-side-recurse trick.

### Branchless partition — the production form

```java
/** Partition by bit b without a data-dependent branch. */
static int partitionBit(long[] a, int lo, int hi, int b) {
    long bit = 1L << b;
    int m = lo;
    for (int j = lo; j < hi; j++) {
        // Build a 0 or 0xFFFF..FF mask from the bit, branch-free.
        long t = (a[j] & bit);                       // 0 or bit
        // Conditional swap: if t == bit, swap a[m] and a[j].
        long diff = (a[m] ^ a[j]) & -((t >> b));     // -1 if bit set, else 0
        long x = (a[m] ^ a[j]) & diff;
        a[m] ^= x; a[j] ^= x;                        // swap iff bit set
        m -= (int) -((t >> b));                      // m++ iff bit set
    }
    return m;
}
```

**Why this matters:** the branch `if (bit == 0)` is **unpredictable** — a modern predictor guesses right ~50% of the time at a random partition, costing ~15–20 cycles per misprediction. Over `n` elements that is `~10n` wasted cycles. The branchless version uses ~6 ALU ops unconditionally and no mispredictions.

**Measured:** branchless partition is **1.3–2× faster** than branchy on random data at `n ≥ 10⁶`. This is the classic "branchless sort" technique and it is the *real* reason people write custom sorts: not fewer operations, but fewer *stalls*.

### Why not just use radix sort?

Because radix sort's passes are `Θ(d(n + B))` with a `B`-element count array that must be cleared and prefix-summed each pass — pure memory traffic. The bitwise partition sort's first `log₂ n` levels are exactly radix-with-small-`B`, so the two are asymptotically the same thing viewed at different granularities. The bitwise version wins when `B` fits in L1 and the key width is small.

---

## 3. The `k ^ (k-1)` family of tricks

### Why these matter

`k - 1` and `k` differ in a way determined by the lowest set bit of `k`:

```
k       = 1 0 1 1 0  (22)
k - 1   = 1 0 1 0 1  (21)
```

- The **lowest set bit and everything below it** flip: bit `t` goes `1 → 0`, bits `0..t-1` go `0 → 1`, higher bits unchanged.

Hence:

| Expression | Effect | Cost |
|-----------|--------|------|
| `k & -k` | isolate the lowest set bit | 2 ops |
| `k & (k - 1)` | clear the lowest set bit | 2 ops |
| `k ^ (k - 1)` | isolate the lowest set bit (all bits at and below it) | 2 ops |
| `k \| (k - 1)` | set all bits below the lowest set bit | 2 ops |
| `k & (k - 1) == 0` | `k` is a power of two (given `k > 0`) | 2 ops |
| `k > 0 && (k & (k - 1)) == 0` | power-of-two test | 3 ops |

### Submask enumeration — `O(2^popcount)` in `O(1)` amortised per step

```java
/** All submasks of k, in decreasing order. Returns the number enumerated. */
static int submaskCount(int k) {
    int count = 0;
    for (int s = k; ; s = (s - 1) & k) {
        process(s);
        if (s == 0) break;               // PITFALL: forgetting this loops forever
        count++;
    }
    return count;
}
```

This is the standard technique for:
- Enumerating all subsets of a set represented as a bitmask (up to `2²⁰` for `int`, `2⁶⁰` is not practical).
- TSP-style DP over subsets (`n ≤ 20`): `O(2ⁿ · n²)`.
- Enumerating all submasks of an available-memory bitmap.

### Popcount iteration

```java
/** Visit each set bit of k exactly once. O(popcount(k)) total. */
for (long x = k; x != 0; x &= x - 1) {
    int bitIndex = Long.numberOfTrailingZeros(x);   // O(1) intrinsic
    process(bitIndex);
}
```

**This is faster than `for (int i = 0; i < 64; i++) if ((k >>> i & 1) != 0)`** by a factor of `64/popcount(k)`. At `popcount = 32`, that is 2× fewer iterations *and* no branches.

---

## 4. Bit trie over machine words

### Structure

A trie over `w`-bit keys has `w` levels. Each node needs exactly **two** children, indexed by one bit:

```java
/** Perfect binary trie over unsigned 32-bit keys. depth = 32. */
final class BitTrie {
    private final int[] left = new int[MAX_NODES];   // index into the value array
    private final int[] right = new int[MAX_NODES];
    private int size = 1;                             // node 0 = root

    /** Insert an unsigned key. */
    void insert(int key, int value) {
        int node = 0;
        for (int b = 31; b >= 0; b--) {
            int bit = (key >>> b) & 1;
            if (bit == 0) {
                if (left[node] == -1) { left[node] = size++; }
                node = left[node];
            } else {
                if (right[node] == -1) { right[node] = size++; }
                node = right[node];
            }
        }
        values[node] = value;
    }

    /** Exact lookup: O(32) array reads, ZERO hashing. */
    int find(int key) {
        int node = 0;
        for (int b = 31; b >= 0; b--) {
            node = ((key >>> b) & 1) == 0 ? left[node] : right[node];
            if (node == -1) return -1;
        }
        return values[node];
    }

    /** Successor: O(32) with backtracking. The operation a HashMap CANNOT do. */
    int ceiling(int key) {
        int node = 0, best = -1, bestBit = -1;
        for (int b = 31; b >= 0; b--) {
            if (((key >>> b) & 1) == 0) {
                if (right[node] != -1) { best = right[node]; bestBit = b; }  // remember the "turn up" option
                node = left[node];
                if (node == -1) break;
            } else {
                node = right[node];
                if (node == -1) break;
            }
        }
        // If we fell off the path, take the smallest key in `best`'s subtree
        if (best != -1) { node = best; while (leftOrRightAvailable(node)) node = deepestLeft(node); }
        return values[node];
    }
}
```

### Why this beats `HashMap<Integer, V>` for `int` keys

| | Bit trie (32 levels) | `HashMap<Integer,V>` |
|---|---|---|
| Search | `Θ(w) = 32` array reads, **no hashing** | `Θ(1)` expected but with `Integer.hashCode` (a multiply), a modulo/bucket index, and a chain walk |
| Memory | `2 ints` per node × up to `n·32` nodes... **but shared prefixes mean far fewer** | ~48 bytes/entry |
| Predecessor / successor | **`Θ(w)` naturally** | **Not supported** — `Θ(n)` scan |
| Ordered traversal | Free (DFS = sorted order) | **Not supported** |
| Cache | One node per level; levels are contiguous-ish | One bucket per probe |
| Insert | `Θ(w)` | `Θ(1)` amortised |

**The decisive advantages are ordered operations.** `ceiling`, `floor`, `predecessor`, `successor`, and "iterate in sorted order" are all `Θ(w)` on a trie and all `Θ(n)` or impossible on a `HashMap`. If your data structure needs range queries, a trie (or an order-statistic tree) is the right answer.

**Memory caveat:** a naive trie over `n` random 32-bit keys has `Θ(n · log₂(n/32))` nodes ≈ `n · 17` for `n = 10⁶`, at 8 bytes/node = **136 MB** vs `HashMap`'s ~48 MB. A **compressed (Patricia/radix) trie** collapses single-child chains and gets back to `Θ(n)` nodes — that is the version to build in production.

### Key order: signed vs unsigned

Trie traversal is **unsigned** lexicographic on the bit string. `Long.compare` is **signed**. So:

```java
// Signed order == unsigned order of the flipped keys:
long flipped = key ^ Long.MIN_VALUE;      // involution, order-preserving
```
Sort with `Long.compareUnsigned` or flip; do not mix.

---

## 5. Morton (Z-order) codes

### Definition

Spread the bits of coordinate fields apart so each field gets a fixed stride, then interleave:

```
morton(x, y)  =  spread(x) | (spread(y) << 1)
where spread(v) = v | (v << 8) | (v << 16) | ...   for 16-bit fields
```

For 2-D with 16-bit coordinates: `morton` is a 32-bit code; nearby `(x, y)` give nearby codes.

### Why it helps

**Locality:** two points that are close in space have codes that differ in a *high-order* bit only for large distances. So:

- A **range query on codes** (`code ∈ [a, b]`) approximates a **rectangle query in space**.
- Sorting by Morton code gives a spatial index you can build with plain `Arrays.sort` and query with binary search (`O(log n)` + a filter).
- Compressing the Morton code (removing the prefix shared with the previous key, as in a Patricia trie over the codes) gives **a spatial index that is itself a trie** — this is exactly how **Google's S2 / H3** and **UB-tree** work.

### The cost

- **Encoding:** `Θ(w log w)` with the naive spread, `Θ(1)` with the magic-number trick:
  ```java
  static long spreadBy2(long v) {
      long x = v & 0x00000000000fffffL;
      x = (x | x << 32) & 0x001f00000000ffffL;
      x = (x | x << 16) & 0x001f0000ff0000ffL;
      x = (x | x <<  8) & 0x100f00f00f00f00fL;
      x = (x | x <<  4) & 0x10c30c30c30c30c3L;
      x = (x | x <<  2) & 0x1249249249249249L;
      return x;
  }
  ```
- **Query cost:** Morton range queries are *approximate* — a range on codes may include points outside the rectangle, so you must verify. **This is a real drawback:** Hilbert curves have better locality (fewer false positives) but no closed-form inverse.
- **Jitter / diagonal problems:** the Z-curve has long "jumps" where spatial neighbours are far apart in code order. **Hilbert curves** are continuous and have no such jumps, which is why production spatial indexes use them.

### Where it is used

- GPU vertex cache optimisation: reorder triangle vertices by Morton code of their screen-space position → fewer cache misses, 2–5× rasterisation speedup.
- Dead-code elimination: quantise fragments to Morton tiles, pack per-tile masks in `UInt` bitsets.
- Spatial databases (H3 uses hexagons, not Morton; but Z-order indexes are standard in ClickHouse's `ZORDER` and in some LSM-tree designs).
- Z-order curves for Hilbert-like locality in cache-oblivious B-trees.

---

## 6. SWAR: popcount and bitwise operations on packed data

### Software popcount before hardware

```java
/** SWAR popcount: 64-bit word treated as 8 bytes, accumulate nibble counts. */
static long popcountSwar(long x) {
    long c = x - ((x >>> 1) & 0x5555555555555555L);
    c = (c & 0x3333333333333333L) + ((c >>> 2) & 0x3333333333333333L);
    c = (c + (c >>> 4)) & 0x0f0f0f0f0f0f0f0fL;
    return (c * 0x0101010101010101L) >>> 56;
}
```
~12 ops per word. **Irrelevant on x86-64** — `Long.bitCount` is one `POPCNT` instruction.

**SWAR is still valuable** where you have no `POPCNT` (ARMv7, some RISC-V, WebAssembly baseline) or where you want *bulk* bit operations that `POPCNT` cannot do:

```java
/** Count the total number of bits set across a long[] — branchless, vectorisable. */
static long totalPopcount(long[] words) {
    long total = 0;
    for (long w : words) total += Long.bitCount(w);   // the JIT emits POPCNT
    return total;
}
```

### Word-parallel set operations

With a bitset of `n` bits in `n/64` words:

| Operation | Complexity |
|-----------|-----------|
| Set/unset/test a bit | `Θ(1)` |
| Intersect / union / difference | `Θ(n/64)` |
| Popcount | `Θ(n/64)` |
| Find first set bit | `Θ(n/64)` worst, `Θ(n/4096)` average (scan words for `!= 0`, then `TZCNT`) |
| Enumerate set bits | `Θ(popcount + n/64)` |

**This is `64×` faster than a `boolean[]` or a `HashSet<Integer>` for bulk set algebra.** The crossover vs a `HashSet` is roughly `|A| + |B| > 10⁵` for dense sets, or whenever you need more than membership.

---

## 7. Modern JDK bit primitives (JDK 9+)

```java
int  bits = Integer.bitCount(x);
int  tz   = Integer.numberOfTrailingZeros(x);     // 32 if x == 0
int  lz   = Integer.numberOfLeadingZeros(x);      // 32 if x == 0
int  hb   = Integer.highestOneBit(x);             // 0 if x == 0
int  lb   = Integer.lowestOneBit(x);              // 0 if x == 0
int  rev  = Integer.reverse(x);
long bswap = Long.reverseBytes(y);
int  rot   = Integer.rotateLeft(x, 7);
```

**All are intrinsics** on x86-64 (`POPCNT`, `TZCNT`, `LZCNT`, `BSWAP`, `ROL`). Before JDK 9, `bitCount` fell back to a SWAR loop and `numberOfTrailingZeros` used a De Bruijn multiply — so this is a **~5–10× upgrade** for anyone on an older JDK.

**`numberOfTrailingZeros` is the single most useful one.** It gives you:
- The index of the lowest set bit in `Θ(1)`.
- The position of the first differing bit between two values: `a ^ b`, then `TZCNT`.
- The bit-length of a value: `32 - LZCNT`.
- The index of the array slot in a bitset.

---

## 8. The trap table

| Trap | Symptom | Fix |
|------|---------|-----|
| `>>` vs `>>>` | negative values sort/hash as huge unsigned | decide explicitly; use `compareUnsigned` / flip with `MIN_VALUE` |
| `1 << 31` / `1L << 63` | compile error ("possible lossy conversion") | `1L << 31`, or `Integer.MIN_VALUE` |
| `1 << 32` | silently `1 << 0` — Java masks shift counts to 5 bits for `int`, 6 for `long` | loop `shift < 32` (or `64`) |
| `~x` in a comparison | `~x` is negative when `x` is positive | convert to unsigned first: `x >>> 1` |
| `-x` for `Integer.MIN_VALUE` | overflows back to `MIN_VALUE` | special-case, or use `long` |
| `0xFFFFFFFF` as an `int` | compile error | `0xFFFFFFFFL`, or `-1` |
| `k & -k` when `k == 0` | `-0 == 0`, result `0` | guard `k > 0` |
| `numberOfTrailingZeros(0)` | returns 32 / 64, not an exception | always guard; it is a documented, easy-to-miss trap |
| Sign extension when widening | `(byte)0xFF` → `0xFFFFFFFF` | `& 0xFF` |
| De Bruijn lookup table size | off-by-one if the table is 64 entries not 64 | use `Integer.bitCount`-based methods instead |

---

## 9. When bit tricks actually pay

| Situation | Pay? | Why |
|-----------|------|-----|
| Membership + range queries on `int` keys | **Yes** | trie gives `Θ(w)` ordered ops that hashing cannot |
| Bulk set algebra on `10⁶` elements | **Yes** | `Θ(n/64)` vs `Θ(n)` |
| Sorting `int[]` in a hot loop | **Maybe** | branchless partition is 1.3–2× faster; hard to beat `Arrays.sort`'s intrinsic |
| GPU vertex reordering by Morton | **Yes** | 2–5× rasterisation |
| Any use of `Long.bitCount` | **Yes** | free instruction |
| Hand-rolled SWAR popcount on x86-64 | **No** | `POPCNT` is one instruction |
| `Integer.reverse` by hand | **No** | `Integer.reverse` is an intrinsic |
| Packing booleans for a Bloom filter | **Yes** | 64× memory reduction (labs 36) |

**Meta-lesson:** bit manipulation is the right tool when you can *pack many logical values into one machine word*. That is a data-representation decision, not an algorithmic one — and it is the bridge between this lab and the bitmap-based labs (`36-bloom-filter-variants`) and the SIMD work in `05-matrix-algorithms` / `06-parallel-algorithms`.