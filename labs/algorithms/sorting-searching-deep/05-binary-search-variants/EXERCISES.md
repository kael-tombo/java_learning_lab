# Exercises — Binary Search Variants

Implement in Java, trace by hand, then attack the edge cases. Java 21, package `com.alglab.binsearch`. Solutions → `SOLUTION/`, tests → `TESTS/`.

---

## Exercise 1 — Trace `lowerBound` / `upperBound`

Compute both for `a = [1, 2, 2, 2, 5, 8]` and `key = 2`.

**`lowerBound(a, 2)`** (find first `≥ 2`):

| iter | lo | hi | mid | `a[mid]` | `a[mid] < 2`? | update | new [lo,hi) |
|------|----|----|-----|----------|---------------|--------|-------------|
| 0 | 0 | 6 | 3 | 2 | no | `hi = 3` | [0, 3) |
| 1 | 0 | 3 | 1 | 2 | no | `hi = 1` | [0, 1) |
| 2 | 0 | 1 | 0 | 1 | **yes** | `lo = 1` | [1, 1) |

Return **1**. ✓ (index 0 holds `1`, which is `< 2`).

**`upperBound(a, 2)`** (find first `> 2`):

| iter | lo | hi | mid | `a[mid] <= 2`? | update |
|------|----|----|-----|----------------|--------|
| 0 | 0 | 6 | 3 | yes | `lo = 4` |
| 1 | 4 | 6 | 5 | no | `hi = 5` |
| 2 | 4 | 5 | 4 | no | `hi = 4` |

Return **4**. ✓

**Count of `2`** = `4 - 1 = 3`. ✓

Now do the same for `key = 6` (absent): `lowerBound = 4`, `upperBound = 4`, count `0`.

**Edge cases to trace:** `key` below the minimum (`lb = 0`), above the maximum (`lb = ub = n`), empty array (`lb = ub = 0`), `n = 1`.

---

## Exercise 2 — Find the off-by-one by exhaustive search

Write both the correct `lowerBound` and four buggy variants, then find the **smallest input** (over all arrays of length ≤ 6 with values in `{0,1}`) on which each disagrees with a brute-force linear implementation.

| Buggy variant | Change |
|---------------|--------|
| B1 | `else hi = mid - 1;` instead of `hi = mid` |
| B2 | `while (lo <= hi)` with `hi = a.length` and `else hi = mid - 1` |
| B3 | `mid = (lo + hi) >>> 1` (overflow version) |
| B4 | `if (a[mid] < key) hi = mid + 1; else lo = mid;` (swapped branches) |

Report for each: the smallest `(array, key)` witness and the wrong return value. **B1's witness is `([0], 0) → returns 0` instead of 0... but `([0,0,0], 0)` with `hi = mid - 1` at `lo=0` gives `hi = -1`, so `lo=0` returned, which is correct by luck.** Find the case where it is actually wrong.

---

## Exercise 3 — The generalisation to any monotone predicate

Implement `static int firstTrue(int lo, int hi, IntPredicate f)` and `static int lastTrue(int lo, int hi, IntPredicate f)`.

Then write a fuzzer that:
1. Generates a random monotone `boolean[]` of length `n` (pick a random threshold `t`, then `[false × t, true × (n-t)]`, shuffled *within* the false region and within the true region to add noise).
2. Runs `firstTrue` / `lastTrue`.
3. Compares against a linear scan.

**Expected:** `firstTrue` returns the first `true` index, or `hi + 1` if none; `lastTrue` returns the last `true`, or `lo - 1` if none.

Then use the predicate form to solve:
- **Aggressive Cows**: minimum distance `d` placing `k` stalls in stalls `0..n-1` with all pairs ≥ `d` apart. Predicate: `feasible(d)`.
- **Wood cutting**: maximum length `L` cut from `k` pieces. Predicate: `canCut(L)`.
- **K-th smallest of a rotated sorted array**: `f(v) = countLessOrEqual(v) >= k`.

Report the number of `feasible` evaluations for each and the resulting complexity.

---

## Exercise 4 — Binary search on the answer: min speed

You have `double times[]` where `times[i]` is your time to finish a race if you run at `times[i]` units of speed, and `times` is **strictly increasing** (faster = later index). Write:

```java
static double minSpeed(double[] times, double limit) {
    return times[minFeasible(times.length - 1, i -> times[i] <= limit)];
}
```

Wait — that predicate is **non-increasing** in `i`. Make it monotone non-decreasing:
`f(i) = times[i] > limit` ⇒ false...false,true...true. ✓

Now write the *wrong* version (predicate not monotone) and find an input where it returns a non-minimal speed. This is the most instructive bug in the lab: it does not crash, it does not loop, it just gives a slightly wrong answer.

**Cost:** `Θ(log n)` time comparisons vs `Θ(n)` for a linear scan. Verify by counting `f` invocations.

---

## Exercise 5 — `k`-th smallest: three implementations

1. **Sort and index**: `Θ(n log n)`.
2. **Quickselect**: `Θ(n)` expected — import the pattern from lab 06, or write it.
3. **Binary search on the answer**: `Θ(log(range) · log n)` using your `upperBound` as `countLessOrEqual`.

Time all three on `n = 10⁷` random `int[]`. Then answer:
- Which wins for `n = 10⁵`? (`Arrays.sort`, because of constant factors)
- Which wins for `n = 10⁸`? (quickselect, because of memory)
- Does the binary-search version help if `f` is `O(1)` via a **Fenwick tree over a coordinate-compressed value set**? What is the resulting complexity, and is it worth building the Fenwick tree?

**The punchline to discover yourself:** binary-search-on-answer only pays when `f` is sublinear *and* the range is large. With `f = Θ(log n)` and `range = Θ(range)` you get `Θ(log(range) · log n)`; with a Fenwick tree over compressed coordinates the range becomes `Θ(n)` so it is `Θ(log² n)` — worse than quickselect's `Θ(n)` for large `n`.

---

## Exercise 6 — Rotated array: prove and probe

**(a) Trace** `searchRotated` on `[4,5,6,7,0,1,2]` for `key = 0`:

| iter | lo | hi | mid | `a[mid]` | sorted half | decision |
|------|----|----|-----|----------|-------------|----------|
| 0 | 0 | 6 | 3 | 7 | `a[0]=4 <= a[3]=7` → left | `4<=0`? no → `lo=4` |
| 1 | 4 | 6 | 5 | 1 | `a[4]=0 <= a[5]=1` → left | `0<=0<=1` → `hi=4` |
| 2 | 4 | 4 | 4 | 0 | — | found at 4 ✓ |

**(b) Prove the invariant.** In writing: why is at least one half always sorted, and why does the chosen half always contain the key if it exists?

**(c) The duplicate trap.** Find an input where `searchRotated` (without the `a[lo]==a[mid]==a[hi]` handler) returns `-1` for a key that IS present. `[1,1,1,1,2,1]` searching for `2` works. Find one that fails for `1`… and confirm the fixed version handles it. Measure the fixed version's worst case on all-equal input and explain why `Θ(n)` is unavoidable.

**(d) Find all indices in a rotated array with duplicates.** `Θ(log n)` for the first, then linear scan outwards. Verify against brute force.

---

## Exercise 7 — Exponential search vs binary search

Implement `gallopSearch` and benchmark against `lowerBound` for **query distributions**:
1. Uniform over the whole array.
2. Always index 0.
3. Always index 3.
4. Always index `n-1`.
5. Geometrically distributed near the head (`k = (int)(Math.pow(n, rnd.nextDouble()))`).
6. Temporal: a monotonically increasing "now" pointer.

Report the iteration counts for each. Then implement the **hybrid** production strategy:

```java
// remember the last hit; if the next query is within 32 of it, linear scan;
// otherwise gallop.
private int lastHit = 0;
int gallopSearchCached(int[] a, int key) {
    int probe = lastHit + 32;
    if (probe < a.length && a[probe] >= key) {
        for (int i = lastHit; i <= probe; i++) if (a[i] == key) { lastHit = i; return i; }
    }
    int i = gallopSearch(a, key);
    if (i >= 0) lastHit = i;
    return i;
}
```

Explain when the cache is harmful (queries jump around randomly) and how you would detect that (track cache hit rate).

---

## Exercise 8 — Parallel binary search

Implement parallel binary search for `q` queries over an array of `n` sorted **rows**: given `q` keys, for each key find in how many rows it is `≤` that key, and locate the boundary in each row.

Naive: `q × rows × log(cols)`.

**Parallel version:**
```
while (true):
    bucket each unresolved query by its current mid index per row  -- O(q * rows)
    process all buckets in parallel: for each mid, sort the keys that need it,
        binary search that one key once, and split the key list
    resolve all queries whose lo == hi
```
Complexity: `O((q·rows + n) log(cols))` work, `O(log cols)` rounds.

Report the speedup on 8 threads for `q = 10⁶`, `rows = 1000`, `cols = 100`. Then answer: what is the **memory** cost, and when is the sequential version better (small `q`, so the setup dominates)?

---

## Exercise 9 — `RandomAccess` trap, measured

Benchmark `lowerBound` on an `ArrayList<Integer>` and a `LinkedList<Integer>` of size `10⁶` for a key at index `n-1`. Predict the ratio and explain it from the `get(i)` cost of each structure. Then:
- Show that a **linear scan** on the `LinkedList` is *faster* than binary search for `n = 10³`.
- Implement a `List` binary search that automatically falls back to `Collections.binarySearch` / linear for non-`RandomAccess` lists and prove the choice is never worse.

---

## Exercise 10 — Debugging drills

1. `minFeasible` with `mid = lo + (hi - lo) / 2` — construct an input where it hangs. Then explain in one sentence why.
2. `firstTrue` with `hi = mid - 1` in the `if (f(mid))` branch — what does it return for `f = [true]`?
3. `Arrays.binarySearch` absent-key handling with `-i + 1` — compute the wrong insertion point for `a = [1,2,3]`, `key = 5`.
4. Rotated search with duplicates but no tie handler, on `[1,0,1,1,1]` for `key = 0`. Trace it.
5. `kthSmallest` binary search with `long lo/hi` but `int mid` — what breaks?
6. Binary search a `String[]` sorted by `length()` but searched with `naturalOrder`. What happens?

---

## Exercise 11 — Deliverable: `BENCHMARK/BranchCost.java`

Binary search is dominated by **branch mispredictions**, not arithmetic. Measure:
1. Randomly shuffled queries over a 10⁷-element sorted array (max mispredictions).
2. Sequential queries (perfectly predictable branches).
3. Eytzinger (BFS) layout instead of sorted order — should predict much better.

For each, report `ns/query` and estimate the misprediction rate from the difference. Implement the Eytzinger layout:

```java
// Build a BFS-indexed permutation: eytz[i] is the element whose in-order index is i
static int[] toEytzinger(int[] sorted) {
    int n = sorted.length, lo = 0, hi = n - 1;
    int[] e = new int[n + 1];
    build(sorted, e, 1, lo, hi);
    return e;
}
static void build(int[] s, int[] e, int k, int lo, int hi) {
    if (lo > hi) return;
    int mid = lo + ((hi - lo) >>> 1);
    e[k] = s[mid];
    build(s, e, 2*k, lo, mid - 1);
    build(s, e, 2*k + 1, mid + 1, hi);
}
```

Then explain the measured improvement in terms of branch-predictor training: the Eytzinger root is the median of the *whole* array and is examined every query, so the predictor learns it immediately; in sorted order the first probe is `a[n/2]`, then `a[n/4]` or `a[3n/4]` — a two-level decision tree that modern predictors (TAGE) can partly learn, giving a smaller but real gain.

**This is the single most performance-relevant exercise in the lab** and the one that transfers to real systems: **data layout can beat a better algorithm.**