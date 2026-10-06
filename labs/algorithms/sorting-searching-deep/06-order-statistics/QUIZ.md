# Quiz — Order Statistics

15 questions. Each key gives the reason.

---

## Q1
Why is selection `Θ(n)` when sorting is `Θ(n log n)`? Give the recurrence-level argument.

<details><summary>Answer</summary>

Quicksort: `T(n) = 2T(n/2) + Θ(n)` — every level re-visits the **whole** array, so the work is `n` per level × `log n` levels = `Θ(n log n)`.

Selection: `T(n) = T(n/2) + Θ(n)` — recurse on **one** side only, so level `i` costs `n/2^i` and the total is `n(1 + 1/2 + 1/4 + …) < 2n = Θ(n)`.

The geometric series converges; the constant series does not. That is the whole difference.
</details>

## Q2
Give the exact expected number of comparisons for randomised quickselect and for randomised quicksort.

<details><summary>Answer</summary>

**Quickselect: `2(1 + ln 2)·n = 3.3863 n`.**
**Quicksort: `2 ln n · n = 1.3863 n log₂ n`.**

At `n = 10⁶`: quickselect `≈ 3.39·10⁶`, quicksort `≈ 2.76·10⁷` — a **8.2×** advantage for selection.

The constants are obtained from the respective recurrences by the standard "subtract consecutive equations and telescope with a weight" argument; see `MATH_FOUNDATION.md` §2.
</details>

## Q3
Generalise: pivot splits `αn` / `(1−α)n`. What is `T(n)`, and what does it say about robustness?

<details><summary>Answer</summary>

`T(n) = T(αn) + Θ(n)` ⇒ `T(n) = Θ( n / max(α, 1−α) )`.

Linear for **any** fixed `α < 1` — so quickselect is robust to systematically mediocre pivots. `α = 0.7` gives `3.33n`; `α = 0.9` gives `10n`.

Only an *adversarially* bad pivot (`α → 0`) breaks it. **This is the crux: the algorithm is not defeated by "bad luck", only by an adversary who can predict the pivot.**
</details>

## Q4
State the median-of-medians pivot guarantee and prove the `7/10` number.

<details><summary>Answer</summary>

> **At least `3n/10` elements are discarded on *each* side, so the surviving side is at most `7n/10`.**

Proof for `n` divisible by 10: there are `n/5` group medians. The median `M` of those has ≥ `n/10` medians `≥ M` and ≥ `n/10` `≤ M`. Each such median `≥ M` brings **2** more elements of its 5-group that are also `≥ M`, giving `≥ n/5` elements `≥ M`. Symmetrically `≥ n/5` elements `≤ M`. So `#< M ≤ n − n/5 − 1 − n/5 = 3n/10`, and similarly for `> M`.
</details>

## Q5
Akra–Bazzi: solve `T(n) = T(n/5) + T(7n/10) + Θ(n)`.

<details><summary>Answer</summary>

Akra–Bazzi: `T(n) = Θ(n^p (1 + ∫₁ⁿ g(u)/u^{p+1} du))` where `p` solves `Σ aᵢbᵢ^p = 1`.

Here: `(1/5)^p + (7/10)^p = 1`. Solving numerically gives **`p ≈ 3.3864`**.

Since `g(n) = Θ(n)` and `p > 1`, the integral converges to a constant, so **`T(n) = Θ(n)`**.
</details>

## Q6
Why groups of **5** and not groups of 3 or 7?

<details><summary>Answer</summary>

Groups of size `2k+1` give a discard guarantee of `(k−1)/(2k+1)` per side:

| group size | survivor | Akra–Bazzi `p` | Result |
|------------|----------|----------------|--------|
| 3 (`k=1`) | `4/5` | ≈ 2.29 | **`Θ(n^2.29)` — worse than sorting** |
| 5 (`k=2`) | `7/10` | ≈ 3.39 | `Θ(n)` ✓ |
| 7 (`k=3`) | `10/14` | ≈ 6.4 | `Θ(n)`, higher constant |

**5 is the smallest group size giving a linear guarantee**, so the `Θ(n/5)` grouping overhead is minimised. The choice is forced, not conventional.
</details>

## Q7
If median-of-medians has the same comparison count as randomised quickselect, why is it 6× slower in practice?

<details><summary>Answer</summary>

- **Extra passes.** Grouping (sorting `n/5` groups of 5) + collecting the medians + the partition = ~3 passes, vs quickselect's 1.
- **Recursion on a fresh array.** The median-of-medians recursion allocates `Θ(n/4)` total scratch (`n/5 + n/25 + …`) per top-level call → GC pressure and cold cache lines.
- **No locality.** The `T(n/5)` sub-call operates on a scattered set of medians, not a contiguous range.
- **Same count, different structure.** The comparison count hides that median-of-medians' comparisons are spread over more distinct memory locations.

Deterministic `Θ(n)` for `~3×` the wall-clock is a trade you rarely want — except when you need the guarantee.
</details>

## Q8
Median-of-3 quickselect has an adversary input that makes it `Θ(n²)`. Why can no adversary do this to randomised quickselect?

<details><summary>Answer</summary>

Median-of-3 is a **deterministic function of the array contents**. An adversary can compute, for every possible subarray, which triple median-of-3 would choose, and recursively construct an array whose median-of-3 is always the extreme. That input gives `Θ(n²)`.

A randomised pivot is chosen from a distribution **independent of the input**. Whatever the adversary builds, the pivot rank is uniform, so the recurrence is `E[T(n)] = 3.386n` regardless. The probability of a bad run is `Θ(poly(1/n))` — astronomically small, and *measurable*.
</details>

## Q9
Why does quickselect **destroy** its input, and what breaks if you call it twice for different `k`?

<details><summary>Answer</summary>

Selection is implemented as a sequence of partitions; only elements provably `≤` the answer end up left of the pivot. The *relative order within each side* is destroyed — that information was traded away to get `Θ(n)`.

Calling it twice for `k₁` then `k₂` is not merely "wrong" — the second call may still be correct (quickselect's invariants survive), but it will be **slower** (the range is already partitioned so early rounds are cheap, which is actually fine) and, critically, **you cannot rely on the array still matching the original**.

For two values: sort once (`Θ(n log n)`) and index, or run quickselect twice on copies. Practical rule: if you need more than ~2 quantiles, sorting once is cheaper than destroying the data repeatedly.
</details>

## Q10
For top-k, why must the heap be a **max**-heap when you want the k *smallest*?

<details><summary>Answer</summary>

The rejection test must be `O(1)`. With a max-heap of the current k best, `peek()` is the **largest** of them — exactly the element most likely to be beaten. So `x >= peek()` → reject in one comparison.

With a min-heap, `peek()` is the smallest of the k best, and **every** incoming `x ≥` it still might belong, so you cannot reject cheaply. You would pay `Θ(log k)` for every element: `Θ(n log k)` unconditionally, ~10–20× slower at `k = 10⁶`.

The general rule: **the heap's ordering must be the negation of the "keep" predicate.**
</details>

## Q11
Bounded-heap top-k on random input: why is it effectively `Θ(n)` rather than `Θ(n log k)`?

<details><summary>Answer</summary>

After `i` elements, the heap root is the `k`-th smallest of those `i`, so a new element replaces it with probability `k/(i+1)`. Expected accepted count:

```
E[A] = Σ_{i=k}^{n-1} k/(i+1) = k·ln(n/k)
```

Total: `Θ(n)` `O(1)` rejections + `Θ(k ln(n/k))` acceptances at `Θ(log k)` each.

For `n = 10⁶`, `k = 10`: `E[A] ≈ 115` out of a million. The `log k` factor only bites when `k = Θ(n)`.
</details>

## Q12
`n = 10⁶`, `k = 100`: quickselect-repeated vs bounded heap vs sort. Which wins and why?

<details><summary>Answer</summary>

Theoretically: repeated quickselect costs `Θ(kn − k²/2) ≈ 10⁸` comparisons; the heap costs `Θ(n log k) = 7·10⁶`; sorting costs `2.76·10⁷`.

**The heap wins by ~14×.** The crossover is around `k ≈ 30`: below that, quickselect's `3.386n` per value beats `n log k`; above it, the heap's `log k` per element beats `3.386 k` per value.

This crossover is non-obvious and worth memorising: **quickselect is for one value, heaps are for many.**
</details>

## Q13
Binary lifting in a Fenwick tree: why `Θ(log n)` and not `Θ(log² n)`?

<details><summary>Answer</summary>

The naive approach binary-searches the prefix-sum array, and each prefix query costs `Θ(log n)` ⇒ `Θ(log² n)`.

Binary lifting instead descends the **interval-decomposition tree** directly. At step `step`, `tree[idx + step]` is exactly the sum of the next block of size `step`. One comparison both **tests** whether to skip the block and **updates** the remaining rank. There are `⌊log₂ n⌋ + 1` steps and no inner loop.

Same trick as in a merge-sort stack: the information needed to narrow the search is available *as you narrow it*.
</details>

## Q14
You need p50, p95, p99, and p99.9 of a latency stream, exactly, with 512 MB of RAM, from 10⁹ samples.

<details><summary>Answer</summary>

**Exact quantiles require `Θ(n)` memory** — any exact `k`-th needs either the data or a structure sized by it. `10⁹` ints is 4 GB, over budget.

Therefore **exact is impossible** and you must choose:

1. **Bounded-memory estimate (KLL / t-digest / DDSketch):** `O(1)`–`O(ε)` memory, relative error `ε` on quantiles. This is what Prometheus `histogram_quantile` and Datadog do.
2. **Downsample:** keep every 100th sample, compute exact quantiles on the sample, report the sample count. Error `O(√(B/N))`.

**Also:** emit the sample count and buffer size with every quantile so consumers can distinguish "p99 = 5 ms" from "p99 = 5 ms estimated from 400 samples". That distinction is the whole difference between a useful and a misleading SLO dashboard.
</details>

## Q15
Parallel selection: what is the depth bound, and how many cores are optimal?

<details><summary>Answer</summary>

Split into `p` blocks. Each thread selects its block's median in `Θ(n/p)`. Selecting the median of the `p` block medians costs `Θ(p)` (or `Θ(log p)` with another parallel step). Depth:

```
D(p) = Θ( n/p + p )
```

Differentiate: `−n/p² + 1 = 0 ⟹ p = √n`, giving **`D = Θ(√n)`** versus `Θ(n)` sequential.

**Practical caveat:** you will not have `√n` cores. At `n = 10⁸`, `√n = 10⁴` — but a real machine has ≤ 64. With `p = 64`, `D = Θ(10⁸/64 + 64) ≈ 1.6·10⁶`, a 64× depth reduction but bounded by **memory bandwidth**, not cores. Measured 8-thread speedup ≈ 5×.
</details>