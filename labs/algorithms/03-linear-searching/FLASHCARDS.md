# Flashcards — Linear Searching

- Q: Linear search worst case? → A: O(n) comparisons
- Q: Linear search best case? → A: O(1) — target first
- Q: Average successful search cost? → A: n/2 = O(n)
- Q: Sorted input required? → A: No — works on any order
- Q: Space complexity (iterative)? → A: O(1)
- Q: Sentinel optimization? → A: Appends target as sentinel; halves comparisons per iteration (constant-factor only)
- Q: Linear vs binary search? → A: Binary needs sorted data and gives O(log n); linear works anywhere at O(n)
- Q: Peak element (LC 162) linear bound? → A: O(n) scan works; gradient binary search gives O(log n)
- Q: When to prefer linear search? → A: Small n, unsorted data, or single query where sorting costs more than O(n) scan
- Q: Cache behavior array vs linked list? → A: Same O(n) comparisons; array wins on locality/prefetching
