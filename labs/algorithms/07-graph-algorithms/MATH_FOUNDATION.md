# MATH_FOUNDATION — Graph Algorithms (Overview)
> Recurrences, Master theorem, amortized analysis for traversals + shortest paths.

## 1. Recurrences (tailored)
- DFS/BFS: `T(V,E)=Θ(V+E)` — each vertex/edge processed O(1) times (not divide recurrence).
- DFS recursive: `T(u)=Σ_{v∈Adj} T(v)+O(1+deg(u))` → sums to `O(V+E)`.
- Dijkstra+PQ: `V` extracts + `E` relaxes → `O((V+E) log V)`.
- Bellman-Ford: `V·E` relaxations → `Θ(VE)`; Floyd `Θ(V³)`.
- Karatsuba-style contrast (Master example): `3T(n/2)+n` → `Θ(n^{log₂3})`.

## 2. Master Theorem
- Limited direct use in graphs (sizes don't split by fraction); applies to subroutines (sort edges, segment splits).
- Kruskal sort `2T(n/2)+n` → `Θ(n log n)` inside MST.
- Centroid decomposition: `T(n)=T(n/2)+O(n)`-ish → `O(n log n)` for path queries.
- State misapplication: `T(V-1)+E` is not Master form.
- Akra–Bazzi for uneven separators (planar `T(n)=2T(2n/3)+O(n)` → `O(n log n)`).

## 3. Counting Proofs
- Handshaking: `Σ deg = 2E` (undirected) → edge-scan bound.
- Each edge relaxed ≤ twice → `O(E)`; vertices settled once (Dijkstra, non-negative).
- BF `V-1` passes suffice: simple paths have ≤ `V-1` edges.

## 4. Amortized Analysis
- DSU (Kruskal): path compression + rank → `O(E·α(V))`.
- Dynamic connectivity / incremental BFS layers: level-charge each edge once.
- PQ lazy decrease-key: push duplicates, stale skipped — total pushes `O(E)`, pops `O(E)`.
- Potential: `Φ` = unsettled vertices; each settle drops `Φ`.

## 5. Probabilistic / Extra
- Randomized min-cut (Karger): `Ω(1/n²)` success → repeat `O(n² log n)`.
- Random pivot quicksort on adjacency (ordering heuristics) — brief.

## 6. Worked Numbers
- Sparse `V=10⁶,E=3·10⁶`: BFS ~4M ops fine; Floyd impossible.
- Dense `V=10³,E~10⁶`: matrix + `O(V²)` Prim/Dijkstra-naive competitive.
- Dijkstra PQ ops ≈ `E` pushes (~3M × log) — heap choice matters.

## 7. Exercises
- [ ] Prove `O(V+E)` via degree sum.
- [ ] Settle-once proof for Dijkstra (non-negative).
- [ ] `V-1` passes proof for Bellman-Ford.
- [ ] Centroid recurrence via Master/Akra–Bazzi.
