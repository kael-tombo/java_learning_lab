# Step-by-Step: Implementing Union-Find

## Step 1: Problem Understanding

Before coding, understand the problem: We need a data structure that:
1. Maintains a collection of disjoint sets
2. Determines which set an element belongs to (Find)
3. Merges two sets (Union)
4. Handles dynamic additions (elements can be added over time)

## Step 2: Design the Interface

Define the operations we need:
`java
public class DisjointSetUnion {
    public DisjointSetUnion(int n)        // create n singleton sets
    public int find(int x)                // find set representative
    public boolean union(int x, int y)    // merge sets containing x and y
    public boolean connected(int x, int y) // check if x and y are in same set
    public int getSets()                  // number of disjoint sets
}
`

## Step 3: Choose Representation

Use arrays for O(1) access:
- parent[]: tracking parent pointers
- rank[] or size[]: for the union heuristic

## Step 4: Implement Initialization

Create arrays of size n, set parent[i] = i for all i.

## Step 5: Implement Find

Start simple: iterative without path compression.
Then add path compression for optimization.

## Step 6: Implement Union

Start with naive union (attach second tree under first).
Then add union by rank.

## Step 7: Test Basic Operations

Test with small n, verify that:
- Every element starts as its own set
- After union(x,y), find(x) == find(y)
- After multiple unions, the structure is consistent

## Step 8: Test Edge Cases

- Union with self
- Union of already connected elements
- Find on isolated element
- Large number of elements (stress test)

## Step 9: Add Connected Components

The connected(x, y) method is simply ind(x) == find(y).

## Step 10: Implement Kruskal's Algorithm

`java
public class KruskalMST {
    public List<Edge> findMST(List<Edge> edges, int n) {
        sort edges by weight
        initialize DSU with n vertices
        for each edge in sorted order:
            if union(edge.u, edge.v):
                add edge to MST result
                if MST has n-1 edges: break
        return result
    }
}
`

## Step 11: Test Performance

Benchmark the implementation with and without optimizations:
- Without path compression: O(log n) per operation
- With both optimizations: O(alpha(n)) per operation
- Test with n = 10^6 operations to see the difference

## Step 12: Consider Variants

- Union by size instead of rank
- Iterative find with path halving
- Persistent DSU (for versioning)
- Thread-safe DSU (using locks or CAS)
