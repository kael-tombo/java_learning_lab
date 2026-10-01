# Exercises — Binary Search

1. **Classic** — Implement iterative `binarySearch(int[] sorted, int target)` with overflow-safe mid. Test on `{1,3,5,7,9}`, targets 7, 1, 9, 4, and empty array.
2. **Lower/upper bound** — Implement `lowerBound` (first `>= target`) and `upperBound` (first `> target`). Use them to count occurrences of 2 in `{1,2,2,2,3}`.
3. **Rotated with duplicates** — Reimplement `SearchRotatedArray` from LEETCODE_SOLUTION.md from memory. Construct a worst-case all-duplicates input and confirm O(n) shrinking behavior with a step counter.
4. **Peak finder** — Reimplement `FindPeakElement` (LC 162 logic) and verify the returned index is a true peak on 100 random arrays (validate neighbors, don't compare exact index).
5. **Search on answer** — Solve "capacity to ship packages in D days" via binary search over `[max(weights), sum(weights)]`. State the monotonic predicate and give time O(n log S).
