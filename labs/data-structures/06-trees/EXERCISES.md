# Exercises — Binary Tree Serialization

## Beginner

1. **Implement BFS Serialization/Deserialization**
   - Write `serialize(TreeNode root)` and `deserialize(String data)` using level-order.
   - Handle empty tree, single node, and complete trees.
   - Test round-trip: `deserialize(serialize(root))` should equal original.

2. **Implement DFS (Pre-order) Serialization/Deserialization**
   - Write recursive `serialize` and `deserialize` using pre-order with "null" markers.
   - Compare string length with BFS for different tree shapes.

3. **Validate Serialization String**
   - Given a string, determine if it's a valid BFS or DFS serialization.
   - BFS: Check null/non-null balance. DFS: Use stack to simulate parsing.

## Intermediate

4. **Serialize/Deserialize N-ary Tree (LeetCode 428)**
   - N-ary tree: each node has `List<Node> children`.
   - Design format: e.g., "1[3,2,4[5,6]]" or pre-order with child count.
   - Implement both serialization and deserialization.

5. **Serialize/Deserialize Binary Search Tree (LeetCode 449)**
   - BST property: left < root < right.
   - Can serialize without null markers! Use pre-order only.
   - Deserialize using bounds: recursively build with min/max constraints.

6. **Compact Binary Tree Serialization**
   - Design more compact format (e.g., binary encoding, bit-packed).
   - Compare size with string-based approach.

## Advanced

7. **Serialize/Deserialize with Parent Pointers**
   - TreeNode has `parent` pointer.
   - Serialize maintaining parent links.
   - Deserialize and restore parent pointers correctly.

8. **Serialize/Deserialize with Random Pointer (Clone Binary Tree with Random Pointer)**
   - Each node has `left`, `right`, `random` pointer.
   - Extend serialization format to capture random connections.
   - Use node IDs or two-pass approach.

9. **Parallel Deserialization**
   - Given a large serialization string, deserialize using multiple threads.
   - Split work by subtrees; coordinate shared node pool.

10. **Streaming Serialization/Deserialization**
    - Serialize to OutputStream / deserialize from InputStream.
    - Don't hold full string in memory.
    - Implement `serialize(TreeNode root, OutputStream out)` and `deserialize(InputStream in)`.