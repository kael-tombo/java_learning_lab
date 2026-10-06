# Flashcards — Binary Search Variants

Format: **Q → A**.

---

| # | Question | Answer |
|---|----------|--------|
| 1 | Recurrence for binary search | `T(n) = T(n/2) + Θ(1)` — Master theorem Case 2 with `a = 1` |
| 2 | Result | `Θ(log n)` |
| 3 | Exact iteration count (half-open form) | `⌈log₂ n⌉` |
| 4 | Best case | `⌈log₂ n⌉ − 1` — same asymptotically |
| 5 | Information per step | exactly 1 bit ⇒ **optimal** (gap = 0) |
| 6 | Two interval conventions | inclusive `[lo, hi]` with `hi = n−1` and `lo ≤ hi`; half-open `[lo, hi]` with `hi = n` and `lo < hi` |
| 7 | `lowerBound` definition | first `i` with `a[i] ≥ key`, else `n` |
| 8 | `upperBound` definition | first `i` with `a[i] > key`, else `n` |
| 9 | `lowerBound`'s `else` update | **`hi = mid`** — `mid` may be the answer |
| 10 | `lowerBound`'s `if` update | `lo = mid + 1` — sortedness means everything ≤ `mid` is also `< key` |
| 11 | `lowerBound` + `upperBound` | count of `== key` |
| 12 | `lowerBound` alone | count of `< key`, and the insert position |
| 13 | Overflow-safe midpoint | `lo + ((hi − lo) >>> 1)` |
| 14 | Overflow needs | `lo + hi > 2³¹ − 1`; possible for arrays with `n > 2³⁰` |
| 15 | Why `hi = a.length` is safe | `lo < hi ⟹ mid ≤ hi−1 ≤ n−1`, so `a[mid]` is always valid |
| 16 | Predicate search cost | `Θ(log R · cost(f))` |
| 17 | Predicate search preconditions | `R ≪ n` **and** `f` monotone non-decreasing |
| 18 | Upward-biased midpoint | `lo + (hi − lo + 1) / 2` — the `+1` prevents an infinite loop |
| 19 | The infinite-loop cause | with `hi = lo + 1`, `mid = lo`, and `f(lo)` true ⇒ `lo` never changes |
| 20 | `firstTrue` with no true | returns the sentinel `hi + 1` |
| 21 | Exponential search | `Θ(log k)` for an answer at distance `k` |
| 22 | Exponential search when it loses | uniformly random queries (`k ≈ n/2` ⇒ wasted doubling phase) |
| 23 | Exponential search wins on | sorted time series, RLE data, sparse bucket probes, posting lists |
| 24 | Production hybrid | cache the last hit; linear scan ~32 ahead, then gallop |
| 25 | Rotated search invariant | one half is sorted; the key (if present) is in exactly one half |
| 26 | Which half is sorted? | `a[lo] <= a[mid]` ⟹ `[lo, mid]`; else `[mid, hi]` |
| 27 | Rotated search complexity | `Θ(log n)` (no duplicates) |
| 28 | Rotated search with duplicates | `Θ(n)` worst case — information-theoretically necessary |
| 29 | Rotated duplicate handler | `if (a[lo]==a[mid] && a[mid]==a[hi]) { lo++; hi--; }` |
| 30 | Find the rotation point | the minimum; `a[mid] > a[hi] ⟹ lo = mid+1 else hi = mid` |
| 31 | Find-rotation-point precondition | **strictly** increasing (duplicates break it) |
| 32 | Binary search on `LinkedList` | `Θ(n log n)` — `get(i)` is `Θ(i)`; check `instanceof RandomAccess` |
| 33 | Binary search on `TreeSet` | `O(log n)` via `TreeSet.floorKey`/`higher` — no manual search needed |
| 34 | `Arrays.binarySearch` absent result | `-(insertionPoint) − 1` |
| 35 | Correct transform | `-i − 1`; the mistake is `-i + 1` |
| 36 | `Arrays.binarySearch` with duplicates | index is **unspecified** among equal keys |
| 37 | `Arrays.binarySearch` on unsorted data | silently wrong — no exception |
| 38 | Sort order ≠ search order | silently wrong; share one `Comparator` constant |
| 39 | `Arrays.binarySearch(int[], long)` | does not exist; no silent widening — use `int[]` |
| 40 | `countLessOrEqual` via `upperBound` | `Θ(log n)` instead of `Θ(n)` — enables search-on-answer |
| 41 | `k`-th smallest by sort | `Θ(n log n)` |
| 42 | `k`-th smallest by quickselect | `Θ(n)` expected, destroys input |
| 43 | `k`-th smallest by search-on-answer | `Θ(log R · log n)` — wins only for huge `R` |
| 44 | Search-on-answer vs sorting | if `f` is `Θ(n)` the trick is `Θ(n log R)` — **worse** |
| 45 | Sorted-matrix `k`-th smallest | `Θ(log rows · log cols)` — the real `log²` case |
| 46 | Parallel binary search | `O((q + n) log(cols))` work, `O(log cols)` depth |
| 47 | Branch-misprediction cost | ~15–20 cycles; dominates `Θ(log n)` arithmetic for large `n` |
| 48 | Eytzinger layout | BFS order of the search tree; children at `2k`, `2k+1` — same cache line |
| 49 | Eytzinger speedup | 1.5–2× for random queries over large arrays |
| 50 | Why Eytzinger helps prediction | the root is probed every query, so the predictor learns it |
| 51 | Sequential queries | branch prediction is nearly perfect; layout matters less |
| 52 | Binary search over 40 MB | ~23 cache misses ≈ 2 000+ cycles, dwarfing the arithmetic |
| 53 | When hashing beats binary search | scattered point lookups on unsorted data: 1–2 misses vs ~23 |
| 54 | When hashing loses | range queries, predecessor/successor, ordered output |
| 55 | #1 binary-search bug | `hi = mid − 1` in the `lowerBound` `else` branch |
| 56 | #2 binary-search bug | forgetting the `+1` in the upward-biased midpoint |
| 57 | #3 binary-search bug | mixing inclusive and half-open conventions in one function |
| 58 | #4 binary-search bug | `(lo + hi) / 2` overflow |
| 59 | #5 binary-search bug | assuming `mid` is "the" answer when duplicates exist |
| 60 | Meta-rule | Write the interval in the loop header and derive updates mechanically; there are no tricks |

## Self-test (one line each)

1. Exact iteration count for the half-open form? → **`⌈log₂ n⌉`**
2. Why `hi = mid` and not `hi = mid − 1` in `lowerBound`? → **`mid` may be the answer; the invariant requires the answer to stay in `[lo, hi]`**
3. Cost of search-on-answer? → **`Θ(log R · cost(f))`** — and it only wins when `f` is sublinear
4. Rotated search with duplicates, worst case? → **`Θ(n)`**, information-theoretically necessary
5. `Arrays.binarySearch` absent result and the transform? → **`-(ip) − 1`**, then **`-i − 1`**