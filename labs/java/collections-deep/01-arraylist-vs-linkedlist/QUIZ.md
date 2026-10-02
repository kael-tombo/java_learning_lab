# ArrayList vs LinkedList / HashMap Internals — Quiz

> **Instructions**: Answer each question before revealing the solution. Click or hover to reveal.

<details>
<summary><strong>1. What is the default initial capacity of a Java HashMap (Java 8+)?</strong></summary>
**Answer: 16** — The default initial capacity is 16 (1 << 4). It must be a power of two for efficient index calculation using bitwise AND.
</details>

<details>
<summary><strong>2. What is the default load factor of HashMap?</strong></summary>
**Answer: 0.75** — When size exceeds capacity × loadFactor, the map resizes (doubles capacity).
</details>

<details>
<summary><strong>3. How does HashMap compute the bucket index from a key's hash code?</strong></summary>
**Answer: (n - 1) & hash** — Where `n` is the capacity (power of two). This is faster than modulo and distributes bits well when combined with supplemental hash.
</details>

<details>
<summary><strong>4. What is the purpose of the supplemental hash function `key ^ (key >>> 16)` in HashMap?</strong></summary>
**Answer: Mix high bits into low bits** — Since index only uses low bits (due to power-of-two capacity), XORing high bits downward improves distribution for keys with poor hash codes.
</details>

<details>
<summary><strong>5. When does HashMap convert a linked-list bucket to a TreeNode (red-black tree)?</strong></summary>
**Answer: When bucket size ≥ 8 (TREEIFY_THRESHOLD) and capacity ≥ 64 (MIN_TREEIFY_CAPACITY)** — Prevents tree overhead for small maps.
</details>

<details>
<summary><strong>6. What is the time complexity of HashMap.get() in the worst case (all keys collide)?</strong></summary>
**Answer: O(n)** — Before treeification: O(n) linked list traversal. After treeification: O(log n) via red-black tree.
</details>

<details>
<summary><strong>7. What is the difference between ArrayList and LinkedList for random access (get by index)?</strong></summary>
**Answer: ArrayList O(1), LinkedList O(n)** — ArrayList uses contiguous array; LinkedList requires traversal from head/tail.
</details>

<details>
<summary><strong>8. What is the difference between ArrayList and LinkedList for insertion/deletion at the beginning?</strong></summary>
**Answer: ArrayList O(n), LinkedList O(1)** — ArrayList must shift all elements; LinkedList only updates head pointer.
</details>

<details>
<summary><strong>9. Which list implementation has better cache locality?</strong></summary>
**Answer: ArrayList** — Contiguous memory layout enables CPU prefetching and cache-line efficiency. LinkedList nodes are scattered in heap.
</details>

<details>
<summary><strong>10. When iterating over all elements, which is faster and why?</strong></summary>
**Answer: ArrayList** — Sequential memory access pattern allows CPU prefetcher to load multiple elements per cache miss. LinkedList incurs a cache miss per node.
</details>

---
*Quiz complete. Review incorrect answers and re-read the THEORY.md for deeper understanding.*