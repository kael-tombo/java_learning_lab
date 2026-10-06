# 06 — Order Statistics

<div align="center">

**Quickselect · Median of Medians · Fenwick k-th · Parallel Selection · Streaming Top-K**

</div>

---

## Learning Objectives

- Implement quickselect and understand why it is `Θ(n)` expected but `Θ(n²)` worst case
- Prove the median-of-medians pivot gives `Θ(n)` **worst-case** selection
- Compute the exact constant factors for median-of-medians (about 3.38 n comparisons)
- Implement `k`-th order statistic with a Fenwick tree / Binary Indexed Tree in `Θ(log n)`
- Implement selection over a stream without buffering it
- Distinguish: select (one value, array destroyed) vs top-k (k values, array preserved)
- Understand when `nth_element` in the JDK is the right answer and when it is not

## Prerequisites

- Quicksort partition from `02-divide-conquer-sorts`
- Probabilistic analysis (expected vs worst case)
- `05-binary-search-variants` for the `O(log n)` k-th lookup

## Estimated Time

- **Theory**: 80 minutes
- **Practice**: 130 minutes
- **Exercises**: 75 minutes
- **Total**: 5 hours

## Key Concepts

| Concept | Description |
|---------|-------------|
| Order statistic | The `k`-th smallest element of a multiset |
| Selection | Finding the `k`-th smallest; **the array is partitioned, not sorted** |
| Ranking / selection | `Θ(n)` expected; no need for the full `Θ(n log n)` ordering |
| Quickselect | Partition around a pivot, then recurse into one side only |
| Expected vs worst | Random pivot ⇒ `Θ(n)` expected; adversarial pivot ⇒ `Θ(n²)` |
| Median of medians | Deterministic `Θ(n)` pivot selection — the only deterministic linear-time selection |
| Discard factor | The fraction of elements provably discarded each iteration; needs to be > 1/3 for linear time |
| Interpolation | Estimate the pivot from the value distribution — `Θ(n)` on uniform data, `Θ(n²)` on adversarial |
| Order-statistic tree | Balanced BST with subtree sizes ⇒ `k`-th in `Θ(log n)`; also `rank`, `select`, `delete` |
| Fenwick k-th | Binary lifting on a prefix-sum array ⇒ `k`-th in `Θ(log n)`, memory `O(n)` |
| Top-k | Return `k` elements; often `Θ(n log k)` with a bounded heap, `Θ(n)` if the input is destructible |
| Streaming selection | Bounded-memory: reservoir sampling, or a size-`k` min/max-heap |

## Complexity Snapshot

| Algorithm | Best | Expected | Worst | Space | Input preserved? |
|-----------|------|----------|-------|-------|------------------|
| Full sort + index | `Θ(n log n)` | `Θ(n log n)` | `Θ(n log n)` | `Θ(n)` | Yes |
| Quickselect (random pivot) | `Θ(n)` | **`Θ(n)`** | `Θ(n²)` | `O(log n)` stack | **No** (partitioned) |
| Quickselect (median-of-medians) | `Θ(n)` | **`Θ(n)`** | **`Θ(n)`** | `O(log n)` stack | **No** |
| Interpolation select | `Θ(n)` | `Θ(n)` uniform | `Θ(n²)` | `O(1)` | **No** |
| Parallel quickselect | — | `Θ(n)` | `Θ(n²)` | `O(log n/p)` | **No** |
| Fenwick tree k-th | — | `Θ(log n)` | `Θ(log n)` | `Θ(n)` | Yes (built once, many queries) |
| Order-statistic tree | — | `Θ(log n)` | `Θ(log n)` | `Θ(n)` | Yes (dynamic insert/delete) |
| Min-heap of size `k` (streaming) | — | `Θ(n log k)` | `Θ(n log k)` | `O(k)` | Yes |
| `Arrays`/`nth_element` | `Θ(n)` | `Θ(n)` | — | `O(1)` | **No** |
| `PriorityQueue.nsmallest` | — | `Θ(n log k)` | `Θ(n log k)` | `O(k)` | Yes |

## Algorithms Covered

### Quickselect
```
select(a, k):                        // k = target RANK (0-based)
    lo, hi = 0, n-1
    while lo < hi:
        p = randomPartition(a, lo, hi)
        if p == k: return a[p]
        else if p < k: lo = p + 1
        else: hi = p - 1
```
**Why linear.** After the first partition the pivot is in its final position, so exactly one side recurs. If the split is `α n` / `(1−α)n`, the recurrence is `T(n) = T(αn) + Θ(n)`, giving `Θ(n/(1−α))` — linear for any fixed `α`. It is **the worst case that makes it look quadratic**, not the average.

### Median of Medians (deterministic linear time)
1. Sort each group of 5 (`Θ(n)` total).
2. Collect the `⌈n/5⌉` medians; recurse to find the median *of the medians* — a genuine selection problem on `n/5` elements.
3. That pivot is guaranteed to have at least `3n/10` elements on each side (the discarded groups contribute 3 that are smaller and 3 larger, plus `n/5 / 2` medians from each side of the median-of-medians).
4. Discard that side and recurse. `T(n) = T(n/5) + T(7n/10) + Θ(n) = Θ(n)`.

**Constant factor: about 3.38 n comparisons** (vs `1.39 n log n ≈ 20n` for quicksort at `n = 10⁶`). So median-of-medians is asymptotically better and **practically 6× worse**. It exists for theory, move-to-front heuristics, and worst-case guarantees — not for speed.

### Fenwick tree k-th
A Fenwick tree stores `tree[i] = sum of a[i - lowbit(i) + 1 .. i]`. The `k`-th smallest is found by **binary lifting**: start at the highest power of two `≤ n`, and walk down, testing whether `k > tree[next]`; if so, subtract and move on. `Θ(log n)`, no separate binary search.

### Streaming top-k
```
heap of size k (max-heap for k smallest)
for each element x:
    if heap.size() < k: heap.push(x)
    else if x < heap.peek(): heap.pop(); heap.push(x)
```
`Θ(n log k)` time, `O(k)` memory, **no buffering of the input**. This is the only option when the source is a stream, a socket, or a query result you cannot hold in memory.

## Files

| File | Purpose |
|------|---------|
| `src/main/java/com/alglab/order-stats/` | Quickselect, median-of-medians, Fenwick, streaming top-k |
| `src/test/java/com/alglab/order-stats/` | Property tests: `result == sorted[k]` |
| `SOLUTION/` | Worked solutions |
| `TESTS/` | Adversarial-pivot suites |
| `BENCHMARK/` | Selection vs sorting vs heap vs parallel |
| `MINI_PROJECT/` | Order-statistic visualiser |
| `REAL_WORLD_PROJECT/` | p50/p95/p99 latency tracker with bounded memory |
| `CHALLENGE/` | Parallel selection, distributed k-th, `WeightedQuantile` |
| `DIAGRAMS/` | Partition narrowing traces |