# Quiz — Dijkstra's Algorithm

1. What is the time complexity of Dijkstra's algorithm using a binary heap (PriorityQueue)?
2. What is the space complexity of Dijkstra's algorithm?
3. Why does Dijkstra's algorithm require non-negative edge weights?
4. What is the "relaxation" step in Dijkstra's algorithm?
5. In the Network Delay Time problem, what does the final answer represent?
6. What happens if you run Dijkstra on a graph with negative edge weights?
7. How does the priority queue key work in Dijkstra's algorithm?
8. Why do we check `if (d > dist[node]) continue;` when polling from the priority queue?
9. What is the difference between Dijkstra and Bellman-Ford in terms of applicability?
10. How would you modify Dijkstra to find the shortest path to a single target (not all nodes)?

---

## Answers

1. **O((V + E) log V)** — Each vertex extracted once (V log V), each edge relaxed once (E log V).
2. **O(V + E)** — Adjacency list O(E), distance array O(V), priority queue O(V).
3. Negative edges violate the greedy choice property: a shorter path might go through a node already "finalized" with a larger distance.
4. **Relaxation**: For edge `(u, v, w)`, if `dist[u] + w < dist[v]`, update `dist[v] = dist[u] + w` and push to PQ.
5. The **maximum** of all shortest distances from source `k` — the time when the last node receives the signal.
6. Dijkstra may produce incorrect results (shorter paths missed) because it never revisits "finalized" nodes.
7. PQ is keyed by **current best distance** to each node. Node with smallest tentative distance is processed next.
8. A node can be in the PQ multiple times with different distances. This check skips stale (outdated) entries.
9. **Dijkstra**: Non-negative weights only, faster O((V+E) log V). **Bellman-Ford**: Handles negative weights, detects negative cycles, slower O(V×E).
10. Early termination: stop when target node is extracted from PQ (its distance is then finalized).