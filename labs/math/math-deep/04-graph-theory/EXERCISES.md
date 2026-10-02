# Graph Theory — Exercises (5 Problems with Hints)

---

## Problem 1: Graph Representation and Traversal

**Implement a Graph class supporting both adjacency matrix and adjacency list representations. Include methods for BFS, DFS, connected components, and checking if the graph is bipartite.**

### Requirements:
- Support both directed and undirected graphs
- `addEdge(u, v, weight=1)` — add edge
- `bfs(source)` — returns distances and parents
- `dfs(source)` — returns discovery/finish times
- `connectedComponents()` — returns component ID for each vertex
- `isBipartite()` — returns true/false and coloring
- Switchable representation: matrix vs list

### Hints:
1. **BFS for bipartite check:** Color source 0. For each neighbor, assign opposite color. If conflict, not bipartite. Repeat for each component.
2. **DFS iterative vs recursive:** Both work. Recursive simpler but may hit stack limit for large graphs.
3. **Component ID:** Run BFS/DFS from each unvisited vertex, assign component number.
4. **Matrix vs List:** For dense graphs (E ≈ V²), matrix is fine. For sparse, list is better.
5. **Test cases:**
   - Tree (bipartite)
   - Odd cycle (not bipartite)
   - Complete graph (not bipartite for n>2)
   - Disconnected graph with mixed components

### Extension:
- Add Dijkstra's algorithm for weighted shortest paths
- Add topological sort for DAGs
- Benchmark matrix vs list for different densities

---

## Problem 2: Eulerian Circuit and Hierholzer's Algorithm

**Implement Hierholzer's algorithm to find an Eulerian circuit in an undirected graph (if one exists). Return the sequence of vertices in the circuit.**

### Requirements:
- Check if graph is Eulerian (connected, all degrees even)
- If not Eulerian, return empty/throw
- Implement Hierholzer: start at any vertex, walk until stuck, splice cycles
- Use adjacency list with edge tracking (mark edges as used)
- Handle multigraphs (parallel edges)

### Hints:
1. **Eulerian check:** Count odd-degree vertices. If > 0, no Eulerian circuit. If disconnected (ignoring isolated vertices), no circuit.
2. **Hierholzer details:**
   - Maintain current path (stack/array)
   - At each step, if current vertex has unused edges, take one and recurse/iterate
   - When stuck, add vertex to circuit and backtrack
   - Splicing: insert sub-circuit into main circuit at the right position
3. **Edge tracking:** For undirected graph, each edge appears in both adjacency lists. Mark both as used.
4. **Time complexity:** $O(V+E)$ — each edge visited exactly once.
5. **Test:** Graph with multiple cycles sharing vertices (e.g., figure-8).

### Extension:
- Find Eulerian trail (not circuit) when exactly 2 odd-degree vertices
- Implement for directed graphs (in-degree = out-degree)
- Find all Eulerian circuits (COUNT)

---

## Problem 3: Planarity Testing and Kuratowski Subgraphs

**Given a graph, implement a planarity test. If non-planar, find a $K_5$ or $K_{3,3}$ subdivision (Kuratowski subgraph).**

### Requirements:
- Implement Boyer-Myrvold planarity test (or use simpler edge-addition approach)
- If planar, output a planar embedding (rotation system)
- If non-planar, extract Kuratowski subgraph
- Test on: $K_5$, $K_{3,3}$, $K_4$, planar graphs, and random graphs

### Hints:
1. **Planarity test (simplified):** Use edge addition algorithm. Start with spanning tree, add edges one by one, maintain planar embedding. If can't add without crossing → non-planar.
2. **Kuratowski extraction:** When edge addition fails, the blocking structure contains a $K_5$ or $K_{3,3}$ subdivision. Trace back to find it.
3. **Simpler approach:** Use library (e.g., JGraphT has planarity) or implement DFS-based edge addition.
4. **Boyer-Myrvold (conceptual):**
   - DFS to get depth-first tree
   - Process edges by low-point
   - Maintain planar embedding of each biconnected component
   - Merge components using virtual edges
5. **Test graphs:**
   - $K_4$: planar, embedding = tetrahedron
   - $K_5$: non-planar, find $K_5$ itself
   - $K_{3,3}$: non-planar, find $K_{3,3}$ itself
   - Cube graph ($Q_3$): planar

### Extension:
- Compute planar embedding coordinates (Schnyder's algorithm for straight-line drawing)
- Find all $K_5$/$K_{3,3}$ subdivisions
- Test planarity of random graphs at different densities

---

## Problem 4: Graph Coloring — Greedy and Exact

**Implement graph coloring algorithms:**
1. Greedy coloring (multiple orderings: natural, largest-degree-first, smallest-last, DSATUR)
2. Exact coloring via backtracking with branch-and-bound
3. Compare on various graphs

### Requirements:
- Greedy: try vertex orderings, return best coloring found
- DSATUR: at each step, pick uncolored vertex with maximum saturation degree (number of different colors used by neighbors)
- Backtracking: try colors for vertices in order, prune if colors used ≥ best found
- Branch-and-bound: use clique lower bound, greedy upper bound
- Output: coloring, number of colors, time

### Hints:
1. **Greedy orderings:**
   - Natural: 0, 1, 2, ...
   - Largest degree first: sort by degree descending
   - Smallest last: repeatedly remove min-degree vertex, reverse order
   - DSATUR: dynamically choose most constrained vertex
2. **DSATUR pseudocode:**
   ```
   while uncolored vertices exist:
       v = argmax(saturation(v))  // ties: max degree
       assign smallest available color to v
   ```
3. **Backtracking with pruning:**
   - Order vertices by degree descending (or DSATUR order)
   - Recursive: try colors 1..k for vertex i
   - If valid, recurse to i+1
   - If all colored, update best
   - Prune: if current colors used + lower_bound(remaining) >= best, backtrack
4. **Lower bounds:** Clique number (find max clique), or $\max \delta(H)+1$ over subgraphs.
5. **Test graphs:**
   - Odd cycles: $\chi=3$
   - Complete graphs: $\chi=n$
   - Bipartite: $\chi=2$
   - Mycielski graphs (triangle-free, high $\chi$)
   - Random graphs

### Extension:
- Add Welsh-Powell heuristic
- Implement exact algorithm using integer programming (SAT/ILP)
- Benchmark on DIMACS coloring instances

---

## Problem 5: Maximum Flow and Min-Cut

**Implement the Edmonds-Karp algorithm (BFS-based Ford-Fulkerson) for maximum flow. Use it to solve the minimum cut problem and verify max-flow min-cut theorem.**

### Requirements:
- Represent flow network: adjacency list with capacities
- `maxFlow(s, t)` — returns max flow value and flow on each edge
- `minCut(s, t)` — returns partition (S, T) of min cut
- Verify: max flow value = min cut capacity
- Test on classic networks: simple series-parallel, bipartite matching

### Hints:
1. **Residual graph:** For each edge $(u,v)$ with capacity $c$ and flow $f$:
   - Forward residual edge: capacity $c - f$
   - Backward residual edge: capacity $f$
2. **Edmonds-Karp:**
   - While there's an augmenting path from $s$ to $t$ in residual graph:
     - Find shortest path using BFS
     - Compute bottleneck = min residual capacity on path
     - Augment flow along path (add to forward, subtract from backward)
   - Time: $O(VE^2)$
3. **Min-cut extraction:**
   - After max flow, run BFS/DFS from $s$ in residual graph
   - Vertices reachable from $s$ form set $S$
   - $T = V \setminus S$
   - Cut edges: original edges from $S$ to $T$
   - Cut capacity = sum of capacities of these edges
4. **Verification:** Sum of flow leaving $s$ should equal cut capacity.
5. **Test cases:**
   - Simple 4-vertex network
   - Bipartite matching as flow (add source to left, right to sink, capacities 1)
   - Network with multiple paths

### Extension:
- Implement Dinic's algorithm (blocking flows, $O(V^2E)$)
- Implement Push-Relabel ($O(V^3)$)
- Add lower bounds on edges
- Solve max-flow with multiple sources/sinks

---

*End of Exercises*