# Security Considerations for Fenwick Tree

## Input Validation

Always validate indices:
`java
public void add(int idx, int delta) {
    if (idx < 0 || idx >= n) {
        throw new IndexOutOfBoundsException("Index: " + idx);
    }
    // proceed
}
`

## Integer Overflow

BIT sums can overflow 32-bit integers. For large datasets:
`java
private long[] bit;  // use long instead of int
`

Maximum safe sum with int: 2^31 - 1 ≈ 2.1B
Maximum sum with long: 2^63 - 1 ≈ 9.2 × 10^18

## Resource Exhaustion

BIT allocates n+1 elements. For n = 10^9:
- int[]: 4 GB (likely too large)
- long[]: 8 GB (way too large)

Use memory-mapped files or distributed BIT for extremely large datasets.

## Thread Safety

Standard BIT is not thread-safe:
- Concurrent adds may lose updates (read-modify-write race)
- Concurrent queries during updates may see inconsistent state

Use AtomicIntegerArray or synchronized wrappers for concurrent access.

## Security Best Practices

1. Validate all input indices
2. Use long for large sums to prevent overflow
3. Implement bounds checking in all public methods
4. Consider concurrent access patterns
5. Document thread-safety guarantees
6. Use appropriate data types for the expected range of values
