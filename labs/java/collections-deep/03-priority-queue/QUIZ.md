# PriorityQueue & Heap Operations — Quiz

> **Instructions**: Answer each question before revealing the solution.

<details>
<summary><strong>1. What is the time complexity of PriorityQueue.offer() / add()?</strong></summary>
**Answer: O(log n)** — Element is added at end and sifted up (heapify-up).
</details>

<details>
<summary><strong>2. What is the time complexity of PriorityQueue.poll()?</strong></summary>
**Answer: O(log n)** — Root is removed, last element moved to root and sifted down (heapify-down).
</details>

<details>
<summary><strong>3. What is the time complexity of PriorityQueue.peek()?</strong></summary>
**Answer: O(1)** — Returns the root element without modification.
</details>

<details>
<summary><strong>4. What ordering does PriorityQueue use by default?</strong></summary>
**Answer: Natural ordering (min-heap)** — Smallest element at head per `Comparable`. For `Integer`, smallest value is polled first.
</details>

<details>
<summary><strong>5. How do you create a max-heap PriorityQueue in Java?</strong></summary>
**Answer: `new PriorityQueue<>(Comparator.reverseOrder())` or `new PriorityQueue<>((a, b) -> b - a)`** — Provide a `Comparator` that reverses natural order.
</details>

<details>
<summary><strong>6. What is the space complexity of merging k sorted lists using a min-heap?</strong></summary>
**Answer: O(k)** — Heap holds at most one node from each of the k lists at any time.
</details>

<details>
<summary><strong>7. What is the time complexity of merging k sorted lists with total N nodes using a min-heap?</strong></summary>
**Answer: O(N log k)** — Each of N nodes is inserted and extracted once; heap size ≤ k.
</details>

<details>
<summary><strong>8. What happens if you call poll() on an empty PriorityQueue?</strong></summary>
**Answer: Returns null** — Unlike `remove()` which throws `NoSuchElementException`.
</details>

<details>
<summary><strong>9. Is PriorityQueue thread-safe?</strong></summary>
**Answer: No** — Use `PriorityBlockingQueue` for concurrent access.
</details>

<details>
<summary><strong>10. What is the initial capacity of PriorityQueue if not specified?</strong></summary>
**Answer: 11** — Default initial capacity is 11 (grows by ~1.5× when full).
</details>

---
*Quiz complete. Review incorrect answers and re-read the THEORY.md for deeper understanding.*