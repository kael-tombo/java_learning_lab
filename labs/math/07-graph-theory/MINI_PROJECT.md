# MINI_PROJECT — Graph Theory: Traversal & Shortest-Path Lab
> Implement + traverse + measure. ~3 hours.

## Goal
Build a graph library (adjacency list) with BFS, DFS, topo sort, cycle detection,
Dijkstra, and Kruskal MST, plus visual ASCII maps of visit order.

## Build Steps
1. `Graph.java`: addVertex/addEdge, directed or undirected, weighted.
2. `Traversal.java`: BFS (queue), DFS (stack + recursive), print visit orders.
3. `TopoSort.java`: Kahn's algorithm; fail loudly on cycle.
4. `ShortestPath.java`: Dijkstra with priority queue; reconstruct paths.
5. `MST.java`: Kruskal with union-find; total weight printed.

## Sample Output
```
BFS from A: A B C D E
Dijkstra A→E: 7 via A→B→D→E
Kruskal total weight: 19
topo: [core, parser, cli, app]
```

## Benchmark Table (fill)
| V | E | BFS ms | DFS ms | Dijkstra ms | Kruskal ms |
|---|---|--------|--------|-------------|------------|
| 100 | 400 | | | | |
| 500 | 2000 | | | | |
| 1000 | 5000 | | | | |

## Acceptance
- [ ] BFS finds shortest (hops) path in unweighted graph.
- [ ] Topo sort rejects cyclic input with a clear message.
- [ ] Dijkstra distances match hand calculation on a 6-node fixture.

## Extensions
- A* with Euclidean heuristic on a grid.
- Visualize components with ASCII flood-fill.
