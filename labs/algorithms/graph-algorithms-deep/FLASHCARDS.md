# FLASHCARDS — Graph Algorithms Deep Track
> ~60 rows. Track `graph-algorithms-deep`.

| # | Front | Back |
|---|---|---|
| 1 | Kruskal | sort + DSU O(E log E) |
| 2 | Prim | heap grow O(E log V) |
| 3 | Boruvka | parallel rounds |
| 4 | Cut property | lightest crossing safe |
| 5 | Cycle property | heaviest on cycle out |
| 6 | Dijkstra needs | w ≥ 0 |
| 7 | Dijkstra bound | O(E log V) |
| 8 | Stale skip | cur != dist check |
| 9 | long dist | overflow guard |
| 10 | Bellman-Ford | O(VE) |
| 11 | BF detect | Vth pass relax |
| 12 | Floyd | O(V³) triple loop |
| 13 | Floyd order | k outer |
| 14 | Johnson | reweight + Dijkstra |
| 15 | Dinic | levels + blocking O(V²E) |
| 16 | Edmonds-Karp | BFS augment O(VE²) |
| 17 | Residual | forward/back pair |
| 18 | Min cut | s-reachable set |
| 19 | Cap scaling | big augments first |
| 20 | Bipartite check | 2-color BFS |
| 21 | Hopcroft-Karp | O(E√V) |
| 22 | Hungarian | O(n³) assignment |
| 23 | Augment path | flip free edges |
| 24 | Hall's condition | N(S)≥S exists match |
| 25 | DSATUR | saturation order |
| 26 | Greedy colors | ≤ Δ+1 |
| 27 | Clique bound | ω ≤ χ colors |
| 28 | Kahn | indegree queue |
| 29 | DFS topo | reverse finish |
| 30 | Cycle directed | gray back edge |
| 31 | Cycle undir | visited non-parent |
| 32 | DSU cycle | union-find detect |
| 33 | HLD chains | heavy contiguous |
| 34 | HLD query | O(log² n) |
| 35 | LCA binary | O(log n) lift |
| 36 | Euler tour | subtree = range |
| 37 | Bridges | low-link Tarjan |
| 38 | SCC | Kosaraju/Tarjan |
| 39 | 2-SAT | SCC implication |
| 40 | Centroid | split halves |
| 41 | Dial's | buckets C·V |
| 42 | 0-1 BFS | deque O(V+E) |
| 43 | A* | heuristic + g |
| 44 | Admissible | never overestimates |
| 45 | Master T=7T/2+n² | Θ(n^2.81) |
| 46 | Master T=2T/2+n | Θ(n log n) |
| 47 | Amortized α | DSU near const |
| 48 | Potential | telescopes |
| 49 | Array push | O(1) amortized |
| 50 | Counter | bit-flip O(1) |
| 51 | Pitfall #1 | Dijkstra negatives |
| 52 | Pitfall #2 | stale heap |
| 53 | Pitfall #3 | int dist overflow |
| 54 | Pitfall #4 | Floyd k-inner |
| 55 | Pitfall #5 | missing residual back |
| 56 | Pitfall #6 | non-bipartite input |
| 57 | Pitfall #7 | recursion depth HLD |
| 58 | Pitfall #8 | s==t flow |
| 59 | Fuzz oracle | brute n≤8 |
| 60 | Interview line | invariant first |
