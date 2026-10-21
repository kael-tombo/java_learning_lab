# Interview Questions: Skip Lists

## LeetCode Problem Map
| Problem | Difficulty | Company Signal | Pattern |
|---------|-----------|----------------|---------|
| [LC 1206 Design Skiplist](https://leetcode.com/problems/design-skiplist/) | Hard | Google, Amazon, Meta, Microsoft | Skip list implementation |
| (No other standard LC problems — system design focus) | — | Google, Amazon, Meta, Microsoft, Oracle | Probabilistic data structures |

## NeetCode Reference
Not in NeetCode 150. Skip lists appear in system design contexts (Redis, LevelDB).

## Company-Specific Questions

### Google
- Implement a skip list with search, insert, and delete operations in O(log n) expected time
- How does probabilistic balancing work in skip lists? Prove the expected time complexity
- Compare skip lists vs balanced BSTs (Red-Black, AVL) — trade-offs in performance and implementation complexity
- How would you implement a skip list that supports range queries (all keys between low and high)?

### Microsoft
- Why does Redis use skip lists for sorted sets instead of balanced trees?
- How would you make a skip list thread-safe for concurrent reads and writes?
- Implement a skip list with a persistent (immutable) interface

### Meta
- Design a leaderboard that supports addScore, top(K), and reset operations using a skip list
- Compare skip list with binary search on sorted array for sorted set operations
- How would you implement a skip list for a high-frequency trading order book?

### Amazon
- Design DynamoDB's internal sorted index using skip list principles
- How would you implement a concurrent skip list using CAS operations (lock-free)?
- Skip list vs LSM-tree for write-heavy workloads — compare

### Apple
- How would you design a sorted playlist using a skip list?
- Implement a skip list-based priority queue — what is the advantage over binary heap?
- Memory overhead of skip list vs BST vs array-backed sorted list

### Oracle
- What is the worst-case space complexity of a skip list? How probable is this worst case?
- How does Redis implement its skip list for sorted sets (ZSET)? What optimizations does it use?
- Compare skip list vs Oracle's B-tree index — what are the fundamental differences?
- How would you implement an order-statistic tree using skip lists (find kth element, find rank of element)?

## Real Production Scenarios

- **Scenario 1: Redis Sorted Sets** — Redis uses skip lists for the underlying implementation of sorted sets (ZSET). The skip list supports O(log n) insert, delete, and score-range queries. The forward-linked structure enables efficient range scans (e.g., "get all users with scores between 1000 and 2000").

- **Scenario 2: In-Memory Database Index** — An in-memory database (like MemSQL/SingleStore) uses skip lists as indexes for sorted columns. The probabilistic nature reduces the complexity of rebalancing compared to BSTs. Range scans are efficient due to forward links at each level.

- **Scenario 3: Log-Structured Merge Tree** — LevelDB/RocksDB uses skip lists for its in-memory memtable (write buffer). When the memtable is full, it's flushed to disk as an SSTable. The skip list supports concurrent insertions and O(log n) lookups while the memtable is active.

## Interview Tips

- Time: O(log n) expected for search/insert/delete, O(n) worst case (extremely unlikely with good randomization)
- Space: O(n) expected (about n*2 pointers on average), O(n log n) worst case with p=0.5
- Common edge cases: empty list, single element, inserting at head/tail, deleting non-existent element
- The random level follows a geometric distribution: P(level = k) = p^(k-1) * (1-p), typically p = 0.25 or 0.5
- Increasing p gives faster search but more memory; decreasing p gives slower search but less memory
- Maximum level: typically maxLevel = log_(1/p)(n) or fixed MAX_LEVEL = 32 (for 2^32 elements)
- Sentinel head nodes store forward pointers at all levels (up to maxLevel)

## Java-Specific Considerations

- No standard skip list class in Java — implement from scratch
- Node structure: `class SkipListNode { int val; SkipListNode[] forward; }` — array of forward pointers
- Random level generation: `Random rand = new Random(); int level = 1; while (rand.nextDouble() < p && level < MAX_LEVEL) level++;`
- `ArrayList<SkipListNode>` or `SkipListNode[]` for update array (tracks nodes at each level that need updating)
- Memory: each node has an array of forward pointers — overhead = (avg level + 1) * reference size + value
- For thread safety: `ConcurrentSkipListMap` / `ConcurrentSkipListSet` — Java's built-in concurrent skip list
- `ConcurrentSkipListMap` implements `ConcurrentNavigableMap` — sorted, concurrent, O(log n) operations
- `ConcurrentSkipListSet` wraps `ConcurrentSkipListMap` — thread-safe sorted set
- `java.util.Collections.synchronizedSortedMap()` — alternative but less performant than skip list
- Use `ThreadLocalRandom` (Java 7+) for random level generation instead of `Random` for better concurrent performance
