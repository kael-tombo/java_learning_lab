# Theory — Linear-Time Sorts

Counting, radix, and bucket sorts share one idea: **stop comparing pairs and start reading the structure of the keys**. The comparison-sort lower bound `⌈log₂ n!⌉` is a bound on *how much information you can extract by asking pairwise questions*. A non-comparison sort extracts far more per operation — e.g. "which bucket is this key in?" reveals `log₂ B` bits at once. That is the only reason these algorithms can beat `n log n`.

---

## 1. Counting sort

### Mechanism

Input: keys in `[0, k)`. Output: sorted array in the same multiset.

```
1. COUNT      for each a[i]: count[a[i]]++
2. PREFIX     for v = 1..k-1: count[v] += count[v-1]
              // now count[v] == number of elements <= v  == the END position for value v
3. SCATTER    for i = n-1 downto 0: out[--count[a[i]]] = a[i]
              // walking BACKWARD with END positions preserves input order of equal keys
```

### Invariant (the part that matters)

During the scatter loop, `count[v]` holds the index **one past the last slot reserved for value `v`**. Therefore `out[--count[v]] = a[i]` fills the next free slot of `v`'s region from the right, and equal values occupy their region in **reverse** order of discovery. Walking the input **backward** therefore lands them in **forward** order → **stable**.

This is the whole stability story, and it is why the loop direction must match the prefix-sum direction. The two legal conventions:

| Scatter direction | Prefix-sum form | Stable? |
|-------------------|-----------------|---------|
| `for i = n-1 downto 0` with `--count[a[i]]` (end positions) | inclusive prefix | **Yes** |
| `for i = 0 to n-1` with `out[count[a[i]]++] = a[i]` (start positions) | exclusive prefix (`count[v] += count[v+1]` variant) | **Yes** |
| `for i = 0 to n-1` with `--count[a[i]]` | inclusive prefix | **No** — reverses equal keys |

Mixing them is the most common counting-sort bug and it is invisible unless you test stability.

### Complexity

- Count: `Θ(n)`.
- Prefix: `Θ(k)` — this is the term people forget. Counting sort is `Θ(n + k)`, **not** `Θ(n)`.
- Scatter: `Θ(n)`.
- Space: `Θ(k)`.

**Key space warning:** if `k = maxValue` and the keys are 32-bit, `Θ(k)` is 4·10⁹ integers = 16 GB. You cannot counting-sort large-range integers. You must either radix-sort them (bucket them by digit) or use a **hash map** variant (`expected O(n)` but with `O(d)` space for `d` distinct keys) — the latter is called **hash sort** / **TimSort's binary-insertion + hashing hybrid** in some libraries.

### Negative keys and offset

Keys in `[min, max]` with `min < 0` need `v = key - min`. Forget the offset and `count[key]` throws `ArrayIndexOutOfBoundsException` — or worse, with `min == 0` and `max == 0` silently produces an all-zero array.

### The "sort with a key range of 1" triviality

If `k = 1` (all keys identical) then `Θ(n + 1) = Θ(n)` — and the algorithm returns the input unchanged. This is the degenerate case where counting sort beats everything.

---

## 2. LSD radix sort

### Mechanism

Keys are fixed-width integers. Choose digit width `k` bits, base `B = 2^k`. With `w` = word size (32 or 64 bits) there are `d = ⌈w / k⌉` digits, extracted as `(key >>> (p * k)) & (B - 1)`.

```
for p = 0 .. d-1:                       // p = 0 is the LEAST significant digit
    stableCountingSort(a, digit = (key >>> (p*k)) & (B-1))
```

### Why LSD must go from the least significant digit

The correctness of LSD rests entirely on **stability** of each pass. Formally:

> **Invariant `P(p)`:** after pass `p` (i.e. after sorting by digits `0..p`), the array `a` is sorted **lexicographically by the tuple** `(digit_p, digit_{p-1}, ..., digit_0)`.

- `P(0)`: after the first pass, `a` is sorted by `digit_0`. Trivially true.
- `P(p) ⇒ P(p+1)`: pass `p+1` stably sorts by `digit_{p+1}`. Two keys with equal `digit_{p+1}` retain their relative order from `P(p)`, which is ascending by `(digit_p, ..., digit_0)`. Keys with different `digit_{p+1}` are now correctly ordered because digit `p+1` is the dominant key. Hence the whole array is sorted by `(digit_{p+1}, ..., digit_0)`. ∎

At `p = d-1` the tuple is the entire key, so `a` is sorted. **Necessity of stability is explicit**: an unstable pass at index `p+1` would destroy the ordering established by the lower digits. This is the single most important thing to know about LSD radix sort.

### Complexity

`Θ(d · (n + B))` time, `Θ(n + B)` space (the output buffer plus the count array).

For `w = 32` bits and `n = 10⁶`:

| `k` (bits/digit) | `B` | `d = ⌈32/k⌉` | `n + B` | Total work `d(n+B)` |
|------------------|-----|--------------|----------|--------------------|
| 8 | 256 | 4 | 1 000 256 | 4.0e6 |
| 11 | 2 048 | 3 | 1 002 048 | 3.0e6 |
| **16** | 65 536 | 2 | 1 065 536 | **2.1e6** |
| 20 | 1 048 576 | 2 | 2 048 576 | 4.1e6 |
| 32 | 2³² | 1 | — | impossible (16 GB counts) |

The `k = 16` row is the practical sweet spot: 2 passes, and the 256 KB count array fits in L2. `k = 11` keeps counts in L1 (8 KB) at the cost of a third pass.

### Base optimisation (analytic)

Write `B = 2^k`, so `d = ⌈w/k⌉ ≈ w/k`:

```
cost(k)  ≈  (w/k) · (n + 2^k)
```

Differentiate in `k`: the minimum is where `n = 2^k`, i.e. **`k = log₂ n`**, giving `B ≈ n` and

```
cost  ≈  (w / log₂ n) · 2n  =  Θ( n · w / log₂ n )
```

Compare with comparison sorting's `Θ(n log n)`. Radix wins by a factor of `(log n)² / w`. For `n = 10⁶` and `w = 32`: factor ≈ `(20)²/32 ≈ 12.5×` fewer operations.

**Caveat:** this analysis ignores the memory hierarchy. `B ≈ n` means a count array the size of the input — cache-hostile. Real implementations pick `B` so the count array fits in L1/L2 (`B = 2¹¹` or `2¹⁶`), which is why measured radix speedups over `Arrays.sort(int[])` are typically 2–4×, not 12×.

### Crossover with comparison sorts

Set `Θ(d(n + B)) = Θ(n log₂ n)`:

```
d = ⌈w / log₂ B⌉,  B ≈ 2048 (k = 11, w = 32)
d = 3,  n + B ≈ n
⟹  3n = n log₂ n  ⟹  log₂ n = 3  ⟹  n = 8
```

**On paper radix beats every comparison sort for `n > 8`.** In practice it wins for `n ≳ 10⁴`, because of:
1. Constant factors — counting passes have no branches, so they vectorise/pipeline well, but each pass does 3 full memory sweeps (count, scatter to buffer, copy back), so *memory bandwidth* dominates.
2. `Arrays.sort(int[])` is dual-pivot quicksort with **introsort-like cutoffs and intrinsics** — roughly `1.39 n log₂ n` comparisons at ~1.5 ns each.

Measured crossover for `int[1..10⁷]`: radix (`k = 11`) is faster from `n ≈ 3·10⁴` upward; below that `Arrays.sort` wins on setup cost.

---

## 3. MSD radix sort

### Mechanism

```
msdRadix(a, lo, hi, digit):
    if (digit < 0 || hi - lo <= SMALL) { insertionSort(a, lo, hi); return }
    countingSort a[lo..hi) by (key >>> (digit*k)) & (B-1)
    for each non-empty bucket [b_j, b_{j+1}):
        msdRadix(a, b_j, b_{j+1}, digit - 1)
```

### Complexity

**First pass: `Θ(n + B)`.** Each subsequent level processes a total of `n` elements across all buckets, so the level costs `Θ(n + B)` *plus* `Θ(B)` per active bucket for the count array reset. With `d` levels and `B` buckets:

```
T(n, d) = Θ(n + B) + max over the largest bucket: T(bucket, d-1)
```

**Worst case:** all keys identical → one bucket of size `n` at every level → `T(n, d) = d·Θ(n + B) = Θ(n log_B n)` — *no better than a comparison sort*. This is MSD radix's Achilles heel and it is why every real implementation switches to insertion sort (or a small comparison sort) when the bucket is small.

**Best case:** all keys distinct → after the first digit every bucket has 1 element → `Θ(n + B)`.

### MSD vs LSD

| | LSD | MSD |
|---|--------|-----|
| Pass order | Least-significant first | Most-significant first |
| Requires a stable inner sort? | **Yes** (essential) | No |
| Benefits from small-bucket comparison sort? | No (all passes are global) | **Yes** — the standard hybrid |
| Memory | `Θ(n + B)` flat | `Θ(n + B)` + `O(d·B)` stack if counts are kept per level |
| Early termination | Never | Possible (all buckets size 1) |
| Cache behaviour | Sequential streaming | Recursive, jumps between buckets |
| Parallelism | Easy: each pass parallelises | Hard: bucket boundaries are data-dependent |

**The hybrid that production code actually uses:**

```java
void msdRadixHybrid(int[] a, int lo, int hi, int digit) {
    if (hi - lo <= 64 || digit < 0) { Arrays.sort(a, lo, hi); return; }   // cut off early
    countAndPartition(a, lo, hi, digit);
    for (int b : buckets) msdRadixHybrid(a, ..., digit - 1);
}
```

This gets MSD's single-Θ(n) first pass plus comparison sort's `O(m log m)` on small buckets: total `Θ(n·(1 + log_C 64))`, effectively `Θ(n)`.

### The American-flag / in-place variant

To avoid the `Θ(n)` output buffer, MSD radix can be done in place with a **cycle-leader permutation**:

```
for v in 0..B-1:
    while cycle-leader of bucket v is not back at its start:
        move the misplaced element into its bucket and pull a new one out
```

Time `Θ(d(n + B))`, space `Θ(B + d)`. It is the basis of the `boost::spreadsort` and `pdqsort`-style hybrid sorters. The permutation loop is genuinely fiddly to get right; treat it as a CHALLENGE, not core material.

---

## 4. Bucket sort

### Mechanism

1. Find `min`, `max`. Let `k = n` (or `n/λ`). Bucket width `w = ⌈(max - min + 1) / k⌉`.
2. `bucketOf(x) = ⌊(x - min) / w⌋`.
3. Distribute into `k` buckets.
4. **Sort each bucket** — usually insertion sort, because buckets are expected to be tiny.
5. Concatenate in order.

### Complexity and its assumption

Let keys be i.i.d. uniform on `[min, max]`. A bucket of width `w` receives `≈ n·w/(max-min+1) ≈ n/k` keys. Insertion sort on `n/k` keys is `Θ((n/k)²)`, and there are `k` buckets:

```
k · Θ((n/k)²)  =  Θ(n²/k)
```

With `k = n`: `Θ(n²/n) = Θ(n)`. ✓ Plus `Θ(n)` for distribution.

**But** this assumes uniformity. Without it:

- **All keys equal** → one bucket of size `n` → `Θ(n²)`.
- **Gaussian keys** → `Θ(n·√n)` = `Θ(n^1.5)` (only ~`√n` buckets are used).
- **Keys in `[min, min+1)` but not uniform** → `Θ(n²)`.

**When bucket sort is right:** when you *know* the distribution. Sensor readings with a known Gaussian, or uniform random keys in a simulation. **When it is wrong:** when you don't. Use `Arrays.sort` — Θ(n log n) is a safe floor that no assumption can break.

### Why sorting is even needed inside a bucket

Because keys within a bucket are unordered. Two cheap alternatives:
- **Skip the sort** if you only need bucketed order (e.g. a histogram), not sorted order.
- **Interpolation sort** if the bucket distribution is smooth: `O(n log log n)` expected on uniform data by searching with the value range instead of the index range. Elegant and fragile; it degenerates to `Θ(n²)` on skewed data.

---

## 5. Which sort when? A decision procedure

```
Are keys non-comparison objects (strings, records, custom types)?
├─ YES ──> comparison sort. Period. (TimSort)
└─ NO (integers/keys):
     Is max-min < 2·n and keys are dense in that range?
     ├─ YES ──> counting sort. Θ(n + k), k < 2n.
     └─ NO:
          Are keys fixed-width integers (int/long/short/char, or BigInteger with bounded size)?
          ├─ YES ──> radix sort (LSD for simplicity, MSD-hybrid for speed). Θ(d(n+B)).
          └─ NO ──> Arrays.sort / Arrays.parallelSort.
```

And one crucial rule:

> **Never use counting sort on raw hash codes or 32-bit IDs without bucketing.** A single key of `2^31 - 1` demands an 8 GB count array. Radix sort by *high bits* first is the fix — and it is exactly what production hash-table partitioning and database index builds do.

---

## 6. Hybrid sorts in production

| Sort | When |
|------|------|
| **Timsort** (`Arrays.sort(T[])`, objects) | Everything object-shaped: stable, adaptive, `Θ(n)` on presorted |
| **Dual-pivot quicksort** (`Arrays.sort(int[])`) | Primitives, `n < 10⁵`, or when setup cost dominates |
| **Parallel merge sort** (`Arrays.parallelSort`) | Large primitive/object arrays with many cores |
| **LSD radix** | Fixed-width integer keys, `n > 10⁴`, latency-sensitive |
| **MSD radix hybrid** (`pdqsort`/`spreadsort` style) | Integer keys where MSD's first-pass locality beats LSD's streaming |
| **Counting sort** | Keys from a dense small domain (chess squares, status codes, small enums) |
| **Bucket sort** | Only with a *known, validated* distribution |

**`Arrays.parallelSort(int[])` uses a parallel merge sort** (with `Arrays.sort` on small leaves) and switches to `Arrays.sort(T[])` (TimSort) for objects — it never uses radix. If you want radix for `int[]`, you supply it.

---

## 7. Summary of what each algorithm *reads* from the keys

| Algorithm | Information extracted per element | Bound it exploits |
|----------|----------------------------------|-------------------|
| Comparison sort | 1 bit ("which of these two is larger?") | `log₂ n!` bits total → `Ω(n log n)` |
| Counting sort | `log₂ k` bits ("which bucket?") | Key domain size `k` |
| Radix sort | `log₂ B` bits per pass | Key *width* `w = d log₂ B` |
| Bucket sort | `log₂ k` bits + local sort | Value *range* + distribution |
| Hash-based sort | `log₂ d` bits (via hashing) | Distinct key count `d`, `O(d)` space |

This is the conceptual core of the lab: **each algorithm's runtime is set by a different property of the input, and only comparison sorts are input-agnostic.**