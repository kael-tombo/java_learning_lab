# Quiz — Breadth-First Search (BFS)

1. What is the time complexity of BFS on a graph with V vertices and E edges?
2. What is the space complexity of BFS in the worst case?
3. How does BFS guarantee finding the shortest path in an unweighted graph?
4. What data structure is used to implement the BFS frontier?
5. In bidirectional BFS, why do we always expand the smaller frontier?
6. What is the difference between BFS and DFS in terms of memory usage for a balanced binary tree of depth d?
7. When would BFS be preferred over Dijkstra's algorithm?
8. In the Word Ladder problem, why do we remove words from the dictionary after visiting them?
9. What is the time complexity of bidirectional BFS compared to standard BFS?
10. How does BFS handle disconnected components in a graph?

---

## Answers

1. **O(V + E)** — Each vertex is visited once, each edge is examined once.
2. **O(V)** — The queue can hold up to all vertices in the worst case (e.g., a star graph).
3. BFS explores all nodes at distance k before any node at distance k+1. The first time we reach a node, it's via the shortest path (minimum edges).
4. **Queue (FIFO)** — Ensures nodes are processed in the order they are discovered.
5. Expanding the smaller frontier reduces the branching factor from b^(d/2) to approximately 2 * b^(d/2), giving significant speedup in practice.
6. BFS uses O(b^d) space (width of tree), DFS uses O(d) space (depth). For balanced tree, BFS space is exponential in depth while DFS is linear.
7. BFS is preferred for unweighted graphs or when all edges have equal weight. Dijkstra is needed for weighted graphs with non-negative edges.
8. Removing visited words prevents revisiting and infinite loops, and ensures each word is processed at most once (reducing time complexity).
9. Standard BFS: O(b^d). Bidirectional BFS: O(b^(d/2)) — exponential improvement in the branching factor.
10. BFS must be run from each unvisited node. The standard approach is to iterate through all vertices and start BFS from any unvisited vertex.