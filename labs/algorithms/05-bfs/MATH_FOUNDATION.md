# Mathematical Foundation — Breadth-First Search (BFS)

## 1. Time Complexity Analysis

### Standard BFS on Graph G = (V, E)

**Theorem**: BFS visits each vertex at most once and examines each edge at most twice (once from each endpoint).

**Proof**:
- Each vertex is enqueued at most once (when first discovered).
- When a vertex `u` is dequeued, we iterate through all adjacent edges `(u, v)`.
- For undirected graphs: each edge appears in adjacency lists of both endpoints → examined twice.
- For directed graphs: each edge examined exactly once (from its source).

**Time Complexity**: **O(V + E)**

---

### Bidirectional BFS

Let:
- `b` = average branching factor
- `d` = distance between source and target

**Standard BFS**: Explores `b + b² + ... + b^d = O(b^d)` nodes
**Bidirectional BFS**: Explores `2 × (b + b² + ... + b^(d/2)) = O(b^(d/2))` nodes

**Speedup Factor**: Approximately `b^(d/2)` — exponential in half the depth.

---

## 2. Space Complexity Analysis

### Queue-Based BFS

**Worst Case**: Queue holds all vertices at maximum level width.
- **Complete binary tree**: Maximum width at depth `h` is `2^h` → **O(2^h) = O(V)**
- **Star graph**: All V-1 neighbors of center enqueued simultaneously → **O(V)**
- **Path graph**: Queue holds at most 1 vertex → **O(1)**

**Space Complexity**: **O(V)** worst case, often much less in practice.

### Bidirectional BFS

Two frontiers, each bounded by `O(b^(d/2))`:
**Space Complexity**: **O(b^(d/2))** — exponential improvement over standard BFS.

---

## 3. Shortest Path Correctness

### Lemma: Level Property
When BFS dequeues vertex `v`, `dist[v]` equals the length of the shortest path from source to `v`.

**Proof by Induction**:
- Base: Source `s` has `dist[s] = 0`, correct.
- Inductive step: Assume true for all vertices at distance ≤ k. When dequeuing `u` at distance k, neighbors `v` get `dist[v] = k + 1`. Any other path to `v` must go through a vertex at distance ≥ k, so length ≥ k+1. Thus `k+1` is optimal.

### Corollary: First Visit is Optimal
In unweighted graphs, the first time BFS discovers a vertex, it has found a shortest path to it.

---

## 4. Complexity Comparison Table

| Algorithm | Time | Space | Use Case |
|-----------|------|-------|----------|
| BFS (unweighted) | O(V + E) | O(V) | Shortest path, connectivity |
| Bidirectional BFS | O(b^(d/2)) | O(b^(d/2)) | Known source & target |
| Dijkstra (weighted) | O((V+E) log V) | O(V) | Non-negative weights |
| Bellman-Ford | O(V × E) | O(V) | Negative weights, negative cycle detection |
| Floyd-Warshall | O(V³) | O(V²) | All-pairs shortest paths |

---

## 5. BFS on Specific Graph Types

| Graph Type | V | E | Time | Space |
|------------|---|---|------|-------|
| Dense | n | n² | O(n²) | O(n) |
| Sparse | n | n | O(n) | O(n) |
| Tree | n | n-1 | O(n) | O(w) where w = max width |
| Grid (n×n) | n² | ~4n² | O(n²) | O(n) |

---

## 6. Bidirectional BFS — Mathematical Derivation

Let the branching factor be `b` and distance be `d`.

**Standard BFS total nodes explored**:
```
N_standard = 1 + b + b² + ... + b^d = (b^(d+1) - 1) / (b - 1) ≈ b^d
```

**Bidirectional BFS** (frontiers meet at depth d/2):
```
N_bidir = 2 × (1 + b + b² + ... + b^(d/2)) ≈ 2 × b^(d/2)
```

**Ratio**:
```
N_standard / N_bidir ≈ b^d / (2 × b^(d/2)) = b^(d/2) / 2
```

For typical values (b=26 for Word Ladder, d=5):
- Standard: 26⁵ ≈ 11.8 million
- Bidirectional: 2 × 26²·⁵ ≈ 2 × 878 ≈ 1,756
- Speedup: ~6,700×