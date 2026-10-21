# Interview Questions: Segment Trees

## LeetCode Problem Map
| Problem | Difficulty | Company Signal | Pattern |
|---------|-----------|----------------|---------|
| [LC 307 Range Sum Query - Mutable](https://leetcode.com/problems/range-sum-query-mutable/) | Medium | Amazon, Google, Meta, Microsoft, Apple | Segment tree / Fenwick tree |
| [LC 303 Range Sum Query - Immutable](https://leetcode.com/problems/range-sum-query-immutable/) | Easy | Amazon, Google, Meta, Microsoft, Apple | Prefix sum (baseline) |
| [LC 699 Falling Squares](https://leetcode.com/problems/falling-squares/) | Hard | Google, Amazon, Meta | Segment tree + coordinate compression |
| [LC 218 The Skyline Problem](https://leetcode.com/problems/the-skyline-problem/) | Hard | Google, Amazon, Meta, Microsoft | Segment tree / sweep line |
| [LC 315 Count of Smaller Numbers After Self](https://leetcode.com/problems/count-of-smaller-numbers-after-self/) | Hard | Google, Amazon, Meta, Microsoft | Segment tree / Fenwick tree + compress |
| [LC 850 Rectangle Area II](https://leetcode.com/problems/rectangle-area-ii/) | Hard | Google, Amazon | Segment tree with lazy propagation |
| [LC 729 My Calendar I](https://leetcode.com/problems/my-calendar-i/) | Medium | Amazon, Google, Meta, Microsoft | Segment tree / TreeMap |
| [LC 731 My Calendar II](https://leetcode.com/problems/my-calendar-ii/) | Medium | Google, Amazon, Meta, Microsoft | Segment tree with overlap count |
| [LC 732 My Calendar III](https://leetcode.com/problems/my-calendar-iii/) | Hard | Google, Amazon, Meta | Segment tree with lazy propagation |
| [LC 715 Range Module](https://leetcode.com/problems/range-module/) | Hard | Google, Amazon, Meta | Segment tree with set/clear ranges |
| [LC 352 Data Stream as Disjoint Intervals](https://leetcode.com/problems/data-stream-as-disjoint-intervals/) | Hard | Google, Amazon | Segment tree / TreeMap |
| [LC 308 Range Sum Query 2D - Mutable](https://leetcode.com/problems/range-sum-query-2d-mutable/) | Hard | Google, Amazon, Meta, Microsoft | 2D segment tree / 2D BIT |

## NeetCode Reference
Not directly in NeetCode 150, but the segment tree concept is essential for advanced tree and range query problems.

## Company-Specific Questions

### Google
- Implement a segment tree for range minimum query with point updates in O(log n)
- Design a data structure for 2D range sum queries (2D segment tree — O(log² n) per operation)
- The Skyline problem — solve using segment tree with lazy propagation
- How would you implement a dynamic segment tree for coordinate ranges up to 10⁹?

### Microsoft
- Design a data structure supporting range add and range sum queries (lazy propagation segment tree)
- Implement a segment tree iteratively (bottom-up, 2n size) — compare with recursive version
- How would you support both point update and range reverse operations on an array?

### Meta
- Range sum query with updates — solve with both segment tree and Fenwick tree; compare
- Falling squares — track heights with coordinate compression and segment tree
- Count of smaller numbers after self — segment tree with coordinate compression

### Amazon
- Implement an order statistics tree (find kth smallest) using segment tree over value frequencies
- Design a resource allocation system that checks overlapping intervals (segment tree for range max)
- How would you handle large coordinates (up to 10⁹) for a segment tree? (Coordinate compression)

### Apple
- Design a calendar system that detects event conflicts (my calendar I/II/III problem family)
- How would you implement a versioned segment tree (persistent segment tree)?
- Real-time analytics: maintain max value over sliding windows using segment tree

### Oracle
- How does segment tree with lazy propagation reduce query time for range updates from O(n) to O(log n)?
- Compare segment tree vs Fenwick tree vs sparse table for range queries
- What are the memory trade-offs between array-based and node-based segment tree implementations?

## Real Production Scenarios

- **Scenario 1: Stock Market Order Book** — A trading system maintains a segment tree over price levels. Each leaf represents a price level with the total volume. Range queries (total volume between prices P1 and P2) and point updates (order placement/cancellation) are both O(log n).

- **Scenario 2: Resource Scheduling** — A cloud computing platform tracks resource allocation (CPU, memory) over time. A segment tree with lazy propagation supports range updates (allocate VMs for time window) and range queries (check available resources in time window).

- **Scenario 3: Geographic Information System** — A GIS system stores elevation data for a terrain grid. A segment tree supports range queries for average elevation over a rectangular region (2D segment tree). Lazy updates modify elevation for a sub-region.

## Interview Tips

- Time: O(log n) per query/update, O(n) for building, O(n) for 4n array initialization
- Space: O(n) for array-based tree (4n), O(n log n) for 2D segment tree
- Common edge cases: empty array, single element, zero-length range, full array range, off-by-one in range boundaries
- Always clarify: inclusive vs exclusive range bounds ([l, r] vs [l, r))
- 4n space is safe for any array length — worst case is 4n for n that is power of 2 + some extra
- Lazy propagation: when a range update doesn't fully cover a node, push the pending update to children before recursing

## Java-Specific Considerations

- No standard segment tree class in Java — implement from scratch
- Array-based tree: use `int[]` or `long[]` of size 4*n (or 2*nextPowerOf2 for iterative)
- Node-based tree: `class SegTree { int l, r, val; SegTree left, right; int lazy; }` — needed for dynamic allocation
- For coordinate compression: collect all unique values, sort, map to indices, build segment tree over compressed range
- Iterative segment tree (2n approach): simpler code, faster execution, but only supports certain operations (associative + identity)
- `interface BinaryOperator { int apply(int a, int b); }` — make segment tree generic over operation (sum, min, max, gcd)
- For lazy propagation: store pending update values; `push(node)` applies lazy value to children and clears
- `int mid = (l + r) >>> 1` — use unsigned shift to avoid overflow for large arrays
- Recursive implementation is easier to understand; iterative is faster but less intuitive
