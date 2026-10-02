# Quiz — Binary Tree Serialization (LeetCode 297)

1. What is the difference between serialization and deserialization of a binary tree?
2. In the BFS (level-order) serialization, why do we include "null" markers?
3. What is the time and space complexity of BFS serialization/deserialization?
4. In the DFS (pre-order) serialization, how does the deserializer know when to stop recursing left?
5. What is the serialized string format for an empty tree in both approaches?
6. How does the BFS deserializer use a queue to reconstruct the tree?
7. What are the advantages of BFS vs DFS serialization?
8. In the BFS approach, why do we use `queue.offer(node.left)` and `queue.offer(node.right)` even when they might be null?
9. What happens if the input string to deserialize has trailing commas?
10. Can you serialize a general N-ary tree using similar approaches? How would the format change?

---

## Answers

1. **Serialization**: Tree → String (persist/transmit). **Deserialization**: String → Tree (reconstruct).
2. Null markers preserve structure — without them, we can't distinguish between different tree shapes with same node values.
3. **Both O(n)** time and space — visit each node once, string/queue holds O(n) data.
4. Pre-order: "root, left, right". Null markers explicitly mark missing children. Deserializer reads values sequentially; "null" returns null without further recursion.
5. **BFS**: Empty string "". **DFS**: Empty string "" (or "null" if root is null).
6. Queue holds parent nodes waiting for children. Poll parent, read next two values for left/right, create children, enqueue non-null children.
7. **BFS**: Level-order natural for complete trees, easier to visualize. **DFS**: More compact for skewed trees, recursive implementation simpler.
8. Null children are enqueued as null, then dequeued and written as "null" in output. This maintains exact position information.
9. The solution uses `split(",")` which handles trailing comma by producing empty string at end. But the code checks `i < values.length` before access.
10. Yes — for N-ary: BFS: include child count or null separator. DFS: include child count before children, or use "null" as end-of-children marker.