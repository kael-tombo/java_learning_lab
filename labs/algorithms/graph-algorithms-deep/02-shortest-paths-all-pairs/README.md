# 02 — Shortest Paths: All-Pairs

<div align="center">

**Floyd–Warshall · Repeated Dijkstra · Johnson · A\* · Johnson–Dijkstra potentials · Dense vs Sparse**

</div>

---

## Learning Objectives

- Implement Floyd–Warshall with `O(V³)` time / `O(V²)` space and state its in-place invariant
- Prove Floyd–Warshall correctness from the path-intermediate-set induction
- Know exactly when negative edges are allowed (Floyd–Warshall detects negative cycles)
- Implement Johnson: Bellman–Ford potentials + reweighting + `V` Dijkstras
- Derive why reweighting preserves all shortest paths (`w'(u,v) = w(u,v) + h(u) − h(v) ≥ 0`)
- Implement A\* with a consistent heuristic and prove it is optimal
- Choose between Floyd–Warshall, `V × Dijkstra`, and Johnson from `(V, E)` and edge-sign constraints
- Diagnose `∞` arithmetic (`INF + INF` overflow, diagonal initialisation) — the #1 source of wrong answers

## Prerequisites

- `01-spanning-trees` (Dijkstra's algorithm, priority queues)
- `08-bellman-ford-floyd` if present
- Matrix representation and the Floyd–Warshall triple loop

## Estimated Time

- **Theory**: 90 minutes
- **Practice**: 150 minutes
- **Exercises**: 75 minutes
- **Total**: 5 hours

## Key Concepts

| Concept | Statement |
|---------|-----------|
| APSP | All `V²` source–destination pairs |
| Floyd–Warshall | `D[i][j] = min(D[i][j], D[i][k] + D[k][j])`, `O(V³)` |
| FW invariant | after iteration `k`, `D[i][j]` = shortest path with intermediates in `{0..k}` |
| FW on DAG | if topologically sorted, `O(V·E)` using only forward edges — the "FW on DAG" trick |
| Repeated Dijkstra | `V` × `O((V+E) log V)` = `O(V(E+V) log V)` |
| Johnson's | BF `O(VE)` + reweight + `V × O(E log V)` = `O(VE + V E log V)` |
| Potential `h(v)` | BF distances from a virtual source with 0-weight edges to all vertices |
| Reweighting | `w'(u,v) = w(u,v) + h(u) − h(v)`; all `w' ≥ 0` if no negative cycles |
| Path preservation | `w'(P) = w(P) + h(s) − h(t)` — a *constant* shift per pair |
| Negative cycle detection | `D[i][i] < 0` after FW, or "reachable from `s`" after BF |
| A\* | best-first search with `f(n) = g(n) + h(n)` |
| Consistent heuristic | `h(u) ≤ w(u,v) + h(v)` — guarantees optimality and no re-expansion |
| Sparse APSP | `O(E log V)` per source beats `O(V²)` |

## Complexity Snapshot

| Algorithm | Time | Space | Works with negative edges? |
|-----------|------|-------|---------------------------|
| Floyd–Warshall | **`O(V³)`** | `O(V²)` | Yes (detects negative cycles) |
| FW on DAG (topo order) | `O(V·E)` | `O(V²)` | Yes |
| Repeated Dijkstra (binary heap) | `O(V·E log V)` | `O(V²)` | **No** |
| Repeated Dijkstra (Fibonacci heap) | `O(V(E + V log V))` | `O(V²)` | **No** |
| **Johnson** | `O(VE + V E log V)` | `O(V²)` | **Yes** |
| Dijkstra with a `d`-ary heap | `O(V·(E + V log_d V))` | `O(V²)` | No |
| A\* (consistent `h`) | between Dijkstra and uninformed | `O(V + E)` frontier | No |
| Seidel (undirected unweighted) | `O(V^{2.58})` | `O(V²)` | n/a |
| Randomised sparse APSP | `O(V² log V)` expected | `O(V²)` | No |

**Selection rule:**
- `V ≤ 500`, any signs → **Floyd–Warshall** (`1.25·10^8` ops at `V=500`, ~0.1 s).
- `V` large, non-negative, sparse → **repeated Dijkstra**.
- `V` large, negative edges possible → **Johnson**.
- Small `V` with `O(V²)` space already needed → FW also gives **transitive closure** (replace
  `+` with `∨` and `min` with `∨`) for free, which is often why you actually wanted it.

## Algorithms Covered

### Floyd–Warshall
```java
for k in 0..V-1:            // k outermost — non-negotiable
  for i in 0..V-1:
    for j in 0..V-1:
      D[i][j] = min(D[i][j], D[i][k] + D[k][j]);
```
The `k` loop **must** be outermost. Reordering it computes a different (wrong) quantity. The
in-place version is correct precisely because of the invariant: `D[i][k]` and `D[k][j]` cannot be
improved during iteration `k` (any improvement would need an intermediate outside `{0..k}`,
or a negative cycle).

### Johnson
```java
1. Add a virtual source s' with a 0-weight edge to every vertex.
2. h = BellmanFord(s', 0)          // h(v) = min distance from s'  ⟹ h(v) ≤ 0, and finite
3. w'(u,v) = w(u,v) + h(u) - h(v)   // now w' ≥ 0
4. for each u: D[u][*] = Dijkstra(u) using w'
5. D[u][v] = D'[u][v] - h(u) + h(v)  // undo the shift
```
Step 5's correction is the constant `h(u) − h(v)` per pair, so all-pairs optimality survives.

### A\*
Priority key `f(n) = g(n) + h(n)` where `g` is the cost so far and `h` estimates the remaining
cost. With `h` **consistent** (`h(u) ≤ w(u,v) + h(v)`), A\* returns the optimal path and never
needs to re-expand a node — its guarantee reduces to Dijkstra's with a reweighted heuristic.
Perfect heuristic (`h` = true distance) ⇒ the search becomes a straight line, `O(path length)`.

## Files

| File | Purpose |
|------|---------|
| `THEORY.md` | FW invariant proof, Johnson reweighting proof, A\* admissibility/consistency |
| `EXERCISES.md` | Implement all three, hand-trace, hit `INF` and negative-cycle edge cases |
| `QUIZ.md` | 15 questions on complexity, invariants, counter-examples |
| `FLASHCARDS.md` | ~60 rapid-recall rows |
| `MATH_FOUNDATION.md` | FW recurrence derivation, reweighting algebra, Johnson cost, `V·E` FW-on-DAG |
| `CODE_DEEP_DIVE.md` | Annotated Java (FW, Johnson, A\*) + pitfalls |
| `DIAGRAMS/` | FW k-layer invariants, reweighting effect |