# Internals of Segment Trees

## Memory Layout

### Array Representation

Segment trees are commonly stored in a flat array for cache efficiency:

`
Index:  1    2    3    4    5    6    7    8  ...
Node:   [0-7][0-3][4-7][0-1][2-3][4-5][6-7][0] ...
`

For a tree with n leaves:
- Array size needed: 4*n (safe upper bound)
- Root at index 1 (simplifies parent-child calculations)
- Left child of i: 2*i
- Right child of i: 2*i + 1

### Memory Calculation

For n = 10^5:
- 4 * n = 400,000 integers
- At 4 bytes per int: ~1.6 MB
- Plus lazy array: ~1.6 MB
- Total: ~3.2 MB (negligible for modern systems)

## Node Structure

Each node conceptually stores:
`java
class Node {
    int sum;        // range aggregate
    int lazy;       // pending range update (if any)
    int left;       // left index in array
    int right;      // right index in array
}
`

In array implementation, these are separate arrays:
`java
int[] tree;   // aggregates
int[] lazy;   // pending updates
`

## Recursive vs Iterative

### Recursive (Standard)
- Pros: Clear, easy to implement, supports lazy propagation naturally
- Cons: Function call overhead, recursion depth limited to O(log n), but n can be 10^6+ for large datasets

### Iterative (ZKW-style)
- Pros: Faster (no recursion), smaller memory (2n instead of 4n), no stack overflow
- Cons: Harder to implement lazy propagation, less intuitive

## Lazy Propagation Details

The lazy array stores pending operations:
`java
// Add x to range [l, r]
void rangeAdd(int node, int l, int r, int ql, int qr, int x) {
    if (ql <= l && r <= qr) {
        tree[node] += (r - l + 1) * x;
        lazy[node] += x;
        return;
    }
    push(node, l, r);  // propagate lazy to children
    int mid = (l + r) / 2;
    if (ql <= mid) rangeAdd(node*2, l, mid, ql, qr, x);
    if (qr > mid) rangeAdd(node*2+1, mid+1, r, ql, qr, x);
    tree[node] = tree[node*2] + tree[node*2+1];
}

void push(int node, int l, int r) {
    if (lazy[node] != 0) {
        int mid = (l + r) / 2;
        tree[node*2] += (mid - l + 1) * lazy[node];
        tree[node*2+1] += (r - mid) * lazy[node];
        lazy[node*2] += lazy[node];
        lazy[node*2+1] += lazy[node];
        lazy[node] = 0;
    }
}
`
"@

System.Collections.Hashtable["MATH_FOUNDATION.md"] = @"
# Math Foundation of Segment Trees

## Tree Properties

### Size of a Segment Tree

A segment tree for an array of n elements:
- Number of leaves: n
- Height of tree: ceil(log2(n))
- Total nodes: at most 2 * 2^ceil(log2(n)) - 1
- Conservative bound: 4n nodes in array representation

Proof of node count: The tree is a full binary tree. The number of internal nodes is at most n-1. Total nodes = n + (n-1) = 2n-1 for a complete tree. The 4n bound comes from using a power-of-two size that may be up to 2x n.

## Query Complexity

### Number of Nodes Visited

A range query visits at most 4 * log2(n) nodes. The standard proof:
1. At each level, at most 4 nodes are visited
2. There are O(log n) levels
3. Total visited: O(log n)

Proof sketch:
- At the root level, 1 node is visited
- At each subsequent level, the query range can partially overlap at most 2 nodes
- Each partially overlapped node expands to at most 2 children at the next level
- The 4 nodes per level bound is tight (not all levels visit 4 nodes)

### Tight Bound

The exact maximum is: 4 * ceil(log2(n)) - 1 nodes for a range query.

## Associative Operations

Segment trees work with any associative operation:
- a + (b + c) = (a + b) + c
- min(a, min(b, c)) = min(min(a, b), c)
- gcd(a, gcd(b, c)) = gcd(gcd(a, b), c)

Non-associative operations cannot be used with standard segment trees.

## Lazy Propagation Analysis

With lazy propagation:
- Each update touches O(log n) nodes
- Each query touches O(log n) nodes
- The lazy array adds O(1) overhead per node

The total time for q operations on n elements is O(q log n).

## Memory Bound

Let size = 2^k where 2^(k-1) < n <= 2^k:
- Array size needed: 2 * size * 2 = 2^(k+2) < 4n
- For n = 10^6, size = 2^20 = 1,048,576
- Array size: 4,194,304 integers â‰ˆ 16 MB (with int)

## Advanced: Persistent Segment Tree

A persistent segment tree creates a new root for each version. Memory becomes O(T log n) where T is the number of versions. Each update creates O(log n) new nodes. The space complexity is O(n + T log n).
