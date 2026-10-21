# Interview Questions: Immutable & Persistent Data Structures

## LeetCode Problem Map
| Problem | Difficulty | Company Signal | Pattern |
|---------|-----------|----------------|---------|
| [LC 303 Range Sum Query - Immutable](https://leetcode.com/problems/range-sum-query-immutable/) | Easy | Amazon, Google, Meta, Microsoft, Apple | Immutable prefix sum |
| [LC 304 Range Sum Query 2D - Immutable](https://leetcode.com/problems/range-sum-query-2d-immutable/) | Medium | Amazon, Meta, Google, Microsoft | Immutable 2D prefix sum |
| [LC 307 Range Sum Query - Mutable](https://leetcode.com/problems/range-sum-query-mutable/) | Medium | Amazon, Google, Meta, Microsoft | Mutable → persistent segment tree |
| [LC 208 Implement Trie (Prefix Tree)](https://leetcode.com/problems/implement-trie-prefix-tree/) | Medium | Amazon, Google, Meta, Microsoft | Persistent trie use case |
| (System design focus) | — | Google, Meta, Amazon, Microsoft | Functional programming / versioned data |

## NeetCode Reference
Not in NeetCode 150. Persistent data structures are relevant for functional programming and versioned systems.

## Company-Specific Questions

### Google
- Implement an immutable (persistent) linked list with structural sharing — head, tail, cons operations
- How does structural sharing reduce memory in persistent data structures? Draw the DAG of shared nodes
- Design a persistent binary tree (BST) with insert and search — explain the path copying technique
- How would you implement undo/redo using persistent data structures?

### Microsoft
- Compare mutable vs immutable data structures for concurrent access scenarios
- Implement a persistent queue using two persistent stacks (Okasaki's banker's queue)
- How does functional programming (like in Clojure) leverage persistent vectors and hash maps?

### Meta
- Design a versioned key-value store where each version is immutable (persistent hash map)
- How would you implement an undo system for a collaborative document editor?
- What are the performance trade-offs of persistent data structures for read-heavy workloads?

### Amazon
- Design a persistent segment tree for versioned range queries (Kth smallest in range — LC 315)
- How would DynamoDB implement versioned items using persistent data structures?
- Implement a persistent counter that tracks all historical values

### Apple
- How does Core Data's undo manager work with persistent data structures?
- Design an immutable list for Swift/Java interop — what changes when porting from mutable to immutable?
- How would you implement a persistent set with union, intersection, and difference operations?

### Oracle
- What is the difference between immutability (unmodifiable wrappers) and persistence (multi-version structures)?
- How does `Collections.unmodifiableList()` differ from a true persistent list?
- What is the role of immutable objects in Java's memory model (safe publication, no synchronization)?
- How would you implement a persistent array (random access, O(log n) update)?

## Real Production Scenarios

- **Scenario 1: Undo/Redo in Text Editor** — A collaborative text editor uses a persistent rope (piece table) for the document. Each edit creates a new version that shares unchanged portions with previous versions (structural sharing). Undo simply reverts to the previous version pointer. Memory is O(edit_size) per operation, not O(document_size).

- **Scenario 2: Time-Travel Debugging** — A debugger records program state using persistent data structures for all mutable variables. The user can "travel" backward and forward in execution time. Each breakpoint creates a new persistent snapshot. The overhead is proportional to changes between snapshots, not total state.

- **Scenario 3: Database Version Control** — A database migration tool uses a persistent B-tree for index pages. Each migration creates a new root with shared unchanged internal nodes. If a migration fails, the database atomically switches back to the old root. This provides instant rollback without expensive undo operations.

## Interview Tips

- Time: O(log n) for persistent BST (path copying), O(1) cons operations on persistent linked list, O(1) amortized for persistent queue
- Space: O(log n) extra per update for path copying (shared unchanged nodes); worst case O(n) if no sharing (full copy)
- Common edge cases: empty persistent structure, concurrent modifications to same version, very large number of versions
- Persistent ≠ immutable: immutable means cannot be changed; persistent means updates produce new versions sharing old structure
- Structural sharing: two versions of a tree share all unchanged subtrees — only the path from root to modified leaf is recreated
- Fat node: store a list of (timestamp, value) pairs at each node — another approach to persistence

## Java-Specific Considerations

- `Collections.unmodifiableList()` / `unmodifiableMap()` etc. — thin wrapper over mutable collection, throws on modification — NOT truly persistent
- `List.of()` (Java 9+) — truly unmodifiable (not a view, no backing mutable collection)
- `ImmutableList` (Guava) — `ImmutableList.copyOf()`, `ImmutableList.builder()` — efficient immutable implementations
- Java Records (Java 16+) — `record Point(int x, int y)` — immutable data carriers with auto-generated equals/hashCode/toString
- `String` is immutable in Java — every substring/concatenation creates a new object
- `BigInteger` and `BigDecimal` are immutable — each arithmetic operation returns a new instance
- For persistent collections: use libraries like Paguro, Vavr, or Cyclops
- Vavr's `TreeSet`, `HashMap`, `Vector`, `Queue` — persistent, functional-style Java collections
- `java.time` classes (LocalDate, Instant, etc.) are all immutable — thread-safe by design
- Custom persistent linked list: `class ConsList<T> { T head; ConsList<T> tail; }` — `cons(element)` creates new node pointing to old list
- Path copying in persistent BST: `class PNode { int val; PNode left, right; }` — `insert(val)` creates new nodes along the path from root to leaf
- Fat node approach: `class FatNode { int val; Map<Integer, Node> versionHistory; }` — useful when many versions of same node exist
