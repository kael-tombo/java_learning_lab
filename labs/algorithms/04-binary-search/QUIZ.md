# Quiz — Binary Search

1. What precondition does classic binary search require?
   - A) None / B) Sorted input ✓ / C) Distinct elements only / D) Power-of-2 length.

2. Worst-case time complexity of binary search on n elements?
   - A) O(n) / B) O(log n) ✓ / C) O(1) / D) O(n log n).

3. Why does `mid = l + (r - l) / 2` instead of `(l + r) / 2`?
   - A) Faster / B) Avoids integer overflow ✓ / C) Required for generics / D) Style only.

4. In LeetCode 33 (rotated sorted array), why can we still binary search?
   - A) Array is fully sorted / B) At least one half is always sorted, so we can discard the other ✓ / C) Rotation makes it linear / D) Duplicates guarantee it.

5. With duplicates (LC 81), worst-case time becomes?
   - A) O(1) / B) O(log n) still / C) O(n) ✓ when `nums[l] == nums[m] == nums[r]` forces shrinking / D) O(n²).

6. How is LC 162 (peak element) solvable with binary search on an unsorted array?
   - A) It is sorted / B) The gradient (`nums[mid] < nums[mid+1]` → peak right, else left) gives a directional guarantee ✓ / C) It guesses / D) It sorts first.

7. Space complexity of iterative binary search?
   - A) O(n) / B) O(log n) / C) O(1) ✓ / D) O(n log n). (Recursive: O(log n) stack.)

8. How many comparisons (worst case) for n = 1024?
   - A) 1024 / B) ~10 ✓ (log2 1024) / C) 512 / D) 1.

9. Termination condition bug: `while (l < r)` vs `while (l <= r)` — when is each right?
   - A) Interchangeable / B) `<` when searching a boundary/index (e.g., peak), `<=` when checking `nums[m] == target` with `r = m - 1` ✓ / C) Opposite / D) Neither terminates.

10. Binary search on answer (e.g., capacity/shipments) applies when?
    - A) Answer space is monotonic (feasible ⇒ all larger feasible) ✓ / B) Input is a tree / C) Only for Strings / D) Never.
