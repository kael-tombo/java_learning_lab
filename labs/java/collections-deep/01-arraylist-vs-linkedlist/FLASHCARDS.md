# ArrayList vs LinkedList / HashMap Internals — Flashcards

| # | Question | Answer |
|---|----------|--------|
| 1 | **Default HashMap initial capacity?** | 16 (2⁴) |
| 2 | **Default HashMap load factor?** | 0.75 |
| 3 | **HashMap bucket index formula?** | `(capacity - 1) & hash` |
| 4 | **Why supplemental hash `key ^ (key >>> 16)`?** | Mixes high bits into low bits for better distribution with power-of-two capacity |
| 5 | **When does HashMap treeify a bucket?** | Size ≥ 8 AND capacity ≥ 64 |
| 6 | **Treeify threshold constant name?** | `TREEIFY_THRESHOLD = 8` |
| 7 | **Min capacity for treeify constant?** | `MIN_TREEIFY_CAPACITY = 64` |
| 8 | **Worst-case get() before treeify?** | O(n) — linked list traversal |
| 9 | **Worst-case get() after treeify?** | O(log n) — red-black tree |
| 10 | **ArrayList random access (get by index)?** | O(1) |
| 11 | **LinkedList random access (get by index)?** | O(n) |
| 12 | **ArrayList insertion at index 0?** | O(n) — shifts all elements |
| 13 | **LinkedList insertion at index 0?** | O(1) — updates head pointer |
| 14 | **Which has better cache locality?** | ArrayList — contiguous array |
| 15 | **Why is ArrayList iteration faster?** | Sequential memory = CPU prefetching; LinkedList = cache miss per node |
| 16 | **HashMap resize strategy?** | Double capacity, rehash all entries |
| 17 | **What happens to entries during resize?** | Rehashed into new bucket array using new capacity |
| 18 | **Node vs TreeNode in HashMap?** | Node = linked list entry; TreeNode = red-black tree entry (extends Node) |
| 19 | **When does HashMap un-treeify?** | When bucket size ≤ 6 (UNTREEIFY_THRESHOLD) after resize |
| 20 | **ArrayList growth factor?** | 1.5× (new capacity = old + old >> 1) |

---

**Study tip**: Cover the Answer column and quiz yourself. Shuffle by picking random numbers.