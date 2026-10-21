# Architecture of Union-Find in Context

## Integration Patterns

### Standalone Usage
DSU is typically used as a utility class:
`java
DisjointSetUnion dsu = new DisjointSetUnion(100);
for (Edge e : edges) {
    if (dsu.union(e.u, e.v)) {
        mst.add(e);
    }
}
`

### Service Layer Integration
`java
@Service
public class ConnectivityService {
    private DisjointSetUnion dsu;
    
    public void initializeGraph(int n) {
        this.dsu = new DisjointSetUnion(n);
    }
    
    public boolean addConnection(int u, int v) {
        return dsu.union(u, v);
    }
    
    public boolean areConnected(int u, int v) {
        return dsu.connected(u, v);
    }
    
    public int connectedComponents() {
        return dsu.getSets();
    }
}
`

### Microservice Context
`java
@RestController
public class ConnectivityController {
    private final ConnectivityService service;
    
    @PostMapping("/connect")
    public ResponseEntity<?> connect(@RequestParam int u, @RequestParam int v) {
        boolean merged = service.addConnection(u, v);
        return ResponseEntity.ok(Map.of("merged", merged));
    }
    
    @GetMapping("/connected")
    public ResponseEntity<?> connected(@RequestParam int u, @RequestParam int v) {
        return ResponseEntity.ok(Map.of("connected", service.areConnected(u, v)));
    }
}
`

## Architecture Decisions

### Array vs Map
- **Array-based**: O(1) access, cache-friendly, but requires contiguous indices
- **Map-based**: Handles non-contiguous elements, but O(log n) or O(1) amortized

### Recursive vs Iterative Find
- **Recursive**: Elegant, uses call stack for path compression
- **Iterative**: More complex but avoids stack overflow for large n

### Rank vs Size
- **Rank**: Upper bound on height, smaller memory update
- **Size**: Exact element count, useful for additional queries

## Performance Architecture

### Tier 1: Basic DSU
- Path compression only
- O(log n) amortized per operation

### Tier 2: Optimized DSU
- Path compression + union by rank
- O(alpha(n)) amortized per operation

### Tier 3: Concurrent DSU
- Lock-based or lock-free
- Thread safety with performance trade-offs

## Testing Architecture

`
Unit Tests:        Each method in isolation
Integration Tests: Full workflow (e.g., Kruskal's algorithm)
Property Tests:    Invariants hold after random sequences
Performance Tests: Benchmarks against naive implementations
`
"@

System.Collections.Hashtable["EXERCISES.md"] = @"
# Exercises: Union-Find

## Beginner

1. **Basic DSU**: Implement a basic DSU with path compression and union by rank. Test with 10 elements doing 5 union operations.

2. **Connected Components**: Write a program that reads n and m (number of nodes and edges), then processes m union operations. Output the number of connected components after each operation.

3. **Cycle Detection**: Given an undirected graph represented as an edge list, use DSU to detect if the graph contains a cycle.

## Intermediate

4. **Kruskal's MST**: Implement Kruskal's algorithm using DSU. Given a weighted graph, find the weight of the Minimum Spanning Tree.

5. **Number of Islands II**: You are given an m x n grid and a list of positions to add land. After each addition, return the number of islands. Use DSU.

6. **Accounts Merge**: Given a list of accounts where each account has a name and emails, merge accounts that share at least one common email. Use DSU to group related emails.

7. **Longest Consecutive Sequence**: Given an unsorted array of integers, find the length of the longest consecutive elements sequence. Solve in O(n) using DSU.

## Advanced

8. **Evaluate Division**: Given equations like ["a/b=2", "b/c=3"], answer queries like "a/c=?" using a weighted DSU (track the ratio between elements).

9. **Dynamic Graph Connectivity**: Support adding and removing edges in a graph. Use a divide-and-conquer approach with a persistent DSU.

10. **Minimum Spanning Tree Verification**: Given a graph and a candidate spanning tree, verify it's an MST using DSU and cycle properties.

11. **Optimized DSU with Path Halving**: Implement DSU using path halving instead of full compression. Compare performance.

12. **Union by Size with Component Queries**: Extend DSU to support querying the size of a component and iterating through elements in a component.

13. **Percolation Threshold**: Use DSU to simulate percolation in an n x n grid. Find the threshold where a path from top to bottom exists.

14. **Social Network Graph**: Given a log of friend connections, find the earliest time when all users are in the same connected component.

15. **Parallel DSU**: Design a lock-free DSU using atomic CAS operations. Implement and test for thread safety.
