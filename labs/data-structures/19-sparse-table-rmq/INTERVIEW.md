# Interview Questions: Sparse Table & RMQ

## LeetCode Problem Map
| Problem | Difficulty | Company Signal | Pattern |
|---------|-----------|----------------|---------|
| [LC 239 Sliding Window Maximum](https://leetcode.com/problems/sliding-window-maximum/) | Hard | Amazon, Meta, Google, Microsoft | Deque / sparse table |
| [LC 303 Range Sum Query - Immutable](https://leetcode.com/problems/range-sum-query-immutable/) | Easy | Amazon, Google, Meta, Microsoft, Apple | Prefix sum (baseline) |
| [LC 307 Range Sum Query - Mutable](https://leetcode.com/problems/range-sum-query-mutable/) | Medium | Amazon, Google, Meta, Microsoft | Segment tree / Fenwick tree |
| [LC 152 Maximum Product Subarray](https://leetcode.com/problems/maximum-product-subarray/) | Medium | Amazon, Meta, Google, Microsoft | Prefix/suffix / sparse table |
| (System design focus) | — | Google, Meta, Amazon, Microsoft | Precomputation trade-offs |

## NeetCode Reference
Not in NeetCode 150. Sparse table is a supplementary technique for range queries without updates.

## Company-Specific Questions

### Google
- Implement a data structure for range minimum query (RMQ) with O(1) query and O(n log n) preprocessing
- Why does a sparse table work for min/max/gcd but not for sum? (Idempotence requirement)
- How would you handle range query for a dynamic array (with updates) using a sparse table? (Full rebuild on update)
- Design a system that precomputes aggregates over rolling time windows using sparse table principles

### Microsoft
- Compare sparse table vs segment tree vs Fenwick tree for range queries — trade-offs
- Implement a sparse table for range minimum query — explain the overlapping intervals approach
- How would you extend sparse table to 2D for image processing operations?

### Meta
- Sliding window maximum — solve with deque and compare with sparse table approach
- Range minimum query on a static array — how would you precompute for O(1) queries?
- Implement a disjoint sparse table (also O(n log n), but all ranges are prefix/suffix — no overlap)

### Amazon
- Design a real-time analytics system for static historical data using sparse table precomputations
- How would you handle range product queries with sparse tables (fix for negative numbers)?
- Compare sparse table preprocessing (O(n log n) time, O(n log n) space) with segment tree (O(n) space)

### Apple
- How would you implement a sparse table for range queries on a buffer of sensor readings (static during analysis)?
- Design an offline query system for genomic data analysis using precomputed range tables
- What are the memory trade-offs of sparse table for 10^6 elements (log_2(10^6) ≈ 20, so ~20 * 10^6 entries)?

### Oracle
- Explain the mathematical foundation of sparse table: `st[i][k]` covers range [i, i + 2^k - 1]
- How does the K-th ancestor problem relate to sparse table? (Binary lifting)
- When would you use a sparse table in an Oracle Database context (precomputed query results)?

## Real Production Scenarios

- **Scenario 1: Static Range Queries on Financial Data** — A financial analytics platform precomputes a sparse table over 10 years of daily stock prices. Analysts can query the minimum/maximum price in any date range in O(1). The data is static (historical), so the rebuild cost of O(n log n) is paid once.

- **Scenario 2: Image Processing** — An image processing pipeline uses a 2D sparse table for range maximum/minimum queries on a static image. This enables efficient morphological operations (dilation/erosion) using sliding window queries with O(1) time.

- **Scenario 3: K-th Ancestor in Trees** — A social network recomputes the k-th ancestor for all nodes in a tree using binary lifting (sparse table on parent pointers). For each node, `up[node][k]` stores the 2^k-th ancestor. This enables O(log n) queries for "is user A an ancestor of user B in the comment tree?"

## Interview Tips

- Time: O(n log n) preprocessing, O(1) per query (for idempotent functions), O(log n) per query (for non-idempotent like sum)
- Space: O(n log n) — table of size n × (⌊log₂ n⌋ + 1)
- Common edge cases: empty array, single element, queries where l = r, queries where k = 0
- Idempotent functions (min, max, gcd, bitwise AND/OR): allow overlap in intervals → O(1) query
- Non-idempotent functions (sum, product): don't allow overlap → need O(log n) by combining multiple intervals
- Building: for k from 1 to logN, for i from 0 to n-2^k, `st[i][k] = combine(st[i][k-1], st[i + 2^(k-1)][k-1])`
- Querying (idempotent): `k = floor(log2(r - l + 1))`; `result = combine(st[l][k], st[r - 2^k + 1][k])`

## Java-Specific Considerations

- No standard sparse table class in Java — implement from scratch
- Table representation: `int[][] st = new int[n][logN + 1];` where `logN = (int)(Math.log(n) / Math.log(2))`
- Precompute logarithms: `int[] log = new int[n + 1]; log[0] = log[1] = 0; for (int i = 2; i <= n; i++) log[i] = log[i/2] + 1;`
- `log2` lookup table avoids computing `Math.log()` per query (expensive)
- Combine function as parameter: `@FunctionalInterface interface RMQ { int combine(int a, int b); }`
- For objects: `int[][]` with `Integer.MAX_VALUE` for min sentinel, `Integer.MIN_VALUE` for max sentinel
- For long values: `long[][]` variant
- Memory: for n = 100,000 and logN = 17, a `int[100_000][17]` table is ~6.8 MB (fine for most applications)
- For n = 10^7, sparse table requires ~400 MB — use segment tree instead (linear space)
- 2D sparse table: `int[rows][cols][logRows][logCols]` — O(rc log r log c) space
- `Arrays.fill(st[i], Integer.MAX_VALUE)` for initialization, then populate by k
