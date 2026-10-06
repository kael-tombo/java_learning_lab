# Exercises — LIS & Kadane

Implement in Java, trace by hand, then attack the edge cases. Java 21, package `com.alglab.lis`. Solutions → `SOLUTION/`, tests → `TESTS/`.

---

## Exercise 1 — Patience sorting, step by step

Trace `lisLength` for `a = [5, 1, 4, 2, 3, 0]`. Fill the table:

| `i` | `x` | `length` before | `tails` before | `p = lowerBound` | `tails` after | `length` after |
|-----|-----|-----------------|----------------|------------------|---------------|----------------|
| 0 | 5 | 0 | `[]` | 0 | `[5]` | 1 |
| 1 | 1 | 1 | `[5]` | 0 | `[1]` | 1 |
| 2 | 4 | 1 | `[1]` | 1 | `[1,4]` | 2 |
| 3 | 2 | 2 | `[1,4]` | 1 | `[1,2]` | 2 |
| 4 | 3 | 2 | `[1,2]` | 2 | `[1,2,3]` | 3 |
| 5 | 0 | 3 | `[1,2,3]` | 0 | `[0,2,3]` | 3 |

**Answer = 3.**

Now the punchline: **is `[0,2,3]` a subsequence of `a`?** Positions are `4, 2, 3` — not increasing ⇒ **NO.** The LIS is `[1,2,3]` (positions 1,3,4).

**Then:** find the smallest `a` (over all arrays of length ≤ 5, alphabet `{0,1,2,3}`) where `tails` is not a subsequence. Verify your answer matches this one.

---

## Exercise 2 — `lowerBound` vs `upperBound`

Compute **both** `lisLength` and `lndsLength` for:

| `a` | LIS | LNDS | differ? |
|-----|-----|------|---------|
| `[1,1,1,1]` | | | |
| `[5,1,4,2,3]` | | | |
| `[1,2,2,3]` | | | |
| `[3,2,1]` | | | |
| `[2,4,6,1,3,5,7]` | | | |

Verify `lndsLength(a) == max over all non-decreasing subsequences` with an `O(n²)` reference.

**Then:** find the smallest input where the two differ. Answer: `a = [1,1]` (LIS 1, LNDS 2)? Check smaller: `a = [1]` — same. So `[1,1]` length 2 is minimal. **Write a test that fails if you use the wrong one** and prove your test would catch the swap.

---

## Exercise 3 — `Θ(n²)` DP vs patience

Benchmark both for `n ∈ {10³, 10⁴, 10⁵, 10⁶}` on:
- random uniform
- random with 5 distinct values
- sorted ascending
- sorted descending

Report ns/op and the ratio. Verify `Θ(n²)/Θ(n log n) = n/log n`:
| `n` | `n/log n` | predicted ratio |
|-----|-----------|----------------|
| 10⁴ | 752 | |
| 10⁶ | 50 200 | |

**Then:** find the largest `n` for which the `Θ(n²)` DP completes in 2 seconds on your machine. Extrapolate: at what `n` does patience sorting become the *only* option?

---

## Exercise 4 — Reconstruction bugs

Implement `lis()` returning indices and values. Then deliberately break it six ways and find the smallest failing input for each:

| bug | break |
|-----|-------|
| B1 | `prev` not initialised to `-1` |
| B2 | start from `tailsIdx[length-1]` replaced by `a[length-1]` |
| B3 | `prev[i] = tailsIdx[lo]` instead of `tailsIdx[lo-1]` |
| B4 | read `tails[lo-1]` AFTER writing `tails[lo]` (use a combined record array) |
| B5 | reconstruct forward instead of backward |
| B6 | tie-break on `upperBound` instead of `lowerBound` |

**For each, state the symptom.** B1 hangs or AIOOBEs; B2 gives an increasing-but-invalid sequence; B4 gives an off-by-one that only shows with specific inputs.

---

## Exercise 5 — Count of LIS

Implement `countLIS` and validate against a brute-force enumeration (all subsequences via `2ⁿ` masks) for `n ≤ 16`, alphabet `{0,1,2}`.

Then answer:
1. For `a = [1,2,3,…,n]`, what is the count? (1.)
2. For `a` a permutation of `{1,…,n}`, the count of LIS is the number of increasing subsequences. For `a = [1,2,…,n,1,2,…,n]` (two increasing runs), what is it? (Compute for `n = 10`; the answer is `2^n`... verify.)
3. At what `n` does the count overflow `long`? (`C(n, n/2) > 2⁶³` — find the smallest `n`.)

Then implement the "enumerate **all** LIS" variant and measure the time for `n = 20` with an alphabet of 3. Confirm `Θ(n log n + r)`.

---

## Exercise 6 — Kadane: five variants and their traps

Implement and validate:

| variant | `[1,-2,3,-2]` | `[-1,-2,-3]` | `[]` |
|---------|--------------|--------------|-------|
| max subarray (non-empty) | | | |
| max subarray (relaxed) | | | |
| max circular | | | |
| max subarray of length **exactly** `k` | | | |
| max subarray of length **at most** `k` | | | |

Then the bugs:
- `best = 0` — what does each variant return for `[-1,-2,-3]`?
- Circular without the all-negative guard — same question.
- Deque with `dq[head] < i - k + 1` instead of `< i - k` — which variant does it actually compute?
- Deque with the expiry done **before** the insert — what window does it use?

**Verify every bug with a concrete input.**

---

## Exercise 7 — The deque, from scratch

Implement the sliding-window minimum of prefix sums three ways:
1. Brute force `O(nk)`
2. Naive rescan `O(nk)`
3. Monotonic deque `O(n)`

Measure for `n = 10⁶` and `k ∈ {1, 10, 1000, 100 000}`. Verify `Θ(nk)/Θ(n) = k`.

**Then:** prove the dominance-pop is correct in writing. Formalise: if `j₁ < j₂` and `P[j₁] ≥ P[j₂]`, then for every future query where `j₁` is still in the window, `j₂` is also in the window and gives a value at least as small. Hence `j₁` can never be the argmin again. ∎

**And answer:** why must the query be `P[i] - minWindow` and not `maxWindow - P[i]`? (Because a subarray sum is `P[end] - P[start]`, and `start < end`, so the *start* prefix must be the minimum.)

---

## Exercise 8 — Max-sum increasing subsequence

Implement `maxSumIncreasing` and validate against an `O(n²)` DP for 20 000 random arrays.

**Then:** why does patience sorting not generalise? Write one paragraph. (Answer: the patience invariant is "smallest tail is best"; for max-sum you need the largest `best[j]` among tails `< a[i]`, and there is no array that keeps both quantities ordered — you need a genuine dominance structure.)

**Bonus:** implement the version with the constraint `a[j] < a[i]` **and** `j < i` **and** `|a[j] - a[i]| ≤ d` — a segment tree over compressed values. Report the constant-factor cost versus the unconstrained Fenwick.

---

## Exercise 9 — Grid LIS

1. Longest increasing path in a grid, moves **right and down only** — patience sorting, `Θ(mn log(mn))`. Validate against `Θ(mn)` DP.
2. Moves **right, down, and diagonally** — validate against DP.
3. Moves in **all four directions** — this is a different problem. Why does patience sorting fail, and what is the right complexity? (`Θ(mn log(mn))` by sorting cells by value and running a Fenwick keyed by row.)
4. **The killer case:** a grid where a right/down path can revisit a value. Show that the `tails`-reuse bug appears if you use one `tails` array across rows.

**Then:** the "maximum sum increasing path" in a grid — `Θ(mn log(mn))` with a Fenwick per column. Validate.

---

## Exercise 10 — Debugging drills

1. `lndsLength` with `<` instead of `<=` in the binary search — what is computed?
2. `tails[lo] = x` moved before `if (lo > 0) prev[i] = tailsIdx[lo-1]` with a combined record array — find the failing input.
3. `countLIS` with `queryMax(rank[i])` instead of `rank[i]-1` — what is counted?
4. `countLIS` with `cnt[]` defaulting to 1 instead of 0 — what changes?
5. `maxSubarrayAtMostK` with `dq[head] < i - k + 1` — find the smallest failing input.
6. `maxCircularSubarray` returning `Math.max(bestMax, total - bestMin)` without the guard, for `a = [-3]` — returns 0 instead of -3. Confirm.
7. `maxSumIncreasing` with `rank[i] = lowerBound(...)` (0-based, no `+1`) — Fenwick index 0 causes an infinite loop in `queryMax`. Confirm.
8. Patience sorting with `int[] tails = new int[n]` but `length` starting at 1 — off-by-one on `n = 1`.

---

## Exercise 11 — Deliverable

`MINI_PROJECT/PatienceVisualizer.java`: print the **patience-sorting tableau** — draw the cards in piles, one column per slot, so the classic picture appears (this is the visual that makes the "tails is not an LIS" idea concrete). For `a = [5,1,4,2,3,0]` the tableau should show `5` → `[1]` → `[1,4]` → `[1,2]` → `[1,2,3]` → `[0,2,3]`, and the number of piles is the answer.

Then `BENCHMARK/RunRace.java` with a markdown table: LIS `n²` / patience / LNDS / count-LIS / max-sum-IS, and Kadane / relaxed / circular / at-most-k / exactly-k, across the input families.

**Answer in writing:** state the one sentence that would prevent the most LIS bugs in a code review, and the one sentence for Kadane.