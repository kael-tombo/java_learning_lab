# Security Considerations for Union-Find

## Input Validation

DSU takes element indices as input. Proper input validation is essential:

`java
public void validateIndex(int x) {
    if (x < 0 || x >= parent.length) {
        throw new IndexOutOfBoundsException("Index " + x + 
            " out of bounds for size " + parent.length);
    }
}
`

## Integer Overflow

When using union by size, the size can theoretically overflow:
`java
if (size[rootX] < size[rootY]) {
    parent[rootX] = rootY;
    size[rootY] += size[rootX];  // Potential overflow for very large sets
}
`

For n <= Integer.MAX_VALUE, this is safe. Use long for extremely large sets.

## Denial of Service

Without path compression, an attacker can craft a sequence of operations that creates deep trees, causing:
- Slow Find operations: O(n) per Find
- Stack overflow with recursive Find

Always enable path compression to prevent this.

## Thread Safety

Standard DSU is not thread-safe. Concurrent access can cause:
- **Race condition in Find**: Two threads may read/write parent pointers simultaneously
- **Corrupted state**: Union operations can interleave, leaving inconsistent state
- **Incorrect results**: Two threads may get wrong connectivity answers

Use synchronized or ReentrantLock for concurrent access.

## Resource Exhaustion

- **Memory**: Large parent arrays (e.g., 10^9 elements) require 8 GB for parent + rank arrays
- **Stack**: Recursive find with depth > 10^4 may cause StackOverflowError
- **Time**: Without optimizations, 10^6 operations can take > 10^12 steps in worst case

## Security in Practice

For security-sensitive applications:
1. Always validate all input indices
2. Enable both path compression and union by rank
3. Use iterative find for large datasets
4. Consider memory limits and cap the maximum size
5. Use thread-safe wrappers in concurrent environments
6. Log unexpected behavior (e.g., very deep recursion)
