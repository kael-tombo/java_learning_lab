# Flashcards — Bellman-Ford & Floyd-Warshall

- Q: Bellman-Ford time? → A: O(V × E)
- Q: Floyd-Warshall time? → A: O(V³)
- Q: Bellman-Ford handles what Dijkstra can't? → A: Negative edge weights, negative cycle detection
- Q: Bellman-Ford negative cycle detection? → A: Run V-th iteration; if any distance improves, negative cycle exists
- Q: Cheapest Flights K stops → Bellman-Ford iterations? → A: K+1 iterations (K stops = K+1 flights)
- Q: Why clone array in K-stop Bellman-Ford? → A: Prevents using > i edges in iteration i (enforces stop limit)
- Q: Floyd-Warshall computes? → A: All-pairs shortest paths
- Q: Floyd-Warshall space? → A: O(V²)
- Q: Floyd-Warshall negative cycle detection? → A: Check if dist[i][i] < 0 after algorithm
- Q: Bellman-Ford vs Dijkstra? → A: Bellman-Ford O(V×E) handles negatives; Dijkstra O((V+E) log V) non-negative only
- Q: Bellman-Ford vs Floyd-Warshall? → A: BF single-source; FW all-pairs
- Q: Floyd-Warshall transitive closure? → A: Replace min with OR, + with AND — reachability matrix
- Q: When to use Bellman-Ford K-stop variant? → A: Explicit limit on edges in path (e.g., at most K stops)
- Q: Bellman-Ford space optimization? → A: O(V) — only need previous iteration's distances
- Q: Johnson's algorithm? → A: Bellman-Ford for reweighting + Dijkstra from each vertex — O(V E log V) for all-pairs with negatives