# Flashcards — Comparison Sorts

Format: **Q → A**. Cover the answer column mentally, then check.

---

| # | Question | Answer |
|---|----------|--------|
| 1 | Insertion sort best case? | Ω(n) — one comparison per element, inner `while` exits immediately on sorted input |
| 2 | Insertion sort worst case? | O(n²) comparisons, O(n²) shifts — reverse-sorted input |
| 3 | What does insertion sort's inner-loop count equal? | The inversion count of the array |
| 4 | Is insertion sort stable? | Yes — the guard is `a[j] > key` (strict), equal elements are never passed |
| 5 | Why hoist `key` out of the inner loop? | Inner loop becomes a pure `memmove`; JIT can vectorise; avoids re-reading `a[i]` |
| 6 | When is the sentinel trick (drop `j >= 0`) valid? | Only when `a[0]` is the global minimum, which requires an O(n) pre-scan |
| 7 | Selection sort comparison count? | Exactly `n(n-1)/2` — *input independent* |
| 8 | Selection sort's only virtue? | At most `n-1` swaps (useful when a swap is a network/block write) |
| 9 | Is naive selection sort stable? | No. `<` puts the minimum at the first minimum index and swaps it right |
| 10 | Stable selection sort exists — what's the cost? | Θ(n²) *writes*, which is worse than stable insertion sort's Θ(n) writes |
| 11 | Bubble sort best case? | Ω(n) **only if** you keep the `swapped` flag and early-exit |
| 12 | Bubble sort invariant after a pass? | The top `k` largest elements are in final sorted positions at the tail |
| 13 | Why is bubble sort quadratic on reverse-sorted input? | Every element must move to the far end, so every pass does `n-1` swaps |
| 14 | What is a "turtle" input? | A small value deep in the array that must travel to the front; bubble sort handles it in O(n²), cocktail shaker in O(n) |
| 15 | Cocktail shaker's core change? | Alternate forward and backward passes, so small values get pulled to the front too |
| 16 | Comb sort's mechanism? | Bubble sort with a shrinking gap (÷1.3), finishing with gap = 1 |
| 17 | Comb sort's proven complexity? | **None** — it is heuristic. Do not quote O(n log n) |
| 18 | Shell sort's core operation? | For each gap `h`, a gapped insertion sort → `h`-sorted sequences |
| 19 | What does "h-sorted" mean? | Every `h`-th subsequence `a[h], a[2h], a[3h], ...` is independently sorted |
| 20 | Why is Shell sort fast at the last gap? | The array is already nearly-sorted, so gap-1 insertion sort runs in near-Θ(n) |
| 21 | Shell's sequence worst case? | O(n²) — no better than insertion sort. Avoid it |
| 22 | Hibbard sequence and bound? | `2^k - 1`, gives O(n^{3/2}) |
| 23 | Knuth sequence and bound? | `(3^k - 1)/2` i.e. `3h+1`, gives O(n^{3/2}) |
| 24 | Sedgewick sequence and bound? | `4^k + 3·2^{k-1} + 1`, interleaved with `2·4^k - 3·2^k + 1`, gives O(n^{4/3}) |
| 25 | Pratt sequence and bound? | All `2^p·3^q`, gives O(n log² n) — best proven known, but Θ(log²n) gaps |
| 26 | Shell sort pitfall #1? | The gap sequence must not be truncated below its first term — you silently get Shell's Θ(n²) |
| 27 | Shell sort pitfall #2? | Inner `while` must test `a[j - gap] > key`, not `a[j] > key` |
| 28 | Lower bound for any comparison sort? | `ceil(log2(n!))` comparisons; ≈ `n log2 n - 1.44n` for large n |
| 29 | `log2(n!)` computed without a loop? | `lgamma(n + 1) / log(2)` |
| 30 | Optimal (non-uniform) comparison decision tree? | Merge sort's worst case attains `log2(n!) + O(n)` — asymptotically optimal |
| 31 | Definition of *stable*? | Equal keys retain their original relative order |
| 32 | Definition of *adaptive*? | Runs in O(n + k) or O(n log k) when there are `k` runs / `n-k` inversions |
| 33 | Which comparison sorts are adaptive? | Insertion, Shell, bubble (with flag), TimSort |
| 34 | Which are not? | Selection sort (always n(n-1)/2) |
| 35 | `Arrays.sort(int[])` uses what? | Dual-pivot quicksort — not stable (irrelevant for primitives, no identity) |
| 36 | `Arrays.sort(T[])` uses what? | TimSort — stable, adaptive, allocates a run buffer of ≤ 1/2 n |
| 37 | Why TimSort is stable AND adaptive? | It finds natural runs and merges them with stable galloping merges |
| 38 | Why is `Arrays.sort(T[])` not safe against adversarial input? | Non-randomised TimSort has known O(n log n) worst case but *engineered* worst cases still cost ~5–10× |
| 39 | Small-array cutoff used by library sorts? | ~32–47 elements, below which insertion sort is faster than recursing |
| 40 | Why is insertion sort used below the cutoff? | No recursion, no allocation, cache-friendly, and near-optimal on nearly-sorted blocks |
| 41 | Comparison count for insertion sort on input with `k` inversions? | Exactly `n - 1 + k` |
| 42 | Binary insertion sort's tradeoff? | Θ(n log n) comparisons but still Θ(n²) moves; `arraycopy` memmove often wins on small n |
| 43 | Binary insertion sort + stable? | Must binary-search the **leftmost** insert position |
| 44 | Counting sort stable if it scans input forward? | Yes — scan backward from the end to be safe with prefix-sum offsets |
| 45 | Which "comparison" sort is *not* a comparison sort? | None of these four — all four are comparison sorts; counting/radix are not |
| 46 | Space complexity of all four? | O(1) auxiliary — all in-place |
| 47 | In-place definition? | O(1) or O(log n) extra space; merge sort is O(n) and therefore *not* in-place |
| 48 | Best case for selection sort? | Θ(n²) — there is no adaptive behaviour at all |
| 49 | Organ-pipe input? | Increasing to the middle then decreasing — defeats bubble sort, tricky for Shell |
| 50 | Sawtooth / few-unique input? | Few distinct keys — insertion and comb sort do well, counting sort would be O(n) |
| 51 | When does Shell sort beat insertion sort? | n ≥ 10⁴ with random keys and a Sedgewick or Pratt gap sequence |
| 52 | Practical niche of hand-written sorts in Java? | Embedded/no-heap contexts, records with in-place key extraction, tiny arrays |
| 53 | When must you write your own comparison sort? | When the comparison isn't a `Comparator` — e.g. comparing into a GPU buffer or a remote store |
| 54 | Counting sort used in? | Radix sort's inner routine; small-integer-range sorts; 2-pass radix for 16-bit keys |
| 55 | How do you count *comparisons* in Java? | Wrap the comparison in a lambda/field with a `++` side effect |
| 56 | Why not use a comparator with side effects in a tree set? | TreeSet assumes the comparator is a strict weak ordering; side effects corrupt ordering |
| 57 | Instrumenting swaps — where? | Inside the `swap` helper; count with a `long` field, reset between runs |
| 58 | Hotspot's sort for tiny `int[]`? | Insertion sort is chosen by `Arrays.sort`'s dual-pivot quickSort below ~47 elements |
| 59 | Does JIT replace `Arrays.sort(int[])`? | Yes, intrinsified via `_dualPivotQuicksort`; hand-rolled code cannot beat it |
| 60 | Rule of thumb for choosing a comparison sort? | Library first; insertion for ≤ 32 elements; otherwise TimSort/`Arrays.sort` — you will rarely beat it |

## Quick self-test

Answer these five in one line each, then check the table:

1. Which of the four has input-independent comparison count? → **Selection sort** (exactly `n(n-1)/2`)
2. What proof obligation makes insertion sort stable? → **Strict `>` in the guard**, so equal keys are never swapped past each other
3. Gap sequence with the best proven bound? → **Pratt**, `2^p 3^q`, O(n log² n)
4. Lower bound on comparisons for sorting 20 distinct keys? → `ceil(log2(20!)) = 62`
5. What does Shell sort's *last* pass do and why is it cheap? → **Gap-1 insertion sort** on an array already sorted along every gap subsequence, so few inversions remain