# EXERCISES — Shortest Paths: All-Pairs

## Level 1 — Floyd–Warshall by Hand

### 1.1 Trace FW on a 4-vertex graph
`V = {0,1,2,3}`. Edges: `0→1 = 5, 0→2 = 3, 1→2 = 1, 1→3 = 12, 2→3 = 4`.
Initial matrix (`∞` = no path):

```
     0   1   2   3
0 [  0   5   3   ∞ ]
1 [  ∞   0   1  12 ]
2 [  ∞   ∞   0   4 ]
3 [  ∞   ∞   ∞   0 ]
```

**k=0:** relax via 0. Row 0 unchanged (nothing improves through 0 — no path `0→0→x` beats `0→x`).
No changes anywhere (`∞` on the left column blocks everything).
**k=1:** via 1.
- `D[0][2] = min(3, 5+1) = 3`; `D[0][3] = min(∞, 5+12) = 17`
- `D[2][1] = min(∞, 4+∞)` → `∞` (no `2→1`); `D[3][*]` stays `∞`
```
     0   1   2   3
0 [  0   5   3  17 ]
1 [  ∞   0   1  12 ]
2 [  ∞   ∞   0   4 ]
3 [  ∞   ∞   ∞   0 ]
```
**k=2:** via 2.
- `D[0][3] = min(17, 3+4) = 7` ✓ (this is the `0→2→3` path)
- `D[1][3] = min(12, 1+4) = 5` ✓ (this is `1→2→3` — an update from `D[2][3]`, so **new after k=1**)
```
     0   1   2   3
0 [  0   5   3   7 ]
1 [  ∞   0   1   5 ]
2 [  ∞   ∞   0   4 ]
3 [  ∞   ∞   ∞   0 ]
```
**k=3:** via 3 — row/col 3 only reaches itself, no change.

**Answer:** `D[0][3] = 7`, `D[1][3] = 5`. Verify: `1→2→3 = 1+4 = 5 < 12` ✓.

### 1.2 Break the `k`-loop order
Run the same graph with `k` as the *innermost* loop. Compute the result and explain in terms of
the invariant why it differs. Then state the exact invariant each loop nesting maintains.

### 1.3 Negative cycle detection
Add edge `2 → 1 = −7` to the graph above. Run FW. Where does `D[i][i] < 0` first appear, and at
which `k`? **Answer:** the cycle `1→2→1 = 1 + (−7) = −6`. At `k=2`, `D[1][1] = min(0, D[1][2]+D[2][1]) = min(0, 1+0)`. At `k=1` itself `D[2][1]` becomes `−7`. Recheck: after `k=1`, `D[2][1] = min(∞, 4+∞) = ∞` — no.
The path `2→1` is a direct edge, so it is in the *initial* matrix: `D[2][1] = −7`. Then at
`k = 1`: `D[1][1] = min(0, D[1][2] + D[2][1]) = min(0, 1 + (−7)) = −6 < 0`. **Detected at k=1.** ✓

### 1.4 Transitive closure
Take the graph from 1.1 and compute reachability with the boolean version of FW (bitwise
operations). Verify `R[0][3] = true` and count the `true` entries.

## Level 2 — Implementations

### 2.1 FW with `INF` guards
Implement FW with the two guard branches (`if (D[i][k] == INF) continue` and
`if (D[k][j] == INF) continue`). Benchmark on: (a) a dense random graph `V=400`,
(b) a sparse graph `V=4000, E=8000`. Report the speedup ratio for each.

### 2.2 FW cache tiling
Implement the blocked FW:
```java
for (kk = 0; kk < V; kk += K)
  for (jj = kk; jj < min(kk+K, V); jj++)
    for (ii = kk; ii < min(kk+K, V); ii++)
      D[ii][jj] = min(D[ii][jj], D[ii][kk] + D[kk][jj]);
  for (jj = 0; jj < V; jj++)
    for (kk2 = kk; kk2 < min(kk+K,V); kk2++)
      for (ii = 0; ii < V; ii++)
        D[ii][jj] = min(D[ii][jj], D[ii][kk2] + D[kk2][jj]);
  for (kk2 = 0; kk2 < min(kk+K,V); kk2++)
    for (jj = 0; jj < V; jj++)
      for (ii = 0; ii < V; ii++)
        D[ii][jj] = min(D[ii][jj], D[ii][kk2] + D[kk2][jj]);
```
Benchmark vs the naive triple loop at `V=600` with `K=32`. Expect `1.5–3×`.

### 2.3 Bitset transitive closure
Implement closure with `long[]` bitsets. `V = 3000`. Compare to FW's `V³ = 2.7·10^10` (about 10 s)
versus `V³/64 ≈ 4.2·10^8` word ops (about 0.2 s).

### 2.4 Repeated Dijkstra
Implement `V × Dijkstra` with `PriorityQueue`. Test against FW on random graphs with `V ≤ 60`,
all weights `≥ 0`. **Any mismatch means a bug in one of them.**

## Level 3 — Johnson

### 3.1 Derive the potentials by hand
Graph: `0→1 = −2, 0→2 = 5, 1→2 = 1, 2→3 = −3, 1→3 = 4`.
- Add `s'` with `0`-edges to all. `h(0) = 0, h(1) = −2, h(2) = min(0, −2+1) = −1, h(3) = min(0−2+4, −1−3) = −4`.
  So `h = [0, −2, −1, −4]`. Verify `h(3)`: via `1→3` = `h(1)+4 = 2`; via `2→3` = `h(2)+(−3) = −4`. Min = `−4` ✓
- Reweight: `w'(0,1) = −2 + 0 − (−2) = 0`; `w'(0,2) = 5 + 0 − (−1) = 6`;
  `w'(1,2) = 1 + (−2) − (−1) = 0`; `w'(1,3) = 4 + (−2) − (−4) = 6`; `w'(2,3) = −3 + (−1) − (−4) = 0`.
  **All non-negative ✓**
- Run Dijkstra from 0 on `w'`: `D'[0][1] = 0, D'[0][2] = 0, D'[0][3] = 0`.
- Correct: `D[0][1] = 0 − 0 + (−2) = −2` ✓; `D[0][2] = 0 − 0 + (−1) = −1` ✓
  (and `−2 + 1 = −1` ✓); `D[0][3] = 0 − 0 + (−4) = −4` ✓ (`−2+1−3 = −4` ✓)

### 3.2 Full Johnson
Implement all three steps. Verify against FW on random graphs with mixed-sign weights and
`V ≤ 50`. Then check that `w'(u,v) ≥ 0` for every edge — this is a **cheap assertion** that
catches most Johnson bugs.

### 3.3 Negative cycle in Johnson
Add `2→1 = −5` to the 3.1 graph. Bellman–Ford must report it. Verify `h` is not finite and that
your code does **not** silently proceed to run Dijkstra on garbage potentials.

### 3.4 When to skip Johnson
Show that if all weights are `≥ 0`, `h(v) = 0` for all `v` (the virtual source reaches everything
with weight 0) and hence `w' = w`. Therefore Johnson's Bellman–Ford step is pure overhead in that
case, and repeated Dijkstra is strictly better. Verify empirically.

## Level 4 — A*

### 4.1 A* on the grid
15×15 grid with unit costs; `h` = Manhattan distance. Count node expansions from corner to corner
vs plain Dijkstra. Expect a large reduction (Dijkstra expands all 225; A* expands roughly the
number of nodes on the shortest path, `~28`).

### 4.2 Admissible but inconsistent `h`
Grid with walls; use `h` = Euclidean distance to goal while movement is Manhattan (still
admissible if `√2 ≤ 1 + h`... it is). Now use `h` = 0 for half the cells and exact for the rest.
Observe re-expansions. Count how many times the worst node is expanded and compare to Dijkstra.

### 4.3 Prove `f` monotonicity
For consistent `h`, show `f(v) ≥ f(u)` for every edge `u → v`. Then explain why Dijkstra's
settled-once argument transfers verbatim.

### 4.4 Precomputed `h` = one Dijkstra
For an undirected graph with non-negative weights and many queries to the same target `t`, run
Dijkstra from `t` once on the reversed graph to get exact `h`, then A* from every source.
Compare total time to `V × Dijkstra`.

## Level 5 — Edge Cases (all must pass)

| Input | Expected | Trap |
|-------|----------|------|
| `V = 1` | `D[0][0] = 0` | `INF + INF` overflow if you don't guard |
| `V = 0` | empty matrix | loops must not run |
| No path `i → j` | `∞` | must not become a finite number from `INF + w` |
| Negative edge, no cycle | correct distances | FW/Johnson fine, Dijkstra fails |
| Negative cycle | report it | FW: `D[i][i] < 0`; Johnson: BF reports |
| Self-loop `w = 0` | no effect | `D[i][i] = min(0, 0+0) = 0` |
| Self-loop `w < 0` | **negative cycle** | `D[i][i] < 0` — correct behaviour, easy to miss |
| Self-loop `w > 0` | no effect | |
| Parallel edges | keep the min | `w'(u,v)` computed per parallel edge |
| Undirected graph | symmetric `D` | FW on a symmetric matrix stays symmetric — verify |
| Weight `10^15` | use `long` | `long` overflows past `~9.2·10^18` |
| Zero-weight edges | fine | but "settled once" requires **non-negative**, not positive |
| `INF` sentinel choice | `Long.MAX_VALUE/4` | so `INF + w` cannot overflow |

## Level 6 — Proof Obligations

6.1 Write the full FW induction proof (`D_k` correctness), including the case analysis on
      whether the optimal path visits `k`.
6.2 Prove the in-place safety of FW: `D[i][k]` and `D[k][j]` are unchanged during iteration `k`.
      Show exactly which assumption (no negative cycles) is required.
6.3 Derive the telescoping in Johnson's reweighting, line by line.
6.4 Prove: `w' ≥ 0` iff `h` is a valid potential, and that BF from `s'` yields such an `h`.
6.5 Prove the `V−1` bound on Bellman–Ford by induction on pass number.
6.6 Prove A\* optimality from consistency by reducing to Dijkstra on the `w''`-reweighted graph.

## Level 7 — Stretch

7.1 **Transitive reduction** vs **transitive closure**: define both, give complexities, and argue
      why closure is sometimes the wrong answer to a "reachability" question.
7.2 **All-pairs with `V` huge and `E` tiny** (e.g. a road network with `10^6` cities, `3·10^6`
      edges): all-pairs is infeasible (`10^12` output entries). Argue for the hierarchy approach
      (Contraction Hierarchies / Hub Labels): preprocessing `O(E log V)` with high constants, then
      `O(log V)` per query.
7.3 **Landmark ALT** potentials: derive why choosing `k` landmarks gives a much tighter `h` and
      predict the query-time improvement as `O(k)` per query.
7.4 **Distance sensitivity oracle**: show that FW gives you, in `O(1)` query time, a structure that
      answers "did the shortest path `s→t` use edge `e`?" via
      `D[s][u] + w + D[v][t] == D[s][t]`. This is the basis of replacement-path algorithms.