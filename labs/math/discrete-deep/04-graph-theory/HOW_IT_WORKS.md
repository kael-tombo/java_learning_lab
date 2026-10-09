# How It Works: Graph Algorithm Mechanics

## 1. BFS: Queue + On-Push Marking

```
visited[s] = true; dist[s] = 0; queue = [s]
while queue not empty:
    u = queue.poll()
    for v in neighbors(u):
        if !visited[v]:
            visited[v] = true          // mark BEFORE enqueue
            dist[v] = dist[u] + 1
            parent[v] = u
            queue.append(v)
```

Why marking on push is correct: the first time v is discovered it comes from the shallowest possible u (FIFO processes levels in order), so its distance is minimal — later encounters can only match or exceed it, and are discarded. Complexity: each vertex enqueued once, each edge scanned once → O(V + E).

## 2. DFS: Three Colors and Back Edges

Gray = on the current stack. On encountering a gray neighbor, you've closed a cycle (the path from that neighbor back to u plus edge u→v). Black = finished, all descendants explored. This is what makes DFS the engine for: topological order (append on black — only valid on DAGs), strongly connected components (Tarjan's low-link / Kosaraju's two-pass), bridges and articulation points (low[v] ≥ disc[u] criteria).

## 3. Dijkstra: The Settling Invariant

Invariant: *when a node u is popped with the smallest tentative distance, dist[u] is final.* Proof sketch: any other route to u must leave the settled set S through some edge (x, y), and since all weights ≥ 0, dist(y) ≥ dist(x) ≥ the popped minimum — so no alternative can undercut it. **This is exactly where negative weights break the proof**: a later-discovered edge could drop dist(y) below dist(u). Relaxation only ever *decreases* distances, which is why the "skip stale entries" line in a lazy heap is safe.

## 4. Kruskal: Greedy + Cycle Rejection

Sort edges ascending; add edge (u,v) iff u and v are in different union–find components. Correctness by the **cut property**: the lightest edge crossing any cut belongs to some MST — when we add it, the two sides may be merged in some MST, so greedy never forecloses an optimal solution. Stops at V − components edges; if fewer edges remain, the graph was disconnected (spanning *forest*, not tree).

## 5. Prim: Grow One Tree

Start at s; maintain a cut between "in tree" and "not," always adding the cheapest crossing edge — the same cut property, applied as Dijkstra-like heap growth. On dense graphs, the O(V²) array version scans all vertices for the minimum each round: V rounds × V scan = O(V²), no heap needed.

## 6. Kahn's Topological Sort

Count in-degrees; repeatedly emit a vertex with in-degree 0 and decrement its successors. A DAG empties completely; if the emitted count < V, the leftover vertices all have in-degree ≥ 0 pointing only at each other — that's a cycle, and Kahn's detection just reports it. Complexity O(V + E), and the output order satisfies every edge u → v as "u before v."

## 7. Max-Flow Augmentation (Edmonds–Karp)

Find an s→t path with positive residual capacity (BFS), push the bottleneck flow, update forward/backward residual capacities, repeat. Each BFS phase increases flow by at least ... the total is O(V·E²) augmenting phases bounded by O(VE) with BFS shortest augmenting paths. The reverse edges are what make "undo a bad earlier choice" possible — that's why residual networks, not just greedy pushes, give optimality; the terminating condition (no augmenting path) *is* the min-cut certificate by the max-flow min-cut theorem.
