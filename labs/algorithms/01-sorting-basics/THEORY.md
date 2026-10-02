# Sorting Basics — Theoretical Foundation

## Bubble Sort

Repeatedly steps through the list, compares adjacent elements, and swaps them if in wrong order.

### Complexity
- Best: O(n) — with optimization flag on sorted array
- Average/Worst: O(n²)
- Space: O(1)

## Selection Sort

Divides input into sorted and unsorted regions, repeatedly selects smallest from unsorted.

### Complexity
- All Cases: O(n²)
- Space: O(1)

## Insertion Sort

Builds sorted array one element at a time by inserting each into correct position.

### Complexity
- Best: O(n) — already sorted
- Average/Worst: O(n²)
- Space: O(1)

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "1.8 Lowerbound of Sorting", Oregon State algorithms course notes (Huanlian) — https://web.engr.oregonstate.edu/~huanlian/algorithms_course/1-datastructures/lowerbound.html — decision-tree argument: n! possible orderings, each comparison halves possibilities, so any comparison sort needs h = log(n!) comparisons with (n/2)·log(n/2) < h < n·log n, i.e. Ω(n log n) — explains why the lab's O(n²) sorts cannot be "tuned" into O(n log n).
- Same source, binary-insertion-sort note — using binary search for the insert position caps comparisons at ≈ n·lg n, yet the algorithm stays O(n²) because shifting elements dominates — sharpens the lab's insertion-sort exercise (comparisons vs moves).
- Same source, taxonomy — slow O(n²) sorts (insertion, selection, bubble) vs fast O(n log n) comparison sorts (quicksort, mergesort, heapsort); O(n log n) is the fastest possible for internal comparison-based sorting — use to motivate the lab's follow-on sorting labs before citing numbers.
