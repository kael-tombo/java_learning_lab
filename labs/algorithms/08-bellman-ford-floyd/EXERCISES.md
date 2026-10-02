# Exercises — Bellman-Ford & Floyd-Warshall

## Beginner

1. **Implement Standard Bellman-Ford**
   - Given edge list `int[][] edges` where `edges[i] = {u, v, w}`, implement single-source shortest paths.
   - Return `int[] dist` and `boolean hasNegativeCycle`.

2. **Bellman-Ford with Path Reconstruction**
   - Track `parent[]` array during relaxation.
   - Implement `getPath(int target)` returning the shortest path or null if negative cycle reachable.

3. **Detect Negative Cycle**
   - After V-1 iterations, run one more pass.
   - Return `true` if any edge can still be relaxed.

## Intermediate

4. **Cheapest Flights Within K Stops (LeetCode 787) — Bellman-Ford**
   - Implement the K+1 iteration version with array cloning.
   - Test with cases where direct flight is more expensive than multi-stop.

5. **Floyd-Warshall Implementation**
   - Given adjacency matrix `int[][] graph` (INF for no edge), implement all-pairs shortest paths.
   - Detect and report negative cycles.

5. **Transitive Closure with Floyd-Warshall**
   - Given boolean adjacency matrix, compute reachability matrix.
   - Use logical operations: `reach[i][j] = reach[i][j] || (reach[i][k] && reach[k][j])`.

## Advanced

7. **Johnson's Algorithm for All-Pairs with Negative Weights**
   - Add dummy source with 0-weight edges to all nodes.
   - Run Bellman-Ford to get potentials `h[v]`.
   - Reweight edges: `w'(u,v) = w(u,v) + h[u] - h[v]` (now non-negative).
   - Run Dijkstra from each vertex with reweighted edges.
   - Adjust distances back: `d(u,v) = d'(u,v) - h[u] + h[v]`.

8. **Minimum Mean Weight Cycle (Karp's Algorithm)**
   - Use DP: `dp[k][v] = min weight of path with exactly k edges ending at v`.
   - Minimum mean cycle = `max_v min_k (dp[n][v] - dp[k][v]) / (n - k)`.

9. **Constrained Shortest Path: Exact K Edges**
   - Modify Bellman-Ford to find shortest path with EXACTLY K edges (not at most).
   - Use DP table `dp[i][v]` = min distance to v with exactly i edges.

10. **Difference Constraints System (Bellman-Ford Application)**
    - Solve system: `x_j - x_i ≤ b_k` for constraints.
    - Create graph with edge `i → j` weight `b_k`.
    - Add source with 0-weight edges to all variables.
    - Run Bellman-Ford; feasible iff no negative cycle.