# Code Deep Dive: DisjointSetUnion.java

## Class Overview

The DisjointSetUnion class provides a complete implementation of the Union-Find data structure with both path compression and union by rank optimizations.

## Implementation Walkthrough

### Instance Variables

`java
private int[] parent;
private int[] rank;
private int sets;
`

- parent: Array where parent[i] is the parent of element i. The root of a set has parent[i] = i.
- ank: Array where rank[i] is an upper bound on the height of the tree rooted at i.
- sets: The number of disjoint sets currently tracked.

### Constructor

`java
public DisjointSetUnion(int n) {
    parent = new int[n];
    rank = new int[n];
    sets = n;
    for (int i = 0; i < n; i++) {
        parent[i] = i;
    }
}
`

Creates n singleton sets. Each element is its own parent, each rank is 0.

### Find with Path Compression

`java
public int find(int x) {
    if (parent[x] != x) {
        parent[x] = find(parent[x]);
    }
    return parent[x];
}
`

The recursive implementation traverses from x to the root, then sets each node's parent directly to the root on the way back. This flattens the tree.

For very large datasets, the recursive approach may cause stack overflow. An iterative version with path compression is preferred:

`java
public int find(int x) {
    int root = x;
    while (root != parent[root]) {
        root = parent[root];
    }
    // Path compression: walk from x to root, setting parents
    while (x != root) {
        int next = parent[x];
        parent[x] = root;
        x = next;
    }
    return root;
}
`

### Union with Rank

`java
public boolean union(int x, int y) {
    int rootX = find(x);
    int rootY = find(y);
    if (rootX == rootY) return false;
    
    if (rank[rootX] < rank[rootY]) {
        parent[rootX] = rootY;
    } else if (rank[rootX] > rank[rootY]) {
        parent[rootY] = rootX;
    } else {
        parent[rootY] = rootX;
        rank[rootX]++;
    }
    sets--;
    return true;
}
`

Returns true if the sets were merged, false if x and y were already connected. The rank comparison ensures the tree remains balanced.

### Connected and Same Set Check

`java
public boolean connected(int x, int y) {
    return find(x) == find(y);
}
`

### Utility Methods

`java
public int getSets() { return sets; }
public int size() { return parent.length; }
`

## Complexity Analysis

- **Space**: O(n) for the two arrays
- **Find**: O(alpha(n)) amortized
- **Union**: O(alpha(n)) amortized
- **Constructor**: O(n)

## Edge Cases

1. **Negative indices**: Throw IllegalArgumentException
2. **Indices beyond length**: Throw IndexOutOfBoundsException
3. **Single element**: find(0) returns 0 immediately
4. **Already connected**: union returns false without modifying structure
