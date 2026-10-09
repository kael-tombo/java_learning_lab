# Debugging Segment Trees

## Verification Techniques

### Print Tree Contents
`java
public void printTree() {
    for (int i = 1; i < 4 * n; i++) {
        System.out.println("tree[" + i + "] = " + tree[i]);
    }
}
`

### Brute Force Validation
For debugging, maintain a simple array alongside the segment tree and compare results:
`java
public boolean validate(int[] arr) {
    for (int i = 0; i < n; i++) {
        for (int j = i; j < n; j++) {
            if (rangeSum(i, j) != bruteForceSum(arr, i, j)) {
                return false;
            }
        }
    }
    return true;
}
`

## Common Bug Symptoms

| Symptom | Likely Cause |
|---------|-------------|
| All queries return 0 | Identity value wrong, or tree never populated |
| Wrong sum for full range | Root value incorrect — check build logic |
| Wrong sum for partial ranges | Recursion bounds incorrect |
| Infinite recursion | Base case not reached (range not narrowing) |
| ArrayIndexOutOfBounds | Tree array too small (use 4*n) |
| StackOverflowError | Too many recursive calls (n too large) |
| Lazy updates not applying | push() not called before traversal |

## Testing Strategy

1. Test with n = 1 (edge case)
2. Test with n = 2, 3, 4 (small exhaustive)
3. Test with n = 100 and random data (statistical)
4. Test with n = 10^5 (performance + correctness)
5. Test range updates with lazy propagation thoroughly

## Logging

Add detailed logging for debugging complex operations:
`java
System.out.printf("Query [%d, %d] at node %d [%d, %d] = %d%n",
    ql, qr, node, l, r, tree[node]);
`
"@

System.Collections.Hashtable["REFACTORING.md"] = @"
# Refactoring Segment Trees

## 1. Extract Interface

`java
public interface RangeQueryStructure {
    int rangeSum(int l, int r);
    int rangeMin(int l, int r);
    int rangeMax(int l, int r);
    void pointUpdate(int pos, int val);
    void rangeUpdate(int l, int r, int val);
}
`

Allows swapping between segment tree, Fenwick tree, and sparse table.

## 2. Generic Segment Tree

`java
public class SegmentTree<T> {
    private final T[] tree;
    private final BinaryOperator<T> combiner;
    private final T identity;
    
    public SegmentTree(T[] arr, BinaryOperator<T> combiner, T identity) {
        this.combiner = combiner;
        this.identity = identity;
        // build tree
    }
}
`

## 3. Iterative (Non-Recursive) Implementation

Replace recursion with loops for better performance:
`java
public int rangeSum(int l, int r) {
    l += size; r += size;
    int sum = 0;
    while (l <= r) {
        if ((l & 1) == 1) sum += tree[l++];
        if ((r & 1) == 0) sum += tree[r--];
        l /= 2; r /= 2;
    }
    return sum;
}
`

## 4. Separate Lazy Update Logic

Extract lazy propagation into its own class:
`java
public class LazyPropagator {
    private int[] lazy;
    
    public void apply(int node, int l, int r, int val) { ... }
    public void push(int node, int l, int r, int[] tree) { ... }
}
`

## 5. Memory-Efficient Variants

For specific use cases:
- Use long[] instead of int[] for large sums
- Use yte[] for boolean range queries
- Use object arrays for complex aggregates

## 6. Persistent Segment Tree

Refactor to support versioning for offline algorithms:
`java
public class PersistentSegmentTree {
    private List<Node> versions = new ArrayList<>();
    
    public int update(int prevRoot, int pos, int val) { ... }
    public int query(int root, int l, int r) { ... }
}
`
"@

System.Collections.Hashtable["PERFORMANCE.md"] = @"
# Performance of Segment Trees

## Theoretical Performance

| Operation | Recursive | Iterative | Lazy Propagation |
|-----------|-----------|-----------|-----------------|
| Build | O(n) | O(n) | O(n) |
| Range Query | O(log n) | O(log n) | O(log n) |
| Point Update | O(log n) | O(log n) | O(log n) |
| Range Update | O(n) naive | O(n) naive | O(log n) |

## Empirical Benchmarks

For n = 10^5, 10^6 random operations on Intel i7:

| Implementation | Time for 10^6 ops | Memory |
|---------------|-------------------|--------|
| Recursive segment tree | ~0.8s | ~3.2 MB |
| Iterative segment tree | ~0.4s | ~1.6 MB |
| With lazy propagation | ~1.2s | ~6.4 MB |
| Fenwick tree (for comparison) | ~0.2s | ~0.8 MB |

## Cache Performance

- Recursive trees have poor cache locality for deep traversals
- Iterative trees have better cache behavior (sequential array access)
- Lazy propagation adds extra cache misses (lazy array is separate)

## Memory Comparison

| Structure | Array Size | Memory (10^6 ints) |
|-----------|-----------|-------------------|
| Segment Tree (recursive) | 4n | 16 MB |
| Segment Tree (iterative) | 2n | 8 MB |
| Fenwick Tree | n+1 | 4 MB |
| Sparse Table | n log n | 80 MB |

## Optimization Tips

1. Use iterative implementation for speed-critical code
2. Minimize recursion depth by making tree size a power of 2
3. Use primitive arrays instead of ArrayList<Integer>
4. Inline the combine operation where possible
5. Use long for sum aggregations to avoid overflow
6. Pre-allocate all arrays in constructor

## When to Use Different Variants

- **Recursive**: Clarity, easy lazy propagation, educational purposes
- **Iterative**: Maximum performance, no lazy propagation needed
- **Lazy propagation**: Range updates are frequent
- **Persistent**: Need versioning (offline queries, undo support)
