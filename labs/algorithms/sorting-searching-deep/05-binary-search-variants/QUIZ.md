# Quiz — Binary Search Variants

15 questions. Each key gives the reason.

---

## Q1
State the exact loop invariant of the half-open `lowerBound` form and prove the iteration count.

<details><summary>Answer</summary>

**Invariant:** (1) every index `< lo` has `a[i] < key`; (2) every index `≥ hi` has `a[i] ≥ key`; (3) `lo ≤ hi`. Hence the answer — the first `i` with `a[i] ≥ key` — lies in `[lo, hi]`, or is `n` when `lo = hi = n`.

**Iteration count:** with `w = hi − lo > 0`, `mid = lo + ⌊w/2⌋`, and both updates give `w' ≤ ⌈w/2⌉ − 1`. So `w_t ≤ ⌈n/2^t⌉ − 1`, which hits `0` at `t = ⌈log₂ n⌉`.

**Why update (1) holds:** if `a[mid] < key` then by sortedness every `a[i] ≤ a[mid] < key` for `i ≤ mid`, so none of them is the answer.
</details>

## Q2
Why must the `else` branch be `hi = mid` and not `hi = mid - 1`?

<details><summary>Answer</summary>

Because `mid` may **be** the answer. `lowerBound` finds the first index `≥ key`; if `a[mid] ≥ key`, then `mid` is a candidate, so it must stay in the interval.

`hi = mid - 1` can skip it entirely — e.g. `lowerBound([5], 5)`: `mid = 0`, `a[0] ≥ 5`, so `hi = -1`, and the loop exits with `lo = 0`. Correct by luck; but `lowerBound([3, 5, 7], 3)`: `mid = 1`, `hi = 0`, then `mid = 0`, `a[0] = 3 ≥ 3`, `hi = -1` → returns `0`, also correct. Construct `([1, 5, 7], 1)` → `mid = 1`, `hi = 0`, `mid = 0`, `hi = -1`, return `0`. The real failure appears when combined with a different loop condition; the invariant, not the specific witness, is the argument.

The invariant version: the answer must lie in `[lo, hi]`, and `mid ∈ [lo, hi]` is a candidate, so `hi = mid` preserves it.
</details>

## Q3
Binary search is `Θ(log n)`. Why is that *optimal*, and what is the exact information argument?

<details><summary>Answer</summary>

The answer is one of `n + 1` outcomes (`n` positions plus "absent"). A single comparison yields at most 1 bit. So any comparison-based search needs `≥ ⌈log₂(n+1)⌉` comparisons.

Binary search's decision tree is a complete balanced binary tree of depth `⌈log₂(n+1)⌉` — it attains the bound exactly. **Gap = 0.**
</details>

## Q4
`while (lo < hi)` with `mid = lo + (hi - lo) / 2` in a "minimum feasible `x`" search. What is wrong, and why does the `+1` fix it?

<details><summary>Answer</summary>

If `hi = lo + 1` then `mid = lo`. If `f(lo)` is true, the body sets `lo ← mid = lo` and the interval never shrinks — **infinite loop**.

The fix is `mid = lo + (hi − lo + 1) / 2`. Then under `lo < hi` we have `⌊(hi−lo)/2⌋ + 1 ≤ hi − lo`, so `lo + 1 ≤ mid ≤ hi`. Therefore `lo ← mid` strictly increases `lo`, and `hi ← mid − 1` strictly decreases `hi`. Either way the interval shrinks by ≥ 1.
</details>

## Q5
Overflow-safe midpoint. For which array sizes does `(lo + hi) / 2` actually break?

<details><summary>Answer</summary>

`lo + hi` overflows `int` when `lo + hi > 2³¹ − 1`.

Even with plain arrays: `lo + hi ≤ (n−1) + (n−1) = 2n − 2`, so overflow needs `n > 2³⁰ ≈ 1.07·10⁹`. Legal for a `byte[]` (max length `2³¹ − 1`) but not for most array types.

Correct form: `lo + ((hi − lo) >>> 1)`, where `hi − lo ∈ [0, MAX_VALUE]` so no intermediate overflows.
</details>

## Q6
When is binary search **not** the right tool, despite the `Θ(log n)` bound?

<details><summary>Answer</summary>

1. **No random access.** `LinkedList.get(i)` is `Θ(i)`, so binary search is `Θ(n log n)` — worse than a linear scan for small `n` and never better asymptotically.
2. **Not sorted and not a monotone predicate.** Binary search's only requirement is monotonicity; if that is absent, the answer is garbage with no exception.
3. **Static data, many queries.** Sorting once (`Θ(n log n)`) plus `q` binary searches (`Θ(q log n)`) beats `q` linear scans (`Θ(qn)`) as soon as `q > n / log n`… but a hash table gives `Θ(q)` expected with no preprocessing. Use hashing unless you need ordered range queries.
4. **Caches.** A binary search over 40 MB costs ~23 cache misses. A hash lookup costs 1–2. For scattered point lookups, hashing wins by an order of magnitude.
</details>

## Q7
"Binary search on the answer" — when does it actually beat the obvious approach? Give the cost model and two conditions.

<details><summary>Answer</summary>

Cost: `Θ(log R · cost(f))` for a value range `R`, versus `Θ(n · cost(f))` for scanning `n` candidates.

**Condition 1:** `R ≪ n` (the value range is much smaller than the number of candidates).
**Condition 2:** `f` is monotone non-decreasing — false prefix, true suffix.

If `f` costs `Θ(n)` (e.g. a feasibility simulation), you get `Θ(n log R)`, *worse* than sorting once. The trick needs `f` to be cheap — `O(1)`, `O(log n)`, or amortised sublinear.
</details>

## Q8
Rotated sorted array: state the invariant and explain how you know which half is sorted.

<details><summary>Answer</summary>

**Invariant:** at least one of `[lo, mid]` and `[mid, hi]` is fully sorted, and if the key is present it lies in exactly one of them.

**Why:** the rotation is a single boundary, so a split at `mid` puts the boundary in at most one half; the other half lies entirely within one ascending run.

**Test:** after ruling out `a[lo] == a[hi]` (all equal), the sorted half is the one with non-decreasing endpoints: `a[lo] <= a[mid]` ⟹ `[lo, mid]` sorted; otherwise `[mid, hi]` is sorted. Then one range test decides which side holds the key.
</details>

## Q9
Why is `Θ(n)` the *necessary* worst case for rotated search with duplicates?

<details><summary>Answer</summary>

Take an all-equal array. Every comparison yields the same answer regardless of the target's position, so each comparison conveys at most **0 bits** about where the target is. The target's position is one of `n` possibilities, requiring `log₂ n` bits of information.

Therefore any correct algorithm needs `Θ(n)` comparisons in the worst case. The `if (a[lo] == a[mid] && a[mid] == a[hi]) { lo++; hi--; }` handler attains it.
</details>

## Q10
Why is the half-open form (`hi = a.length`, `while (lo < hi)`) safer than the inclusive form?

<details><summary>Answer</summary>

It removes two whole classes of bug:

1. **No sentinel check needed.** Under `lo < hi`, `mid = lo + ⌊(hi−lo)/2⌋ ≤ hi − 1 ≤ n − 1`, so `a[mid]` is *always* valid. No `mid >= a.length` branch exists to get wrong.
2. **No "not found" state.** `lo == hi` on exit *is* the answer, and `n` naturally means "past the end". The inclusive form needs a separate `-1` sentinel that can then be dereferenced.

It also forces both updates to shrink (`lo = mid + 1` or `hi = mid`), so `hi = mid − 1` becomes a compile-time-visible inconsistency rather than a silent infinite loop.
</details>

## Q11
Exponential (galloping) search: what does it beat, when, and by how much?

<details><summary>Answer</summary>

`Θ(log k)` for an answer at distance `k`, versus plain binary search's `Θ(log n)`.

It wins when `k ≪ n`: sorted time series (query near "now"), RLE'd data, sparse hash-bucket probes, run-length encoded postings lists.

It **loses** for uniformly random queries, where `k ≈ n/2` and the doubling phase is pure overhead (`⌈log₂ n⌉` wasted probes before the binary phase starts).

Production pattern: cache the last hit and linear-scan up to ~32 before galloping. This dominates both pure strategies for realistic locality.
</details>

## Q12
`Arrays.binarySearch(a, key)` returns `-i` for a missing key. How do you get the insertion point, and what is the classic mistake?

<details><summary>Answer</summary>

```java
int i = Arrays.binarySearch(a, key);
if (i < 0) i = -i - 1;      // insertion point in [0, a.length]
```

**The classic mistake is `-i + 1`.** For `a = [1,2,3]`, `key = 5`: `Arrays.binarySearch` returns `-(3) - 1 = -4`. The correct transform is `-(-4) - 1 = 3` ✓. The wrong one gives `-(-4) + 1 = 5` ✗ — past the end.

**Also unspecified:** *which* index you get when the key appears multiple times. Never rely on it for "the last occurrence"; use `upperBound`.
</details>

## Q13
Your predicate search is `Θ(log R · cost(f))` and `f` costs `Θ(log n)`. Is that `Θ(log² n)`?

<details><summary>Answer</summary>

**Not necessarily — and this is a common misanalysis.** It is `Θ(log R · log n)`, a *product*. It equals `Θ(log² n)` only when `R = Θ(n)`.

Examples where the product is not `log²`:
- `k`-th smallest of a sorted array: `R = 2³²` (the whole `int` range), `f = Θ(log n)` ⇒ `Θ(32 log n) = Θ(log n)`.
- Capacity fitting `n` items of size `s` in `m` containers: `R = n`, `f = Θ(log m)` ⇒ `Θ(log n log m)`.

`Θ(log² n)` genuinely arises for a 2-D problem like the sorted-matrix `k`-th smallest: `Θ(log rows · log cols)`.
</details>

## Q14
Your `k`-th smallest via binary search on the answer is slower than sorting. Why, and what fixes it?

<details><summary>Answer</summary>

Sorting is `Θ(n log n)`. Binary-search-on-answer with `f = countLessOrEqual(x)` is:

- `Θ(n)` per evaluation if you count linearly ⇒ `Θ(n log R)` — **worse**.
- `Θ(log n)` per evaluation using `upperBound` ⇒ `Θ(log R · log n) = Θ(log² n)` — better asymptotically but with a huge constant and no sequential locality.

**Fixes:**
1. Quickselect — `Θ(n)` expected, one pass, destroys input order.
2. A Fenwick tree over coordinate-compressed values — `f` becomes `Θ(log n)` but `R = Θ(n)`, so still `Θ(log² n)`.
3. Just sort.

**The general lesson:** the trick only pays when `f` is *much* cheaper than a linear scan **and** the range is large. Verify with a counter before you build anything.
</details>

## Q15
Binary search over 40 MB is ~23 cache misses. What data layout fixes this, and why does it work?

<details><summary>Answer</summary>

**Eytzinger (BFS) layout** — store the sorted array in *breadth-first* order of the implicit binary search tree, so index `k` is the `k`-th node in BFS order.

Two effects:
1. **Branch prediction.** The root (global median) is at index 1 and is probed on *every* query, so the predictor learns it perfectly. In sorted order the first probe is `a[n/2]`, then `a[n/4]`/`a[3n/4]` — a two-level decision tree that predictors learn only partially.
2. **Prefetch.** The two children of node `k` live at `2k` and `2k+1`, adjacent in memory, so a hardware prefetcher can fetch them together after one cache line.

Measured: 1.5–2× faster for random queries over large arrays. This is the cleanest demonstration in the lab that **data layout can beat a better algorithm** — the same `Θ(log n)` comparisons, ~30% fewer stalls.
</details>