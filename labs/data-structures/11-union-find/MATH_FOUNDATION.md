# Math Foundation of Union-Find

## The Inverse Ackermann Function

The time complexity of Union-Find with both optimizations is O(alpha(n)), where alpha(n) is the inverse of the Ackermann function.

### Ackermann Function

The Ackermann function is defined recursively:

`
A(0, n) = n + 1
A(m, 0) = A(m-1, 1)     for m > 0
A(m, n) = A(m-1, A(m, n-1))  for m > 0 and n > 0
`

This function grows extremely fast:
- A(1, n) = 2n
- A(2, n) = 2^n
- A(3, n) = 2^2^...^2 (n times) — tower of exponents
- A(4, n) grows faster than any practical number

### Inverse Ackermann Function

alpha(n) = min{ k >= 0 : A(k, 1) > n }

This is the smallest k such that A(k, 1) exceeds n.

Values:
- A(1, 1) = 3
- A(2, 1) = 7
- A(3, 1) = 2047
- A(4, 1) = 2^2047 - 3, which is astronomically large

Therefore:
- For n <= 3: alpha(n) = 0
- For n <= 7: alpha(n) = 1
- For n <= 2047: alpha(n) = 2
- For any realistic n: alpha(n) = 3
- For n > A(4, 1): alpha(n) = 4

## Proof Sketch for O(alpha(n)) Bound

1. Each element's rank increases at most log n times (union by rank guarantee)
2. Path compression ensures that once an element's parent changes, it moves to a node of strictly higher rank
3. The number of times any element's parent can change before it becomes a direct child of a root is bounded by the rank
4. These two constraints together yield the inverse Ackermann bound

## Key Properties

### Rank Property
After any sequence of operations, for any element x with rank r, the subtree rooted at x contains at least 2^r elements.

Proof: By induction. When two trees of equal rank r merge, the new root has rank r+1 and contains at least 2 * 2^r = 2^(r+1) elements.

### Size Property
The size of a tree with rank r is at least 2^r. This follows from the rank property above.

### Height Bound
The height of any tree in DSU with n elements is at most log n. With union by rank, the height is bounded by O(log n) even without path compression.

## Amortized Analysis

The key insight of Tarjan's analysis is that the total work across all operations is O(n * alpha(n)). Each Find operation starts at a node and follows parent pointers to the root. While some Finds are expensive (following many pointers), subsequent Finds on the same path are cheap due to path compression.
