# Quiz — Bellman-Ford & Floyd-Warshall Algorithms

1. What is the time complexity of Bellman-Ford algorithm?
2. What is the time complexity of Floyd-Warshall algorithm?
3. What problem does Bellman-Ford solve that Dijkstra cannot?
4. In the Cheapest Flights Within K Stops problem, why does Bellman-Ford run exactly K+1 iterations?
5. How does Bellman-Ford detect negative cycles?
5. What does Floyd-Warshall compute?
6. What is the space complexity of Floyd-Warshall?
7. In the Bellman-Ford DP formulation for K stops, why do we use a temporary array (clone)?
8. When would you use Bellman-Ford over Dijkstra?
9. What is the difference between Bellman-Ford and Floyd-Warshall in terms of problem scope?
10. Can Floyd-Warshall detect negative cycles? How?

---

## Answers

1. **Bellman-Ford**: O(V × E) — V-1 iterations, each relaxing all E edges.
2. **Floyd-Warshall**: O(V³) — Three nested loops over all vertices.
3. **Negative edge weights** — Bellman-Ford handles them correctly; Dijkstra fails. Also detects negative cycles.
4. K stops = K+1 flights. Each iteration finds shortest paths using at most i flights. After K+1 iterations, we have paths using ≤ K+1 flights (K stops).
5. After V-1 iterations, run one more iteration. If any distance improves, a negative cycle exists reachable from source.
6. **All-pairs shortest paths** — Shortest distance between every pair of vertices.
7. **O(V²)** — Distance matrix of size V×V.
8. The temporary array prevents using updated distances in the same iteration. Each iteration should only use paths with ≤ i edges (i flights). Without cloning, paths could use > i edges in one iteration.
9. **Bellman-Ford**: Single-source, handles negative weights. **Dijkstra**: Faster, non-negative only. Use Bellman-Ford when negatives exist or K-stop constraint needed.
10. **Bellman-Ford**: Single-source. **Floyd-Warshall**: All-pairs. Floyd-Warshall also computes transitive closure.
11. Yes. After algorithm completes, if `dist[i][i] < 0` for any i, a negative cycle exists.