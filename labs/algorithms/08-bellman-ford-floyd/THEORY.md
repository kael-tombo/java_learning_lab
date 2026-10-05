# THEORY — Bellman-Ford + Floyd-Warshall
> Mechanics + invariants + complexity proof sketch for negative-tolerant shortest paths.

## 1. Problem Statement
- Input: directed/undirected weighted graph, possibly negative `w` (no negative cycle on query paths).
- BF: single source; FW: all pairs. Output distances + cycle verdict.
- Success: BF `O(VE)` + detection; FW `O(V³)` simple triple loop.
- Contrast: Dijkstra faster but forbids negatives.

## 2. Bellman-Ford Mechanics
- Init `dist[s]=0`, rest `∞`. Repeat `V-1` times: relax every edge `dist[v]=min(dist[v],dist[u]+w)`.
- Pass `V`: if any relax improves → negative cycle reachable → report it.
- Order of edges irrelevant to correctness (affects speed only).
- Path: `prev[]` on successful relax; walk back for cycle nodes.
- Early exit: pass with zero updates → done (still need final detection pass).
- Queue优化 SPFA: same idea, no worst-case guarantee — keep classic for teaching.

## 3. Floyd-Warshall Mechanics
- Init `d[i][j]=w(i,j)`, `0` on diagonal, `∞` absent.
- Triple loop `k,i,j`: `d[i][j]=min(d[i][j], d[i][k]+d[k][j])` — `k` outermost (load-bearing).
- `k`-loop order wrong (e.g., `i` outer) breaks intermediate-set semantics.
- Negative cycle: any `d[i][i]<0` after completion.
- Path reconstruction: `next[i][j]` updated alongside.

## 4. Invariants
- BF I: after `i` passes, `dist[v]` = shortest path using ≤ `i` edges (induction on passes).
- Simple shortest path uses ≤ `V-1` edges (no cycles needed unless negative) → `V-1` passes suffice.
- FW I: after `k` iteration, `d[i][j]` = shortest using intermediates ⊆ `{1..k}`.
- Init (`k=0`): direct edges only — holds. Step adds vertex `k` as allowed intermediate.
- Termination: `k=V` allows all intermediates → all-pairs optimal.

## 5. Worked Traces
- BF `s→a=5,s→b=6,b→a=-4`: pass1: b=6,a=2 (via b if edge order allows, else pass2) → converges to a=2.
- Neg cycle `a→b=-1,b→a=-1`: pass V still improves → flag cycle.
- FW 3-node: `1→2=3,2→3=2,1→3=10`: k=2 updates `d[1][3]=5`; k loop order matters.

## 6. Complexity Proof Sketch
- BF: `V` passes × `E` edges × `O(1)` relax = `O(VE)` time, `O(V)` space.
- FW: `V³` inner ops → `Θ(V³)` time, `Θ(V²)` space (in-place allowed).
- BF lower sketch: chain graph forces `Ω(VE)` relaxations in worst order.
- Detection cost included (one extra pass / diagonal scan) — no extra order.
- Space FW can drop `k` dimension (2-D in place) by I monotonicity.

## 7. Correctness Arguments
- BF path-relaxation lemma: relaxing edges along a shortest path in order tightens to optimum.
- `V-1` passes cover every simple path's edge sequence regardless of global edge order.
- FW induction on `k` (above); negative diagonal ⟺ negative cycle.

## 8. When NOT to Use
- Non-negative + single source → Dijkstra (much faster).
- Sparse all-pairs → Johnson (BF + V×Dijkstra) beats `V³`.
- Unweighted → BFS per source.

## 9. Java Notes
- Use `long` + `INF=Long.MAX_VALUE/4`; check `dist[u]!=INF` before `+w`.
- Edge list `int[]{u,v,w}` for BF; `long[][]` for FW (n ≤ ~400 practical).
- FW loop order `for k for i for j` — comment why.

## 10. Checklist
- [ ] `V-1` + detection pass both present.
- [ ] FW `k`-outer order + comment.
- [ ] Negative-cycle demo traced.
- [ ] Overflow-safe INF handling.
