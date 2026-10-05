# MINI_PROJECT — Graph Algorithms: Dispatch Dashboard
> Implement + benchmark + visualize. ~3 hours.

## Goal
One dashboard that dispatches BFS/DFS/Dijkstra by edge-type, renders all three traces on
one map, and times sparse vs dense representations.

## Build Steps
1. `Dispatch.java`: `if weighted→Dijkstra else if hops→BFS else DFS-structure`.
2. Traces: BFS levels, DFS stack, Dijkstra settle order on same 12-node map.
3. Visualize: side-by-side ASCII orders + settled sequence numbers.
4. Benchmark: sparse (E≈3V) vs dense (E≈V²/4) list-vs-matrix timings.
5. Wrong-tool demos: BFS on weighted (wrong), DFS for hops (long), Dijkstra on negative (wrong).

## Benchmark Table (fill)
| graph | BFS | DFS | Dijkstra | dispatch picks |
|-------|-----|-----|----------|----------------|
| unweighted | | | | BFS/DFS |
| weighted+ | | | | Dijkstra |
| negative | | | | Bellman-Ford (refuse) |

## Visualize
```
BFS: s A C B | DFS: s A B C | Dijk settle: s(0) B(2) A(3) T(4)
```

## Acceptance
- [ ] Dispatch logic + refusal on negatives.
- [ ] All three wrong-tool demos recorded.
- [ ] Sparse/dense representation verdict.

## Extensions
- Add topo/MST dispatch branches (DAG? undirected?).
