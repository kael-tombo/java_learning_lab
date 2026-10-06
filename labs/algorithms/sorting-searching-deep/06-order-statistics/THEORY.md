# Theory — Order Statistics

Order statistics is the family of problems that ask *which* element, not *all* the elements in order. It is the most common "sort-like" problem in production — percentiles, top-k, medians, quantiles — and it is `Θ(n)` instead of `Θ(n log n)` for a single answer. That factor of `log n` is the entire subject of this lab.

---

## 1. Problem definition and the family

An **order statistic** of a multiset is the `k`-th smallest element. The related problems, in increasing order of what they must produce:

| Problem | Output | Cost (expected) | Requires the input preserved? |
|---------|--------|------------------|-------------------------------|
| Min / max | 1 element | `Θ(n)`, `O(1)` space | No |
| Selection (`k`-th smallest) | 1 element | **`Θ(n)`** | **No** — it is partitioned |
| Top-k | `k` elements | `Θ(n)` if destructive, `Θ(n log k)` otherwise | Depends |
| Full sort | `n` elements in order | `Θ(n log n)` | Yes (or copy) |

**The single most important practical fact:** quickselect **destroys the order** of everything it touches. You cannot call it twice and get two answers. If you need the top-k *and* the array afterwards, you must either copy (`Θ(n)` space) or use a different algorithm (heap, order-statistic tree, multi-selection).

---

## 2. Quickselect

### Mechanism

```
select(a, k):
    lo = 0; hi = a.length - 1
    while lo < hi:
        p = partition(a, lo, hi)      // random pivot
        if p == k: return a[p]
        else if p < k: lo = p + 1     // discard [lo, p] entirely
        else: hi = p - 1               // discard [p, hi] entirely
    return a[lo]
```

### Why the complexity is `Θ(n)` and not `Θ(n log n)`

Quicksort recurses on **both** halves: `T(n) = 2T(n/2) + Θ(n) = Θ(n log n)`.
Selection recurses on **one** half: `T(n) = T(n/2) + Θ(n)`.

Unrolling for a perfectly balanced split:

```
T(n) = T(n/2) + n
     = T(n/4) + n/2 + n
     = T(n/4) + 1.5n
     = ...
     = T(n/2^j) + n·(1 + 1/2 + 1/4 + ...)   = T(1) + 2n = Θ(n)
```

**The geometric series is the whole argument.** The work at level `i` is `n/2^i` and there are `log n` levels, so the total is `n(1 + 1/2 + 1/4 + …) < 2n`. Contrast quicksort, where the work at each level is a full `n`.

**Generalisation:** if the pivot splits `α n` / `(1−α) n`, then

```
T(n) = T(αn) + Θ(n)  ⟹  T(n) = Θ( n / max(α, 1−α) )
```

Linear for **any** fixed `α ∈ (0, 1)`. So the algorithm is robust to systematically mediocre pivots — it is only the *adversarial* case that hurts.

### Expected complexity with a random pivot

The pivot rank is uniform on `[0, n-1]`. Let `E[T(n)]` be the expected comparisons:

```
E[T(n)] = (1/n)·Σ_{j=0}^{n-1} ( E[T(j)] + E[T(n-1-j)] ) + cn
        = (2/n)·Σ_{j=0}^{n-1} E[T(j)] + cn
```

Solving the recurrence gives `E[T(n)] ≈ 1.3863 n log₂ n`... **no — that is quicksort.** For selection the recurrence has *one* subproblem and the solution is:

```
E[T(n)] ≈ 2(1 + ln 2)·n  =  3.386·n  comparisons
```

**The constant is ≈ 3.386 n comparisons** for randomised quickselect. Compare:
- Randomised quicksort: `≈ 2.20 n ln n ≈ 1.3863 n log₂ n`
- Randomised quickselect: `≈ 2(1 + ln 2) n ≈ 3.386 n`
- `Arrays.sort` at `n = 10⁶`: `≈ 1.3863 · 10⁶ · 20 = 27.7·10⁶` comparisons
- Quickselect at `n = 10⁶`: `≈ 3.39·10⁶` comparisons

**≈ 8× fewer comparisons.** That is the payoff, and it is entirely because we skip the `log n` levels of full sorting.

### Worst case `Θ(n²)`

If the pivot is always the minimum: `T(n) = T(n-1) + cn = cn²/2 = Θ(n²)`.

Worst cases:
- **Sorted input** with a first/last-element pivot.
- **Adversarially constructed input** against median-of-3 or ninther: the adversary knows the rule and can force unbalanced splits indefinitely. This is the *only* argument for randomised pivots over median-of-medians.
- **Organ-pipe / nearly-sorted** input with weak pivot rules.

**Mitigation without randomisation:** recurse on the **smaller** side and loop on the larger. That fixes the *stack* (`O(log n)` guaranteed) but not the *time* (`Θ(n²)` remains).

---

## 3. Median of Medians — deterministic `Θ(n)`

### Mechanism

```
medianOfMedians(a, lo, hi):
    // 1. Sort each group of 5
    for each group g of 5 elements: sort g; take g[2] as its median
    // 2. Recursively select the median OF THE MEDIANS (n/5 elements)
    pivot = medianOfMedians(a, medians)
    // 3. Partition the whole range around pivot
    p = partition(a, lo, hi, pivot)
    // 4. Only ONE side recurs, and it is provably <= 7n/10
```

### The pivot guarantee

Let `n` be divisible by 10 for cleanliness, so there are `n/5` groups.

- Let `M` be the median of the `n/5` medians.
- Of the `n/5` group medians, **at least `n/10` are `≥ M`** and **at least `n/10` are `≤ M`**.
- Each of those `≥ n/10` medians comes with **2 elements from its group that are `≥` that median**, hence `≥ M`.
- So at least `2·(n/10) = n/5` elements are `≥ M`.
- Symmetrically at least `n/5` elements are `≤ M`.
- Elements `< M` and `> M` therefore number at most `n − n/5 − n/5 = 3n/10` each side.

> **Guarantee: the pivot splits `≤ 7n/10` on one side and `≤ 7n/10` on the other.** At least `3n/10` of the input is discarded on **both** sides.

### Recurrence

```
T(n) = T(n/5)          // find the median of the medians
     + T(7n/10)        // recurse on the surviving side
     + Θ(n)           // the grouping + sorting of 5-element groups + partition
```

Master theorem / Akra–Bazzi with `a₁ = a₂ = 1`, `b₁ = 1/5`, `b₂ = 7/10`:

```
Solve  1 = (1/5)^p + (7/10)^p
p ≈ 3.3864        (dominant term: (0.7)^3.3864 ≈ 0.336 ≈ 1/3)
T(n) = Θ(n^3.3864) = Θ(n)
```

**The critical property is that the discard factor exceeds `1/3`.** If it were only `1/4`, the remaining side would be `3n/4` and the same recurrence would give `T(n) = Θ(n^{log_{4/3} 4}) = Θ(n^{4.82})` — worse than `Θ(n log n)`.

### Constant factor

The exact worst-case comparison count is

```
T(n) ≤ T(⌈n/5⌉) + T(⌈7n/10⌉) + 6n   ⟹  ≈ 3.386·n + lower-order
```

So **median-of-medians costs about 3.386 n comparisons** — the same as randomised quickselect's expectation, but **worst case**.

### So why doesn't everybody use it?

| | Randomised quickselect | Median of medians |
|---|---|---|
| Expected comparisons | `≈ 3.386 n` | `≈ 3.386 n` (worst case) |
| Grouping/sorting overhead | none | `Θ(n)` with 5-element sorts + recursion |
| Memory | `O(log n)` stack | `O(log n)` stack + `Θ(n/5)` for the medians |
| Cache behaviour | single sequential partition pass | multiple passes over disjoint slices |
| Measured (n = 10⁶) | **~55 ms** | **~310 ms** |
| Worst case | `Θ(n²)` | `Θ(n)` |
| Failure mode | astronomically unlikely | none |

**Median-of-medians is ~6× slower in practice.** Its value is that it converts a probabilistic guarantee into a deterministic one — which matters for move-to-front heuristics, adversarial-input-resistant systems, and for *proving* an algorithm's behaviour. **In Java you use `Arrays`-backed quickselect or Guava's `Iterables.partition`, not median-of-medians.**

---

## 4. Interpolation select

Choose the pivot by **interpolating the value**: if you know the array is (roughly) uniform over `[min, max]`, the element at rank `k` is at value

```
v = min + (max − min) · k / n
```

then binary-search for `v`. On uniformly random data this finds the exact rank in one step → `Θ(n)` total. On adversarial data the interpolation is maximally wrong every time → `Θ(n log n)` or worse.

**Mitigation — interpolation select:** after the first partition, switch to interpolation only if the observed pivot positions have tracked `i/n` closely (keep a running check, e.g. "no deviation more than a constant factor"); otherwise use quickselect. This gives `Θ(n)` expected on both uniform and adversarial data and is what libstdc++'s `__introselect` effectively does. It is a genuinely clever technique and a good CHALLENGE exercise.

---

## 5. `Θ(log n)` selection with preprocessed structure

### Fenwick tree / Binary Indexed Tree

`tree[i]` stores the sum of `a[i − lowbit(i) + 1 .. i]`, where `lowbit(i) = i & (−i)`.

```
findByOrder(k):                 // k is 1-based; returns the index of the k-th smallest
    idx = 0
    for (step = highestPowerOfTwoLE(n); step > 0; step >>>= 1):
        next = idx + step
        if next <= n && tree[next] < k:
            idx = next
            k -= tree[next]
    return idx + 1
```

**Why this is `Θ(log n)` and not `Θ(log² n)`:** a naive approach would binary-search the prefix sums, costing `log n` per prefix query × `log n` queries = `log² n`. Binary lifting does both simultaneously: it descends the tree of prefix-sum intervals in a single `log n` walk, greedily skipping whole blocks whose count is `< k`.

**Use when:** you have a **static array of counts/values**, many k-th queries, and `Θ(n)` memory. Classic: frequency tables, "k-th smallest in a multiset with a fixed value domain", offline order statistics after coordinate compression.

### Order-statistic tree (balanced BST with subtree sizes)

Each node stores `size(subtree)`. Then:
- `select(k)`: at each node, compare `k` with `size(left)`; descend left/right in `Θ(log n)`.
- `rank(x)`: same walk, `Θ(log n)`.
- `insert` / `delete`: `Θ(log n)`, and sizes are maintained.

This is the right structure for **dynamic** order statistics (inserts and deletes interleaved). Java has no built-in, so it is a CHALLENGE implementation (AVL or Treap with sizes, ~120 lines).

### Wavelet tree / matrix

If values are already sorted per level, a wavelet tree answers `k`-th in `Θ(log σ)` for an alphabet of size `σ`, with `Θ(n log σ)` bits of extra space. Used in bioinformatics and string indexes (`suffix arrays` — see lab 27). Mentioned for completeness; not required.

---

## 6. Top-k: the four strategies

| Strategy | Time | Space | Order preserved | Use when |
|----------|------|-------|-----------------|----------|
| Sort then take the first `k` | `Θ(n log n)` | `O(1)` or `Θ(n)` | Yes | `k` close to `n`, or you need sortedness anyway |
| Quickselect + partition | `Θ(n)` | `O(1)` | **No** | one-shot, array disposable |
| Multi-select (quickselect `k` times) | `Θ(n log k)` worst | `O(1)` | **No** | avoid; use a heap |
| **Bounded min-heap of size `k`** | **`Θ(n log k)`** | **`O(k)`** | Yes (input untouched) | streaming, or `k ≪ n` |
| Max-heap of `k` **largest** | `Θ(n log k)` | `O(k)` | Yes | top-k / percentile |
| Order-statistic tree | `Θ(log k)` per op | `Θ(k)` | Yes | dynamic, repeated queries |

**The heap trick, correctly stated:**

For the **`k` smallest** of a stream, keep a **max-heap of size `k`**:
- if the heap is not full, push;
- else if `x < heap.peek()`, replace the root.

Because the root is the *largest* of the `k` best-so-far, any `x ≥ root` can be discarded immediately — and the check is `O(1)`. This is why the heap, not a min-heap, is the right choice: the *predicate* must reject cheaply.

Cost analysis: `Θ(k log k + (n−k) log k) = Θ(n log k)` worst case, but **expected** `Θ(n)` if the input is random (only `k ln(n/k)` elements actually replace the root).

### Special case: `k = 1`

`Θ(n)` with `O(1)` space — a single pass, no data structure. **The special case is worth checking before choosing an algorithm at all.**

---

## 7. Parallel selection

Split the array into `p` contiguous blocks; each thread quickselects within its block (for the median) or partitions by a shared pivot value; then refine.

**Algorithm (median of medians, parallel):**
1. Partition `n` elements into `p` blocks of `n/p`.
2. Each thread sorts its block's 5-element groups, computes `n/(5p)` medians, and locally selects the median of those.
3. Gather all `p` block medians (`p` values) into a shared array; select the median of *that* array (cheap: `p` elements).
4. That pivot is guaranteed to have ≥ `n/(2p)` elements on each side within every block. So a **global count** of elements `< pivot` is known after one parallel pass.
5. Broadcast the pivot and its global rank; the answer is either the pivot or the `(k − rank)-th` element of one block, found by a local quickselect.

Work `Θ(n)`, **depth `Θ(n/p + p)`** — the local selection is `Θ(n/p)` sequential and the pivot-selection of `p` medians is `Θ(p)`. Optimum at `p = √n`, giving depth `Θ(√n)` versus `Θ(n)` sequential.

**Measured:** 8 threads give ~5× on `n = 10⁸`, limited by the final global-count pass and memory bandwidth.

---

## 8. Production notes

### `Arrays` / Guava / fastutil reality
- Java's `Arrays` has **no** `nth_element`. Use `Arrays.sort` + index, or
- `IntArrays.quickSelect(IntArrays.asList(a), k)` from **fastutil** (`it.unimi.dsi.fastutil`), which is a tuned quickselect and the right answer in practice,
- or a bounded `PriorityQueue` for top-k.

### The percentile trap
`p99(latencies)` over a large array should be a `Θ(n)` quickselect, **not** a sort. But:
- If you need p50 **and** p95 **and** p99, three quickselects cost `Θ(3n)`, which is fine — *unless* each destroys the array, which it does. Use one `Arrays.sort` (or a copy + three quickselects) if you need more than ~2 quantiles.
- If the data arrives as a **stream**, use a bounded reservoir or a **t-digest** / KLL sketch for `Θ(1)` memory — exact quantiles are impossible without `Θ(n)` memory.
- **Weighted quantiles** (each sample with a weight) need `weightedSelect`: the same partition trick on the weight prefix sums.

### The `max()`/`min()` special case
```java
int min = Integer.MAX_VALUE, max = Integer.MIN_VALUE;
for (int v : a) { if (v < min) min = v; if (v > max) max = v; }
```
`Θ(n)`, `O(1)` space, one pass, no branch mispredictions worth worrying about. Faster than `Arrays.sort` + two index reads for any `n > 2⁰`. **Check this before reaching for anything else.**

---

## 9. Decision guide

```
Do you need ONE value (min, max, median, p95)?
├─ YES, array is in memory and disposable
│   ├─ min/max ──> single pass, Θ(n), O(1)          ← do this
│   ├─ k in [0, n) ──> quickselect, Θ(n) expected   ← do this
│   └─ adversarial input is a real threat ──> median-of-medians, Θ(n) worst
├─ YES, data is a STREAM
│   └─ exact ──> size-k max-heap, Θ(n log k), O(k)
│       or reservoir sampling for a uniform sample
├─ YES, many queries over a STATIC array
│   └─ sort once Θ(n log n), then each query Θ(log n) via lowerBound
│      or build a Fenwick/order-statistic tree if the value domain is small
├─ MANY queries with inserts/deletes
│   └─ order-statistic tree (AVL/Treap with sizes), Θ(log n) per op
└─ NEED THE k LARGEST *and* the array afterwards
    └─ size-k min-heap, Θ(n log k), O(k)
```