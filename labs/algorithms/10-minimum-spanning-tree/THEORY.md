# THEORY — Minimum Spanning Tree (Kruskal + Prim)
> Mechanics + invariants + complexity proof sketch for MST.

## 1. Problem Statement
- Input: connected undirected weighted `G=(V,E)`.
- Output: tree spanning all `V` with minimum total weight (any MST if ties).
- Disconnected → MSF (forest). Negative weights fine (no cycles in output).
- Success: cut-property-driven greedy, `O(E log E)` / `O(E log V)`.

## 2. Kruskal Mechanics
- Sort edges ascending. Union-Find over `V`. For each edge: if `find(u)!=find(v)` take it + union.
- Stop at `V-1` edges. Skip-edges are exactly cycle-edges (already connected).
- Union by rank + path compression → ~`α(V)` per op.
- Needs edge list; sorting dominates cost.

## 3. Prim Mechanics
- Grow tree from `s`: PQ of fringe edges `(w,u,v)`; pop min crossing edge, add vertex, push its edges.
- Skip stale (both ends in tree). `key[v]` = min edge to tree (alt view).
- `O(E log V)` binary heap; `O(V²)` array scan for dense.
- Single tree; restart per component for forest.

## 4. Invariants + Proof Sketch
- Cut property: for any cut, lightest crossing edge belongs to some MST.
- Kruskal I: taken set ⊆ some MST (safe). Each taken edge is lightest crossing its component cut.
- Prim I: tree ⊆ some MST; added edge lightest crossing tree cut.
- Cycle property (dual): heaviest edge on any cycle is never needed.
- Termination: Kruskal `V-1` takes or edges exhausted; Prim PQ empty.
- Uniqueness: distinct weights ⇒ unique MST; ties ⇒ many (tie-break decides which).

## 5. Worked Traces
- Triangle `AB1 BC2 AC3`: Kruskal takes AB,BC (skip AC — cycle), total 3.
- Prim from A: fringe AB1 AC3 → take AB → fringe BC2 AC3 → take BC.
- Tie square all weight 1: any 3 edges acyclic — valid MST weight 3.

## 6. Complexity Proof Sketch
- Kruskal: sort `O(E log E)` + `E·α(V)` unions → `O(E log E)` total.
- Prim+PQ: `V` extracts + `E` pushes × `log V` → `O(E log V)` (connected `E≥V-1`).
- Prim naive: `V` min-scans `O(V)` → `O(V²)`. Space `O(V+E)`.
- Union-Find amortized: `α(V)≤5` practical — effectively constant (Tarjan bound).

## 7. Correctness Arguments
- Induction with cut property per greedy step; exchange argument for safety.
- Counter-example: directed graphs — MST undefined (need arborescence/Edmonds).

## 8. When NOT to Use
- Directed → branching, not MST. Shortest-path needs → Dijkstra/BFS.
- Steiner/degree-constrained → NP-hard variants; MST is relaxation only.
- Dynamic weights → dynamic MST structures, not rerun-from-scratch at scale.

## 9. Java Notes
- `Arrays.sort(edges, comparingInt)`; DSU arrays `parent[], rank[]` iterative find.
- Prim: `PriorityQueue<long[]>` fringe; `boolean[] inTree`.
- `long total` — sums overflow int on big graphs.

## 10. Checklist
- [ ] DSU path compression + union by rank.
- [ ] `V-1` stop + disconnected-forest handling.
- [ ] Cut-property comment on greedy pick.
- [ ] `long` total + tie policy noted.
