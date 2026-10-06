# Flashcards — Order Statistics

Format: **Q → A**.

---

| # | Question | Answer |
|---|----------|--------|
| 1 | Order statistic definition | the `k`-th smallest element of a multiset |
| 2 | Selection recurrence | `T(n) = T(αn) + Θ(n)` |
| 3 | Selection complexity | `Θ( n / max(α, 1−α) )` — linear for fixed `α` |
| 4 | Randomised quickselect comparisons | **`2(1 + ln 2) n = 3.386 n`** |
| 5 | Randomised quicksort comparisons | `2 ln n · n = 1.3863 n log₂ n` |
| 6 | Speedup of selection over sorting at `n = 10⁶` | ≈ **8.2×** (comparison count) |
| 7 | Why selection is linear and sorting is not | geometric series `Σ 2^{-i} < 2` converges; `Σ 1 = log n` does not |
| 8 | Quickselect worst case | `Θ(n²)` with a deterministic adversarial pivot |
| 9 | The only defence against an adversarial pivot | **randomisation** — pivot independent of the input |
| 10 | Stack safety for recursive quickselect | recurse on the **smaller** side, loop on the larger ⇒ `O(log n)` stack |
| 11 | Smaller-side-recurse fixes time? | **No** — only the stack; `Θ(n²)` remains |
| 12 | Median-of-medians pivot guarantee | ≥ `3n/10` discarded on **each** side; survivor `≤ 7n/10` |
| 13 | Median-of-medians recurrence | `T(n) = T(n/5) + T(7n/10) + Θ(n)` |
| 14 | Akra–Bazzi `p` for MoM | `(0.2)^p + (0.7)^p = 1 ⟹ p ≈ 3.3864` ⇒ `Θ(n)` |
| 15 | Median-of-medians comparisons | `≈ 3.386 n` — the same as randomised quickselect's expectation |
| 16 | Median-of-medians wall-clock vs quickselect | ~**6× slower** (extra passes, recursion, no locality) |
| 17 | Why groups of 5 | smallest `2k+1` with `k ≥ 2` giving a linear guarantee |
| 18 | Groups of 3 would give | `p ≈ 2.29` ⇒ `Θ(n^2.29)` — **worse than sorting** |
| 19 | The discard factor must exceed | `1/3`, else `p < 2` and the algorithm superlinear |
| 20 | When to ship median-of-medians | worst-case guarantees: real-time, move-to-front, adversarial inputs |
| 21 | 3-way partition benefit for selection | `Θ(n log d)`; all-equal input becomes `Θ(n)` instead of `Θ(n²)` |
| 22 | Interpolation select | pivot estimated from value distribution; `Θ(n)` uniform, bad adversarial |
| 23 | Guarded interpolation select | track whether the pivot tracked `i/n`; fall back to quickselect if not |
| 24 | Fenwick k-th complexity | **`Θ(log n)`** — `⌊log₂ n⌋ + 1` iterations |
| 25 | Why binary lifting is not `Θ(log² n)` | `tree[idx+step]` gives the block count *during* the descent |
| 26 | Fenwick build cost | `Θ(n)` with the linear construction |
| 27 | Fenwick limitation | no negative point values — breaks `findByOrder`'s monotonicity |
| 28 | Order-statistic tree | balanced BST + subtree sizes; `select`, `rank`, `insert`, `delete` all `Θ(log n)` |
| 29 | Wavelet tree | `Θ(log σ)` query, `n log σ` **bits** of space — used by suffix arrays |
| 30 | Top-k heap: k smallest | **max**-heap of size `k` — rejection test is `O(1)` |
| 31 | Top-k heap: k largest | **min**-heap of size `k` |
| 32 | The heap-ordering rule | the heap's order must be the **negation** of the "keep" predicate |
| 33 | Wrong heap type cost | `Θ(n log k)` unconditionally instead of `Θ(n + A log k)` — 10–20× slower |
| 34 | Top-k heap worst case | `Θ(n log k)` time, `O(k)` space |
| 35 | Top-k heap expected (random input) | `Θ(n + k·ln(n/k)·log k)` ≈ `Θ(n)` for small `k` |
| 36 | Repeated quickselect cost | `Θ(kn − k²/2)` |
| 37 | Repeated quickselect vs heap crossover | **`k ≈ 30`** |
| 38 | `k = 1` special case | one pass, `Θ(n)`, `O(1)` space — no heap needed |
| 39 | Quickselect destroys input | it only partitions; relative order within each side is lost |
| 40 | More than ~2 quantiles needed | sort once and index — cheaper than repeated destructive selection |
| 41 | Streaming k-th, `O(k)` memory | max-heap of size `k`; `peek()` **is** the `k`-th smallest |
| 42 | Reservoir sampling | uniform random `k`-sample, `O(k)` memory, one pass, `Θ(n)` expected |
| 43 | Reservoir correctness invariant | after `seen` items, the reservoir is a uniform random `k`-subset |
| 44 | Reservoir is not an order statistic | you must sort the reservoir and accept `O(√(B/N))` error |
| 45 | Weighted order statistics | partition on weight prefix sums instead of values; used for retried requests |
| 46 | Parallel selection depth | `Θ(n/p + p)` |
| 47 | Optimal core count for parallel selection | `p = √n` (theory); you are bandwidth-bound well before that |
| 48 | Parallel selection measured speedup (8 threads) | ≈ **5×** |
| 49 | Parallel median's shared counter | must be `LongAdder`/`AtomicInteger`/per-thread slots — `int++` is a race |
| 50 | Real-world percentile trap | exact quantiles need `Θ(n)` memory; use t-digest/KLL for streams |
| 51 | Emit sample count with quantiles | otherwise a p99 from 400 samples is indistinguishable from one from 10⁹ |
| 52 | `Arrays` has `nth_element`? | **No** — use fastutil/hppc or a bounded heap |
| 53 | Java min/max idiom | single pass, `Θ(n)`, `O(1)` — always check this first |
| 54 | Java standard-library route to k-th | `Arrays.sort` + index, or `PriorityQueue.nsmallest/nlargest` |
| 55 | `PriorityQueue.nsmallest` complexity | `Θ(n log k)` via a bounded max-heap |
| 56 | Organ-pipe input vs interpolation select | catastrophic — the value distribution is nowhere near uniform |
| 57 | Quickselect's `Θ(n²)` failure on sorted input | only with a first/last/median-of-3 pivot; **randomised is fine** |
| 58 | Median-of-3 killer construction | build recursively so the median-of-3 is always the extreme |
| 59 | Wall-clock vs comparison-count gap | cache behaviour — sorting's merges are sequential; selection's passes still touch every line |
| 60 | Rule of thumb | one value → quickselect; many values → heap; both values + order preserved → sort |

## Self-test (one line each)

1. Randomised quickselect comparison count? → **`3.386 n`**
2. Median-of-medians pivot guarantee? → **≥ `3n/10` discarded on each side, survivor `≤ 7n/10`**
3. Why groups of 5? → **smallest `2k+1` giving a linear guarantee (`p ≈ 3.39`); 3 gives `p ≈ 2.29`**
4. Top-k heap type for k smallest, and why? → **max-heap** — `peek()` is the worst of the k best, so rejection is `O(1)`**
5. Fenwick k-th complexity and the trick? → **`Θ(log n)`** — binary lifting gets the block count during the descent