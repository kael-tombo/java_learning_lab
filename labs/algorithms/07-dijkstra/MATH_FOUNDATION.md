# Mathematical Foundation — Dijkstra's Algorithm

## 1. Time Complexity Analysis

### Binary Heap Implementation

Let G = (V, E) be a directed graph with non-negative edge weights.

**Operations**:
- **Extract-Min**: Performed V times → V × O(log V)
- **Decrease-Key (Relax)**: Performed at most E times → E × O(log V)

**Total Time**: **O((V + E) log V)**

**Space**: **O(V + E)**
- Adjacency list: O(E)
- Distance array: O(V)
- Priority queue: O(V)

---

### Complexity Comparison by Priority Queue Implementation

| PQ Implementation | Extract-Min | Decrease-Key | Total Time |
|-------------------|-------------|--------------|------------|
| Array (unsorted) | O(V) | O(1) | O(V²) |
| Binary Heap | O(log V) | O(log V) | **O((V+E) log V)** |
| Fibonacci Heap | O(log V) | O(1) amortized | **O(V log V + E)** |
| d-ary Heap (d = E/V) | O(log_{E/V} V) | O(log_{E/V} V) | O(E log_{E/V} V) |

**Note**: Fibonacci heap is theoretically faster but has large constant factors; rarely used in practice.

---

## 2. Correctness Proof — Greedy Choice Property

### Lemma: Optimal Substructure
If `P` is a shortest path from `s` to `t`, then any subpath of `P` is a shortest path between its endpoints.

### Theorem: Dijkstra's Greedy Choice
When vertex `u` is extracted from the priority queue (i.e., `u` has minimum `dist[u]` among all vertices in Q), then `dist[u]` is the **final shortest distance** from source `s` to `u`.

**Proof by Contradiction**:
1. Assume `dist[u]` is not the true shortest distance `δ(s, u)`.
2. Then there exists a shorter path `s → ... → x → y → ... → u` where `x` is the last vertex with correct distance (in S), and `y` is the first vertex outside S on this path.
3. Since `x` was finalized before `u`, `dist[x] = δ(s, x)`.
4. When `x` was processed, edge `(x, y)` was relaxed, so `dist[y] ≤ dist[x] + w(x, y) = δ(s, y)`.
5. Since `y` is on a shortest path to `u`, `δ(s, y) ≤ δ(s, u)`.
6. But `u` was chosen as minimum in Q, so `dist[u] ≤ dist[y]`.
7. Combining: `dist[u] ≤ dist[y] ≤ δ(s, y) ≤ δ(s, u)`.
8. This contradicts `dist[u] > δ(s, u)`.

---

## 3. Why Non-Negative Weights Are Required

### Counterexample with Negative Edge

```
    5
s ─────► u
│        │
│ -10    │ 2
▼        ▼
v ◄───── w
   3
```

- Dijkstra processes `u` first (dist=5), then `w` (dist=7).
- Edge `(w, v)` with weight -10 would give `dist[v] = -3`, but `v` already processed with dist=3.
- Dijkstra never revisits `v` → misses shorter path `s → u → w → v = -3`.

### Key Insight
With non-negative weights, **distance can only increase** along a path. So once a vertex has the minimum tentative distance, no future relaxation can improve it.

---

## 4. Relaxation as Dynamic Programming

Define `dist[v]` as the length of the shortest path from `s` to `v` using only vertices in `S` (finalized set).

**Relaxation**:
```
if dist[u] + w(u,v) < dist[v]:
    dist[v] = dist[u] + w(u,v)
```

This is equivalent to:
```
dist[v] = min(dist[v], dist[u] + w(u,v))
```

Dijkstra computes the **fixed point** of this relaxation equation, processing vertices in order of increasing true distance.

---

## 5. Special Cases and Optimizations

### 0-1 BFS (Deque Optimization)
When edge weights ∈ {0, 1}:
- Use `Deque` instead of PriorityQueue
- Push to front for weight 0, push to back for weight 1
- **Time**: O(V + E) — linear!

### Dial's Algorithm (Bucket Queue)
When weights are integers in [0, C]:
- Use array of buckets indexed by distance
- **Time**: O(V + E + C×V) — linear for small C

### Topological Sort + Relaxation (DAG)
For DAGs only:
- Topologically sort vertices
- Relax edges in topological order
- **Time**: **O(V + E)** — optimal, no PQ needed

---

## 6. Network Delay Time — Problem Analysis

**Problem**: Given directed graph with positive weights, find max shortest distance from source `k` to all nodes. Return -1 if any node unreachable.

**Graph**: `n ≤ 100` nodes, `m ≤ 6000` edges.

**Complexity**:
- V = n ≤ 100
- E = m ≤ 6000
- Dijkstra: O((100 + 6000) log 100) ≈ O(6100 × 7) ≈ 42,700 operations — trivial

**Why Dijkstra Works**:
- All travel times (weights) are positive
- Single source `k` to all destinations
- Need maximum of all shortest paths

---

## 7. Variants and Extensions

| Variant | Modification | Complexity |
|---------|--------------|------------|
| **A* Search** | PQ key = g(n) + h(n) | Same as Dijkstra |
| **Bidirectional Dijkstra** | Forward + backward search | ~Half nodes explored |
| **Multi-objective** | Multiple cost dimensions | Pareto frontier tracking |
| **Time-dependent** | Weight = f(time) | Modified relaxation |
| **Constrained shortest path** | Resource limits | NP-hard in general |

---

## 8. Stale Entries in Priority Queue

### Why Multiple Entries Exist
When `dist[v]` is updated, we push a new entry `(v, new_dist)` to PQ. The old entry `(v, old_dist)` remains.

### Stale Entry Check
```java
int[] cur = pq.poll();
int node = cur[0], d = cur[1];
if (d > dist[node]) continue;  // Skip stale entry
```

**Correctness**: Only the entry with `d == dist[node]` represents the current best distance. All older entries have `d > dist[node]` and can be safely ignored.

**Space Impact**: PQ size can grow to O(E) in worst case, but typically much smaller.

---

## 9. Summary: Dijkstra's Guarantees

| Property | Guarantee |
|----------|-----------|
| **Time** (binary heap) | O((V + E) log V) |
| **Space** | O(V + E) |
| **Correctness** | Requires non-negative weights |
| **Single-source shortest paths** | ✅ |
| **All-pairs** | Run V times: O(V² log V + VE) |
| **Path reconstruction** | Store parent[] during relaxation |
| **Early termination (single target)** | ✅ When target extracted from PQ |