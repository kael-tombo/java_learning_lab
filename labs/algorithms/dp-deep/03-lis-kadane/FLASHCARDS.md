# Flashcards — LIS & Kadane

Format: **Q → A**.

---

| # | Question | Answer |
|---|----------|--------|
| 1 | LIS `Θ(n²)` DP state | `dp[i]` = LIS length **ending at index `i`** |
| 2 | LIS `Θ(n²)` transition | `dp[i] = 1 + max{dp[j] : j<i, a[j] < a[i]}` (strict) |
| 3 | Patience invariant | `tails[k]` = min tail of any length-`k+1` increasing subsequence so far |
| 4 | `tails` is | **strictly increasing** ⇒ sorted ⇒ binary search valid |
| 5 | `tails` is **not** | an LIS — `a=[1,4,2,3,0]` gives `tails=[0,2,3]`, not a subsequence |
| 6 | Patience update | `p = lowerBound(tails, x); tails[p] = x; if p == length: length++` |
| 7 | Why overwrite `tails[p]` | a smaller tail is easier to extend, so it dominates the old one |
| 8 | `lowerBound` vs `upperBound` | strictly increasing vs **non-decreasing** — one comparison |
| 9 | LIS complexity | `Θ(n log n)` time, `Θ(n)` space |
| 10 | LIS reconstruction needs | `tailsIdx[]` + `prev[]`; `prev` initialised to `-1` |
| 11 | Reconstruction starts from | `tailsIdx[length-1]`, **not** `a[length-1]` |
| 12 | LIS `n²`→`n log n` at `n=10⁶` | `10¹²` → `2·10⁷` |
| 13 | Patience vs Fenwick | same bound; patience wins on **cache** (small hot prefix) |
| 14 | LDS | patience with `upperBound` |
| 15 | LNDS | patience with `upperBound` |
| 16 | LIS reformulated as | a 2-D **dominance max query** over `(a[j], dp[j])` |
| 17 | Max-sum increasing subseq | `Θ(n log n)` **Fenwick**; patience does **not** generalise |
| 18 | Why patience fails for max-sum | you need max `sum`, not min `tail`; no array keeps both ordered |
| 19 | Count of LIS | `Θ(n log n)`; Fenwick node holds `(maxLen, count)` |
| 20 | Count of LIS overflow | `C(n,n/2)` ⇒ `long` breaks around `n ≈ 40` |
| 21 | All LIS | `Θ(n log n + r)`, `r` = output size (can be exponential) |
| 22 | LIS with gap bound `d` | range max over a sliding value **window** ⇒ segment tree, `Θ(n log n)` |
| 23 | Kadane recurrence | `cur = max(a[i], cur + a[i]); best = max(best, cur)` |
| 24 | Kadane time / space | **`Θ(n)` / `O(1)`** |
| 25 | Kadane vs brute force | a **linear** win, not a log win |
| 26 | Kadane `best` initialiser | `Long.MIN_VALUE` (or `a[0]`) — `0` breaks all-negative input |
| 27 | Relaxed vs non-empty Kadane | relaxed allows the empty subarray ⇒ `0` for all-negative |
| 28 | Kadane prefix-sum form | `max_j P[j+1] − min_{i≤j} P[i]` — the same scan |
| 29 | Circular subarray | `max( maxNormal, total − minNormal )` |
| 30 | Circular all-negative edge case | `minNormal == total` ⇒ wrapping candidate is `0`; guard `if (bestMax < 0)` |
| 31 | Exactly-`k` subarray | `Θ(n)`, no structure: `P[i] − P[i−k]` |
| 32 | At-most-`k` subarray | sliding min of `P` ⇒ **monotonic deque**, `Θ(n)` |
| 33 | Deque window | `[i−k, i−1]` — off by one ⇒ silently computes `k−1` |
| 34 | Deque dominance pop | `j₁ < j₂` and `P[j₁] ≥ P[j₂]` ⇒ `j₁` can never be the argmin again |
| 35 | Deque insert/query order | push, then expire; swapping shifts the window |
| 36 | Subarray sum is | `P[end] − P[start]` with `start < end` ⇒ window **minimum**, subtracted |
| 37 | Grid LIS right/down | patience, `Θ(mn log(mn))` |
| 38 | Grid LIS all four directions | patience **fails**; sort by value + Fenwick keyed by row |
| 39 | Largest rectangle in a matrix | **not** Kadane; histogram stack, `Θ(nm)` |
| 40 | LDS/LNDS complexity | `Θ(n log n)` |
| 41 | LIS streaming | patience with a bounded `tails` buffer |
| 42 | Kadane streaming | naturally online, `O(1)` state |
| 43 | The `Θ(n²)` DP is still worth writing | it is the **oracle** for every variant |
| 44 | Duplicate values in the test data | **essential** — otherwise the `<`/`<=` bug is invisible |
| 45 | Common LDS-by-nesting trick | `LDS(a) = LIS(reverse(a))` |
| 46 | LIS of strictly decreasing | patience with `upperBound`, or `LIS(-a)` |
| 47 | Max sum circular, `total = 0` | answer is `max(maxNormal, −minNormal)` — fine, no special case |
| 48 | Kadane with `long` | required for `n ≥ 10⁵` × `10⁹` values |
| 49 | `cur` initialiser in Kadane | `0` works with `max(x, cur+x)`; `0` is wrong with `max(0, cur+x)` |
| 50 | LIS answer is | the number of occupied `tails` slots (`length`) |
| 51 | `tails` array size | `n` — every element can in principle open a new slot |
| 52 | LIS `Θ(n²)` DP vs patience, best case | both fast on sorted input; `Θ(n²)` still pays `n²/2` |
| 53 | Counting the DP oracle's cost | `Θ(n²)` — only usable for `n ≤ 10⁴` |
| 54 | Brute-force LIS oracle | `Θ(2ⁿ)` — `n ≤ 22` |
| 55 | Brute-force Kadane oracle | `Θ(n²)` all subarrays |
| 56 | Brute-force circular oracle | enumerate all arcs: `Θ(n²)` |
| 57 | LIS on a sorted array | patience runs in `Θ(n log n)` still, but with a perfect branch pattern |
| 58 | LIS on a strictly decreasing array | length 1; patience does `p = 0` every time ⇒ `Θ(log 1) = Θ(1)` per element |
| 59 | LIS on all-equal array | length 1 (strict) or `n` (non-decreasing) |
| 60 | Review sentence for LIS | **`tails` is a sorted array of minimum tails, never a subsequence** |
| 61 | Review sentence for Kadane | **`best` must start at `Long.MIN_VALUE`, because `0` is the empty subarray** |
| 62 | Unified view | "longest/max run satisfying a monotone condition"; the optimisation is always replacing the inner `max` with a maintained aggregate |
| 63 | The 3 DP forms of max subarray | brute `Θ(n²)`, prefix sums `Θ(n²)`, Kadane `Θ(n)` |
| 64 | Fenwick vs patience for LIS | identical asymptotics, different memory access patterns |
| 65 | When to use the segment tree | whenever the valid-predecessor set is a *window*, not a *prefix* |

## Self-test (one line each)

1. Patience invariant and why it enables binary search? → **`tails[k]` = min tail of length-`k+1` subsequences, and `tails` is strictly increasing ⇒ sorted**
2. Is `tails` an LIS? → **No** — `[1,4,2,3,0]` gives `tails = [0,2,3]`, whose positions are `4,2,3` (not increasing) ⇒ not a subsequence
3. Kadane's `best` initialiser and the bug it prevents? → **`Long.MIN_VALUE`** — `0` is the empty subarray, so all-negative input wrongly returns `0`
4. Circular max subarray and its edge case? → **`max(maxNormal, total − minNormal)`**; if all elements are negative the second term is `0`, so guard with `if (bestMax < 0) return bestMax`
5. Why doesn't patience sort max-sum increasing subsequences? → **It needs the maximum *sum*, not the minimum *tail*; no sorted array keeps both ordered ⇒ use a Fenwick**