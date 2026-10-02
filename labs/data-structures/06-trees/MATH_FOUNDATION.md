# Mathematical Foundation — Binary Tree Serialization

## 1. Problem Definition

**Serialization**: Convert a binary tree into a string representation.
**Deserialization**: Reconstruct the binary tree from the string.

A binary tree is defined as:
```
class TreeNode {
    int val;
    TreeNode left;
    TreeNode right;
}
```

The serialization must be **lossless** — deserialization must produce an identical tree structure and values.

---

## 2. Information-Theoretic Lower Bound

### Number of Binary Tree Shapes
The number of distinct binary tree shapes with n nodes is the **Catalan number**:
```
C_n = (1/(n+1)) × (2n choose n) = (2n)! / (n! × (n+1)!)
```

### Minimum Bits Required
To encode shape + values:
- Shape: log₂(C_n) bits
- Values: n × log₂(V) bits (V = value range)

**Asymptotic**: log₂(C_n) ~ 2n - O(log n) bits for shape.
So **any serialization needs at least ~2n bits for structure** (plus values).

### String Representation Overhead
- BFS: "val,null,null,..." — ~2n tokens for n nodes
- DFS: "val,null,null,..." — exactly 2n+1 tokens for n nodes (including final nulls)
- Each token: value + comma ≈ 4-10 bytes
- **Total: O(n) bytes** — optimal up to constant factor

---

## 3. BFS (Level-Order) Serialization

### Algorithm
```
serialize(root):
    if root == null: return ""
    queue = [root]
    result = []
    while queue not empty:
        node = queue.pop(0)
        if node == null:
            result.append("null")
        else:
            result.append(str(node.val))
            queue.append(node.left)
            queue.append(node.right)
    return join(result, ",")
```

### Example
```
    1
   / \
  2   3
     / \
    4   5

BFS: "1,2,3,null,null,4,5,null,null,null,null"
```

### Properties
- **Complete trees**: Most compact (few trailing nulls)
- **Skewed trees**: Many trailing nulls (exponential in height)
- **Queue max size**: O(width) = O(2^h) worst case

### Deserialization
```
deserialize(data):
    if data == "": return null
    values = data.split(",")
    root = TreeNode(int(values[0]))
    queue = [root]
    i = 1
    while queue not empty and i < len(values):
        parent = queue.pop(0)
        # Left child
        if values[i] != "null":
            parent.left = TreeNode(int(values[i]))
            queue.append(parent.left)
        i += 1
        # Right child
        if i < len(values) and values[i] != "null":
            parent.right = TreeNode(int(values[i]))
            queue.append(parent.right)
        i += 1
    return root
```

### Correctness Proof
By induction on levels:
- Level 0: Root created from values[0]
- Level k: Parents dequeued in level order, assigned children from sequential values
- Null markers preserve exact positions
- Queue processes parents in same order as serialization

---

## 4. DFS (Pre-order) Serialization

### Algorithm
```
serialize(root):
    result = []
    def dfs(node):
        if node == null:
            result.append("null")
            return
        result.append(str(node.val))
        dfs(node.left)
        dfs(node.right)
    dfs(root)
    return join(result, ",")

deserialize(data):
    if data == "": return null
    values = iter(data.split(","))
    def dfs():
        val = next(values)
        if val == "null": return null
        node = TreeNode(int(val))
        node.left = dfs()
        node.right = dfs()
        return node
    return dfs()
```

### Example
```
    1
   / \
  2   3
     / \
    4   5

DFS Pre-order: "1,2,null,null,3,4,null,null,5,null,null"
```

### Properties
- **Always exactly 2n+1 tokens** for n nodes (each node has 2 children pointers, each either node or null)
- **Skewed trees**: Very compact (no extra nulls beyond structural)
- **Recursion depth**: O(h) where h = tree height
- **Stack space**: O(h) for both serialize and deserialize

### Deserialization Correctness
Pre-order traversal uniquely determines tree with null markers:
- First token = root
- Next tokens = entire left subtree (recursively)
- Remaining tokens = entire right subtree (recursively)
- Null tokens are base cases returning null

---

## 5. Complexity Comparison

| Aspect | BFS (Level-Order) | DFS (Pre-order) |
|--------|-------------------|-----------------|
| Time (serialize) | O(n) | O(n) |
| Time (deserialize) | O(n) | O(n) |
| Space (serialize) | O(w) queue + O(n) string | O(h) stack + O(n) string |
| Space (deserialize) | O(w) queue + O(n) tree | O(h) stack + O(n) tree |
| String length | Variable (trailing nulls) | Fixed: 2n+1 tokens |
| Best for | Complete/balanced trees | Skewed trees |
| Implementation | Iterative (queue) | Recursive (simple) |

Where w = max width, h = height.

### Space Analysis Detail

**BFS Queue**: Maximum width of tree
- Complete tree: w = 2^h ≈ n/2 → **O(n)**
- Skewed tree: w = 1 → **O(1)**

**DFS Stack**: Height of tree
- Complete tree: h = log n → **O(log n)**
- Skewed tree: h = n → **O(n)**

---

## 6. Tree Reconstruction Uniqueness

### Theorem
A binary tree is uniquely determined by:
1. **Pre-order + In-order** traversal (no null markers needed)
2. **Post-order + In-order** traversal
3. **Pre-order with null markers** (our DFS)
4. **Level-order with null markers** (our BFS)

### Why Null Markers Are Necessary for Single Traversal
Without null markers:
```
Pre-order: 1,2,3
Could be:
    1           1          1
   / \         /          /
  2   3       2          2
               \          \
                3          3
```

Null markers resolve ambiguity by explicitly marking missing children.

---

## 7. Generalizations

### N-ary Tree Serialization
For node with variable number of children:
```
class Node {
    int val;
    List<Node> children;
}
```

**Format Options**:
1. **Child count prefix**: "1,3,2,0,4,2,5,0,6,0" (val, num_children, children...)
2. **Delimiter**: "1[2,3[4,5]]" (brackets for children)
3. **Null separator**: Pre-order with "null" ending children list

### Graph Serialization (with cycles)
- Assign IDs to nodes
- Serialize as adjacency list: "1:2,3; 2:4; 3:2,5; ..."
- Requires cycle detection (visited set)

### Binary Tree with Parent Pointers
- Serialize tree normally
- During deserialization, set parent pointers when creating children

---

## 8. Practical Considerations

### String vs Binary Format
| Format | Pros | Cons |
|--------|------|------|
| String (CSV) | Human-readable, debuggable | Larger, parsing overhead |
| Binary (protobuf, etc.) | Compact, fast | Not human-readable |
| JSON | Standard, nested | Verbose for trees |

### Handling Special Values
- **Negative numbers**: Include "-" in token
- **Large integers**: Use 64-bit or variable-length encoding
- **Null root**: Return empty string ""

### Trailing Comma Handling
```java
String[] values = data.split(",");  // "1,2," → ["1", "2", ""]
// Always check bounds before access
if (i < values.length && !values[i].equals("null")) { ... }
```

### Memory Optimization for Large Trees
- **Streaming**: Serialize directly to output stream
- **Chunked**: Process in chunks for very large trees
- **Compression**: GZIP serialized string (reduces ~70% for repetitive nulls)

---

## 9. Applications

1. **Persistence**: Save tree to file/database
2. **Network Transfer**: Send tree between processes/machines
3. **Caching**: Store computed tree structures
4. **Testing**: Compare tree structures via string equality
5. **Distributed Systems**: Tree-based data structures (Merkle trees, B-trees)

---

## 10. Summary

| Method | Format | Tokens | Space (queue/stack) | Best Case |
|--------|--------|--------|---------------------|-----------|
| BFS | Level-order + nulls | ~2n + trailing | O(width) | Complete tree |
| DFS | Pre-order + nulls | Exactly 2n+1 | O(height) | Skewed tree |

**Both are O(n) time and space overall.** Choice depends on:
- Expected tree shape (balanced vs skewed)
- Implementation preference (iterative vs recursive)
- Downstream processing (level-order vs depth-first)