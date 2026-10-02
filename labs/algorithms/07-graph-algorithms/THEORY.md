# Graph Algorithms — Theoretical Foundation

## Graph Traversal

### BFS (Breadth-First Search)
- Uses queue, explores level by level
- Finds shortest path in unweighted graphs
- Time: O(V + E), Space: O(V)

### DFS (Depth-First Search)
- Uses stack (recursive or explicit)
- Explores depth first, backtracks
- Time: O(V + E), Space: O(V) for stack

## Shortest Paths

### Dijkstra
- Greedy, non-negative weights only
- Time: O((V+E) log V) with PQ
- Space: O(V)

### Bellman-Ford
- Handles negative edges, detects negative cycles
- Time: O(VE)

### Floyd-Warshall
- All-pairs shortest paths
- Time: O(V³), Space: O(V²)

## Minimum Spanning Tree

### Prim's
- Greedy, grows tree from a start node
- Time: O(E log V) with PQ

### Kruskal's
- Greedy, adds smallest edges without cycles
- Time: O(E log E) with Union-Find

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "Dijkstra — finding shortest paths from given vertex", CP-algorithms (page last updated Sep 24, 2023) — https://cp-algorithms.com/graph/dijkstra.html — confirms the lab's Dijkstra entry: requires non-negative edge weights; with a binary-heap/priority-queue implementation on sparse graphs the bound is O(n log n + m), matching the lab's O((V+E) log V) claim — verify against the lab's Dijkstra exercise before citing.
- Same source, correctness proof idea — the key invariant is "after any vertex v becomes marked, d[v] is final and never changes", proved by induction using non-negativity of weights — useful framing for the lab's Bellman-Ford contrast exercise (negative edges break exactly this invariant).
- Same source, path restoration via predecessor array p[to] = v on each successful relaxation, then walking backpointers from target to s — directly applicable to the lab's shortest-path reconstruction exercises.
- Same source, dense-graph note — the naive O(n² + m) implementation is optimal when m ≈ n², so the lab's PQ variant should be presented as the sparse-graph choice — check the lab's complexity table distinguishes dense vs sparse.
