# Theory — Divide & Conquer Sorts

This lab is the reference treatment of the divide-and-conquer sorting pattern: **split → solve → merge**, where the combine step is linear. Merge sort makes the combine step explicit and *unconditional*; quick sort makes it a *partition* and pushes the merging burden into recursion.

---

## 1. The shape of a divide-and-conquer sort

A D&C sort has three phases:

1. **Divide** — partition the index range `[lo, hi]` into sub-ranges. Must be cheap: Θ(1) or Θ(n).
2. **Conquer** — recurse on the sub-ranges until a base case (size ≤ 1) is reached.
3. **Combine** — produce the sorted result from the solved sub-ranges. Θ(n) for merge sort, Θ(n) for the partition step of quick sort.

The interesting design question is *where the work lives*. Merge sort does Θ(n) work per level for the combine and Θ(1) work for the divide. Quick sort does Θ(n) for the partition (which is its "combine"-equivalent, though it does not merge) and Θ(1) for the divide.

---

## 2. Merge sort

### Mechanism

```
mergeSort(a, lo, hi):
    if hi - lo + 1 <= 1: return              // base case: 0 or 1 elements is sorted
    mid = lo + (hi - lo) / 2                 // careful: (lo+hi)/2 overflows for huge n
    mergeSort(a, lo, mid)
    mergeSort(a, mid + 1, hi)
    merge(a, lo, mid, hi)
```

### The merge step and its invariant

**Precondition:** `a[lo..mid]` and `a[mid+1..hi]` are each sorted.
**Postcondition:** `a[lo..hi]` is sorted and holds exactly the multiset of the input elements.

The loop invariant, precisely stated:

> **I1.** At the start of each iteration, `a[lo..lo+i-1]` holds the `i` smallest elements of the union of the two runs, in sorted order.
> **I2.** `i ≤ (mid - lo + 1)` and `j ≤ (hi - mid)`, where `i`, `j` are the read cursors into the two runs.
> **I3.** Every element not yet copied is in `a[lo+i..mid]` or `a[mid+1+j..hi]`, and each remaining range is still sorted.

The loop pops the smaller head: if `a[lo+i] <= a[mid+1+j]` take from the left, else from the right. Correctness of the loop follows by induction on the number of remaining elements. Termination: exactly `(mid - lo + 1) + (hi - mid) = hi - lo + 1` elements are written.

```java
// Non-destructive merge: copies from a[] into aux[], never from aux[] into a[].
// The "one-way data flow" rule is what makes this version stable.
for (int k = lo; k <= hi; k++) {
    if (i > mid)                     aux[k] = a[j++];
    else if (j > hi)                 aux[k] = a[i++];
    else if (a[i] <= a[j])           aux[k] = a[i++];   // <= preserves stability
    else                             aux[k] = a[j++];
}
for (int k = lo; k <= hi; k++) a[k] = aux[k];
```

### Stability — the one-character rule

The merge must use `<=` (take from the left run on ties). With `<`, equal elements from the right run are written first and stability is destroyed. This is the single most common merge-sort bug in the world.

### Complexity proof sketch

Recurrence with the auxiliary pass counted:

- Divide: Θ(1) (`mid` computation).
- Recurse: `2T(n/2)`.
- Merge: Θ(n) — `hi - lo + 1` writes plus the two-copy pass, and every element is examined at least once and copied exactly once.

So `T(n) = 2T(n/2) + Θ(n)`, `T(1) = Θ(1)`.

**Master theorem** with `a = 2, b = 2, f(n) = n`:
- `n^(log_b a) = n^1 = n`.
- `f(n) = Θ(n) = Θ(n^(log_b a))` → **Case 2**.
- Hence `T(n) = Θ(n log n)`, and the work at every recursion level is Θ(n) summed over `log₂ n` levels.

The recurrence tree has `log₂ n` levels with a total of `Θ(n)` work at each level, hence `Θ(n log n)`. This bound holds for **all** inputs — no best/average/worst distinction, because the split is always exact and the merge is always linear. That is merge sort's defining property and also its weakness: it cannot exploit existing order.

### The natural-run optimisation

Before merging, test `if (a[mid] <= a[mid + 1]) return;`. If it holds, the two sorted runs are already in global order, so the whole range is sorted and the Θ(n) copy is unnecessary. On presorted input this reduces the whole sort to Θ(n log n) comparisons with Θ(n) writes; on random input it fires at the leaves.

### The "natural merge sort" version

Scan for maximal ascending runs iteratively, push them onto a stack, merge adjacent runs (like a min-heap of runs, e.g. balanced merging). This is TimSort's ancestor; it is Θ(n) on presorted input and Θ(n log n) on random input, and it is *stable*. See `01-comparison-sorts` for what the JDK does.

### Space

- Top-down array merge sort: Θ(n) auxiliary (the `aux` array), plus Θ(log n) stack.
- Bottom-up merge sort: Θ(n) auxiliary, but only `O(1)` stack — better for recursion-limited or iterative contexts.
- **Intrusive** merge sort on a doubly linked list: **O(1) auxiliary**. The "array" is the list itself; merging relinks `next` pointers in Θ(n) and recurses to the top of a Θ(n)-deep list → so use **bottom-up** to keep stack O(1). Total Θ(n log n) time, stable, O(1) space.

### The overflow trap

`mid = (lo + hi) / 2` overflows for `lo + hi > Integer.MAX_VALUE`. On arrays this cannot happen (`n` bounded by the JVM), but it *does* happen in index-arithmetic utilities, external sorts, and string split points. Use `lo + (hi - lo) / 2`.

---

## 3. Quick sort

### Mechanism

```
quickSort(a, lo, hi):
    if hi - lo + 1 <= 1: return
    p = partition(a, lo, hi)
    quickSort(a, lo, p - 1)
    quickSort(a, p + 1, hi)
```

### Partition invariant (Lomuto)

With pivot `v = a[hi]`, after `partition` returns index `p`:

> **I1.** `a[k] <= v` for all `k ∈ [lo, p]`.
> **I2.** `a[k] >= v` for all `k ∈ [p+1, hi]`.
> **I3.** `a[p] == v`.
> **I4.** `partition` is a *permutation*: the multiset of `a[lo..hi]` is unchanged.

The loop invariant during the scan is the standard "boundary index" `i`: `a[lo..i-1]` is all `≤ v`, `a[i..j-1]` is all `> v`, and `a[j..hi-1]` is unscanned. Incrementing `i` on `a[i] <= v` and swapping into place on `a[i] > v` maintains it. At the end, swapping `a[i]` with `a[hi]` finalises the pivot.

Note **I2 says `>=` not `>`** — Lomuto with the last element as pivot can leave equal elements on the right side. This is exactly why naive quick sort degrades to Θ(n²) on all-equal input: each partition splits `n` into `0` and `n-1`.

### Complexity

Recurrence: `T(n) = T(k) + T(n-k-1) + Θ(n)` where `k` is the number of elements sent left.

- **Best** (perfect balance, `k ≈ n/2`): `2T(n/2) + Θ(n)` → Case 2 → `Θ(n log n)`.
- **Worst** (`k = 0` every time, e.g. presorted input with last-element pivot): `T(n-1) + Θ(n)` → `Θ(n²)`.
- **Average** under the random-permutation model: `Θ(n log n)`. Proof sketch: the expected cost satisfies `E[T(n)] = (2/n)Σ_{k=0}^{n-1} E[T(k)] + cn`, and by a substitution/`Θ(n log n)` guess with a standard induction bound one obtains `E[T(n)] < 1.39 n log₂ n` for the randomised variant.

### Randomised pivot — the Θ(n log n) expected bound

Replace the pivot choice with `uniform random index in [lo, hi]`. The expected depth of any element is `Θ(log n)`:

Let `D(n)` be the expected depth of a fixed element. Each time it becomes a pivot (or the pivot lands on either side of it), one level is consumed. Since the pivot position is uniform, `E[T(n)] = (2/n) Σ E[T(k)] + cn` and the standard solution is `E[T(n)] ≤ c' n ln n` for a universal `c' ≈ 1.386·(2/ln 2)` factor. Concretely: **randomised quick sort runs in Θ(n log n) expected time with probability ≥ 1 - 1/n of running in O(n log n)**.

Crucially, randomising the pivot makes *every* fixed input safe — including a pre-computed adversarial input. Median-of-3 does **not** have this property: an adversary who knows the median-of-3 rule can still build an input that yields Θ(n²) comparisons. This is the difference between a *probabilistic* and a *heuristic* guarantee, and it is the single most important argument in sorting.

### Hoare partition

```java
static int partitionHoare(int[] a, int lo, int hi) {
    int pivot = a[lo + (hi - lo) / 2];
    int i = lo, j = hi;
    while (i <= j) {
        while (a[i] < pivot) i++;     // bounds are guaranteed by sentinels in the classic form
        while (a[j] > pivot) j--;
        if (i <= j) { swap(a, i, j); i++; j--; }
    }
    return j;                          // pivot lies in (lo, j] .. [j+1, hi]
}
```

- Roughly **3× fewer swaps** than Lomuto on random data (each swap fixes two elements at once).
- Must guard the inner `while`s against running off the array unless you place sentinels (`a[0] = MAX`, `a[n+1] = MIN`).
- Returns `j`, and the correct recursion is `quickSort(lo, j)` and `quickSort(j+1, hi)` — **not** `lo..j-1` / `j+1..hi`. Getting this wrong is the classic Hoare bug and it silently drops or double-counts the pivot.
- **Unstable**: the pivot can travel far, crossing equal elements.

### 3-Way partition (Dutch National Flag)

```java
int lt = lo, gt = hi, i = lo;          // invariant: a[lo..lt-1] < v, a[lt..gt] == v, a[gt+1..hi] > v
while (i <= gt) {
    int c = Integer.compare(a[i], v);
    if (c < 0) swap(a, lt++, i++);
    else if (c > 0) swap(a, i, gt--);      // i is NOT advanced: the swapped-in element is unexamined
    else i++;
}
// recurse on [lo, lt-1] and [gt+1, hi]; the [lt, gt] block is already final
```

**The forgotten increment** is the whole bug surface of 3-way quicksort. When you swap with `gt--`, the element arriving at `i` has not been examined, so `i` must stay.

**Complexity:** with `d` distinct values, 3-way quicksort performs `Θ(n log d)` comparisons in expectation. For all-equal input it is a single Θ(n) pass instead of Θ(n²). For `d = n` it matches ordinary quicksort. So 3-way quicksort is *always at least as good* — the only cost is a third of the bookkeeping and slightly worse constants when all values are distinct.

### Stability

Quick sort is fundamentally **unstable** because partitioning moves elements across each other. A stable quick sort exists (block-based, or merge-sort-style "index array" trick: sort an `int[]` of indices and indirect through a comparator) but costs Θ(n) extra space and more cache misses, so it is never used. **Rule: if you need stability, use merge sort or TimSort.**

### When quick sort beats merge sort (and this is empirical, not theoretical)

Both are Θ(n log n). Quick sort wins in practice because:

1. **Cache locality** — in-place partitioning touches memory sequentially; merge sort streams from one buffer to another and back, doubling memory traffic.
2. **Lower constant factor** — fewer writes (merge sort writes each element twice: `a → aux → a`).
3. **No allocation** — merge sort's Θ(n) buffer costs page faults / GC pressure for large arrays.

Merge sort wins when: stability matters, external/disk sorting (sequential I/O, no random access penalty), linked lists, or when you want a **guaranteed** worst case.

---

## 4. Bottom-up merge sort

```java
for (int width = 1; width < n; width *= 2)
    for (int lo = 0; lo + width < n; lo += 2 * width)
        merge(a, aux, lo, lo + width - 1, Math.min(lo + 2 * width - 1, n - 1));
```

**Why prefer it:**
- **O(1) call stack** — safe for `n` up to 2³¹ where recursion would overflow.
- **Cache-friendlier in a specific sense** — the merge width doubles, so early passes work entirely in L1/L2.
- **Fits external merge sort** — the pass structure maps directly onto "merge run files of length 1, then 2, then 4, ...".
- **Predictable timing** — no recursion overhead; useful for hard real-time budgets.

Disadvantage: cannot exploit presortedness as cleanly as natural merge sort, and it always writes the full Θ(n) per level.

---

## 5. Summary table of mechanisms

| Algorithm | Divide | Combine | Consequence |
|-----------|--------|---------|-------------|
| Merge sort | index midpoint, Θ(1) | merge two sorted runs, Θ(n) | Θ(n) extra space, stable, guaranteed Θ(n log n) |
| Quick sort (Lomuto) | pivot value, Θ(n) | partition, Θ(n) | Θ(n²) worst, unstable, no extra space |
| Quick sort (Hoare) | pivot value | bidirectional partition | fewer swaps, fiddly recursion bounds |
| 3-way quick sort | pivot value | `<`/`=`/`>` partition | Θ(n log d), immune to duplicates |
| Bottom-up merge | fixed widths | merge runs | O(1) stack |
| Intrusive merge | list midpoint | relink pointers | O(1) space, stable, must be bottom-up |