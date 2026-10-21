# Common Mistakes with Union-Find

## 1. Forgetting Path Compression

**Mistake**: Implementing Find without path compression.

`java
// BAD: No path compression
int find(int x) {
    while (parent[x] != x) {
        x = parent[x];
    }
    return x;
}
`

**Why it's wrong**: Without path compression, Find operations take O(log n) instead of O(alpha(n)). After many operations, trees become tall and Find becomes slow.

**Fix**: Always include path compression (or at least path halving) in Find.

## 2. Incorrect Union Logic

**Mistake**: Not finding roots before union.

`java
// BAD: Using x and y directly instead of their roots
void union(int x, int y) {
    parent[x] = y;  // Does not connect the actual sets!
}
`

**Why it's wrong**: This just connects x and y directly, not the roots of their sets. The sets remain mostly disconnected.

**Fix**: Always call find(x) and find(y) to get the roots, then connect the roots.

## 3. Not Handling Same-Set Union

**Mistake**: Merging ranks when elements are already in the same set.

`java
// BAD: No check for same root
void union(int x, int y) {
    int rx = find(x), ry = find(y);
    if (rank[rx] < rank[ry]) {
        parent[rx] = ry;
    } else {
        parent[ry] = rx;
        if (rank[rx] == rank[ry]) rank[rx]++;
    }
    sets--;  // Decrements even when x and y are already connected!
}
`

**Fix**: Check if rootX == rootY before modifying.

## 4. Off-by-One in Initialization

**Mistake**: Creating arrays of wrong size or forgetting to initialize.

`java
// BAD: Wrong size
int[] parent = new int[n];  // For elements 1..n, need n+1 size
`

**Fix**: Use 0-indexing consistently, or allocate n+1 for 1-indexed elements.

## 5. Stack Overflow with Recursive Find

**Mistake**: Using recursive find for very deep trees without compression.

**Fix**: Use iterative find, especially for large datasets where worst-case tree depth might exceed the call stack limit.

## 6. Ignoring the Return Value of Union

**Mistake**: Not checking whether union actually merged two sets.

**Fix**: Return boolean from union, use it to track progress (e.g., in Kruskal's algorithm).

## 7. Confusing Rank with Size

**Mistake**: Using rank as the exact tree height or the set size.

`java
// Method expecting exact size
public int getSetSize(int x) {
    return rank[find(x)];  // Wrong! rank is not size
}
`

**Fix**: Maintain a separate size array if you need set sizes.

## 8. Not Rebuilding After Operations

DSU is designed only for union operations. You cannot efficiently split sets once merged. If you need to undo unions, consider a persistent or reversible DSU.
