# MATH_FOUNDATION — Graph Algorithms Deep Track
> Recurrences / Master theorem / amortized. Track `graph-algorithms-deep`.

## 1. Recurrence toolkit
- T(n) = a·T(n/b) + f(n); Master 1/2/3.
- Boruvka rounds halve components: O(E log V) total.
- Centroid decomposition: T(n) = T(n/2) + O(n) → O(n log n).

## 2. Master theorem cases
- Memorize 30s decision: compare f vs n^{log_b a}.
- Drill: Karatsuba, Strassen, mergesort.

## 3. Shortest-path counting
- Dijkstra: each edge relaxed when its tail settles → O(E) relaxations × log heap.
- Bellman-Ford: V-1 passes × E edges = O(VE); proof by shortest-path hop bound.
- Floyd: n³ triples; k-outer ordering proof by intermediate set.

## 4. Flow bounds
- Edmonds-Karp: O(VE) augments × O(E) BFS = O(VE²).
- Dinic: O(V) phases × blocking flow O(VE) = O(V²E).
- Unit networks: Dinic O(min(V^{2/3},√E)·E).

## 5. Matching bounds
- Hopcroft-Karp phases O(√V) × O(E) = O(E√V).
- Hungarian O(n³) via potentials; assignment LP duality.

## 6. Amortized: DSU
- Union by size + halving → O(α(n)); charges path nodes to size doubling.
- Underpins Kruskal + offline connectivity.

## 7. Amortized: dynamic array/counter
- Push O(1); counter O(1); same telescoping as reuse proofs.

## 8. HLD + segment math
- Heavy child = max subtree; light edges O(log n) per root path.
- Query touches O(log n) chains × O(log n) seg = O(log² n).

## 9. Practice proofs (do on paper)
- Prove Dijkstra via settled-invariant induction.
- Prove max-flow min-cut weak→strong duality sketch.
- Prove Hopcroft-Karp phase bound.
- Prove HLD light-edge O(log n).

## Checklist
- [ ] State Master case in 30s. [ ] Sketch one amortized proof. [ ] Derive Dijkstra bound.
