# Quiz — LIS & Kadane

15 questions. Each key gives the reason.

---

## Q1
State the patience-sorting invariant and explain why it makes the binary search valid.

<details><summary>Answer</summary>

> `tails[k]` = the minimum, over all strictly increasing subsequences of length `k+1` seen so far, of the last element.

**`tails` is strictly increasing in `k`.** Proof: a length-`k+2` subsequence's length-`k+1` prefix has a strictly smaller tail.

A sorted array admits `Θ(log n)` binary search, which is the entire source of the `Θ(n²) → Θ(n log n)` improvement. (It relies on **strict** increase; that is why `upperBound` — the non-decreasing variant — also keeps `tails` sorted.)
</details>

## Q2
Is `tails` an LIS? Give a counter-example.

<details><summary>Answer</summary>

**No.** `a = [1,4,2,3,0]`:

```
5→ (n/a)   1→[1]   4→[1,4]   2→[1,2]   3→[1,2,3]   0→[0,2,3]
```

Final `tails = [0,2,3]`. The `0` is at index 4, the `2` at index 2, the `3` at index 3 ⇒ positions `4,2,3` are not increasing ⇒ `[0,2,3]` **is not a subsequence**.

`t(k)` is a *minimum tail*, not a chain. Reconstructing requires `prev[]` + `tailsIdx[]`.
</details>

## Q3
Why do we **overwrite** `tails[p]` rather than keeping the old value?

<details><summary>Answer</summary>

A smaller tail is **strictly more useful**: any future element `x` that can extend the old tail (old `< x`) can also extend a smaller one (`new < x` is easier). So the new element dominates the old for all future queries, and keeping the old would be strictly worse.

That is also why `tails[p]` is the *minimum tail*, which is the quantity the recurrence needs.
</details>

## Q4
`lowerBound` vs `upperBound` in patience sorting.

<details><summary>Answer</summary>

| | computes |
|---|---|
| `lowerBound` (first `≥ x`) | longest **strictly increasing** subsequence |
| `upperBound` (first `> x`) | longest **non-decreasing** subsequence |

The difference is one comparison (`<` vs `<=` in the binary search). It is **silent** — the output is always increasing-looking — so the test data must contain duplicates to catch the swap.
</details>

## Q5
The LIS DP as a 2-D dominance query. How does each method reduce the inner loop?

<details><summary>Answer</summary>

Associate `(a[j], dp[j])` to each processed `j`. The query for `i` is "max `dp[j]` over points with `a[j] < a[i]`".

| method | query cost | total |
|---|---|---|
| linear scan | `Θ(n)` | `Θ(n²)` |
| patience (sorted `tails` + binary search) | `Θ(log n)` | `Θ(n log n)` |
| Fenwick on compressed values | `Θ(log n)` | `Θ(n log n)` |
| segment tree | `Θ(log n)` | `Θ(n log n)` |

Patience beats Fenwick on **cache behaviour**, not asymptotics: the binary search touches only the current length prefix, which is small and hot.
</details>

## Q6
Why does patience sorting not generalise to max-sum increasing subsequences?

<details><summary>Answer</summary>

The patience invariant is "the smallest tail is the most useful". For max-sum you need `max{ best[j] : j < i, a[j] < a[i] }` — the largest *sum*, and the two quantities are independent.

No sorted array can maintain both "ordered by tail" and "ordered by sum" at once, so you need a genuine dominance structure: a **Fenwick tree of maxima over compressed values**, `Θ(n log n)`.
</details>

## Q7
Kadane's recurrence and its correctness in one sentence.

<details><summary>Answer</summary>

`cur = max(a[i], cur + a[i])` because any subarray ending at `i` either **is** `[a[i]]` or **extends** a subarray ending at `i-1`; taking the best of the two is optimal by that exhaustive two-case argument.

`Θ(n)` time, `O(1)` space. Note this is a **linear-time discovery**, not a log-factor win over the brute force.
</details>

## Q8
Why is `best = 0` the classic Kadane bug?

<details><summary>Answer</summary>

`0` is the sum of the *empty* subarray. With `best = 0`, all-negative input returns `0`:

```
a = [-3, -1, -2]  ->  cur: -3, -1, -1   best: 0 (never negative)
```

The correct non-empty answer is `-1`. **Fix:** initialise `best = Long.MIN_VALUE` (or `a[0]`).

This is the same class of bug as `INF = Integer.MAX_VALUE` in lab `01`: a sentinel that collides with the answer domain.
</details>

## Q9
Circular maximum subarray: the formula and the edge case.

<details><summary>Answer</summary>

```
answer = max( maxNormalSubarray(a),  total − minNormalSubarray(a) )
```

A circular arc either does not wrap (a normal subarray) or does, in which case its complement is a normal subarray — so maximising the wrapping candidate means **minimising** the omitted part.

**Edge case:** if all elements are negative, `minNormal == total`, so the wrapping candidate is `0` — the empty complement, which is invalid. Guard with `if (bestMax < 0) return bestMax;`.

Test: `[-1,-2,-3]` must give `-1`, not `0`.
</details>

## Q10
Kadane's prefix-sum form, and why it is the same algorithm.

<details><summary>Answer</summary>

```
sum(a[i..j]) = P[j+1] − P[i]
max sum       = max_j P[j+1] − min_{i ≤ j} P[i]
```

Sweeping `j` left to right while maintaining `minPrefix` **is** Kadane: `cur` is `P[i] − running min`, `best` is the running max. Two independent derivations of the same `Θ(n)` scan — and a strong cross-check in tests (`assert kadane(a) == prefixSweep(a)` for every input).
</details>

## Q11
Maximum subarray with **at most** `k` elements, in `Θ(n)`. Why?

<details><summary>Answer</summary>

```
answer = max over i of ( P[i] − min{ P[j] : max(0, i−k) ≤ j ≤ i−1 } )
```

The inner `min` is a **sliding-window minimum of width `k`**. A monotonic deque maintains it in `Θ(n)` amortised (each index pushed once, popped at most once).

**Dominance-pop proof:** if `j₁ < j₂` and `P[j₁] ≥ P[j₂]`, then `j₂` is at least as small and expires later, so `j₁` can never be the argmin again.

For **exactly** `k`, no data structure is needed at all: `max_i (P[i] − P[i−k])`, a single `Θ(n)` loop.
</details>

## Q12
In the deque, why must the query be `P[i] − minWindow` and not `maxWindow − P[i]`?

<details><summary>Answer</summary>

A subarray sum is `P[end] − P[start]` with **`start < end`**. Maximising over all `end = i` means choosing the smallest possible `P[start]` among indices **before** `i`. So it is a window **minimum**, and it is subtracted.

`maxWindow − P[i]` would correspond to `P[start] − P[end]` with `start > end` — a negative-length subarray, which is meaningless.

The window is `[i−k, i−1]` (from `length = i − j ≤ k`), and getting that off by one silently computes "at most `k−1`".
</details>

## Q13
LIS with a difference bound `|a[i]−a[j]| ≤ d`. Why not patience?

<details><summary>Answer</summary>

The patience invariant only handles a **prefix** condition (`tails[p] < x`), i.e. a half-line of valid predecessors. A band `x − d ≤ a[j] < x` is a **window**, so you need a range-maximum query over a sliding value window: a segment tree or a `TreeMap<Integer,Integer>` keyed by value.

`Θ(n log n)` either way; patience is simply inapplicable.
</details>

## Q14
Grid LIS. Which move set allows patience sorting, and what is the complexity?

<details><summary>Answer</summary>

- **Right/down only:** patience sorting works, `Θ(mn log(mn))`, validated against `Θ(mn)` DP.
- **Right/down/diagonal:** same, but you must be careful that the per-row `tails` reflects the reachable frontier.
- **All four directions:** patience **fails** — a single `tails` array cannot express a 2-D reachability constraint. The right approach is to sort cells by value and run a Fenwick keyed by row, `Θ(mn log(mn))`.

**The general rule:** patience sorting encodes a *linear* ordering constraint. Two independent constraints need a dominance structure.
</details>

## Q15
Number of LIS. What state does the Fenwick hold, and what can overflow?

<details><summary>Answer</summary>

Each Fenwick node stores a **`(maxLen, countAtMaxLen)` pair** — not just a max. On query, a longer length replaces the running best; an equal length **accumulates** the count.

**Overflow:** the count can be `C(n, n/2) ≈ 2ⁿ/√n`. `long` overflows around `n ≈ 40`; use `BigInteger` or cap the test size near 30.

Enumerating **all** LIS costs `Θ(n log n + r)` where `r` is the output size — and `r` can be exponential, so that is optimal.
</details>