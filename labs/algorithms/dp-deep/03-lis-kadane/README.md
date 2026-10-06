# 03 — LIS & Kadane

<div align="center">

**Longest Increasing Subsequence · Patience Sorting · Kadane's Maximum Subarray · Circular & Constrained Variants**

</div>

---

## Learning Objectives

- Implement the `Θ(n²)` LIS DP and then the `Θ(n log n)` patience-sorting algorithm
- Explain why the tails array is *not* an LIS and why that distinction matters
- State the O(n²) → O(n log n) improvement as a DP-to-greedy-with-binary-search transformation
- Implement Kadane's algorithm and its prefix-sum reformulation, and prove they agree
- Handle circular maximum subarray, maximum subarray with a length constraint, and maximum-sum circular subarray
- Recognise the general "maximum run satisfying a predicate" family: LIS, max subarray, max increasing path in a grid, max rectangle

## Prerequisites

- `01-dp-classics` — the DP framework
- `05-binary-search-variants` — `lowerBound` on an array of tails
- Recurrence relation, prefix sums

## Estimated Time

- **Theory**: 90 minutes
- **Practice**: 140 minutes
- **Exercises**: 75 minutes
- **Total**: 5–6 hours

## Key Concepts

| Concept | Description |
|---------|-------------|
| Subsequence | Order-preserving, gaps allowed |
| **Strictly** increasing | `a[j] < a[i]` — using `≤` changes the algorithm's meaning entirely |
| `dp[i]` | length of the LIS **ending at index `i`** |
| `tails[k]` | smallest possible tail value of an increasing subsequence of length `k+1` seen so far |
| `lowerBound(tails, x)` | first `k` with `tails[k] >= x` — the insertion point |
| Kadane | `dp[i] = max(a[i], dp[i-1] + a[i])` |
| Prefix sums | `max over (i,j)` of `P[j] − P[i]`; Kadane = the `Θ(n)` version |
| Negative-default trap | `bestSoFar` initialised to `0` returns `0` for all-negative input |
| Circular variant | `max(normal, total − minSubarray)` |
| Length-constrained | add a state `dp[len][i]` or use a monotonic deque |
| Grid LIS | longest increasing path, `Θ(mn log n)` via per-row `lowerBound` |

## Complexity Snapshot

| Problem | Naive | DP | Optimised | Space |
|---------|-------|-----|-----------|-------|
| LIS (length + one seq) | `O(n 2ⁿ)` | **`Θ(n²)`** | **`Θ(n log n)`** patience | `Θ(n)` |
| LIS (all sequences) | — | `Θ(n²)` | `Θ((n+r) log n)` | output-sized |
| LIS (count of LIS) | — | `Θ(n²)` | `Θ(n log n)` with BIT | `Θ(n)` |
| Longest **decreasing** subsequence | — | same | same algorithm, reversed comparison | `Θ(n)` |
| Max sum **contiguous** subarray | `Θ(n²)` | `Θ(n)` Kadane | `Θ(n)` | `O(1)` |
| Max sum circular subarray | — | `Θ(n)` | `total − minSubarray` | `O(1)` |
| Max sum subarray with `≤ k` elements | `O(nk)` | `O(nk)` | `Θ(n)` monotonic deque | `O(k)` |
| Max sum subarray with **exactly** `k` | `O(nk)` | `O(nk)` | `Θ(n)` with prefix sums + deque | `O(k)` |
| Longest increasing path in a grid | `O(mn²)` | `Θ(mn log n)` | patience per row | `Θ(n)` |
| Max sum **increasing** subseq | — | `Θ(n log n)` | prefix-sum BIT | `Θ(n)` |

## Algorithms Covered

### The `Θ(n²)` LIS DP
```
dp[i] = 1 + max { dp[j] : j < i and a[j] < a[i] },  max over ∅ = 0
answer = max_i dp[i]
```
Note the state is the LIS **ending at `i`**, not "in the prefix". That distinction matters for reconstruction and for the Fenwick-tree variant.

### Patience sorting / `Θ(n log n)` LIS
```java
int[] tails = new int[n];
int k = 0;
for (int x : a) {
    int p = lowerBound(tails, 0, k, x);   // FIRST position with tails[p] >= x
    tails[p] = x;
    if (p == k) k++;
}
return k;   // the answer
```

**`tails` is not an LIS.** `tails[k]` is the smallest tail of *some* increasing subsequence of length `k+1`. The array `tails` itself may not be increasing in the value sense you expect — it *is* increasing in the index sense (tails is a sorted array) but the values come from different positions in `a`. This is the #1 misconception.

**Reconstruction** needs a `prev[]` array plus the `p` recorded at each insertion.

**Why `lowerBound` (strictly increasing LIS) and not `upperBound`:** using `upperBound` computes the longest **non-decreasing** subsequence. Both are correct; they answer different questions. `tails` stays sorted under either, which is the invariant that makes the binary search valid.

### Kadane's maximum subarray
```java
int best = a[0], cur = a[0];
for (int i = 1; i < a.length; i++) {
    cur = Math.max(a[i], cur + a[i]);   // extend or restart
    best = Math.max(best, cur);
}
```
**The three-state version**, which is what you should actually write (see `CODE_DEEP_DIVE`):
```java
long total = 0, best = Long.MIN_VALUE, cur = 0;
for (int x : a) { total += x; cur = Math.max(x, cur + x); best = Math.max(best, cur); }
```

### Prefix-sum equivalence
```
max sum of a[i..j]  =  max_j ( P[j+1] − P[i] )  =  max_j P[j+1] − min_{i ≤ j} P[i]
```
The second form is "max prefix sum minus min prefix sum before it", which is exactly what Kadane computes incrementally. **Two derivations of the same algorithm — a good sanity check.**

### Circular maximum subarray
```
answer = max( maxNormalSubarray,  totalSum − minNormalSubarray )
```
**Why:** a circular subarray either does **not** wrap (it is a normal subarray) or **does** wrap, and a wrapping one is the complement of a normal subarray in the array. So `total − (minimum-sum subarray)`. **Edge case:** if the answer from the second term is `0` and every element is negative, the correct answer is `max(a)`, not `0` (the "wrap" would be the whole array, which is invalid).

## Files

| File | Purpose |
|------|---------|
| `src/main/java/com/alglab/lis/` | LIS variants, Kadane variants |
| `src/test/java/com/alglab/lis/` | Cross-validation vs `Θ(n²)` and brute force |
| `SOLUTION/` | Worked solutions |
| `TESTS/` | All-negative, all-equal, strictly-decreasing, `k=0`/`k=n` |
| `BENCHMARK/` | `n²` vs `n log n` crossover, Kadane vs prefix sums |
| `MINI_PROJECT/` | Patience-sorting visualiser (the classic card tableau) |
| `REAL_WORLD_PROJECT/` | Rolling-window anomaly detector / time-series p99 |
| `CHALLENGE/` | LIS with constraints, all-LIS enumeration, LIS in a matrix |
| `DIAGRAMS/` | Tails-array evolution, Kadane state machine |