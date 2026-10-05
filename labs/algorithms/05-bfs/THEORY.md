# THEORY — Breadth-First Search (BFS)
> Mechanics + invariants + complexity proof sketch for BFS.

## 1. Problem Statement
- Input: graph `G=(V,E)` (adj list), source `s`.
- Output: `dist[]` (fewest edges from `s`), `parent[]` tree, visit order.
- Unweighted only; directed or undirected.
- Success: level order, shortest-edge paths, `O(V+E)`.
- Contrast: DFS ignores distance; Dijkstra generalizes to weights.

## 2. Algorithm Mechanics
- Init `dist[s]=0`, queue `Q=[s]`, `visited={s}` (mark on enqueue, not dequeue).
- While `Q` nonempty: `u=dequeue`; for each `v∈Adj[u]`: if unvisited → `dist=dist[u]+1`, parent=u, enqueue.
- Mark-on-enqueue prevents duplicate pushes (exponential blowup otherwise).
- Level trick: process queue in layers (`size=Q.size()` per level) for level lists.
- Parent pointers reconstruct paths by back-chaining.
- Disconnected: outer loop over all vertices for full forest.
- Directed: follow out-edges only; undirected: both directions.

## 3. Invariants
- I1 (queue order): `Q` holds vertices in nondecreasing `dist`, differing by ≤1.
- I2 (finality): dequeued `u` has minimal `dist` among unseen — final value.
- I3 (parent): `dist[child]=dist[parent]+1` along tree edges.
- Init: `Q=[s]`, `dist[s]=0` — all hold.
- Maintenance: enqueued neighbors get `dist+1`, appended after current level.
- Termination: `Q` empty → all reachable visited (else a frontier edge would remain).
- Proof of I2: any alternative path must leave settled set via frontier ≥ current dist.

## 4. Worked Trace
- Line `s-A-B`, `s-C`: Q=[s] → pop s, push A,C → pop A push B → order s,A,C,B.
- `dist: s=0,A=1,C=1,B=2`. Parents chain `B→A→s`.
- Diamond `s→A→t, s→B→t`: first discoverer parents `t` (either A or B).
- Self-loop/disconnected node: loop ignored; isolated stays `∞`.

## 5. Complexity Proof Sketch
- Each vertex enqueued/dequeued ≤ once → `O(V)` queue work.
- Each edge examined ≤ twice (undirected) / once (directed) → `O(E)` scans.
- Total `T=O(V+E)` with adj lists; `O(V²)` with matrix (scan row per dequeue).
- Space: `dist+parent+visited+Q` → `O(V)`.
- Level-order claim: induction on distance using I1 — level `k` dequeued before `k+1` enqueued-complete.
- Shortest-path: any `s→v` path has ≥ `dist[v]` edges (each edge extends distance by ≤1 along BFS layers).

## 6. Correctness Argument
- I1+I2 by induction on dequeue order; shortest paths from I2 + parent chains.
- Counter-example: weighted edge `s→t=10, s→a→t=1+1` — BFS picks direct 1-hop, wrong for weights.

## 7. When NOT to Use
- Weighted shortest → Dijkstra/A*.
- Deep + narrow + target likely deep → DFS/IDDFS uses less memory.
- All-pairs → run BFS per source or Floyd-Warshall (dense).
- Topological needs → DFS postorder, not BFS (except Kahn).

## 8. Java Notes
- `ArrayDeque<Integer>` as queue; `boolean[] visited` or `BitSet`.
- Adj list: `List<List<Integer>>`; avoid `LinkedList` per adjacency (ArrayList better).
- Recursion is wrong tool — BFS is inherently iterative.

## 9. Common Misconceptions
- "BFS finds weighted shortest" — only unweighted (edge count).
- "Mark on dequeue is fine" — causes duplicate enqueues, worst-case blowup.
- "BFS is always O(V+E)" — only with adj lists; matrix differs.

## 10. Checklist
- [ ] Mark-on-enqueue + parent set together.
- [ ] Level trace matches `dist` layers.
- [ ] Disconnected + self-loop cases covered.
- [ ] Path reconstruction tested via parent chain.
