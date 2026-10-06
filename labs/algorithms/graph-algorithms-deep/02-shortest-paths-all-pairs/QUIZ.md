# QUIZ — Shortest Paths: All-Pairs

1. State the Floyd–Warshall invariant, precisely, in terms of `D_k`.
2. Give FW's time and space complexity.
3. Why must the `k` loop be outermost in FW?
4. Why is the in-place version of FW correct? What assumption does it require?
5. What does FW use to detect a negative cycle?
6. Explain the `INF` overflow trap and the standard fix.
7. Give FW's complexity on a DAG, and the key property that enables it.
8. How do you turn FW into a reachability (transitive closure) computation, and what speedup does bitset packing give?
9. State the reweighting formula Johnson uses and prove `w'(u,v) ≥ 0`.
10. Show that Johnson's reweighting preserves the argmin shortest path for a fixed `(s,t)` pair — the telescoping.
11. What does Johnson's Bellman–Ford step produce, and what value does `h` take when all weights are already non-negative?
12. Give Johnson's total time complexity and the regime in which it beats Floyd–Warshall.
13. What is the difference between an *admissible* and a *consistent* A\* heuristic, and which one gives node-expanded-at-most-once?
14. Give the concrete counter-example showing Dijkstra fails with a negative edge.
15. Why does Bellman–Ford need exactly `V−1` relaxation passes, and what does the `V`-th pass detect?

---

## Answers

1. **After iteration `k` completes, `D[i][j]` holds the length of the shortest `i → j` path whose
   *intermediate* vertices are all drawn from `{0, 1, …, k}`.** Endpoints `i` and `j` may be
   outside that set (they are `∞` unless `i == j`, in which case `D[i][i] = 0`). The answer is
   `D_{V−1}`, i.e. after the last iteration.
2. Time `Θ(V³)`, space `Θ(V²)`. For `V = 500` that's `1.25·10^8` updates and 2 MB.
3. Because the invariant admits **exactly one** new intermediate vertex per `k` pass. With `k`
   in an inner loop, one pass would propagate *several* vertices through `k` transitively — a
   path using `k` plus `k'` plus `k''` would be discovered in one sweep — so `D_k` no longer means
   "intermediates in `{0..k}`" and you silently compute something else. The invariant argument
   forces the ordering.
4. During iteration `k`, the entries `D[i][k]` and `D[k][j]` cannot be improved: any improvement
   would require `D[k][k] < 0`, i.e. a negative cycle through `k`. So the in-place update reads
   values that are still `D_{k−1}[i][k]` and `D_{k−1}[k][j]`, making it identical to the
   two-buffer version. **It requires the absence of negative cycles.** With a negative cycle the
   in-place values drift and the result is meaningless (though it still usually reports
   `D[i][i] < 0`).
5. `D[i][i] < 0` for some `i`. `D[i][i]` is the minimum-weight non-empty closed walk through `i`;
   if it is negative, that cycle can be traversed repeatedly to drive any distance to `−∞`.
6. `INF + w` with `INF = Long.MAX_VALUE` wraps around to a large **negative** number, so
   unreachable pairs become reachable-looking negatives and propagate. Use `INF = Long.MAX_VALUE / 4`
   (or `Long.MAX_VALUE / 4 - 1`) so that adding any representable weight cannot overflow, **and**
   guard the update with `if (D[i][k] < INF && D[k][j] < INF)`. Both together: the sentinel keeps
   the arithmetic safe, the guard keeps the semantics clean.
7. `Θ(V·E)` (vs `Θ(V³)`). Enabled by **topological order**: in a DAG, all intermediates on a
   shortest `i → j` path come strictly before `j` in a topological order, so processing vertices
   in that order and doing only forward relaxations is sufficient — you never need to consider
   `k` after `j`. Equivalently, "no cycles" means the `D_{k−1}` vs `D_k` distinction collapses.
8. Replace `min` with `∨` (logical or) and `+` with `∧` (logical and):
   `R[i][j] = R[i][j] ∨ (R[i][k] ∧ R[k][j])`, starting from the adjacency matrix and `R[i][i] = true`.
   Packing each row into `long[]` bitsets makes each update a word operation instead of a boolean,
   so `Θ(V³)` becomes `Θ(V³/64)`. `V = 3000`: `2.7·10^10` → `4.2·10^8` word ops (~10 s → ~0.2 s).
   Note this is a **constant-factor** win (64 is a constant), so state it as "64× fewer operations",
   not as an asymptotic improvement.
9. `w'(u,v) = w(u,v) + h(u) − h(v)`, where `h(v) = dist(s', v)` from Bellman–Ford with `s'`
   joined to every vertex by a `0`-edge. **Proof of `w' ≥ 0`:** the path `s' → u → v` has weight
   `h(u) + w(u,v)`; since `h(v)` is the *minimum* over all `s'`-rooted paths,
   `h(v) ≤ h(u) + w(u,v)`, i.e. `h(u) + w(u,v) − h(v) ≥ 0`. ∎
10. For a path `P = (p₀, p₁, …, p_k)`:
    `w'(P) = Σ_{t<k}[w(p_t,p_{t+1}) + h(p_t) − h(p_{t+1})]`. The potential terms telescope because
    `Σ_{t<k} h(p_t) = h(p₀) + h(p₁) + … + h(p_{k−1})` and `Σ_{t<k} h(p_{t+1}) = h(p₁) + … + h(p_k)`;
    every interior term cancels, leaving `w'(P) = w(P) + h(p₀) − h(p_k)`. The correction
    `h(s) − h(t)` depends only on the endpoints, so it is the **same constant for every `s → t`
    path**; adding a constant to all candidates preserves both the minimum and the set of minimisers. ∎
11. `h(v)` = the shortest distance from the virtual source `s'` (equivalently, `h(v)` = the minimum
    over all `s`-rooted distances, shifted so the virtual source is at 0), which is `≤ 0` and finite
    exactly when no negative cycle exists. **If all edge weights are already non-negative, `h(v) = 0`
    for every `v`** (because `s'` reaches `v` directly with cost 0, and nothing is cheaper), so
    `w' = w` and the entire Bellman–Ford + reweighting phase is pure overhead — which is why
    Johnson's first step can be skipped in the non-negative case.
12. `Θ(V·E)` for Bellman–Ford plus `V × Θ((V + E) log V)` for the Dijkstras, i.e.
    `Θ(V·E + V·E log V) = Θ(V·E log V)`. Johnson beats FW when `V·E log V < V³`, i.e.
    **`E < V² / log V`** — precisely the sparse regime. It also handles negative edges, and FW
    wins for dense graphs (`E = Θ(V²)`: `Θ(V³ log V)` vs `Θ(V³)`).
13. **Admissible:** `h(n) ≤ h*(n)` (true remaining cost) for all `n` — guarantees A\* returns an
    optimal path. **Consistent:** `h(u) ≤ w(u,v) + h(v)` for every edge — implies admissibility
    *and* guarantees `f` is non-decreasing along edges, so each node is expanded **at most once**.
    Admissible-but-inconsistent heuristics still give optimal answers but may expand nodes many
    times, degrading the worst case toward the number of simple paths (exponential). Consistency
    is the property you actually need for efficiency.
14. `s → a` with weight 2, `s → b` with weight 5, `b → a` with weight `−10`. Dijkstra settles
    `a` first (tentative 2 is the smallest), marks it done. It then settles `b` (5), and relaxing
    `b → a` yields `5 − 10 = −5 < 2` — but `a` is already settled and never reopened, so the
    algorithm reports `dist[a] = 2`. The true shortest `s → a` is `−5` via `b`. **The failure mode
    is silent:** no exception, just a wrong number, because the "settled ⇒ final" argument relies
    on no future relaxation producing a smaller value, which non-negativity guarantees.
15. Because after `k` passes, all shortest paths using at most `k` edges have correct distances
    (induction: a `≤ k+1`-edge path is a `≤ k`-edge path plus one final edge, relaxed in pass
    `k+1`). A shortest path is always *simple* — otherwise removing a cycle of weight `≥ 0` does
    not increase its weight — so it has at most `V−1` edges. After `V−1` passes everything is
    final; the **`V`-th pass finds any relaxation that still improves a distance, which can only
    happen via a negative cycle**. That pass is a negative-cycle detector.