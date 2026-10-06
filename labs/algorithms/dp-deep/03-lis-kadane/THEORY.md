# Theory — LIS & Kadane

Two families, one shape: **"the longest / maximum run of things satisfying a monotone condition"**. LIS is the monotone-in-*value* case; Kadane is the monotone-in-*position* case. Both have a `Θ(n²)` DP and a `Θ(n log n)` or `Θ(n)` improvement, and the improvement works by replacing the inner loop with a maintained aggregate.

---

## 1. Longest Increasing Subsequence — the DP

### State

> `dp[i]` = the length of the longest **strictly increasing** subsequence of `a` that **ends at index `i`**.

Two words carry all the weight: **ends at** (not "in the prefix") and **strictly** (not "non-decreasing"). Changing either changes the problem.

### Transition

```
dp[i] = 1 + max { dp[j] : 0 ≤ j < i  and  a[j] < a[i] },   max over ∅ = 0
answer = max_i dp[i]
```

**Space:** `Θ(n)`. **Time:** `Θ(n²)`.

### The `Θ(n²)` → `Θ(n log n)` transformation

The inner loop is `max over j < i of dp[j] subject to a[j] < a[i]`. That is a **2-D dominance query**: over points `(a[j], dp[j])`, find the max `dp` with `a[j] < a[i]`.

**Approach 1 — Fenwick/segment tree.** Coordinate-compress `a`, then for each `i` query the prefix max over ranks `< rank(a[i])`. `Θ(n log n)`, and it generalises to "max sum increasing subsequence" by storing `(max dp[j])` and `(max dp[j] + a[i])` together.

**Approach 2 — patience sorting (better constants).** The observation is that we only ever need, for each length `k`, the **smallest possible tail**. Define:

> `tails[k]` = the smallest possible last element of any strictly increasing subsequence of length `k+1` using only elements seen so far.

**Invariant:** `tails` is strictly increasing in `k`. (Proof: a subsequence of length `k+2` has a prefix of length `k+1` whose tail is smaller, so `tails[k] < tails[k+1]`.)

So `tails` is a **sorted array** and the update is a `lowerBound`:

```
p = first index with tails[p] >= a[i]
tails[p] = a[i]        // this element can end a subsequence of length p+1, and does so with
                       // the SMALLEST tail -- which is what helps future elements
if p == length: length++
```

**Why overwrite `tails[p]` rather than append?** A smaller tail is strictly better: any future element that could extend the old tail `tails[p]` can also extend a smaller one (the `<` condition is easier to satisfy). So we keep only the best tail. And why is `p` the right slot? Because `tails[p-1] < a[i] ≤ tails[p]`, so `a[i]` can extend a length-`p` subsequence into a length-`p+1` one, and cannot extend a longer one.

**Answer:** `length` = the number of slots used.

### The critical misconception: `tails` is not an LIS

`tails = [2, 3, 1]` could arise from `a = [2, 3, 1]`. The LIS is `[2, 3]` (length 2), and `length = 2`. But `tails = [2, 3, 1]` is **not increasing**, and `[2, 3, 1]` is **not** a subsequence of `a` in the tails order.

`tails[k]` is "the minimum tail among all length-`k+1` subsequences seen so far", and the slots are independent — `tails[0]` and `tails[2]` may come from incompatible positions.

**The reconstruction** needs `prev[]`: when `a[i]` lands at slot `p`, record `prev[i] = indexOf(tails[p-1] before this update)`. Then walk backwards from the slot that produced `length`.

**This is exactly the "no reconstruction after rolling" lesson from lab `01`, one level down.**

### `lowerBound` vs `upperBound`

| comparison | algorithm computes |
|-----------|--------------------|
| `lowerBound(tails, x)` = first `≥ x` | longest **strictly increasing** subsequence |
| `upperBound(tails, x)` = first `> x` | longest **non-decreasing** subsequence |

`tails` is sorted under either, so the binary search is valid either way. **Using the wrong one is the single most common LIS bug**, and it is invisible if your test data has no duplicates.

---

## 2. Variants of LIS

### Longest decreasing subsequence
Run patience sorting with `upperBound` (or reverse the array, or negate the values). `Θ(n log n)`.

### Number of distinct LIS of maximum length
`Θ(n log n)`:
1. Compute `dpLen[i]` = LIS length ending at `i` via patience sorting (and the `prev` chain).
2. `count[i] = Σ count[j]` over `j < i` with `a[j] < a[i]` and `dpLen[j] == dpLen[i] - 1` — a Fenwick tree keyed by compressed value.
3. Sum `count[i]` over `i` with `dpLen[i] = L`.

### Maximum **sum** increasing subsequence
Replace the Fenwick's stored value with `dp[j] + a[i]`:
```
best[i] = a[i] + max { best[j] : j < i, a[j] < a[i] },   max over ∅ = 0
```
Fenwick over compressed values → `Θ(n log n)`. Patience sorting does *not* generalise here, because "smallest tail" is not the right invariant for maximising a sum — you want the maximum `best` among tails `< a[i]`, which is a genuine dominance query.

### LIS with constraints (e.g. difference at most `d`)
```
dp[i] = 1 + max { dp[j] : j < i, a[i] - d ≤ a[j] < a[i] }
```
A **range-maximum query over a sliding value window** → segment tree or a `TreeMap`, `Θ(n log n)`. Patience sorting does not work.

### Longest increasing path in a grid
Move right or down (or right/down/diagonal). For each cell in row-major order, run patience sorting over that row's values with the row's `dp` array as the state. `Θ(mn log n)`. The per-row "tails" must be reset or carried carefully depending on whether moves between rows are allowed.

### LIS with index *and* value both constrained
Becomes a 2-D dominance problem with `Θ(n log n)` offline (sort + BIT) or `Θ(n log² n)` online (Fenwick of BITs).

---

## 3. Kadane's maximum subarray

### The problem

Given `a[0..n-1]`, find the contiguous subarray with the largest sum.

- **Non-empty required** in the classic formulation; the empty subarray (sum 0) is allowed in the "relaxed" version. **State which one you are implementing.**
- All-negative input is the discriminator: relaxed Kadane returns `0`, strict returns `max(a)`.

### The DP

```
dp[i] = max( a[i],  dp[i-1] + a[i] )      // extend the best subarray ending at i-1, or start fresh
answer = max_i dp[i]
```

**Correctness (the two-case argument):** any subarray ending at `i` either is `[a[i]]` alone, or extends a subarray ending at `i-1`. The best of those is `max(a[i], dp[i-1] + a[i])`. ∎

**Space:** `O(1)`. **Time:** `Θ(n)`.

### The prefix-sum equivalence

```
sum(a[i..j]) = P[j+1] − P[i]        where P[k] = a[0] + … + a[k-1]

max sum  =  max_j P[j+1] − min_{i ≤ j} P[i]
```

Sweeping `j` left to right while maintaining `minPrefix` **is** Kadane. Two independent derivations of the same `Θ(n)` algorithm — and a strong cross-check in tests (`assert kadane(a) == prefixSweep(a)`).

### The three-state version (the one to write)

```java
long total = 0, best = Long.MIN_VALUE, cur = 0;
for (int x : a) {
    total += x;
    cur = Math.max(x, cur + x);
    best = Math.max(best, cur);
}
```

`total` is needed for the circular variant; `best` initialised to `Long.MIN_VALUE` (not `0`) is the strict semantics; `cur` initialised to `0` works because `max(x, 0 + x) = x` on the first iteration.

**`best = 0` is the classic bug**: `a = [-3, -1, -2]` returns `0` instead of `-1`.

### The prefix/suffix decomposition

An equally useful framing:

```
max sum of a subarray
    = max over j of ( maxSumEndingAt(j) + maxSumStartingAt(j+1) )
```

This is the basis of Kadane's **maximum-sum circular** variant and of "maximum sum with a gap" problems.

---

## 4. Variants of maximum subarray

### Circular maximum subarray

```
answer = max( maxNormalSubarray(a),  total − minNormalSubarray(a) )
```

**Correctness:** a circular subarray either does not wrap — it is a normal subarray — or it wraps, in which case it is the complement of a *normal* subarray, so its sum is `total − (sum of the omitted part)`. Maximising over wrapping candidates means **minimising** the omitted part.

**Edge case:** if `minNormalSubarray == total`, the complement is empty (sum 0), which is invalid. The fix: if the wrapping candidate is `0` and all elements are negative, return `max(a)`. Concretely: `if (answer == 0 && allNegative) answer = max(a)`.

**Test case that catches it:** `a = [-1, -2, -3]`. Normal max = `-1`. `total = -6`, normal min = `-6`, so `total − min = 0`. Correct answer is `-1`. Without the edge case you return `0`. (Some judges specify "allow the whole array" and accept `0`; state which convention.)

### Maximum subarray with **at most** `k` elements

`Θ(nk)` DP, but `Θ(n)` with a monotonic deque:

```
S[i]  = sum of a[0..i]
want  = max over j in [i-k, i-1] of S[i] - S[j]     = S[i] - min{ S[j] : j in [i-k, i-1] }
```

Maintain the sliding minimum of `S` over a window of size `k` with a **monotonic deque** → `Θ(n)`.

### Maximum subarray with **exactly** `k` elements

Same formula with the window fixed at exactly `k`, i.e. `min{ S[j] : j = i-k }` — just `S[i-k]`, `Θ(n)`.

### Maximum subarray with an element constraint

"no two chosen elements both in a forbidden set" → DP with a `2`-state machine, `Θ(n)`. Same shape as the three-state Kadane.

### Maximum subarray in a 2-D matrix (largest rectangle)

**Different algorithm class.** `Θ(nm)` Kadane does not generalise; the answer is the **largest-rectangle-in-histogram** algorithm (stack-based, `Θ(m)` per row, `Θ(nm)` total) or the divide-and-conquer `Θ(nm)`. See `18-computational-geometry` for the geometry variants.

---

## 5. The unified view

Every problem in this lab is:

```
Given a sequence a[0..n-1] and a "valid continuation" relation, find the
longest / highest-scoring contiguous or skipping chain.
```

| instance | relation | inner loop | total |
|---|---|---|---|
| LIS | `a[j] < a[i]`, `j < i` | dominance max | `Θ(n²)` → `Θ(n log n)` |
| Max-sum increasing subseq | same | dominance max **plus `a[i]`** | `Θ(n log n)` (Fenwick) |
| Max subarray | contiguous only | 2-case recurrence | `Θ(n)` |
| Max subarray, `≤ k` | contiguous, length-bounded | sliding min of prefix sums | `Θ(n)` (deque) |
| LIS, `|a[i]-a[j]| ≤ d` | value-window | range max | `Θ(n log n)` (segment tree) |
| Grid increasing path | right/down | patience per row | `Θ(mn log n)` |

**The optimisation move is always the same:** the `Θ(n²)` DP's inner `max over j` is a *range/dominance query*, and replacing the linear scan with a maintained aggregate (binary search + sorted array, Fenwick, segment tree, monotonic deque) is the entire improvement.

---

## 6. Choosing

| Problem | Use | Complexity |
|---|---|---|
| One LIS length | patience sorting, `lowerBound` | `Θ(n log n)` |
| One LIS, **and** the sequence | patience + `prev[]` | `Θ(n log n)`, `Θ(n)` space |
| **All** LIS of max length | patience for `dpLen`, DFS the `prev` chains | `Θ((n + r) log n)`, `r` = output size |
| Number of LIS | patience + Fenwick count | `Θ(n log n)` |
| Max-sum increasing subseq | Fenwick | `Θ(n log n)` |
| LIS with a difference bound | segment tree / `TreeMap` | `Θ(n log n)` |
| Max subarray | Kadane, three-state | `Θ(n)`, `O(1)` space |
| Max subarray, circular | total − min | `Θ(n)`, `O(1)` space |
| Max subarray, `≤ k` elements | prefix sums + monotonic deque | `Θ(n)` |
| Max subarray in a matrix | histogram stack | `Θ(nm)` |
| Streaming (online) | patience / Kadane with a bounded `tails` buffer | `Θ(n log n)` / `Θ(n)` |

**Streaming note:** Kadane is naturally online (`O(1)` state). LIS needs `tails`, which is `Θ(n)` in the worst case but `Θ(L)` where `L` is the current best length — so it is effectively bounded if you cap it and accept approximate answers for very old elements.

---

## 7. Common bugs

| Bug | Symptom | Fix |
|-----|---------|-----|
| `upperBound` in patience sorting | wrong when duplicates exist | `lowerBound` for strictly increasing |
| `tails[p-1]` read after writing `tails[p]` | wrong sequence reconstruction | read before write |
| `best = 0` in Kadane | `0` for all-negative input | `Long.MIN_VALUE` |
| Forgetting the circular edge case | `0` for all-negative input | `max(a)` when all-negative |
| Off-by-one in the deque window | wrong at exactly `k` elements | window `[i-k, i-1]`, insert before query |
| `dp[i]` = "LIS in the prefix" instead of "ending at `i`" | breaks reconstruction and the Fenwick variant | read the definition aloud |
| Non-strict comparison in "increasing" | quietly computes non-decreasing | say which one you mean |
| Reconstructing from `tails` directly | returns a non-subsequence | `tails` is **not** an LIS |

**The single most valuable sentence in this lab:** `tails` is a sorted array of *minimum tails*, not a subsequence, and reading it as one is the most common LIS bug in the world.