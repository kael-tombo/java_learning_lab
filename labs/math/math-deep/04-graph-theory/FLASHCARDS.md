# Graph Theory — Flashcards

---

## Basic Definitions

### Graph Types
**Q:** Undirected vs. directed graph?
**A:** Undirected: edges are unordered pairs $\{u,v\}$. Directed: edges are ordered pairs $(u,v)$.

**Q:** Simple graph?
**A:** No self-loops, no parallel edges.

**Q:** Complete graph $K_n$?
**A:** All $\binom{n}{2}$ edges present. $\Delta = n-1$.

**Q:** Bipartite graph?
**A:** Vertex set partitions into $V_1, V_2$ such that all edges cross partitions. No odd cycles.

**Q:** Tree?
**A:** Connected, acyclic undirected graph. $|E| = |V| - 1$.

---

### Representations
**Q:** Adjacency matrix?
**A:** $A[i][j] = 1$ if edge $(i,j)$ exists. Space: $O(V^2)$. Edge check: $O(1)$. Dense graphs.

**Q:** Adjacency list?
**A:** Array of lists, one per vertex. Space: $O(V+E)$. Iterate neighbors: $O(\deg(v))$. Sparse graphs.

**Q:** Edge list?
**A:** List of $(u,v)$ pairs. Good for Kruskal's algorithm (sort edges).

---

### Degree
**Q:** Handshaking Lemma?
**A:** $\sum_{v \in V} \deg(v) = 2|E|$.

**Q:** Max degree $\Delta$?
**A:** $\max_v \deg(v)$.

**Q:** Minimum degree $\delta$?
**A:** $\min_v \deg(v)$.

---

## Connectivity & Paths

### Components
**Q:** Connected component?
**A:** Maximal connected subgraph.

**Q:** Strongly connected (directed)?
**A:** $\forall u,v: \text{path } u \to v \text{ and } v \to u$.

**Q:** Bridge / Cut-edge?
**A:** Edge whose removal increases number of components.

**Q:** Articulation point / Cut-vertex?
**A:** Vertex whose removal increases number of components.

---

### Paths & Cycles
**Q:** Walk, trail, path?
**A:** Walk: sequence of vertices. Trail: no repeated edges. Path: no repeated vertices.

**Q:** Cycle?
**A:** Closed path (start = end), length $\geq 3$.

**Q:** Distance?
**A:** Shortest path length (number of edges) between two vertices.

**Q:** Diameter?
**A:** Maximum distance over all pairs.

---

## Traversals

### BFS
**Q:** BFS properties?
**A:** Finds shortest paths (in edges) from source. $O(V+E)$ time. Uses queue.

**Q:** BFS tree?
**A:** Tree of edges used to discover vertices. Root = source. Non-tree edges connect same or adjacent levels.

### DFS
**Q:** DFS properties?
**A:** Explores deep before broad. $O(V+E)$ time. Uses stack (recursion).

**Q:** DFS tree / forest?
**A:** Tree edges (discovery), back edges (to ancestor), forward edges (to descendant), cross edges (between subtrees).

**Q:** Topological sort?
**A:** For DAG only. Order vertices so all edges go forward. DFS post-order reversed.

**Q:** SCC (Kosaraju/Tarjan)?
**A:** Kosaraju: DFS on $G$, reverse edges, DFS on $G^T$ in decreasing finish time. Tarjan: single DFS with low-link values.

---

## Eulerian & Hamiltonian

### Eulerian
**Q:** Eulerian trail?
**A:** Trail using every edge exactly once.

**Q:** Eulerian circuit?
**A:** Eulerian trail that starts and ends at same vertex.

**Q:** Undirected Eulerian circuit condition?
**A:** Connected + all vertices even degree.

**Q:** Undirected Eulerian trail condition?
**A:** Connected + exactly 0 or 2 vertices odd degree.

**Q:** Directed Eulerian circuit?
**A:** Strongly connected + $\forall v: \text{in-degree}(v) = \text{out-degree}(v)$.

**Q:** Hierholzer's algorithm?
**A:** Splice cycles together. $O(V+E)$.

---

### Hamiltonian
**Q:** Hamiltonian path?
**A:** Path visiting every vertex exactly once.

**Q:** Hamiltonian cycle?
**A:** Hamiltonian path that forms a cycle.

**Q:** Complexity?
**A:** NP-complete (decision). No known polynomial algorithm.

**Q:** Dirac's Theorem (sufficient)?
**A:** If $G$ is simple, $n \geq 3$, and $\deg(v) \geq n/2$ for all $v$, then $G$ is Hamiltonian.

**Q:** Ore's Theorem?
**A:** If $G$ is simple, $n \geq 3$, and $\deg(u)+\deg(v) \geq n$ for all non-adjacent $u,v$, then $G$ is Hamiltonian.

---

## Graph Isomorphism

### Definition
**Q:** Graph isomorphism?
**A:** Bijection $f: V_1 \to V_2$ such that $\{u,v\} \in E_1 \iff \{f(u), f(v)\} \in E_2$.

**Q:** Isomorphism invariants?
**A:** Degree sequence, number of vertices/edges, connected components, diameter, spectrum of adjacency matrix, chromatic number.

**Q:** Complexity?
**A:** Not known to be in P or NP-complete (GI class). Quasi-polynomial algorithm (Babai 2015).

---

## Planarity

### Definition
**Q:** Planar graph?
**A:** Can be drawn in plane without edge crossings.

**Q:** Euler's Formula?
**A:** For connected planar graph: $V - E + F = 2$ (where $F$ includes outer face).

**Q:** Corollaries of Euler?
**A:** If $V \geq 3$: $E \leq 3V - 6$. If bipartite: $E \leq 2V - 4$.

**Q:** Kuratowski's Theorem?
**A:** $G$ non-planar iff $G$ contains a subdivision of $K_5$ or $K_{3,3}$.

**Q:** Wagner's Theorem?
**A:** $G$ non-planar iff $G$ contains $K_5$ or $K_{3,3}$ as a minor.

**Q:** Planarity testing?
**A:** Linear time (Hopcroft-Tarjan). Simpler: Boyer-Myrvold.

---

## Graph Coloring

### Vertex Coloring
**Q:** Proper coloring?
**A:** Adjacent vertices get different colors.

**Q:** Chromatic number $\chi(G)$?
**A:** Minimum number of colors for proper coloring.

**Q:** Clique number $\omega(G)$?
**A:** Size of largest complete subgraph. $\omega(G) \leq \chi(G)$.

**Q:** Greedy coloring bound?
**A:** $\chi(G) \leq \Delta(G) + 1$.

**Q:** Brook's Theorem?
**A:** $\chi(G) \leq \Delta(G)$ unless $G = K_n$ or $G = C_{2k+1}$.

**Q:** Perfect graphs?
**A:** $\chi(H) = \omega(H)$ for all induced subgraphs $H$. Strong Perfect Graph Theorem: no odd hole or anti-hole of length $\geq 5$.

---

### Edge Coloring
**Q:** Edge coloring?
**A:** Edges colored such that incident edges have different colors.

**Q:** Vizing's Theorem?
**A:** $\Delta \leq \chi'(G) \leq \Delta + 1$. Class 1: $\chi' = \Delta$. Class 2: $\chi' = \Delta + 1$.

**Q:** König's Theorem (bipartite)?
**A:** For bipartite graphs: $\chi'(G) = \Delta$.

---

## Special Graph Classes

### Trees
**Q:** Properties of trees?
**A:** Connected, acyclic, $|E|=|V|-1$, unique path between any two vertices.

**Q:** Spanning tree?
**A:** Subgraph that is a tree and includes all vertices.

**Q:** MST algorithms?
**A:** Kruskal (sort edges, union-find), Prim (priority queue on vertices). $O(E \log V)$.

### Bipartite Graphs
**Q:** Characterization?
**A:** 2-colorable. No odd cycles.

**Q:** Matching?
**A:** Set of edges with no shared vertices.

**Q:** Maximum matching?
**A:** Hopcroft-Karp: $O(E\sqrt{V})$. Augmenting paths.

**Q:** Hall's Marriage Theorem?
**A:** Bipartite $G=(X,Y,E)$ has perfect matching iff $\forall S \subseteq X: |N(S)| \geq |S|$.

---

## Network Flows

### Max Flow
**Q:** Flow network?
**A:** Directed graph with capacities $c(u,v) \geq 0$, source $s$, sink $t$.

**Q:** Max-flow min-cut theorem?
**A:** Maximum flow value = minimum $s$-$t$ cut capacity.

**Q:** Ford-Fulkerson?
**A:** Augment along paths in residual graph. $O(E \cdot \text{max flow})$ for integers.

**Q:** Edmonds-Karp (BFS)?
**A:** $O(VE^2)$ — finds shortest augmenting paths.

**Q:** Dinic's algorithm?
**A:** $O(V^2 E)$ — blocking flows in layered network.

**Q:** Push-relabel?
**A:** $O(V^3)$ — works with preflow, pushes excess, relabels heights.

---

## Algorithms Summary

| Problem | Algorithm | Time |
|---------|-----------|------|
| BFS/DFS | Queue/Stack | $O(V+E)$ |
| Shortest path (unweighted) | BFS | $O(V+E)$ |
| Shortest path (weighted, no neg) | Dijkstra | $O(E \log V)$ |
| Shortest path (neg weights) | Bellman-Ford | $O(VE)$ |
| All-pairs shortest path | Floyd-Warshall | $O(V^3)$ |
| MST | Kruskal / Prim | $O(E \log V)$ |
| Eulerian circuit | Hierholzer | $O(V+E)$ |
| Topological sort | DFS | $O(V+E)$ |
| SCC | Kosaraju / Tarjan | $O(V+E)$ |
| Max flow | Dinic / Push-relabel | $O(V^2 E) / O(V^3)$ |
| Max matching (bipartite) | Hopcroft-Karp | $O(E\sqrt{V})$ |
| Graph coloring | Greedy / Backtracking | NP-hard |
| Planarity test | Boyer-Myrvold | $O(V)$ |

---

*End of Flashcards*