# PriorityQueue & Heap Operations — Flashcards

| # | Question | Answer |
|---|----------|--------|
| 1 | **offer()/add() time complexity?** | O(log n) — sift up |
| 2 | **poll() time complexity?** | O(log n) — sift down |
| 3 | **peek() time complexity?** | O(1) — read root |
| 4 | **Default ordering?** | Min-heap (natural ordering, smallest first) |
| 5 | **How to create max-heap?** | `new PriorityQueue<>(Comparator.reverseOrder())` |
| 6 | **Space complexity for merge k lists?** | O(k) — heap holds ≤ k nodes |
| 7 | **Time complexity for merge k lists (N total)?** | O(N log k) |
| 8 | **poll() on empty queue returns?** | null |
| 9 | **remove() on empty queue throws?** | NoSuchElementException |
| 10 | **Is PriorityQueue thread-safe?** | No — use PriorityBlockingQueue |
| 11 | **Default initial capacity?** | 11 |
| 12 | **Growth factor?** | ~1.5× (newCapacity = oldCapacity * 1.5 + 1) |
| 13 | **Heap property for min-heap?** | parent ≤ children |
| 14 | **Sift-up (swim) operation?** | Compare with parent, swap if smaller, repeat |
| 15 | **Sift-down (sink) operation?** | Compare with smaller child, swap if larger, repeat |
| 16 | **Array index of left child of i?** | 2*i + 1 |
| 17 | **Array index of right child of i?** | 2*i + 2 |
| 18 | **Array index of parent of i?** | (i - 1) / 2 |
| 19 | **Why use heap for merge k lists?** | Always extracts global minimum among k candidates in O(log k) |
| 20 | **Alternative to heap for merge k lists?** | Divide & conquer (pairwise merge) — O(N log k) time, O(1) extra space |

---

**Study tip**: Cover the Answer column and quiz yourself. Shuffle by picking random numbers.