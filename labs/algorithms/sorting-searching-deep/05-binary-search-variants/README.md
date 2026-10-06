# 05 — Binary Search Variants

<div align="center">

**Lower/Upper Bound · Binary Search on the Answer · Exponential Search · Rotated Arrays · Binary Search on a Monotone Predicate**

</div>

---

## Learning Objectives

- Master the two-loop (`lowerBound`/`upperBound`) formulation and never write an off-by-one binary search again
- Identify the four preconditions for the textbook `while (lo <= hi)` form and know when each breaks
- Implement binary search on the answer: `Θ(log(range) · log n)` instead of `Θ(n)`
- Implement exponential (galloping) search as a doubling pre-phase for O(log n) position finding
- Solve the rotated-sorted-array search in `Θ(log n)` and prove the invariant
- Search over a **monotone predicate** (not a sorted array) — the most general and most useful form
- Diagnose integer overflow in `mid = lo + (hi - lo) / 2` and `lo + hi`
- Know when `Arrays.binarySearch` differs from your hand-rolled version (duplicate handling, key range)

## Prerequisites

- `02-divide-conquer-sorts` for the `a=1, b=2` recurrence
- Monotonicity (a function that never reverses direction)
- Java overflow rules for `int`/`long` arithmetic

## Estimated Time

- **Theory**: 75 minutes
- **Practice**: 120 minutes
- **Exercises**: 60 minutes
- **Total**: 4–5 hours

## Key Concepts

| Concept | Description |
|---------|-------------|
| Monotone predicate | A `boolean f(x)` with an interval where it is false followed by an interval where it is true |
| `lowerBound` | Smallest `i` with `a[i] >= key`, else `n` |
| `upperBound` | Smallest `i` with `a[i] > key`, else `n` |
| Search space | The interval `[lo, hi]` of *candidate* positions or *candidate answer values* |
| Invariant | The answer lies in `[lo, hi]`, maintained by every iteration |
| Halving | Each iteration must discard ≥ 1/2 of the remaining space — the only correctness + complexity argument that matters |
| Galloping / exponential search | Find an upper bound on the distance by doubling, then binary search inside |
| Binary search on the answer | When the decision "is `x` feasible?" is monotone, binary search the *value* `x` |
| Sentinel | An artificial element at `hi = n` that makes the loop condition uniform |
| Rotated array | Two ascending runs; invariant becomes "the subarray containing `key` is sorted" |

## Complexity Snapshot

| Variant | Time | Space | Precondition |
|---------|------|-------|--------------|
| Textbook `while (lo <= hi)` | `Θ(log n)` | O(1) | sorted ascending array |
| `lowerBound` / `upperBound` half-open | `Θ(log n)` | O(1) | sorted array; handles all duplicates uniformly |
| Binary search on the answer | `Θ(log(range) · cost(f))` | O(1) | `f` monotone |
| Exponential (galloping) search | `Θ(log k)` where `k` = distance | O(1) | sorted array, small answer likely |
| Rotated sorted search | `Θ(log n)` | O(1) | one rotation of a sorted array |
| Binary search on monotone predicate | `Θ(log(range))` | O(1) | `f` monotone in the *parameter* |
| `Arrays.binarySearch` | `Θ(log n)` | O(1) | sorted; **unspecified result among duplicates** |

## Algorithms Covered

### The Two-Loop Formulation (the only one you should memorise)
```java
int lowerBound(int[] a, int key) {
    int lo = 0, hi = a.length;              // hi is EXCLUSIVE: [lo, hi)
    while (lo < hi) {                        // <, not <=
        int mid = lo + ((hi - lo) >>> 1);    // overflow-safe
        if (a[mid] < key) lo = mid + 1;      // a[mid] cannot be the answer -> skip it
        else hi = mid;                       // a[mid] may be the answer -> keep it
    }
    return lo;                               // lo == hi, answer or n
}
```
**Why this is the canonical form:**
1. `hi = n` means there is no need for a sentinel or an "array out of bounds" branch.
2. `lo < hi` means the loop always makes progress (`mid ∈ [lo, hi-1]`, so `lo = mid+1` or `hi = mid` both shrink).
3. `lo == hi` on exit is the answer, guaranteed to be in `[0, n]`.
4. `lo < hi + 1` ⟹ `hi - lo > 0` ⟹ `hi - lo ≥ 1`, so the space shrinks by at least half each time ⇒ **`⌈log₂(n+1)⌉` iterations exactly**.

`upperBound` is identical with `a[mid] <= key` instead of `<`.

### Textbook Form — and its four failure modes
```java
int find(int[] a, int key) {
    int lo = 0, hi = a.length - 1;           // [lo, hi] INCLUSIVE
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;         // overflow-safe
        if (a[mid] == key) return mid;
        if (a[mid] < key) lo = mid + 1; else hi = mid - 1;
    }
    return -1;                                // -1 means "absent"
}
```
Fails when you need: (1) the *insertion point* rather than an exact match, (2) all occurrences of a duplicate key, (3) a monotone predicate rather than an equality test, (4) an answer that is not an element of the array. That is 4 out of 4 real use cases — use `lowerBound`.

### Binary Search on the Answer
Whenever `f(x)` is monotone in `x`, the answer is a *value*, not an index.
```
lo = min feasible-or-infeasible value, hi = max feasible-or-infeasible value
while lo < hi:
    mid = lo + (hi - lo + 1) / 2              // note the +1: bias upward so lo=hi terminates
    if feasible(mid) lo = mid                  // try larger
    else hi = mid - 1
return lo
```
Applications: minimum capacity, smallest `k` satisfying a constraint, latest deadline, `max min` river width, aggressive cows. The **invariant** is "the answer lies in `[lo, hi]`", and the `+1` in the midpoint is what guarantees progress when `hi = lo + 1`.

### Exponential (Galloping) Search
```
int i = 0;
while (i < n && a[i] < key) i = 2*i + 1;       // 0,1,3,7,15,... — exponential growth
// now a[i] >= key or i >= n: the answer is in ((i-1)/2, i]
binary search a[(i+1)/2 .. min(i, n-1)]
```
`Θ(log k)` for an answer at distance `k` — better than `Θ(log n)` when the answer is usually near the front. This is the right primitive for **run-length encoded data**, **sparse time series**, and **`Arrays.binarySearch` on a lazily-loaded index**.

### Rotated Sorted Array
```
lo, hi = 0, n-1
while lo <= hi:
    mid = lo + (hi-lo)/2
    if a[mid] == key return mid
    if (a[lo] <= a[mid]):        // left half is sorted
        if (a[lo] <= key && key < a[mid]) hi = mid - 1 else lo = mid + 1
    else:                        // right half is sorted
        if (a[mid] < key && key <= a[hi]) lo = mid + 1 else hi = mid - 1
return -1
```
**Invariant:** at every step, at least one half is sorted and the key (if present) is confined to exactly one half. `Θ(log n)` — you halve the search space each time regardless of the rotation.

## Files

| File | Purpose |
|------|---------|
| `src/main/java/com/alglab/binary-search/` | All variants + predicate search |
| `src/test/java/com/alglab/binary-search/` | Exhaustive small-`n` fuzz tests |
| `SOLUTION/` | Worked exercise solutions |
| `TESTS/` | Off-by-one regression suites |
| `BENCHMARK/` | Branch-misprediction and memory-latency measurements |
| `MINI_PROJECT/` | Visual trace of the search interval |
| `REAL_WORLD_PROJECT/` | Time-window rate limiter built on predicate search |
| `CHALLENGE/` | Parallel binary search, binary search on a linked list |
| `DIAGRAMS/` | Search-interval narrowing diagrams |