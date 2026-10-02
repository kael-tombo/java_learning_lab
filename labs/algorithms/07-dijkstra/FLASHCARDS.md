# Flashcards — Dijkstra's Algorithm

- Q: Dijkstra time (binary heap)? → A: O((V + E) log V)
- Q: Dijkstra space? → A: O(V + E)
- Q: Dijkstra weight requirement? → A: Non-negative edges only
- Q: Relaxation step? → A: If dist[u] + w < dist[v], update dist[v] = dist[u] + w
- Q: Why check stale PQ entries? → A: Node can be enqueued multiple times; skip outdated distances
- Q: Early termination for single target? → A: Stop when target popped from PQ — distance is finalized
- Q: Dijkstra vs Bellman-Ford? → A: Dijkstra faster, non-negative only; Bellman-Ford handles negatives, O(V×E)
- Q: PQ key in Dijkstra? → A: Current best distance to node
- Q: Network Delay Time answer? → A: Max shortest distance from source (time when all nodes reached)
- Q: Negative edge in Dijkstra? → A: Breaks greedy property — shorter path may go through "finalized" node
- Q: What if graph disconnected? → A: Unreachable nodes stay at INF distance; return -1 if any INF
- Q: Dijkstra on DAG? → A: Topological sort + relaxation gives O(V + E) — faster than PQ
- Q: A* search vs Dijkstra? → A: A* uses heuristic h(n) to guide search; Dijkstra is A* with h(n)=0
- Q: Dijkstra with Fibonacci heap? → A: O(V log V + E) — theoretical improvement, rarely used in practice
- Q: How to reconstruct path? → A: Store parent[] during relaxation; follow from target to source