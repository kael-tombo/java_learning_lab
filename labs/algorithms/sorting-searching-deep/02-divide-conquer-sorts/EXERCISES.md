# Exercises — Divide & Conquer Sorts

Implement in Java, trace by hand, then attack the edge cases. Java 21, package `com.alglab.dc`. Solutions → `SOLUTION/`, tests → `TESTS/`.

---

## Exercise 1 — Bottom-up merge sort

Implement `static void mergeSort(int[] a)` with an iterative bottom-up driver: merge runs of width 1, then 2, then 4, ... using one auxiliary array allocated once.

**Trace** on `[5, 2, 4, 6, 1, 3]` (widths in order):

| width | merges performed |
|-------|------------------|
| 1 | (5,2)→[2,5], (4,6)→[4,6], (1,3)→[1,3] |
| 2 | [2,5]+[4,6]→[2,4,5,6]; [1,3] + tail → unchanged |
| 4 | [2,4,5,6]+[1,3]→[1,2,3,4,5,6] |

**Edge cases:**
- `n = 0` → the outer loop never runs; the method must not touch `aux[0]`.
- `n = 1` → `width=1`, `lo + width = 1 < 1` is false → no merges. Correct.
- `n = 5`, widths 1,2,4 — the width-4 merge has an empty right run for the last group. **Bug to avoid:** `Math.min(lo + 2*width, n) - 1` can produce `lo + width - 1`, i.e. `mid >= hi`. Guard with `if (mid < hi)`.
- All elements equal → every merge compares equal pairs; must use `<=` or you silently break stability (test with index-tagged records).

---

## Exercise 2 — Merge sort on an intrusive list

Implement `static Node mergeSort(Node head)` for a singly linked list where `Node` has `int value` and `Node next`. Return the new head.

**Requirements:** O(1) *auxiliary* space (no arrays, no node copying). Use the slow/fast pointer to find the midpoint.

**Trace** `[5]→[2]→[4]→[1]→[3]`:
1. `slow=head(5)`, `fast=head(5)`. `fast.next.next` = 4 → move: `slow=2, fast=4`.
2. Split: left = `[5,2]`, right = `[4,1,3]`.
3. `mergeSort([5,2])` → `[2,5]`. `mergeSort([4,1,3])` → `[1,3,4]`.
4. Merge: `[1,3,4,5,2]`→`[1,2,3,4,5]`.

**Edge cases:** empty list (`head == null`) → return `null`; single node → return it; a list that is already sorted must return the *same* node objects in the *same* order (proves stability).

**Trap:** recursion depth is Θ(n) on a list, so a 100k-element list overflows the stack. Use **bottom-up** merging of lists (maintain a queue of runs) if `n` is unbounded.

---

## Exercise 3 — Stability test harness

Write `boolean isStableMergeSort(int[] values)` by packing `(value << 20) | index` into a `long`, sorting with each algorithm, and checking the index field is ascending within each equal-value run.

Generate 2000 random arrays of length 50 with values from `{0..4}` (ties everywhere). Assert:
- merge sort (`<=`) → stable ✓
- merge sort (`<`) → unstable ✗ (find a minimal witness by exhaustive search over all arrays of length ≤ 5)
- quick sort (Lomuto) → unstable ✗

---

## Exercise 4 — Lomuto partition, instrumented

```java
/** Returns the final pivot index; count comparisons and swaps via out-params. */
static int partition(int[] a, int lo, int hi, int[] counters) {
    int v = a[hi], i = lo;
    for (int j = lo; j < hi; j++) {
        counters[0]++;
        if (a[j] <= v) { swap(a, i, j); counters[1]++; i++; }
    }
    swap(a, i, hi); counters[1]++;
    return i;
}
```

**Trace** `[3, 1, 4, 1, 5, 9, 2, 6]` with pivot `a[7]=6`:

| j | a[j] | action | array after |
|---|------|--------|-------------|
| 0 | 3 | swap(0,0) | 3 1 4 1 5 9 2 6 |
| 1 | 1 | swap(1,1) | 3 1 4 1 5 9 2 6 |
| 2 | 4 | swap(2,2) | 3 1 4 1 5 9 2 6 |
| 3 | 1 | swap(1,3) | 3 1 4 1 5 9 2 6 → **3 1 1 4 5 9 2 6** |
| 4 | 5 | swap(2,4) | 3 1 5 4 1 9 2 6 |
| 5 | 9 | — (>6) | 3 1 5 4 1 9 2 6 |
| 6 | 2 | swap(2,6) | 3 1 2 4 1 9 5 6 |
| — | — | swap(2,7) | 3 1 2 4 1 9 5 6 → pivot lands at index 2 |

Result: 8 comparisons, 7 swaps. Note the equal `1`s at indices 1 and 3 were **not** separated by the pivot — they can end up on either side.

**Edge cases:** `lo == hi` → returns `lo`; `hi = lo+1` → 2 comparisons, ≤ 1 swap.

---

## Exercise 5 — Hoare partition correctness

Implement Hoare partition and quick sort using it. Then prove by test that the returned `j` satisfies `lo <= j < hi` always, and that recursion `quickSort(lo, j); quickSort(j + 1, hi);` terminates.

**Deliberate bug to introduce, then fix:** use recursion `quickSort(lo, j-1); quickSort(j+1, hi)`. On what input does it drop elements or loop forever? (Try `[5, 5, 5, 5]`.)

**Compare** swap counts on 100k random ints: Hoare ≈ 0.39 n log n, Lomuto ≈ 1.20 n log n. Record both.

---

## Exercise 6 — 3-way quicksort and the duplicate-value curve

Implement `quickSort3Way(int[] a, int lo, int hi, Random rnd)`. Then measure comparison counts for `n = 10⁵` with `d = 2, 10, 100, 1000, 10⁴, 10⁵` distinct values:

| d | expected Θ(n log d) factor |
|---|---------------------------|
| 2 | ~n |
| 10 | ~3.3 n |
| 100 | ~6.6 n |
| 10⁵ | ~16.6 n |

Compare against naive Lomuto quick sort on the same data — with `d = 2` it is **Θ(n²)**. This single table is the strongest justification for 3-way partitioning in real workloads (log lines with a small level field, country codes, booleans, small enums).

**Trace** `[5, 5, 5, 1, 5, 5]` with pivot `v = a[0] = 5`:
- i=0: `5 == 5` → i=1
- i=1..3: equal → i grows
- i=4: `5 == 5` → i=5
- i=5: equal → i=6 > gt=5, exit.
Result: `lt=0, gt=5`, whole array is `== v`, **zero** recursion. One pass.

---

## Exercise 7 — Randomised pivot: empirical worst case

Implement quick sort with (a) last-element pivot, (b) median-of-3, (c) uniform random pivot. Feed each the *same* pre-computed adversarial input: build an array recursively so that the last element is always the minimum, then the second-minimum, and so on.

**Predict:** (a) explodes to ~n²/2 comparisons; (b) also explodes because the adversary knows the rule; (c) stays at ~1.39 n log₂ n. Verify with n = 20 000 (expect (a) ≈ 2×10⁸ comparisons — several seconds).

Then **re-run the adversary's input against `Arrays.sort`**: TimSort detects the runs and finishes in O(n log n) or better. Write up which guarantee you would defend in a code review and why.

---

## Exercise 8 — Parallel merge sort

Use `java.util.concurrent.ForkJoinPool` + `RecursiveAction`:

```java
class ParSort extends RecursiveAction {
    final int[] a, aux; final int lo, hi;
    protected void compute() {
        if (hi - lo < THRESHOLD) { Arrays.sort(a, lo, hi); return; }
        int mid = lo + (hi - lo) / 2;
        invokeAll(new ParSort(a, aux, lo, mid), new ParSort(a, aux, mid, hi));
        merge(a, aux, lo, mid, hi);
    }
}
```

**Issue you must solve:** both children write to disjoint `aux` ranges — that is safe. But they both *read* `a`, which is fine because children only write their own ranges. Document why no synchronisation is needed.

**Measure** n = 2²⁴ on 1, 2, 4, 8 threads. Predict speedup ≈ `min(p, T1/T∞)`; Amdahl's law with 1% serial merge fraction caps speedup at 100×. Record and plot.

**Also:** why is `RecursiveAction` better than `CompletableFuture` + common pool here? (Work-stealing locality, no thread-pool starvation, `invokeAll` fork-join semantics.)

---

## Exercise 9 — Hybrid: introsort behaviour

Implement `static void sort(int[] a, int lo, int hi, int depthLimit)`:
- if size ≤ 16 → insertion sort
- else if `depthLimit == 0` → heap sort (fallback)
- else partition and recurse with `depthLimit - 1`

This is the shape of `std::sort` (introsort). Benchmark against `Arrays.sort` and against pure quick sort on adversarial input. Explain what happens to the *worst case* guarantee: recursion depth is bounded by `2·log₂ n`, so the stack is O(log n), and the heap-sort fallback caps time at O(n log n).

---

## Exercise 10 — Counting inversions via merge sort

Modify the merge step to count cross-inversions: when `a[i] > a[j]` is taken from the right run, add `(mid - i + 1)` to the answer. Trace on `[5, 2, 4, 6, 1, 3]` — answer should be **8**. Then write a brute-force O(n²) inversion counter and fuzz-test against the merge-based one on 10 000 random arrays.

**Bonus:** assert the counter is non-negative, never overflows for `n ≤ 10⁵` (`max = n(n-1)/2 = 4 999 950 000`, which **exceeds `int`** — this is a real overflow bug; use `long`).

---

## Exercise 11 — Debugging drills

Find and fix:

1. Merge with `if (a[i] < a[j])` instead of `<=` — what test catches it? (stability test)
2. `mid = (lo + hi) / 2` — fine for arrays, but breaks in `mergeSort(int[] a, int from, int to)` when called with indices near `Integer.MAX_VALUE`. Reproduce with a synthetic index-space simulator.
3. 3-way partition with `i++` after `swap(a, i, gt--)` — fails on `[5, 1, 5, 5, 5]`. Trace it.
4. Hoare partition with `return i` instead of `return j`.

---

## Exercise 12 — Deliverable

`BENCHMARK/SortShow.java`: render a text animation of merge sort and 3-way quick sort side by side on the same 60-element random array, printing the recursion depth, the pivot, and the `[lt|=|gt]` or run boundaries after each partition. Then answer in writing: for which of your 8 test distributions does quick sort's recursion depth exceed `log₂ n`, and why?