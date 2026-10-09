# Performance: Graph Algorithms

## Representations Decide the Cost

| Representation | Memory | neighbors(v) | edge lookup (u,v) |
|---|---|---|---|
| adjacency list | Θ(V + E) | Θ(deg(v)) | Θ(deg(u)) |
| adjacency matrix | Θ(V²) | Θ(V) | O(1) |
| edge list | Θ(E) | Θ(E) scan | Θ(E) |

V = 10⁵, E = 4·10⁵: list ≈ (V+E)·8 bytes ≈ 4 MB (primitive arrays); matrix = 10¹⁰ cells — impossible (≈ 80 GB even as primitive `long`). Matrix only becomes viable for V ≤ ~10⁴, and there its O(1) edge tests and cache-dense loops make it competitive or better.

## Traversal and Ordering (all linear)

- **BFS/DFS/topological sort (Kahn):** O(V + E) — every vertex enqueued once, every edge examined once.
- **Connected components:** O(V + E) via one DFS/BFS sweep.
- **Cycle detection:** O(V + E) with three-color DFS (back edge to a gray node).

No graph algorithm beats Ω(V + E) for full traversal — the input itself has V + E entries.

## Shortest Paths

- **Dijkstra + binary heap (lazy):** O((V + E) log V). With Fibonacci heap: O(E + V log V) — asymptotically better, but the constants make it impractical outside theory.
- **Dijkstra + matrix, no heap:** O(V²) — for dense graphs (E ≈ V²) this beats the heap version: O(V²) vs O(V² log V).
- **Bellman–Ford:** O(V·E) — needed for negative edges; also detects negative cycles.
- **Floyd–Warshall (all pairs):** O(V³) time, O(V²) space (O(V) with on-the-fly reconstruction). Sensible up to V ≈ 1,000 (10⁹ word ops).
- **BFS:** O(V + E) — only for unweighted/equal-weight graphs.

## Minimum Spanning Tree

- **Kruskal:** O(E log E) from the sort (union–find is O(E·α(V)) ≈ O(E)).
- **Prim + binary heap:** O(E log V); with Fibonacci heap O(E + V log V).
- Since E ≤ V² , E log E = O(E log V) — same order; choose Kruskal for sparse+edge-list input, Prim for dense+adjacency-matrix-adjacent workloads.

## Max Flow

- **Edmonds–Karp (BFS augmenting):** O(V·E²) — simple and predictable.
- **Dinic:** O(V²E) general, O(E√V) on unit-capacity bipartite graphs — the practical default.
- **Push-relabel (highest-label):** O(V²E), often fastest in practice; relabel-to-front O(V³).
- **Hopcroft–Karp bipartite matching:** O(E√V) — matching is a special case of flow with unit capacities.

## Matching and Bipartite Testing

- **Hungarian algorithm (assignment):** O(V³) for weighted bipartite matching.
- **Bipartite check:** O(V + E) (BFS 2-coloring).

## Density Thresholds in One Line

E < V/log V → lists clearly; E ≈ V² → matrices. The crossover for Dijkstra is around E/V ≈ V/log V: below it the heap wins, above it the O(V²) array scan wins. Always state which representation your quoted complexity assumes — "O(V+E)" silently presumes adjacency lists.
