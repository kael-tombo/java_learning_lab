# Mathematical Foundation — Bellman-Ford & Floyd-Warshall

## 1. Bellman-Ford Algorithm

### Time Complexity

**Standard Bellman-Ford**: V-1 iterations, each relaxing all E edges.
- **Time**: **O(V × E)**
- **Space**: **O(V)** for distance array (+ O(V) for parent if path reconstruction needed)

### Dynamic Programming Interpretation

Define `dp[i][v]` = shortest path from source `s` to `v` using **at most i edges**.

**Recurrence**:
```
dp[0][s] = 0, dp[0][v≠s] = ∞
dp[i][v] = min(dp[i-1][v], min_{(u,v)∈E} (dp[i-1][u] + w(u,v)))
```

**Bellman-Ford computes this iteratively with space optimization**:
```java
int[] dist = new int[V];  // dp[i-1][*]
Arrays.fill(dist, INF);
dist[s] = 0;

for (int i = 1; i <= V-1; i++) {
    int[] newDist = dist.clone();  // dp[i][*] starts as dp[i-1][*]
    for (int[] edge : edges) {
        int u = edge[0], v = edge[1], w = edge[2];
        if (dist[u] != INF) {
            newDist[v] = Math.min(newDist[v], dist[u] + w);
        }
    }
    dist = newDist;
}
```

### Why V-1 Iterations?

**Theorem**: Any simple path (no repeated vertices) has at most V-1 edges.

**Proof**: A path with V edges must repeat a vertex (pigeonhole principle). If all weights are non-negative, removing the cycle gives a shorter or equal path. If negative weights allowed but no negative cycles, we can still remove zero/positive cycles. Thus shortest paths (when no negative cycles) are simple and have ≤ V-1 edges.

### Negative Cycle Detection

After V-1 iterations, run iteration V:
```
for each edge (u,v,w):
    if dist[u] + w < dist[v]:
        return "Negative cycle reachable from source"
```

**Proof**: If a negative cycle is reachable, distances can be decreased indefinitely by traversing the cycle. After V-1 iterations, if a shorter path still exists, it must use ≥ V edges, implying a cycle. That cycle must be negative (otherwise removing it wouldn't increase distance).

---

## 2. K-Stop Variant (Cheapest Flights Within K Stops)

### Problem Constraint
Find shortest path from `src` to `dst` using **at most K stops** (i.e., at most K+1 edges).

### Algorithm: K+1 Iterations of Bellman-Ford

```java
int[] prices = new int[n];
Arrays.fill(prices, INF);
prices[src] = 0;

for (int i = 0; i <= k; i++) {  // K+1 iterations = K stops
    int[] tmp = prices.clone();
    for (int[] f : flights) {
        int from = f[0], to = f[1], price = f[2];
        if (prices[from] != INF) {
            tmp[to] = Math.min(tmp[to], prices[from] + price);
        }
    }
    prices = tmp;
}
```

### Why Array Cloning is Essential

**Without cloning** (using same array):
- Updates within iteration `i` could be used for other edges in the **same** iteration.
- This allows paths with > i edges to form in iteration i.
- Violates the "at most i edges" invariant.

**With cloning**:
- `prices` = distances using ≤ i-1 edges (read-only this iteration)
- `tmp` = distances using ≤ i edges (being computed)
- Each iteration strictly adds at most one edge to paths.

### Complexity
- **Time**: O(K × E) — K iterations, each processes E edges
- **Space**: O(V) — two arrays of size V

### Comparison with Dijkstra (State = (node, stops))

| Approach | Time | Space | Notes |
|----------|------|-------|-------|
| Bellman-Ford K iterations | O(K × E) | O(V) | Simple, optimal for small K |
| Dijkstra with state | O(E log(VK)) | O(VK) | Better for large K, more complex |

For LeetCode 787 (n ≤ 100, K < n): Bellman-Ford is preferred.

---

## 3. Floyd-Warshall Algorithm

### Time and Space Complexity

**Time**: **O(V³)** — Three nested loops over V vertices
**Space**: **O(V²)** — Distance matrix `dist[V][V]`

### Dynamic Programming Formulation

Define `dp[k][i][j]` = shortest path from `i` to `j` using only intermediate vertices from set `{1, 2, ..., k}`.

**Recurrence**:
```
dp[0][i][j] = w(i,j)  (direct edge weight, or ∞ if no edge)
dp[k][i][j] = min(dp[k-1][i][j], dp[k-1][i][k] + dp[k-1][k][j])
```

**Space-optimized** (in-place):
```java
for (int k = 0; k < V; k++) {
    for (int i = 0; i < V; i++) {
        for (int j = 0; j < V; j++) {
            if (dist[i][k] != INF && dist[k][j] != INF) {
                dist[i][j] = Math.min(dist[i][j], dist[i][k] + dist[k][j]);
            }
        }
    }
}
```

**Correctness**: By iteration `k`, `dist[i][j]` contains shortest path using intermediates in `{0, ..., k-1}`. Order of `k` loop is critical (outermost).

### Negative Cycle Detection

After algorithm completes:
```java
for (int i = 0; i < V; i++) {
    if (dist[i][i] < 0) {
        // Negative cycle exists at vertex i
    }
}
```

**Proof**: `dist[i][i]` is shortest path from `i` to `i`. If negative, a cycle with negative total weight exists. Since Floyd-Warshall finds all shortest paths, it will detect any negative cycle in the graph (not just reachable from a single source).

### Transitive Closure (Reachability)

Boolean version for unweighted graphs:
```java
boolean[][] reach = new boolean[V][V];
// Initialize with direct edges
for (int k = 0; k < V; k++)
    for (int i = 0; i < V; i++)
        for (int j = 0; j < V; j++)
            reach[i][j] = reach[i][j] || (reach[i][k] && reach[k][j]);
```

**Time**: O(V³), **Space**: O(V²)

---

## 4. Complexity Comparison

| Algorithm | Time | Space | Scope | Handles Negatives | Detects Neg Cycles |
|-----------|------|-------|-------|-------------------|-------------------|
| Dijkstra (binary heap) | O((V+E) log V) | O(V+E) | Single-source | ❌ | ❌ |
| Bellman-Ford | O(V × E) | O(V) | Single-source | ✅ | ✅ (reachable) |
| Floyd-Warshall | O(V³) | O(V²) | All-pairs | ✅ | ✅ (all) |
| Johnson's | O(VE log V) | O(V²) | All-pairs | ✅ | ✅ |

### When to Use Which

| Scenario | Recommended |
|----------|-------------|
| Single-source, non-negative weights | Dijkstra |
| Single-source, negative weights | Bellman-Ford |
| Single-source, K-edge constraint | Bellman-Ford K iterations |
| All-pairs, small V (≤ 400) | Floyd-Warshall |
| All-pairs, sparse with negatives | Johnson's |
| Transitive closure / reachability | Floyd-Warshall (boolean) |

---

## 5. Bellman-Ford vs Floyd-Warshall: Key Differences

| Aspect | Bellman-Ford | Floyd-Warshall |
|--------|--------------|----------------|
| **Problem** | Single-source | All-pairs |
| **DP State** | `dp[i][v]` = ≤ i edges | `dp[k][i][j]` = intermediates ≤ k |
| **Negative Cycle** | Only reachable from source | Any in graph |
| **Space** | O(V) | O(V²) |
| **Path Reconstruction** | Parent array | Next matrix |

---

## 6. Applications Beyond Shortest Paths

### 1. Difference Constraints
System: `x_j - x_i ≤ c_k`
- Graph: edge `i → j` weight `c_k`
- Add super-source with 0-weight edges to all variables
- Feasible ⇔ No negative cycle

### 2. Currency Arbitrage
- Vertices = currencies
- Edge weights = -log(exchange_rate)
- Negative cycle = arbitrage opportunity

### 3. Network Routing (RIP Protocol)
- Bellman-Ford used in distance-vector routing
- Each router maintains distance table to all destinations
- Periodically exchanges with neighbors

### 4. Critical Path / Scheduling
- Longest path in DAG (negate weights, find shortest)
- Project scheduling with task dependencies

---

## 7. Summary of Complexity Bounds

| Algorithm | Best Case | Average | Worst Case | Space |
|-----------|-----------|---------|------------|-------|
| Bellman-Ford | O(V×E) | O(V×E) | O(V×E) | O(V) |
| Bellman-Ford (K stops) | O(K×E) | O(K×E) | O(K×E) | O(V) |
| Floyd-Warshall | O(V³) | O(V³) | O(V³) | O(V²) |
| Johnson's | O(VE log V) | O(VE log V) | O(VE log V) | O(V²) |

**Key Insight**: Bellman-Ford trades time (V×E) for ability to handle negative weights. Floyd-Warshall trades space (V²) for all-pairs queries in O(1) after preprocessing.