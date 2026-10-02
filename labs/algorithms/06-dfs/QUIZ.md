# Quiz — Depth-First Search (DFS)

1. What is the time complexity of DFS on a graph with V vertices and E edges?
2. What is the space complexity of recursive DFS in the worst case?
3. How does DFS differ from BFS in terms of path finding?
4. What are the three vertex colors used in standard DFS (CLRS) and what do they represent?
5. What is a back edge in DFS, and what does it indicate in a directed graph?
6. In the Number of Islands problem, why does DFS use grid modification (sinking) instead of a visited set?
7. What is the time complexity of the Union-Find solution for Number of Islands?
8. What does topological sort require, and how is DFS used to produce it?
9. When would you prefer iterative DFS over recursive DFS?
10. How does DFS handle cycles in a directed graph?

---

## Answers

1. **O(V + E)** — Each vertex visited once, each edge examined once (twice for undirected).
2. **O(V)** — Recursion stack depth can reach V in a path graph. Iterative DFS with explicit stack also O(V).
3. DFS does **not** guarantee shortest paths in unweighted graphs. It goes deep first, finding some path but not necessarily the shortest. BFS finds shortest paths.
4. **WHITE** (undiscovered), **GRAY** (discovered, in recursion stack), **BLACK** (finished, all descendants processed).
5. A **back edge** connects a vertex to an ancestor in the DFS tree. In directed graphs, a back edge indicates a **cycle**. In undirected graphs, the edge to parent is not considered a back edge.
6. Modifying the grid in-place (setting '1' to '0') saves O(m×n) space for a visited array. It marks cells as processed permanently.
7. **O(m × n × α(m×n))** where α is the inverse Ackermann function (effectively constant). Nearly linear in practice.
8. Topological sort requires a **DAG** (Directed Acyclic Graph). DFS post-order traversal (reverse of finish times) produces a valid topological ordering.
9. Iterative DFS avoids stack overflow for very deep graphs (e.g., 100k+ depth). Also allows more control over traversal order and state.
10. DFS uses vertex colors or a visited set. GRAY vertices are in the current recursion stack — encountering a GRAY neighbor means a cycle exists.