# Why Fenwick Tree Exists

## The Problem: Prefix Sums with Updates

Arrays support O(1) prefix sum queries (with prefix precomputation) but O(n) updates. Segment trees support O(log n) for both but are complex. The Fenwick tree strikes a balance: simpler than a segment tree while still providing O(log n) for both operations.

## The Innovation

Peter Fenwick recognized that the binary representation of indices could guide a tree structure. The insight was that the BIT uses the same storage as the original array (plus one element), making it extremely memory-efficient.

## Why Not Use Other Structures?

### Prefix Sum Arrays vs BIT
- Prefix sums: O(1) query, O(n) update
- BIT: O(log n) query, O(log n) update
- BIT wins when updates are frequent

### Segment Trees vs BIT
- Segment trees: O(log n) for all operations, complex implementation
- BIT: O(log n) for prefix sums, simple implementation
- BIT doesn't support arbitrary range queries (min, max) easily
- Segment trees are more general but more complex

### Balanced BSTs vs BIT
- BSTs: O(log n) for order statistics, complex balancing
- BIT: O(log n) for prefix sums, no balancing needed

## Impact

The Fenwick tree became one of the most popular data structures in competitive programming due to its simplicity and efficiency. It's often the first choice for problems involving prefix sums with point updates.
