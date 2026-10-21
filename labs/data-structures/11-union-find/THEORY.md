# Theory: Disjoint Set Union (Union-Find)

## Fundamentals

The Disjoint Set Union (DSU), also known as Union-Find, is a data structure that tracks a partition of a set into disjoint (non-overlapping) subsets. It supports two primary operations:

- **Find**: Determine which subset a particular element belongs to
- **Union**: Merge two subsets into a single subset

Each subset is represented by a representative element (also called the root or parent). Initially, each element is its own representative, forming singleton sets.

## Representation

DSU is typically implemented using two arrays:

- parent[]: parent[i] stores the parent of element i. The root element has itself as its parent.
- ank[] or size[]: stores the rank (upper bound on tree height) or size (number of elements) of each subset.

### Initial State

For n elements, initially parent[i] = i and rank[i] = 0 for all i.

### Find Operation

The Find operation traverses from an element up to the root by following parent pointers:

`
function find(x):
    if parent[x] != x:
        parent[x] = find(parent[x])  // path compression
    return parent[x]
`

### Union Operation

The Union operation merges two subsets:

`
function union(x, y):
    rootX = find(x)
    rootY = find(y)
    if rootX == rootY: return
    if rank[rootX] < rank[rootY]:
        parent[rootX] = rootY
    else if rank[rootX] > rank[rootY]:
        parent[rootY] = rootX
    else:
        parent[rootY] = rootX
        rank[rootX]++
`

## Complexity

With both path compression and union by rank, the amortized time per operation is O(alpha(n)), where alpha(n) is the inverse Ackermann function. For all practical values of n, alpha(n) <= 5.

| Operation | Without Optimization | With Path Compression | With Both Optimizations |
|-----------|---------------------|----------------------|-------------------------|
| Find      | O(log n)            | O(log n) amortized   | O(alpha(n)) amortized   |
| Union     | O(log n)            | O(log n) amortized   | O(alpha(n)) amortized   |
| Space     | O(n)                | O(n)                 | O(n)                    |

## Applications

1. Kruskal's Minimum Spanning Tree Algorithm
2. Dynamic connectivity in graphs
3. Finding connected components
4. Cycle detection in undirected graphs
5. Image processing (connected component labeling)
6. Social network analysis (friend groups)
7. Percolation theory
8. Maze generation
