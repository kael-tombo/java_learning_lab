# Internals: Graph Representations and Mechanics

## Adjacency List

The default for sparse graphs. Two layouts:

**Object form (Java):** `Map<V, List<Edge>>` or `List<int[]>[] adj`. Flexible, but each edge costs object headers, a list node, and boxed integers — a graph with V = 10⁵ and E = 3·10⁵ can consume hundreds of MB from boxing alone.

**Primitive form (forward-star / CSR):** three arrays — `int[] to`, `long[] weight`, `int[] head` (or CSR: `int[] offsets` of length V+1 plus `int[] targets` of length E). Memory is Θ(V + E) machine words with no per-edge object: for E = 10⁶ edges, two int arrays = 8 MB. CSR requires an O(E log E)-ish build (sort edges by source) or an O(E) counting-sort build, after which the graph is read-only — ideal for algorithms, painful for dynamic edits.

Costs: neighbors of v are `adj[v]..adj[v+1)` in CSR — iteration is cache-sequential; membership test (u,v) ∈ E is O(degree(u)) unless you add a hash set.

## Adjacency Matrix

`int[][]` / `long[][]` of size V×V: Θ(V²) memory. V = 5,000 → 25·10⁶ cells ≈ 200 MB as `long`; V = 10⁵ → 10¹⁰ cells — impossible. Benefit: edge lookup O(1) and dense algorithms (Floyd–Warshall triple loop) become simple, cache-friendly array scans; Dijkstra with a matrix runs in O(V²) without any heap — *faster* than heap-based O((V+E) log V) once E ≈ V².

Bit matrix (`long[][]` as bitsets): V = 10⁴ → 10⁸ bits ≈ 12.5 MB, and reachability closure does 64 edges at a time via word AND.

## Edge List

`record Edge(int u, int v, long w)[]` — the storage of choice for Kruskal (sort once: O(E log E)) and for input parsing. Terrible for traversal (finding v's neighbors is a full O(E) scan), so convert to adjacency structure after sorting.

## Traversal Bookkeeping

- `boolean[] visited` — O(1) per probe, Θ(V) memory; reset between runs costs Θ(V), so for repeated searches use an `int[] stamp` with an incrementing run id (avoiding the reset entirely).
- `int[] dist` / `long[] dist` — INF sentinel must exceed any real path: `Long.MAX_VALUE / 4` (not MAX_VALUE — adding to it overflows).
- Parent array `int[] parent` reconstructs paths by walking back from t: O(path length), no stack needed.

## Priority Queue for Dijkstra

Java's `PriorityQueue<long[]>` (dist, node) with lazy deletion: each edge may cause one push → O(E) pushes, each O(log E); pops O(E log E) worst case including stale ones. This is O((V+E) log V) total. A real decrease-key heap would give O(E + V log V) with a Fibonacci heap — but the constant factors and complexity make the lazy binary heap the engineering default. The `visited`-on-pop skip is what makes laziness correct.

## Union–Find (Kruskal, connectivity)

Arrays `parent[]`, `rank[]`. `find` with path compression plus `union` by rank is O(α(V)) amortized — inverse Ackermann, effectively ≤ 4 for any realistic V. On E = 10⁶ edges the whole Kruskal sort dominates at O(E log E) while the union–find work is negligible.

## Bipartite Storage

Store `side[] = 0|1` per vertex instead of splitting lists — halves the indexing bugs and lets BFS coloring be a single array check (`side[v] = 1 - side[u]`).
