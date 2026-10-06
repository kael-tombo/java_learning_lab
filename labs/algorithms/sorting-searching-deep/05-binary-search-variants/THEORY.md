# Theory — Binary Search Variants

Binary search is the simplest algorithm that is genuinely hard to write correctly. It has a two-line body and one of the highest bug densities per line of any algorithm in this course, because the difficulty is not the logic — it is **maintaining an invariant under integer rounding**.

---

## 1. The recurrence and why `log n` is right

```
T(n) = T(n/2) + Θ(1),   T(1) = Θ(1)
```

Master theorem with `a = 1, b = 2, f(n) = 1`: `n^(log₂1) = 1`, `f(n) = Θ(1)` ⇒ **Case 2** ⇒ `T(n) = Θ(log n)`.

**Exact iteration count for the `lowerBound` form.** The invariant is `hi - lo > 0` at the top of each iteration. Each iteration sets either `lo = mid + 1 ≥ lo + 1` or `hi = mid ≤ hi - 1`, so the width `hi - lo` strictly decreases. Since `⌈(hi-lo)/2⌉ ≤ (hi-lo)/2 + 1/2`, the width after `t` iterations is at most `⌈(n+1)/2^t⌉ - 1`, which reaches `0` at `t = ⌈log₂(n+1)⌉`.

For `n = 10`: 4 iterations. `⌈log₂ 11⌉ = 4`. ✓

**The information-theoretic view.** Binary search asks "is the answer ≤ `mid` or > `mid`?" — one bit per iteration. So it needs exactly `log₂(range)` iterations. This is the *optimal* number for a decision problem with `range + 1` outcomes.

---

## 2. Interval conventions: the root of all off-by-one bugs

There are exactly two consistent conventions. Mixing them is where every bug comes from.

### Convention A — inclusive `[lo, hi]`

```
lo = 0, hi = n - 1
while (lo <= hi) {          // <= because the interval may be EMPTY
    mid = lo + (hi-lo)/2    // mid is always a VALID index
    ...
    // must always SHRINK:
    lo = mid + 1   or   hi = mid - 1
}
```

- Empty interval ⟺ `lo > hi`. Empty means "not found".
- `mid ∈ [lo, hi]` guaranteed because `lo ≤ hi`.
- Overflow risk: `hi = mid - 1` when `mid == 0` gives `-1` — safe as an *exit condition*, unsafe as an *index*.

### Convention B — half-open `[lo, hi)`

```
lo = 0, hi = n
while (lo < hi) {           // < because the interval is never empty when lo < hi
    mid = lo + (hi-lo)/2    // mid ∈ [lo, hi-1], ALWAYS valid
    ...
    // must always SHRINK:
    lo = mid + 1   or   hi = mid
}
return lo                  // the answer, or n
```

- Empty interval ⟺ `lo == hi`. Empty means "the answer is `lo`" — there is no "not found" state, because `lo = n` *is* "not found".
- `mid ∈ [lo, hi-1]` because `lo < hi ⟹ hi - lo ≥ 1 ⟹ mid = lo + ⌊(hi-lo)/2⌋ ≤ lo + hi - 1 - lo = hi - 1`.

**Convention B is strictly safer** because it eliminates the `mid + 1`/`mid - 1` off-by-one entirely and removes the `n + 1` sentinel check. It is also the basis of the C++ std library idiom and of every "count how many elements are ≤ x" routine.

---

## 3. `lowerBound` / `upperBound` — the workhorses

```
lowerBound(a, key) = min { i : a[i] >= key },  else n
upperBound(a, key) = min { i : a[i] >  key },  else n
```

Everything else is derived:

| Query | Expression |
|-------|-----------|
| exact index | `lowerBound(a, k)` if it exists and `a[lb] == k`, else "absent" |
| is `k` present | `lb < n && a[lb] == k` |
| count of `== k` | `upperBound(a, k) - lowerBound(a, k)` |
| count of `< k` | `lowerBound(a, k)` |
| count of `<= k` | `upperBound(a, k)` |
| range `[p, q)` | sort by `lowerBound(p)`, take `lowerBound(q) - lowerBound(p)` |
| insert position | `lowerBound(a, k)` |
| `floor` in a sorted array | `upperBound(a, k) - 1` if `k` present |

**This is the single most reusable primitive in the lab.** "Count occurrences", "range query on a sorted multiset", and "find the insert point" are all the same four lines with a different comparison operator.

### Why `a[mid] < key` must move `lo = mid + 1`

Suppose `a[mid] < key`. Since `a` is sorted ascending, **every index ≤ `mid` also satisfies `a[i] < key`** (monotonicity!). Therefore `mid` cannot be a valid answer for `lowerBound`, and neither can anything to its left. So `lo = mid + 1`.

And if `a[mid] >= key`, `mid` *may* be the answer, so `hi = mid` — we keep `mid` in the interval. Getting `hi = mid - 1` here is the single most common bug: it can skip the answer entirely when `a[0] == key`.

---

## 4. Binary search on the answer (predicate search)

### The general theorem

> If `f` is monotone non-decreasing over `[lo, hi]` (i.e. `f(x) ≤ f(y)` whenever `x ≤ y`), then the set `{ x : f(x) = true }` is a suffix of `[lo, hi]`. Therefore there is at most one threshold `x*` with `f(x*) = true` and `f(x*-1) = false`, and it can be found in `Θ(log(hi - lo + 1))` evaluations of `f`.

This is the *only* thing binary search needs. It does **not** need a sorted array, an index, or a comparator.

```
/** Find the SMALLEST x in [lo, hi] such that f(x) is true. Returns hi+1 if none. */
static int firstTrue(int lo, int hi, IntPredicate f) {
    int result = hi + 1;                         // sentinel for "none"
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (f(mid)) { result = mid; hi = mid - 1; }   // remember and look smaller
        else lo = mid + 1;                            // look larger
    }
    return result;
}
```

Note this uses Convention A plus an explicit `result` variable — the cleanest way to express "first true".

### Binary search on the answer, upward-biased form

For "minimum feasible `x`" problems:

```
lo = 0; hi = RANGE;
while (lo < hi) {
    int mid = lo + (hi - lo + 1) / 2;      // <-- the +1 biases UP
    if (feasible(mid)) lo = mid;           //   so progress is guaranteed
    else hi = mid - 1;
}
return lo;
```

**Why the `+1` is mandatory.** With `lo = hi - 1` and `mid = lo + (hi-lo)/2 = lo`, the body can set `lo = mid` (no change) or `hi = mid - 1 = lo - 1` (`lo > hi`, exit). In the first case the loop **never terminates**. The `+1` makes `mid = hi` when `hi = lo + 1`, and both branches shrink. This is the second most common binary search bug after the `hi = mid - 1` one.

### The cost analysis that makes it a win

| Approach | Cost |
|----------|------|
| Linear scan over candidates | `Θ(n · cost(f))` |
| Binary search on the answer | `Θ(log R · cost(f))`, `R` = value range |

`log R` beats `n` when `R ≪ n`. Classic examples:
- **Minimum speed to finish a race in `t` seconds**: `f(v) = canFinish(v)` is monotone in `v`. Binary search `v` over `[1, v_max]` → `Θ(log v_max)` instead of `Θ(n)` timing trials.
- **Minimum refuelling stops** (Aggressive Cows): `f(x) = feasible with spacing x)` monotone → `Θ(log(max_pos))`.
- **Minimum initial energy** (Pumpkin, threshold): `Θ(log(energy))`.
- **K-th smallest in a sorted matrix**: `f(k) = countLessOrEqual(k) ≥ k)`.
- **Smallest `k` such that `n/k` exceeds a bound** (capacity): `Θ(log n)`.

The pattern generalises: **any problem phrased as "find the extreme value at which some monotone condition flips" is a binary search on the answer.**

---

## 5. Exponential (galloping) search

### Mechanism

```
i = 1
while (i < n && a[i] < key) i *= 2;      // probe 1, 2, 4, 8, ...
// Now either a[i] >= key or i >= n. If the answer is k:
//   a[k] == key and k < i, and k >= i/2.
binarySearch(a, i/2, min(i, n) - 1, key)
```

**Why it works:** if the answer is at index `k`, the doubling loop exits at the first power of two `i ≥ k` (or `i ≥ n`). So `k ∈ [i/2, i)`. The subsequent binary search over a window of size `i/2` costs `log(i/2)` more steps, and the doubling itself cost `log i` steps. Total `Θ(log k)`.

### When it beats plain binary search

`Θ(log k)` vs `Θ(log n)`. The gap matters when `k` is *typically small*:

| Data | Plain binary | Exponential |
|------|-------------|-------------|
| Dense array, uniform query | `Θ(log n)` | `Θ(log k)` — **worse** on average (`k ≈ n/2` → `log n - 1`) |
| Sorted time series, query near now | `Θ(log n)` | `Θ(log k)` — **much better** |
| Sparse hash-bucket probe | `Θ(log n)` | `Θ(log k)` |
| Run-length encoded blocks | `Θ(log n)` | `Θ(log k)` |

**Real uses:** `Arrays.binarySearch` on a lazily materialised index (gallop to find the right chunk, then binary search the chunk); in-memory k-mer tables; inverted-index posting lists (first call gallops, subsequent probes binary search the cached window); **run-length encoded streams**.

**Amortised form used in practice:** remember the last found index; if the new query is close, do a linear scan for a few elements first, and only gallop after `k > 32`. This is what `LongAdder`-style optimisations and locality-aware caches do, and it is strictly better than either pure strategy.

---

## 6. Rotated sorted array

### The problem

`a` is a sorted ascending array rotated by an unknown amount (e.g. `[4,5,6,1,2,3]`). Find a target, or the rotation pivot, in `Θ(log n)`.

### The invariant

> At every step, **at least one of `[lo, mid]` or `[mid, hi]` is fully sorted**, and if the target is present it lies in exactly one of those halves.

Proof: the rotation point is a single boundary. A rotation split at `mid` puts the boundary in at most one of the halves; the other half is entirely within one ascending run and therefore sorted.

**Telling the two halves apart.** After establishing `a[lo] != a[mid]` (guaranteed once `a[mid] != target` and `a[lo] != a[mid]`), the sorted half is the one whose endpoints are non-decreasing:

```
if (a[lo] <= a[mid])  ->  [lo, mid] is sorted
else                  ->  [mid, hi] is sorted
```

The `a[lo] <= a[hi]` test that you see in textbook versions is the alternative test (it detects rotation by comparing endpoints); the `a[lo] <= a[mid]` test is the more common and more robust one because it identifies *which* half is sorted.

### Rotated-array pivot search (strictly increasing assumption)

```
lo, hi = 0, n-1
while lo < hi:
    mid = lo + (hi-lo)/2
    if a[mid] > a[hi]: lo = mid + 1          // rotation is in (mid, hi]
    else hi = mid                            // a[mid] <= a[hi] -> rotation at or before mid
return lo                                    // index of the minimum
```

**Invariant:** the rotation point (the minimum) lies in `[lo, hi]`. Each step halves.

### The duplicates trap

With duplicates (`[1,1,1,1,2,1]`), the "which half is sorted" test fails: `a[lo] <= a[mid]` and `a[mid] <= a[hi]` can both hold without either half being sorted.

**Correct handling:**
```
if (a[lo] == a[mid] && a[mid] == a[hi]) { lo++; hi--; continue; }   // shrink both ends
```
This gives `Θ(n)` worst case (all-equal input) but `Θ(log n)` on non-degenerate input. **There is no way around this** — the information-theoretic argument shows `Θ(n)` is necessary for all-equal input with an unknown target position.

---

## 7. Binary search on a monotone predicate — the general case

### Predicate classes that admit binary search

| Predicate | Monotone in | Application |
|-----------|-------------|-------------|
| `a[i] >= key` | index `i` (needs sorted `a`) | `lowerBound` |
| `isCapacitySufficient(c)` | `c` | capacity/aggressive-cows/min-speed |
| `countLessOrEqual(x) >= k` | `x` | k-th smallest, median of two arrays |
| `canReach(node)` | `node` | graph BFS frontiers, `bottleneck` Dijkstra |
| `sum(prefix) <= budget` | prefix length | subarray with constraint |
| `isFeasible(deadline)` | deadline | scheduling, rate limiting |
| `pref[x+1]/x >= ratio` | `x` | max-min ratio, gas-station |

### Binary search on a sorted `List` (Java)

```java
List<Integer> list = ...;                  // random access: O(1) get(i)
int lo = 0, hi = list.size();              // half-open
while (lo < hi) {
    int mid = lo + (hi - lo) >>> 1;
    if (list.get(mid) < key) lo = mid + 1; else hi = mid;
}
```

**PITFALL: `list.get(i)` is `O(1)` only for `ArrayList`, `RandomAccess` lists.** On `LinkedList` this is `Θ(n)` and the whole search becomes `Θ(n log n)`. **Never binary search a `LinkedList`** — use `List.binarySearch` only after checking `instanceof RandomAccess`, or walk it linearly.

### Binary search on a linked list

You can do it in `Θ(n)` total by "finger search" (exponential from the head), but you cannot do better than `Θ(n)` because reaching index `k` is already `Ω(k)`. **The lesson:** binary search needs `O(1)` random access. When the structure lacks it, binary search is the wrong tool.

---

## 8. `Arrays.binarySearch` — what it does *not* tell you

```java
int i = Arrays.binarySearch(a, key);       // returns -(insertion point) - 1 if absent
if (i < 0) i = -i - 1;                     // the insertion point
```

- **Guaranteed:** `Θ(log n)` on a sorted array.
- **NOT guaranteed:** *which* index you get when there are duplicates. The JDK documents no stable choice.
- **Trap:** `-(insertion point) - 1` means you must apply `-i - 1`, and doing `-i + 1` is a classic off-by-one that yields a wrong insertion point for the very common absent-key case.
- **Trap:** the array **must** be sorted with the same ordering used for the search. `Arrays.sort(int[])` then `Arrays.binarySearch(int[], int)` is fine. Sorting a `String[]` and searching with `binarySearch(a, s, cmp)` is fine. Sorting by `id` and searching by `name` is a silent infinite wrong answer.
- **Trap:** `long[]` vs `int[]` — `Arrays.binarySearch(int[], int)` does **not** accept a `long`. You must decide the key type up front.

---

## 9. Why binary search is hard: a taxonomy

| Bug | Symptom | Prevention |
|-----|---------|-----------|
| `hi = mid - 1` in the `lowerBound` `else` branch | Misses `key == a[0]` | Use the two-loop form; test `lowerBound(a, a[0]) == 0` |
| `mid = (lo + hi) / 2` | Overflow for `lo + hi > MAX` | Use `lo + (hi - lo) / 2` |
| `mid = lo + (hi - lo + 1) / 2` without the `+1` intent | Infinite loop on `hi = lo + 1` | Write the upward-biased form deliberately with a comment |
| Exclusive/inclusive mixed | Off-by-one at either end | Pick Convention A or B **per function** and never mix |
| `while (lo < hi)` with a `hi = mid - 1` update | Infinite loop | Under `lo < hi`, updates must be `lo = mid + 1` or `hi = mid` |
| Assuming `mid` is the answer when `a[mid] == target` | Wrong when duplicates exist | Use `lowerBound`/`upperBound` |
| Binary searching unsorted data | Silent garbage | Assert sortedness in tests (`isSorted`) |
| `list.get(i)` on `LinkedList` | `Θ(n log n)` instead of `Θ(log n)` | Check `instanceof RandomAccess` |
| `-(ip) - 1` misread as `-ip + 1` | Wrong insertion point | Write a test for the absent-key case |
| Search key ordering ≠ sort ordering | Silent garbage | One shared `Comparator` constant |

**The meta-lesson:** every one of these is an invariant violation, and every invariant violation is prevented by writing the *interval* in the loop header (`while (lo < hi)`) and deriving updates mechanically. There are no clever tricks; there is only discipline about which of two interval conventions you are in.