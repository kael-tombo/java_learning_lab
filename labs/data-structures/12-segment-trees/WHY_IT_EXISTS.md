# Why Segment Trees Exist

## The Problem: Efficient Range Operations

Before segment trees, performing range operations on arrays was inefficient:
- **Brute force**: Range sum query on [l, r] required O(n) time
- **Prefix sums**: O(1) queries but O(n) updates
- **Balanced BSTs**: Could maintain order but not range aggregates

The need for a data structure supporting both efficient range queries and updates led to the invention of segment trees.

## The Innovation

Segment trees were developed in the 1970s for computational geometry problems. The key insight was that any interval can be represented as a union of O(log n) disjoint segments from the tree. By storing aggregate information (sum, min, max) at each node, queries can be answered by combining O(log n) node values.

## Why Not Use Other Structures?

### Prefix Sums vs Segment Trees
- Prefix sums give O(1) range sum but O(n) updates
- Segment trees give O(log n) for both

### Fenwick Tree vs Segment Tree
- BIT is simpler and faster for prefix sums
- Segment trees handle more operations (min, max, arbitrary combine)

### Balanced BST vs Segment Tree
- BSTs maintain order but don't naturally support range aggregates
- Segment trees are specialized for range operations

## Applications

The versatility of segment trees made them essential in:
- Computational geometry (line sweep, interval stabbing)
- Database systems (range queries on indexed columns)
- Competitive programming (range query problems)
- Image processing (2D segment trees for image regions)
- Geographic information systems (spatial range queries)
