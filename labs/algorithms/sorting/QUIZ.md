# QUIZ — Sorting Track
> 15 questions with answers. Track `sorting`.

1. Quicksort average/worst? → E[O(n log n)]; worst O(n²) bad pivots.
2. Randomization fixes? → Expected pivot rank halves; worst vanishingly unlikely.
3. Hoare vs Lomuto? → Hoare fewer swaps, better with dupes; Lomuto simpler, degrades.
4. 3-way wins when? → Duplicate-heavy: O(n) all-equal vs O(n²) naive.
5. Recurrence average? → T(n)=(1/n)Σ(T(k)+T(n-1-k))+O(n) → Θ(n log n).
6. Stack bound trick? → Recurse smaller side; iterate larger → O(log n) depth.
7. Quickselect expected? → E[O(n)] by discarding a constant fraction on average.
8. Cutoff to insertion? → ~8-16; kills recursion overhead on tiny ranges.
9. Stability? → Quicksort unstable; tie-break comparator or use mergesort.
10. Lower bound? → Ω(n log n) comparisons for general sorting.
11. Counting sort escapes? → Non-comparison, O(n+k) with bounded integer keys.
12. Introsort? → Quicksort + heapsort fallback at depth 2·log n.
13. Median-of-3? → Cheap pivot quality; median-of-medians for worst guarantee.
14. Parallel quicksort? → ForkJoin on partitions; threshold ~10k.
15. Fuzz oracle? → Arrays.sort for order; sorted[k] for select.

## Scoring
- 13-15: expert. 10-12: practitioner. < 10: revisit THEORY + flashcards.

## Follow-ups
- Prove one bound on paper; implement one variant from memory.
