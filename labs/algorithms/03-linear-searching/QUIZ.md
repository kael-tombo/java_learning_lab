# Quiz — Linear Searching

1. What is the worst-case time complexity of linear search on n elements?
   - A) O(1) / B) O(log n) / C) O(n) ✓ / D) O(n log n)

2. What is the best-case time complexity of linear search?
   - A) O(1) ✓ (target is the first element) / B) O(n) / C) O(log n) / D) O(n²)

3. Does linear search require sorted input?
   - A) Yes / B) No ✓ — it works on any order, including unsorted arrays and lists.

4. How does linear search relate to LeetCode 162 (Find Peak Element)?
   - A) Peak finding requires sorting / B) A linear scan finds a peak in O(n), but binary search does it in O(log n) ✓ / C) Peaks cannot be found linearly / D) Only recursion works.

5. What is the average-case number of comparisons for a successful linear search (uniform target)?
   - A) n / B) n/2 ✓ / C) log n / D) 1

6. Which Java construct is the idiomatic linear search over an array?
   - A) `Arrays.binarySearch` / B) A simple `for` loop comparing each element ✓ / C) `Collections.sort` / D) `System.arraycopy`

7. When is linear search preferable to binary search?
   - A) Always / B) Never / C) Small n or unsorted data where sort cost exceeds search savings ✓ / D) Only on Strings.

8. What is the space complexity of iterative linear search?
   - A) O(n) / B) O(log n) / C) O(1) ✓ / D) O(n²)

9. Sentinel linear search improves what?
   - A) Asymptotic complexity / B) Constant factor: one comparison per iteration instead of two (no bounds check) ✓ / C) Space / D) Stability.

10. Linear search on a linked list vs array — which statement is true?
    - A) Array is O(1) / B) Both are O(n) comparisons; array has better cache locality ✓ / C) Linked list is O(log n) / D) Neither works.
