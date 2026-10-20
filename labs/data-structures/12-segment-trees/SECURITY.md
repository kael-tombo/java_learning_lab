# Security Considerations for Segment Trees

## Input Validation

Always validate query and update parameters:
`java
public void rangeSum(int l, int r) {
    if (l > r) throw new IllegalArgumentException("l must be <= r");
    if (l < 0 || r >= n) throw new IndexOutOfBoundsException();
    // proceed with query
}
`

## Integer Overflow

Range sums can exceed Integer.MAX_VALUE. Use long for sum operations:
`java
private long[] tree;  // use long for sum trees
`

## Stack Overflow

Recursive segment trees on very large arrays (n > 10^7) may cause StackOverflowError:
- Use iterative implementation for large datasets
- Or increase JVM stack size: -Xss64m

## Denial of Service

Without lazy propagation, repeated range updates on large ranges are O(n) each:
`java
// Vulnerable: 10^5 range updates on [0, n-1] = O(n^2)
for (int i = 0; i < 100000; i++) {
    naiveRangeUpdate(0, n-1, 1);  // O(n) each!
}
`

**Mitigation**: Always use lazy propagation for range updates in production code.

## Thread Safety

Segment trees are not thread-safe by default. For concurrent access:
- Use read-write locks for range queries vs updates
- Consider immutable/persistent segment trees for concurrent reads
- Avoid sharing mutable segment tree instances between threads

## Memory Exhaustion

4*n array allocation for large n:
- n = 10^8 → 1.6 GB (may cause OutOfMemoryError)
- Monitor memory and use incremental construction if needed
- Consider using disk-based or memory-mapped segment trees

## Security Best Practices

1. Always validate input ranges and indices
2. Use long for aggregate values to prevent overflow
3. Implement lazy propagation to prevent DoS via range updates
4. Use iterative implementation for large n to prevent StackOverflow
5. Make segment trees immutable or use synchronization in concurrent environments
