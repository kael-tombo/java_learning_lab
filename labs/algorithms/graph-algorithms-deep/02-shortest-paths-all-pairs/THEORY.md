# THEORY — Shortest Paths: All-Pairs

## 1. Problem Statement

Given a directed or undirected weighted graph `G = (V, E)`, compute `D[u][v]` = the total weight of
a minimum-weight path from `u` to `v`, for **every** pair. Single-source versions (Dijkstra,
Bellman–Ford) are covered elsewhere; this lab is about the all-pairs problem, which has a
fundamentally different cost structure: any single-source algorithm must be run `V` times.

## 2. Floyd–Warshall

### 2.1 The recurrence and the definition trick

Define

```
D_k[i][j] = shortest distance from i to j using only vertices in {0, 1, …, k} as intermediates
```

Then the answer is `D_V[i][j]`. Base case `D_{−1}[i][j]` = `w(i,j)` if the edge exists, else `∞`
(and `D_{−1}[i][i] = 0`). Transition:

```
D_k[i][j] = min( D_{k−1}[i][j],  D_{k−1}[i][k] + D_{k−1}[k][j] )
```

**Derivation.** A shortest `i → j` path whose intermediates lie in `{0..k}` either:
1. does **not** pass through `k` — then its weight is `D_{k−1}[i][j]`; or
2. does pass through `k` — then it decomposes into an `i → k` path and a `k → j` path, both with
   intermediates in `{0..k−1}` (a simple path visits `k` once), so its weight is
   `D_{k−1}[i][k] + D_{k−1}[k][j]`.
Taking the minimum covers both cases exhaustively. ∎

### 2.2 Why the in-place version is correct

The naive implementation needs a fresh `D_k` per step, i.e. `O(V³)` memory. The standard trick
mutates one matrix in place. This is sound because during iteration `k`:

- `D[i][k]` cannot be improved: any improvement `D[i][k] < D[i][k] + D[k][k] = D[i][k]` would need
  `D[k][k] < 0`, i.e. a negative cycle through `k` (which we exclude).
- `D[k][j]` cannot be improved, by the same argument with `D[k][k] ≥ 0`.

So the values read at `D[i][k]` and `D[k][j]` are still `D_{k−1}[i][k]` and `D_{k−1}[k][j]`, making
the in-place update identical to the two-buffer version. **This is the only reason FW can be done
in `O(V²)` space.**

### 2.3 The `k` loop must be outermost

Putting `k` inside the `i` loop (a very common mistake) lets one `k` pass propagate through
several intermediate vertices, so the invariant `D_k` is violated and the result is wrong. The
invariant argument makes the required ordering explicit: one `k` pass admits **exactly one** new
intermediate vertex.

### 2.4 Complexity and the "sweet spot"

- Time `Θ(V³)` — for `V = 500`, `1.25·10^8` updates, roughly 0.1–0.3 s in Java with a
  cache-friendly `long[][]` row-major layout.
- Space `Θ(V²)` — for `V = 500`, 2 MB.
- Practical speedups: skip `i == k` and `j == k`; skip when `D[i][k] == INF` or `D[k][j] == INF`
  (this branch matters a lot on sparse graphs and can give a `10×` win); use the cache-blocked
  variant that processes a `K×K` tile at a time so `D[k][*]` stays in L1.

### 2.5 Negative cycles

FW detects a negative cycle iff `D[i][i] < 0` for some `i`. `D[i][i]` is the shortest non-empty
closed walk through `i`; a negative one means you can traverse it repeatedly to drive the total
to `−∞`, so no finite shortest path exists for any pair. **Any** vertex on a negative cycle
(before FW finalises) will show `D[i][i] < 0`; more robustly, detect negative cycles before
running FW if you intend to *use* the distances.

### 2.6 FW on a DAG: `O(V·E)`

If the graph is acyclic, compute a topological order and process vertices in that order; then
`D[i][j]` can only be improved through vertices that come before `j` in the order, so only
forward relaxations are needed. Total `O(V·E)` instead of `O(V³)`. This is used for
reachability-at-each-timepoint analyses and is the basis of shortest-path queries in
temporal graphs.

### 2.7 Transitive closure for free

Replacing `min` with `∨` and `+` with `∧` turns FW into a reachability computation:
`R[i][j] = R[i][j] ∨ (R[i][k] ∧ R[k][j])`, `Θ(V³/64)` with bitset rows. **If your real problem is
"can `u` reach `v`", do not run FW with `long[]` — run closure with `long[]`-as-bitsets and get a
64× constant speedup** (`V = 2000`: `8·10^9` naive vs `1.25·10^8` word ops).

## 3. Repeated Dijkstra

```
for each s in V:
    D[s][*] = Dijkstra(s)     // Θ((V + E) log V) with a binary heap
```
Total `Θ(V·(V + E) log V)` time, `Θ(V²)` space for the output (which is unavoidable).

- **Binary heap:** `Θ(V·E log V)`. For `E = Θ(V)` (sparse): `Θ(V² log V)`.
- **Fibonacci heap:** `Θ(V·(E + V log V))` — a `log V` improvement on the extract-min-heavy part.
- **Array scan per source:** `Θ(V(V + E))` — for dense graphs this beats the heap, same reasoning
  as array-Prim.

**Requires all edge weights `≥ 0`.** Any negative edge can make Dijkstra finalise a vertex whose
true distance is later improved.

## 4. Johnson: APSP with negative edges

### 4.1 Step 1 — potentials via Bellman–Ford

Add a virtual source `s'` with a `0`-weight edge to every vertex. Run Bellman–Ford from `s'`
(or use the SPFA variant). Let `h(v) = dist(s', v)`.

Since a path from `s'` enters any vertex via a `0`-edge, `h(v) ≤ 0` for all `v`, and `h` is finite
provided no negative cycle is reachable — which Bellman–Ford reports.

### 4.2 Step 2 — reweighting

```
w'(u, v) = w(u, v) + h(u) − h(v)
```

**Claim 1 (non-negativity).** `w'(u,v) ≥ 0`.
*Proof.* `h` is the shortest distance from `s'`, and the path `s' → u → v` has weight
`h(u) + w(u,v)`. Since `h(v)` is the *minimum* over all such paths, `h(v) ≤ h(u) + w(u,v)`, so
`h(u) + w(u,v) − h(v) ≥ 0`. ∎

**Claim 2 (path preservation).** For any path `P = (p₀, p₁, …, p_k)`:

```
w'(P) = Σ_{t=0}^{k−1} [w(p_t, p_{t+1}) + h(p_t) − h(p_{t+1})]
      = w(P)  +  Σ_{t=0}^{k−1} h(p_t) − Σ_{t=0}^{k−1} h(p_{t+1})
```

The potential terms telescope: `Σ_{t<k} h(p_t) = Σ_{t>0} h(p_t)`, so the difference is exactly
`h(p₀) − h(p_k)`:

```
w'(P) = w(P) + h(p₀) − h(p_k)
```

The correction `h(s) − h(t)` is **constant for a fixed `(s, t)` pair** — it does not depend on `P`.
Therefore minimising `w'` over all `s → t` paths minimises `w`, and the argmin sets are identical.
∎

**This telescoping is the whole trick.** Without it, reweighting would be meaningless.

### 4.3 Step 3 — run Dijkstra per source on `w'`, then correct

```
D'[s][*] = Dijkstra_w'(s)
D[s][t]  = D'[s][t] − h(s) + h(t)
```

### 4.4 Complexity

- Bellman–Ford: `Θ(V·E)` (or `Θ(VE)` for SPFA on average).
- `V` Dijkstras: `Θ(V·(V + E) log V)`.
- Total: **`Θ(VE + V·E log V)`**. Since `VE ≥ V²` (as `E ≥ V` in a connected graph), the
  Bellman–Ford term is dominated: `Θ(V·E log V)`.
- Space: `Θ(V²)` for the output plus `Θ(V + E)`.

**Johnson beats FW when `V·E·log V < V³`, i.e. `E < V²/log V`** — exactly the sparse regime.
It also handles negative edges, which FW's `V³` bound also allows but at `V³` cost.

### 4.5 When Johnson loses

| Situation | Better choice |
|-----------|---------------|
| `E = Θ(V²)` (dense) | **Floyd–Warshall**, `Θ(V³)` vs `Θ(V³ log V)` |
| All weights non-negative | Dijkstra — skip BF and reweighting entirely |
| `V` small (`≤ 300`) | FW, simpler and no negative-cycle edge cases |
| Negative cycles present | FW or BF report it; Johnson's BF step does too |

## 5. A*

`f(n) = g(n) + h(n)`, where `g(n)` is the cost from the source and `h(n)` estimates the remaining
cost. Pop from the priority queue by smallest `f`.

**Admissible:** `h(n) ≤ h*(n)` for all `n`, where `h*` is the true remaining cost.
**Consistent (monotone):** `h(u) ≤ w(u, v) + h(v)` for every edge `u → v`.

**Theorem.** With a consistent `h`, A\* is **admissible-optimal**: it returns a shortest path and
never re-expands a node. *Proof sketch.* Consistency gives `f(v) − f(u) = w(u,v) + h(v) − h(u) ≥ 0`,
so `f` is non-decreasing along every edge — exactly Dijkstra's key-monotonicity property. Running
Dijkstra with key `f` on the reweighted graph where `w''(u,v) = w(u,v) + h(v) − h(u) ≥ 0` therefore
yields the shortest `s → t` path in `w''`, which equals `w` on `s → t` paths for the same
telescoping reason as Johnson's reweighting. ∎

**Consistency is what makes it cheap; admissibility alone only makes it correct.**
- Admissible but inconsistent (e.g. `h` = straight-line distance in a maze): still optimal,
  but a node may be expanded multiple times, so the worst case degrades toward the number of
  simple paths — exponential.
- Consistent (e.g. `h` = exact distance, or a consistent relaxed heuristic): each node expanded
  at most once ⇒ `O(E + V log V)`, strictly better than Dijkstra because the priority ordering
  focuses the search.

**Precompute `h` = true distances from `t` by one reversed Dijkstra run**, then A* becomes
"bidirectional Dijkstra dressed up". If the graph is undirected and weights non-negative, this
gives `O(E + V log V)` *per query to a fixed target*, with a large constant-factor win.

## 6. Negative Cycles and the `V`-iteration bound

Bellman–Ford relaxes all edges `V−1` times, then a `V`-th pass detects improvements. Why `V−1`?
**Invariant:** after `k` passes, all shortest paths with at most `k` edges have correct distances.
*Proof.* Induct on `k`. Base `k=0`: only the source itself (distance 0). Step: any path with
`≤ k+1` edges is a `≤ k`-edge path to some vertex plus one edge; pass `k+1` relaxes that last edge
using already-correct values. ∎ A shortest path is always simple (otherwise removing a cycle of
weight `≥ 0` does not increase its weight), so it has `≤ V−1` edges.

**Counter-example for Dijkstra:** `s → a = 2, s → b = 5, b → a = −10`. Dijkstra settles `a` at 2
(the smallest tentative), then relaxes `b` to `5` and settles it; the edge `b → a` gives `−5`, which
would beat 2 — but `a` is already closed, so the algorithm returns 2, which is wrong (the true
shortest `s → a` is `−5` via `b`). **This is the exact negative-edge failure of Dijkstra.**

## 7. Choice Summary

| Situation | Algorithm | Why |
|-----------|-----------|-----|
| `V ≤ 500`, any weights, may have negative cycles | **Floyd–Warshall** | `V³` beats `V·E log V`; detects negative cycles |
| Large sparse, all weights `≥ 0` | **Repeated Dijkstra** | Skip the BF overhead |
| Large sparse, negative weights allowed | **Johnson** | Reweight + Dijkstra |
| Repeated queries to a fixed target | **A\* with precomputed `h`** | Consistent `h` ⇒ no re-expansion |
| Reachability only | **Bitset closure** | `Θ(V³/64)` |
| DAG | **FW on DAG** | `Θ(V·E)` |
| One source only | Dijkstra / BF | All-pairs is pure waste |