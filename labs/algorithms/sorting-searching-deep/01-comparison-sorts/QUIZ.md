# Quiz — Comparison Sorts

15 questions. Answer before checking the key. Every key includes the *reason*, not just the letter.

---

## Q1
What is the exact number of comparisons performed by selection sort on `n` elements, regardless of input arrangement?

<details><summary>Answer</summary>

`n(n-1)/2`.

**Reason:** the inner loop always runs `n-1, n-2, ..., 1` times because the loop bounds depend only on `i`, never on the data. The `if (min != i)` swap guard does not skip comparisons, only swaps.
</details>

## Q2
Insertion sort's inner loop runs `k` times in total across the whole sort. What combinatorial quantity is `k`?

<details><summary>Answer</summary>

The **inversion count** of the input array: the number of pairs `(i, j)` with `i < j` and `a[i] > a[j]`.

**Reason:** each inner-loop execution moves one element strictly past a larger element, destroying exactly one inversion and creating none. Therefore total shifts = initial inversions. Corollary: total comparisons = `n - 1 + inversions`.
</details>

## Q3
Your bubble sort has the `if (!swapped) break;` line. What is its best-case time, and what would it be without the line?

<details><summary>Answer</summary>

With the flag: **Ω(n)** — one pass of `n-1` comparisons, no swaps, exit.
Without the flag: **Θ(n²)** — the flag is the *only* thing making bubble sort adaptive.

**Reason:** termination logic, not the comparison, is what distinguishes them.
</details>

## Q4
True or false: "cinnabar sort" (gap sequence `n/2, n/4, ..., 1`) is an improvement over plain insertion sort in the worst case."

<details><summary>Answer</summary>

**False.** The Shell sequence has a proven worst case of **O(n²)** — no better than insertion sort. Hibbard/Knuth give O(n^{3/2}), Sedgewick O(n^{4/3}), Pratt O(n log² n).

**Reason:** the gap sequence, not the mechanism, determines the bound. Half-the-array gaps do not shrink the 0-1 principle witness fast enough.
</details>

## Q5
Why must insertion sort's guard be `a[j] > key` and not `a[j] >= key`?

<details><summary>Answer</summary>

With `>=`, an element *equal* to `key` is shifted right, so equal keys end up in reverse original order — the sort loses stability.

**Reason:** stability requires that ties never cross. Insertion is the only one of the four sorts where a single strictness choice controls stability.
</details>

## Q6
Sort `[2a, 2b, 1, 3]` (letters denote original positions) with the standard selection sort. Is it stable?

<details><summary>Answer</summary>

**No.** Final array is `[1, 2b, 2a, 3]`; the two equal keys are inverted.

**Reason:** the minimum `1` is at index 2 and gets swapped with `2a` at index 0. Stability is destroyed because a swap moves a value across its equal partner. Smallest witness for a failing case.
</details>

## Q7
Give a counter-example: an input on which cocktail shaker sort is dramatically faster than standard bubble sort. Explain the mechanism.

<details><summary>Answer</summary>

`[1, 2, ..., k, n, n-1, ..., k+1]` — a sorted small run followed by a descending large run.

Bubble sort pushes each large element one position per pass, needing O(n) passes → **Θ(n²)**. Cocktail shaker's backward passes pull the small values toward the front immediately → **Θ(n)**.
</details>

## Q8
What is the tight comparison lower bound for sorting `n` distinct elements with any comparison-based algorithm? How is it computed for `n = 100`?

<details><summary>Answer</summary>

`ceil(log2(n!))`, because a decision tree with depth `d` has at most `2^d` leaves and must distinguish `n!` permutations.

For `n = 100`: `log2(100!) ≈ 524.76`, so **≥ 525 comparisons**.
</details>

## Q9
You want a sort that is both stable and uses O(1) auxiliary memory. Which of the four can you use, and which must you avoid?

<details><summary>Answer</summary>

Use **insertion sort** (stable, O(1), Θ(n) on nearly-sorted data).
Avoid **stable selection sort** — it is O(1) but needs Θ(n²) *writes*, strictly worse than insertion sort's Θ(n) writes on the same input.

**Reason:** stability + O(1) space is satisfiable; the trap is thinking "stable selection sort is fine because writes are cheap" — they are not.
</details>

## Q10
The inner loop of a Shell sort implementation reads `while (j >= gap && a[j] > key)`. Name two distinct correctness bugs.

<details><summary>Answer</summary>

1. **Wrong index:** must be `a[j - gap] > key`, not `a[j] > key`. Comparing `a[j]` with itself while `a[j]` is being overwritten yields garbage.
2. **Truncated gap sequence:** if the generator starts at `n/2` and halves, you get the Shell sequence with an O(n²) worst case, not the intended Sedgewick O(n^{4/3}).

**Reason:** both bugs compile and both produce sorted-looking output on small sorted inputs.
</details>

## Q11
`Arrays.sort(T[])` uses TimSort, which is stable. Why is that *not* sufficient to guarantee an O(n log n) worst case in every implementation?

<details><summary>Answer</summary>

Because **stable** forces merge sort (adjacent-run merging), while worst-case O(n log n) + stable + no randomness is not achievable without the extra structure TimSort's run detection provides. Worst case is still O(n log n) — but stability rules out quicksort, so you cannot get O(n log n) *with randomization* and stability at the same time.

**Reason:** design tension: stable ⇒ merge-based ⇒ no randomised pivot ⇒ no probabilistic worst-case protection.
</details>

## Q12
Sort `[5, 2, 4, 6, 1, 3]` with insertion sort. How many shifts occur, and how many comparisons?

<details><summary>Answer</summary>

**8 shifts**, **13 comparisons**.
Shifts per iteration: 1, 1, 0, 4, 2 = 8. Comparisons = shifts + failures = 8 + 5 = 13.
</details>

## Q13
Why do production sorts (TimSort, dual-pivot quickSort) switch to insertion sort for arrays under ~47 elements?

<details><summary>Answer</summary>

**Constant factors beat asymptotics.** Insertion sort needs no recursion, no allocation, works in L1 cache, and on n ≤ 47 the Θ(n²) work is ~1100 comparisons versus ~280 comparisons plus 6 recursive calls and pivot partitioning overhead. QuickSort's crossover with insertion sort is empirically around n ≈ 47.

**Reason:** asymptotic analysis assumes n → ∞; real crossover points are measured, not derived.
</details>

## Q14
Comb sort is widely reported as "O(n log n)". Why is that claim wrong?

<details><summary>Answer</summary>

Because **no worst-case bound has been proven**. The empirical behaviour with shrink factor 1.3 is roughly O(n log n) on typical inputs, but there is no theorem and the constant 1.3 is a magic number, not derived.

**Reason:** conflating empirical behaviour with a proof is the most common error in algorithm folklore. Prefer Hibbard/Knuth/Sedgewick/Pratt where you can cite a bound.
</details>

## Q15
Your team needs to sort 10 million records where keys repeat heavily and the original order of equal keys is meaningful (e.g. audit log). Which algorithm, and why not the others?

<details><summary>Answer</summary>

**`Arrays.sort(comparator)` — TimSort.**

- Stable: preserves audit order for equal keys. Insertion is stable too but Θ(n²) is fatal at 10⁷.
- Selection sort is unstable and Θ(n²).
- Shell sort is **unstable** — equal keys get reordered across gap passes.
- Bubble/shaker are stable but Θ(n²) worst case and far too slow.
- Radix/counting are non-comparison; fine only if keys are bounded integers and ties are handled by scanning input forward (stable).

**Reason:** the deciding constraint is *stability at scale*, and only TimSort satisfies it.
</details>