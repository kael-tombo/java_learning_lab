# Mathematical Foundation — Depth-First Search (DFS)

## 1. Time Complexity Analysis

### Standard DFS on Graph G = (V, E)

**Theorem**: DFS visits each vertex exactly once and examines each edge at most twice (once from each endpoint in undirected graphs).

**Proof**:
- Each vertex is marked VISITED when first discovered and never processed again.
- For each vertex `u`, we iterate through all outgoing edges `(u, v)`.
- Undirected: edge `(u, v)` appears in adjacency list of both `u` and `v` → examined twice.
- Directed: edge examined exactly once.

**Time Complexity**: **O(V + E)**

### Comparison with BFS

| Aspect | DFS | BFS |
|--------|-----|-----|
| Time | O(V + E) | O(V + E) |
| Space (recursive) | O(V) stack | O(V) queue |
| Space (iterative) | O(V) stack | O(V) queue |
| Shortest path | ❌ | ✅ |
| Memory pattern | Deep, narrow | Wide, shallow |

---

## 2. Space Complexity Analysis

### Recursive DFS

**Worst Case**: Path graph (or deep linear chain) of length V.
- Recursion depth = V
- Call stack size = O(V)

**Best Case**: Star graph or balanced tree.
- Recursion depth = O(log V) for balanced tree
- But worst-case remains O(V)

### Iterative DFS (Explicit Stack)

Same asymptotic bounds, but:
- Avoids system call stack limits
- Allows custom stack frame data
- Can be paused/resumed

---

## 3. DFS Tree and Edge Classification

During DFS on a directed graph, each edge `(u, v)` is classified:

| Type | Condition | Meaning |
|------|-----------|---------|
| **Tree Edge** | `v` is WHITE | Part of DFS forest |
| **Back Edge** | `v` is GRAY | `v` is ancestor of `u` → **Cycle** |
| **Forward Edge** | `v` is BLACK, `v` is descendant of `u` | Non-tree edge to descendant |
| **Cross Edge** | `v` is BLACK, `v` is NOT descendant | Edge between subtrees |

### Key Theorem: Cycle Detection
> A directed graph has a cycle **iff** DFS yields a back edge.

**Proof**:
- (⇒) If cycle exists, DFS must eventually follow an edge to an ancestor in the recursion stack (GRAY).
- (⇐) A back edge `(u, v)` where `v` is ancestor of `u` forms cycle `v → ... → u → v`.

---

## 4. Topological Sort via DFS

### Algorithm
1. Run DFS on all vertices
2. Record vertices in order of **decreasing finish time** (post-order)
3. Reverse the list → valid topological order

### Correctness Proof
For any edge `(u, v)` in a DAG:
- When exploring `u`, `v` is either:
  - **WHITE**: DFS recurses to `v` and finishes `v` before `u` finishes.
  - **BLACK**: `v` already finished, so `finish[v] > finish[u]`.
- In both cases, `finish[v] > finish[u]` → `v` appears before `u` in reverse finish order.

**Time**: O(V + E) — same as DFS

---

## 5. Union-Find Complexity for Number of Islands

### Operations
- **Find(x)**: With path compression → amortized O(α(n))
- **Union(x, y)**: With union by rank → amortized O(α(n))

Where α(n) is the inverse Ackermann function:
- α(n) ≤ 4 for all practical n (n < 2^65536)
- Effectively **O(1)** in practice

### Number of Islands (m×n grid)
- V = m × n vertices
- E ≤ 2 × m × n edges (each cell connects to right and down)
- Time: O(V × α(V)) ≈ **O(m × n)**
- Space: O(m × n) for parent/rank arrays

### Comparison
| Approach | Time | Space | Notes |
|----------|------|-------|-------|
| DFS (recursive) | O(m × n) | O(m × n) | Stack overflow risk on large grids |
| DFS (iterative) | O(m × n) | O(m × n) | Safe for large grids |
| Union-Find | O(m × n × α) | O(m × n) | Iterative, no stack issues |

---

## 6. DFS vs BFS — When to Use Which

### Use DFS When:
- Path existence (not shortest path)
- Topological sorting
- Cycle detection in directed graphs
- Finding strongly connected components
- Maze generation/solving
- Tree/graph serialization (pre-order, post-order)
- Memory-constrained deep graphs (iterative DFS)

### Use BFS When:
- Shortest path in unweighted graphs
- Level-by-level processing
- Finding all nodes within distance k
- Multi-source shortest paths
- Bipartite checking (easier with BFS levels)

---

## 7. Recursion Depth Limits

### Java Default Stack Size
- Typical: 512KB - 1MB per thread
- Each stack frame: ~few hundred bytes
- Practical limit: ~5,000 - 10,000 recursive calls

### Mitigation Strategies
1. **Iterative DFS**: Use explicit `ArrayDeque` stack
2. **Increase stack**: `-Xss2m` JVM flag
3. **Tail recursion**: Not optimized in Java (unlike Scala/Kotlin)
4. **Hybrid**: Recursive for small depths, iterative for large

---

## 8. DFS on Implicit Graphs

For problems like:
- **Number of Islands**: Grid is implicit graph (4-neighbors)
- **Word Ladder II**: Dictionary words are nodes, edges implicit
- **N-Queens**: State space is implicit tree

**Complexity**: O(V + E) where V and E are defined by the problem's state space, not explicitly stored.

---

## 9. Summary: DFS Complexity Guarantees

| Scenario | Time | Space |
|----------|------|-------|
| Explicit graph (adj list) | O(V + E) | O(V) |
| Implicit graph (grid) | O(V + E) | O(V) |
| With memoization (DP on DAG) | O(V + E) | O(V) |
| Backtracking (all paths) | O(paths × path_len) | O(path_len) |

**Key Insight**: DFS explores the **state space** depth-first. Time is proportional to reachable states, space to maximum recursion depth.