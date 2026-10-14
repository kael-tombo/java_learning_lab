# Lab Notebook: Graph Algorithms Week

Day 1 - traversal. Iterative BFS/DFS over adjacency lists on the transit
fixture; visit-order agreement with recursive DFS on 300 small graphs.
Deep-chain fixture (50k nodes) admitted only to the iterative side.

Day 2 - shortest paths. Dijkstra with binary heap on weighted transit
edges; Bellman-Ford on a small fixture with negative edges but no
negative cycles; BFS distances as the unweighted check. All three agree
with a Floyd-Warshall oracle on small graphs.

Day 3 - spanning. Kruskal with the lab DSU plus Prim with a heap on the
same fixtures; total weights must agree. Union counts and edge-sort cost
recorded separately so the DSU contribution is visible.

Day 4 - flow and order. Edmonds-Karp on a small capacity network vs a
reference max-flow value; topo sort on the build graph with per-edge
validation. Cycle fixture must fail topo with the printed cycle.

Day 5 - components and cuts. Connected components, strongly connected
components (Kosaraju/Tarjan, cross-checked against each other), and
articulation spot-checks on hand-built graphs with known answers.

Day 6 - scale. 20k-node / 120k-edge random graph: BFS time, Dijkstra
time, Kruskal time, memory delta. Numbers reported beside O(V + E) and
O(E log V) expectations; deviations investigated, not smoothed.

Day 7 - writeup. One page per algorithm: invariant, complexity, oracle
margin, and the fixture that would break the naive version. Attach all
oracle logs and the scale table. Bar: oracle agreement 12, negative and
cycle handling 10, scale honesty 8.
## Fixture locker
- Transit 5k-stop file versioned.
- Build-graph cycle case pinned.
- Negative-edge case preserved.
- Seeds published alongside.
Keep the scale table beside the oracle logs.

