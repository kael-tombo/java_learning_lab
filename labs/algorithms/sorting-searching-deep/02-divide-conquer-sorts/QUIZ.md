# Quiz — Divide & Conquer Sorts

15 questions. Each key gives the reason.

---

## Q1
Apply the Master theorem to merge sort's recurrence `T(n) = 2T(n/2) + Θ(n)`. Which case applies and what is the result?

<details><summary>Answer</summary>

`a = 2`, `b = 2`, so `n^(log_b a) = n^(log₂2) = n`. Since `f(n) = Θ(n) = Θ(n^(log_b a))`, this is **Case 2**, giving **`T(n) = Θ(n log n)`**.
</details>

## Q2
Why does merge sort have the same bound on sorted and reverse-sorted input while quick sort does not?

<details><summary>Answer</summary>

Merge sort's split is a fixed **index midpoint**, so both subproblems always have size `⌊n/2⌋, ⌈n/2⌉`; the merge is always Θ(n). Nothing about the data changes either term.

Quick sort's split depends on the **data**: a fixed pivot on sorted input gives `(0, n-1)` every time → `T(n) = T(n-1) + Θ(n) = Θ(n²)`.
</details>

## Q3
Your merge step uses `if (a[i] < a[j])`. What property is lost and what test detects it?

<details><summary>Answer</summary>

**Stability.** On ties the element from the right run is taken first, reversing the original order of equal keys.

Detect it by packing `(value, originalIndex)` into a `long`, sorting, and checking that indices are ascending within each equal-value run. Also assert that the output *multiset* is unchanged — a naive "sorted + same multiset" test passes, which is why stability needs its own test.
</details>

## Q4
State the exact Lomuto partition invariant and explain precisely why it makes all-equal input quadratic.

<details><summary>Answer</summary>

**Invariant:** after `partition` returns `p`, `a[k] <= a[p]` for all `k < p` in range and `a[k] >= a[p]` for all `k > p`, with `a[p] == v`.

The guarantee on the right is `>=`, **not** `>`. With all elements equal to `v`, the `a[j] <= v` branch fires for every `j`, so `i` ends at `hi`: the split is `(lo, hi-1)` and `(hi, hi)` — i.e. `(0, n-1)`. Hence `T(n) = T(n-1) + Θ(n) = Θ(n²)`.
</details>

## Q5
Give the correct recursion for Hoare partition and state the bug that the "obvious" recursion causes.

<details><summary>Answer</summary>

Correct: `quickSort(a, lo, j); quickSort(a, j + 1, hi);`

Hoare returns the index `j` such that the pivot lies in `(lo, j] ∪ [j+1, hi]` — a *boundary*, not the pivot's position. Using `lo..j-1` / `j+1..hi` excludes position `j` from the recursion on one side and can leave elements unsorted or loop forever (e.g. on `[5,5,5,5]`).
</details>

## Q6
Why is randomised pivot selection a *guarantee* while median-of-3 is only a *heuristic*?

<details><summary>Answer</summary>

Randomisation picks the pivot independently of the input, so the adversary cannot shape the outcome. It gives `Θ(n log n)` **expected** time with failure probability ≤ `1/n`, on *every* input including adaptive ones.

Median-of-3 is a deterministic rule: an adversary who knows it can construct an input whose median-of-3 is always the extreme, forcing `Θ(n²)`. "No known bad input" ≠ "no bad input".
</details>

## Q7
Trace the 3-way partition on `[5, 5, 5, 1, 5, 5]` with pivot `v = a[0] = 5`. What are `lt`, `gt` after the loop, and how much recursion happens?

<details><summary>Answer</summary>

Every element equals the pivot, so the `else` branch fires every time: `i` goes `0→6` with `lt = 0`, `gt = 5` unchanged. Exit condition `i > gt` holds.

Result: the whole array is in the `== v` region, both recursive ranges are empty, **zero recursion**. One Θ(n) pass.
</details>

## Q8
Why must `i` not be incremented after `swap(a, i, gt--)` in 3-way quicksort?

<details><summary>Answer</summary>

Because the element that arrives at index `i` from position `gt` has **not yet been examined**. Incrementing `i` skips it, so it is never classified and can end up in the wrong region — producing an unsorted result.

Correct: `if (c < 0) swap(a, lt++, i++); else if (c > 0) swap(a, i, gt--); else i++;`
</details>

## Q9
Bottom-up merge sort with `n = 5`: what happens during the width-4 pass? What guard is needed?

<details><summary>Answer</summary>

The last group is `[4, 4]` (a single element). Its `mid = lo + width - 1 = 3`, and `hi = Math.min(lo + 2*width - 1, n-1) = 4`, so `mid = 3 < hi = 4` — the merge is valid but degenerate.

The real bug case is when the trailing run is empty: `mid >= hi`. You must guard with `if (mid < hi)` or clamp `hi = Math.min(...)` and skip. Without the guard you call `merge` with an inverted or empty range and, depending on the loop structure, read `a[mid+1]` out of bounds.
</details>

## Q10
Give an O(1)-auxiliary-space, stable merge sort over a singly linked list. Why must it be bottom-up?

<details><summary>Answer</summary>

Intrusive merge sort: recursively (or iteratively) split the list at its midpoint and *relink* `next` pointers to merge — no element copies, so no Θ(n) buffer.

It must be **bottom-up** because top-down recursion depth is Θ(n) on a list (there is no array index halving), giving Θ(n) stack. Bottom-up maintains a queue of runs of length 1, 2, 4, ... and keeps stack at O(1).
</details>

## Q11
Merge sort's `merge` writes each element exactly twice. Why is this the decisive practical argument for quicksort on large in-memory arrays?

<details><summary>Answer</summary>

Memory bandwidth, not instruction count, is the limit. Merge sort streams `a → aux` then `aux → a`, doubling bytes moved and touching two working sets. Quicksort partitions in place — one sequential working set, ~half the writes.

On `int[10⁸]` this is the difference between ~1.6 GB and ~0.8 GB of traffic per full pass, which is why `Arrays.sort(int[])` (dual-pivot quicksort) beats a textbook merge sort by ~20–30%.
</details>

## Q12
What does the natural-merge optimisation `if (a[mid] <= a[mid+1]) return;` change, and what does it *not* change?

<details><summary>Answer</summary>

It **skips the Θ(n) copy** when the two sorted runs are already in global order. On presorted input, combined with run detection, the whole sort becomes Θ(n) comparisons + Θ(n) writes.

It does **not** change merge sort's worst case or its memory bound, and it does not change the result for random input (it simply never fires at the top levels).
</details>

## Q13
You must sort `List<Order>` where `Order` has an ID that can repeat and the arrival order of equal IDs must be preserved. Which algorithm, and what is the *worst case* guarantee?

<details><summary>Answer</summary>

**Merge sort (or TimSort / `Arrays.sort(comparator)`).** Quick sort and Shell sort are unstable, so they cannot satisfy the requirement. Selection sort and bubble sort are stable but `Θ(n²)`.

Worst case: **`Θ(n log n)` guaranteed** — merge sort's split is input-independent.
</details>

## Q14
Introsort switches to heap sort at a depth limit of `2·log₂ n`. What two guarantees does this buy, and what is the cost?

<details><summary>Answer</summary>

1. **Stack guarantee:** recursion depth ≤ `2 log₂ n` → `O(log n)` stack, no stack overflow.
2. **Time guarantee:** if quick sort is unbalancing, the fallback is heap sort → `O(n log n)` worst case.

Cost: constant-factor overhead from the depth counter, and heap sort is slower per element than insertion/quicksort, so the constant is ~10–20% higher on benign inputs.
</details>

## Q15
Why can parallel merge sort not scale linearly with cores, and what is the theoretical cap?

<details><summary>Answer</summary>

The final merge is inherently serial — a single Θ(n) pass over the whole array that no amount of partitioning can split without more communication than work saved. Also, the last few recursion levels have too little work per task to amortise fork-join overhead.

By **Amdahl's law**, if the serial fraction is `s`, speedup `≤ 1/s`. With `s ≈ 1%`, the cap is **100×** no matter how many cores you add. Measured 8-thread speedups for `int[2²⁴]` are typically 4–6×, well below the cap, because memory bandwidth saturates first.
</details>