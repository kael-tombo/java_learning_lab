# Exercises — Hash Table (Design HashMap)

## Beginner

1. **Implement HashMap with Separate Chaining**
   - Implement `MyHashMap` with `put`, `get`, `remove`, `size`.
   - Use array of linked lists (`Entry` nodes).
   - Implement resize at load factor 0.75.

2. **Implement HashSet using HashMap**
   - `MyHashSet` with `add`, `remove`, `contains`.
   - Internally use `MyHashMap` with dummy value.

3. **Two Sum (LeetCode 1)**
   - Given array and target, find indices of two numbers summing to target.
   - Use HashMap for O(n) solution.

## Intermediate

4. **Design HashMap with Open Addressing (Linear Probing)**
   - Implement without linked lists — use array with tombstones for deleted entries.
   - Handle clustering and resize.

5. **Group Anagrams (LeetCode 49)**
   - Group strings by anagram equivalence.
   - Use HashMap with sorted string or character count as key.

6. **LRU Cache (LeetCode 146) — HashMap + Doubly Linked List**
   - Implement `LRUCache` with `get` and `put` in O(1).
   - HashMap for O(1) lookup, doubly linked list for O(1) move-to-front.

## Advanced

7. **HashMap with Treeify (Java 8+ Style)**
   - When bucket chain length exceeds 8, convert to red-black tree.
   - Revert to linked list when size drops below 6.
   - Implement `TreeNode` with tree operations.

8. **Consistent Hashing**
   - Implement consistent hashing ring for distributed systems.
   - Virtual nodes for load balancing.
   - O(log n) lookup for node responsible for key.

9. **Bloom Filter Implementation**
   - Probabilistic set membership with bit array + k hash functions.
   - False positives possible, no false negatives.
   - Analyze optimal k and m for given n and error rate.

10. **Cuckoo Hashing**
    - Two hash tables, two hash functions.
    - Each key has two possible locations.
    - Kick-out relocation on collision, with cycle detection and rehash.