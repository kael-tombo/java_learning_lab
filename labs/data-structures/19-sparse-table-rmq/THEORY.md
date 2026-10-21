# Theory: Sparse Table & RMQ

## Fundamentals

A sparse table is a data structure for answering range queries on static arrays. It precomputes answers for all intervals of length 2^k, enabling O(1) queries. The trade-off is O(n log n) space and preprocessing time.

## Structure

The sparse table is a 2D array where:
- st[i][j] = result for range [i, i + 2^j - 1]
- st[i][0] = arr[i] for all i
- st[i][j] = combine(st[i][j-1], st[i + 2^(j-1)][j-1])

## Range Minimum Query (RMQ)

For min queries, the operation is idempotent: min(x, x) = x
- Query(l, r): find largest k such that 2^k <= r-l+1
- Return min(st[l][k], st[r - 2^k + 1][k])

This works because the two intervals [l, l+2^k-1] and [r-2^k+1, r] cover the entire range with overlap. Since min is idempotent, overlapping is fine.

## Range Sum Query

Sum is not idempotent, so the standard sparse table doesn't work for O(1) sum queries. However, we can use the sparse table for O(log n) sum queries using binary decomposition of the range length.

## Disjoint Sparse Table

The disjoint sparse table handles non-idempotent operations in O(1) by storing prefix/suffix sums for each block at each level, ensuring no overlap in queries.

## Complexity

| Operation | Sparse Table | Segment Tree |
|-----------|-------------|--------------|
| Preprocess | O(n log n) | O(n) |
| Query | O(1) | O(log n) |
| Update | Not supported | O(log n) |
| Space | O(n log n) | O(n) |
