# Debugging Union-Find

## Logging Strategy

Insert detailed logging at key points:

`java
public int find(int x) {
    System.out.println("find(" + x + ") called, parent[" + x + "] = " + parent[x]);
    if (parent[x] != x) {
        parent[x] = find(parent[x]);
        System.out.println("Path compression: parent[" + x + "] = " + parent[x]);
    }
    return parent[x];
}

public boolean union(int x, int y) {
    System.out.println("union(" + x + ", " + y + ")");
    int rx = find(x), ry = find(y);
    System.out.println("  rootX = " + rx + ", rootY = " + ry + ", rank = [" + 
                       Arrays.toString(rank) + "]");
    if (rx == ry) {
        System.out.println("  Already connected, skipping");
        return false;
    }
    // ... union logic ...
    System.out.println("  After union: parent = " + Arrays.toString(parent) + 
                       ", sets = " + sets);
    return true;
}
`

## Verification Methods

### Check Invariant: Root Has Self-Parent
`java
public boolean verify() {
    for (int i = 0; i < parent.length; i++) {
        if (parent[i] == i) continue;  // root
        // Non-root: verify it's not a root
        if (parent[parent[i]] == parent[i]) continue;  // parent is root
        // Otherwise, check that find(i) returns the same root consistently
        if (find(i) != find(parent[i])) {
            System.out.println("Invariant violated at " + i);
            return false;
        }
    }
    return true;
}
`

### Check Rank Property
`java
public boolean checkRankProperty() {
    for (int i = 0; i < parent.length; i++) {
        if (parent[i] == i && rank[i] > 0) {
            // Root with rank > 0 should have at least 2^rank[i] descendants
            int size = countDescendants(i);
            if (size < (1 << rank[i])) {
                System.out.println("Rank property violated at root " + i + 
                                   ": size = " + size + " < 2^" + rank[i]);
                return false;
            }
        }
    }
    return true;
}
`

## Common Bug Symptom Checklist

| Symptom | Likely Cause |
|---------|-------------|
| find() hangs or loops forever | Cycle in parent pointers (incorrect union) |
| Same-set elements return different roots | Missing path compression or bug in union |
| sets count wrong | Not checking if roots were already equal |
| StackOverflowError | Recursive find on very deep tree |
| union() creates incorrect trees | Forgetting to find roots before comparing ranks |
| Kruskal selects wrong edges | union() not returning correct boolean |
| Memory issues | DSU array size mismatch with actual elements |

## Tools

1. **Assertions**: Enable with -ea flag, add assertion checks
2. **Visualization**: Print parent array and tree structure after each operation
3. **Small Tests**: Test with n=3 or n=4, verify manually
4. **Random Testing**: Fuzz test with random operations, verify invariants
