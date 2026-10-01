# Flashcards — Binary Search

- Q: Precondition? → A: Sorted (or a monotonic property like rotated-half-sorted / peak gradient)
- Q: Time / space (iterative)? → A: O(log n) time, O(1) space
- Q: Overflow-safe mid? → A: `l + (r - l) / 2`
- Q: Rotated array (LC 33) key insight? → A: One half is always sorted; test if target lies in it
- Q: Duplicates (LC 81) worst case? → A: O(n) when ends equal mid — shrink both ends
- Q: Peak element (LC 162) rule? → A: `nums[mid] < nums[mid+1]` → go right, else go left
- Q: `l < r` vs `l <= r`? → A: Boundary search uses `<` with `r = m`; equality-check search uses `<=` with `r = m - 1`
- Q: Comparisons for n? → A: ⌈log2(n+1)⌉ worst case
- Q: Recursive space? → A: O(log n) call stack
- Q: Binary-search-on-answer pattern? → A: Monotonic feasibility predicate over an integer range
