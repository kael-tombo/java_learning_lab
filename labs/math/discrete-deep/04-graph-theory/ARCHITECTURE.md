# Architecture: Graph Code Design

## Choose the Representation From the Query Pattern

The representation is the load-bearing decision; everything else follows:

1. **Traversal-heavy, sparse (E ≈ few × V):** adjacency lists (primitive arrays or CSR). BFS/DFS/topo become O(V+E) with sequential memory access.
2. **Edge-existence queries or dense graphs (E ≈ V²):** adjacency matrix — O(1) `hasEdge`, and O(V²) Dijkstra without a heap beats the heap version once E is near V².
3. **Sort-then-process (Kruskal, connectivity by sorting):** edge list as the input format, converted once.
4. **Static, huge, read-only:** CSR built in O(E) via counting sort, then all algorithms run against it.

Document the choice at the type level: `class AdjListGraph` vs `class MatrixGraph` behind a `Graph` interface, so an algorithm's complexity claim ("O(V+E)") is auditable against the storage it received.

## The Graph Interface

```java
interface Graph {
    int vertexCount();
    Iterable<Integer> neighbors(int v);   // iteration, not random access
    long weight(int u, int v);            // absent edge = INF sentinel
    boolean directed();
}
```

Algorithms depend only on this — Dijkstra, BFS, topo sort, Kruskal (via an `edges()` view) are free functions over the interface. The alternative (passing `Map<String, List<String>>` around) bakes representation into every call site and makes the complexity contract unstatable.

## Keep Direction, Weight, and Mutability Explicit

Three orthogonal flags must be decided and written down:

- **Directed?** Undirected edges are stored as two directed arcs — never store one and hope algorithms mirror it.
- **Weighted?** Use a sentinel (`Long.MAX_VALUE / 4`) for "no edge," and keep all accumulators in `long`.
- **Mutable?** If weights/edges can change after Dijkstra starts, the heap invariant breaks (stale keys). Recommended: build an immutable snapshot (copy-on-build) for algorithm runs; mutate only between runs.

## Path Reconstruction as Output

Algorithms return `dist[]` plus `parent[]`, not path lists — O(V) memory regardless of how many paths are later requested. A separate `rebuildPath(parent, t)` walks parents in O(path length). For multiple sources, a `source[]` array distinguishes which tree each node belongs to (BFS forest for disconnected graphs).

## Component Handling

A `components()` pass (O(V+E)) runs before any per-component algorithm: single-source algorithms from an arbitrary node silently ignore other components. Architecture rule: any "whole graph" claim (diameter, average path, connectivity) must either prove connectivity first or iterate components explicitly.

## Testing Architecture

- **Oracle:** for V ≤ 8, Floyd–Warshall all-pairs vs per-node Dijkstra vs BFS (unweighted case) — cross-validation of three independent implementations.
- **Property tests:** random sparse graphs (Erdős–Rényi style: include each edge with p = c/V) with known invariants — MST weight = Kruskal = Prim; max flow ≤ min cut (always) and equal (by theorem); BFS dist ≤ Dijkstra dist on unit weights (equal).
- **Fixture style:** the 6-node lab graph (STEP_BY_STEP) is the golden fixture: distances 0, 3, 2, 8, 10, 13 must be reproduced exactly by any shortest-path implementation.
