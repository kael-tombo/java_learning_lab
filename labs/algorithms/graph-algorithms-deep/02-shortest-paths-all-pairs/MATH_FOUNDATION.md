# MATH_FOUNDATION — Shortest Paths: All-Pairs

## 1. Floyd–Warshall: Deriving the Recurrence from a Set Definition

Define, for `K ⊆ V`,

```
D_K[i][j] = min { w(P) : P is a path i → j whose internal vertices ⊆ K }
```

with `D_∅[i][j] = w(i,j)` if `(i,j) ∈ E` (or `0` if `i == j`), else `∞`.

**Step 1 — monotone in `K`.** If `K' ⊆ K` then `D_{K'}[i][j] ≥ D_K[i][j]` (fewer allowed paths).
Every shortest path has a *minimal* intermediate set, so we only ever need `K` = the first `k`
vertices in any fixed order.

**Step 2 — the split.** Let `K_k = {0..k}` and `K_{k−1} = K_k \ {k}`. Take a path `P` achieving
`D_{K_k}[i][j]` (assume a shortest path exists and is simple). Either:

- `k ∉ P` (as an internal vertex) ⟹ `w(P) ≥ D_{K_{k−1}}[i][j]`
- `k ∈ P` ⟹ `P = P₁ ∘ P₂` where `P₁ : i → k` and `P₂ : k → j`. Because `P` is simple, `k` occurs
  once, and the internal vertices of `P₁` and `P₂` all lie in `K_{k−1}` (they are internal to `P`,
  hence in `K_k`, and `k` itself is an endpoint of both halves). So
  `w(P) = w(P₁) + w(P₂) ≥ D_{K_{k−1}}[i][k] + D_{K_{k−1}}[k][j]`.

Taking the min of both cases (both are achievable by concatenating optimal halves) gives exactly

```
D_{K_k}[i][j] = min( D_{K_{k−1}}[i][j],  D_{K_{k−1}}[i][k] + D_{K_{k−1}}[k][j] )
```

**Step 3 — unroll.** `K_{V−1} = V`, so `D_{V−1}` allows all vertices as intermediates: it is the
true APSP. Depth of the recursion = `V`, so `V` layers × `V²` entries × `O(1)` = `Θ(V³)`. ∎

**Step 4 — why in-place works (formal).** Suppose during pass `k` the update
`D[i][k] ← min(D[i][k], D[i][k] + D[k][k])` were to change `D[i][k]`. It changes only if
`D[k][k] < 0`. And `D[k][k] < 0` means a negative closed walk through `k`, hence a negative cycle.
Excluding that, `D[i][k]` and `D[k][j]` are frozen during pass `k`, so the single array
simultaneously serves as `D_{k−1}` (for the `[i][k]`, `[k][j]` reads) and `D_k` (for the `[i][j]`
write). ∎

**Step 5 — the exact meaning of `D[i][i] < 0`.** With `D_{∅}[i][i] = 0`, `D_k[i][i]` is the minimum
weight of a *non-empty* closed walk through `i` with internals in `{0..k}`. Negative ⟹ a negative
cycle ⟹ `min` over all `s→t` paths is `−∞` (traverse the cycle `k` times before departing).
So FW both *detects* and *diagnoses*: `D[i][i] < 0` names a vertex on a negative cycle.

## 2. FW on a DAG: Why `O(V·E)`

Fix a topological order `≺`. For `i ≺ j`, every internal vertex of any `i → j` path satisfies
`u ≺ j` (a path moves forward in the order). Hence processing vertices in topological order and
relaxing **forward only**:

```
for j in topo order:
   for each edge (i, j) with i ≺ j:
       for each edge (j, k):
           D[i][k] = min(D[i][k], D[i][j] + w(j,k))
```

Total = `(number of edges) × (max in-degree)` = `O(V·E)`. Better formulation: for each `i`,
a single forward DAG relax in topo order costs `O(V + E)`, so APSP is `O(V(V+E)) = O(V·E)` when
`E = Θ(V)`. **Same output as FW, cheaper, because acyclicity collapses the `V` layers into one
topological pass.** This is why DAG shortest-path tooling is `O(V+E)` per source rather than
`O(V·E)` per source.

## 3. Transitive Closure and Bitsets

Closure: `R[i][j] = R[i][j] ∨ (R[i][k] ∧ R[k][j])`, `Θ(V³)` booleans.
Bitset version: represent row `i` as `⌈V/64⌉` words.

```
for k in 0..V-1:
  for i in 0..V-1:
    if R[i].test(k):
      R[i] |= R[k]          // ⌈V/64⌉ word ORs, not V boolean ops
```

Time `Θ(V² · ⌈V/64⌉) = Θ(V³/64 + V²) = Θ(V³)` with a `1/64` constant. Honest framing: a
**64× reduction in operation count** (plus vectorisation), not an asymptotic one. In practice the
measured speedup exceeds 64× because boolean→word operations also remove branch mispredictions
and allow SIMD.

For `V = 3000`: `2.7·10^10` boolean ops (~10–15 s) vs `⌈3000/64⌉ = 47` words × `9·10^6` pairs =
`4.2·10^8` word ops (~0.15 s).

## 4. Johnson's Reweighting: Full Algebra

### 4.1 Existence of a valid potential
Add `s'` with `w(s', v) = 0` for all `v`. If there is no negative cycle in `G`, then
`h(v) = dist(s', v)` is finite for all `v`. Because `s'` reaches `v` directly at cost 0 and `h` is
a *minimum*, `h(v) ≤ 0` for all `v`.

### 4.2 Feasibility: `w'(u,v) ≥ 0`
The walk `s' → u → v` has weight `0 + w(u,v) = w(u,v)`, so
`h(v) ≤ h(u) + w(u,v)`, giving `w'(u,v) = w(u,v) + h(u) − h(v) ≥ 0`. ∎
Conversely, if any `w'(u,v) < 0` then `h` was not a valid potential (BF produced garbage, or a
negative cycle exists). **So `w' ≥ 0` is both a proof and a runtime assertion.**

### 4.3 Telescoping (the core identity)
For a path `P = (p₀, …, p_k)`:

```
w'(P) = Σ_{t=0}^{k−1} w'(p_t, p_{t+1})
      = Σ_{t=0}^{k−1} w(p_t, p_{t+1}) + Σ_{t=0}^{k−1} h(p_t) − Σ_{t=0}^{k−1} h(p_{t+1})
```

The second and third sums share `h(p₁) … h(p_{k−1})` and cancel:

```
      = w(P) + h(p₀) − h(p_k)
```

Define the **reduced cost** `π(s,t) = h(s) − h(t)`. Then `w'(P) = w(P) + π(s,t)`, so

```
argmin over s→t paths of w'(P)  =  argmin over s→t paths of w(P)
```

and

```
w'(P*) = w(P*) + π(s,t)   ⟹   w(P*) = w'(P*) − π(s,t) = w'(P*) + h(t) − h(s)
```

∎ **Every path gets the same constant boost. Minimisation is invariant.**

### 4.4 Cost
- `h` via BF: `Θ(V·E)`.
- Reweighting: `Θ(E)`.
- `V` Dijkstras on `w'`: `Θ(V·(V+E) log V)`.
- Correction pass: `Θ(V²)`.
- Total `Θ(V·E + V·(V+E) log V)`. With `E ≥ V−1`: `Θ(V·E log V)`.

**Comparison against FW:** `V·E log V < V³ ⟺ E log V < V² ⟺ E < V²/log V`.
At `V = 10^5, log V ≈ 17`: Johnson wins when `E < 5.9·10^8`, i.e. **any sparse graph.**
At `V = 10^3, log V ≈ 10`: Johnson wins when `E < 10^5` — with `V² = 10^6`, so only genuinely
sparse graphs. **Johnson is the sparse-all-pairs algorithm; FW is the dense one.**

## 5. Dijkstra's Complexity Variants

Per source on a graph with `E = Θ(V log V)` (sparse, random):
- Binary heap: `Θ((V+E) log V) = Θ(V log² V)`
- d-ary heap, `d = V^(1/m)`: `Θ(E + V log V)` → APSP `Θ(V·E + V² log V)`
- Fibonacci heap: `Θ(E + V log V)` amortised → same

For a random graph with average degree `d̄`, `E = Vd̄/2`. Per source: `Θ(V log d̄ · log V)` for a
binary heap (heap size `Θ(d̄)`). APSP: `Θ(V² log² d̄ · log V)`. Compare to FW's `Θ(V³)`:
Dijkstra-from-each-source wins iff `log² d̄ · log V < V`, essentially always for real sparse graphs.

## 6. A\* and the `w''` Reduction

Consistency `h(u) ≤ w(u,v) + h(v)` rearranges to `w(u,v) + h(v) − h(u) ≥ 0`. Define

```
w''(u,v) = w(u,v) + h(v) − h(u)   ≥ 0
```

Then, by the same telescoping identity as Johnson's, for any `s → t` path,
`w''(P) = w(P) + h(t) − h(s)` — again a constant per pair. Running **Dijkstra with key `f = g + h`**
is exactly Dijkstra on `w''` with key `g` shifted by `h(s)`, because
`f(n) = g(n) + h(n)` and `h` is constant along the search. Since `w'' ≥ 0`, Dijkstra's
settled-once argument applies verbatim: each node is expanded at most once, `O(E + V log V)`.
∎

**Admissible-only `h`:** `h ≤ h*` does **not** imply `w'' ≥ 0`, so `f` can *decrease* along an edge,
so a settled node can later be improved and re-expanded. The worst case is the number of simple
`s → t` paths, up to `Θ((V−2)!)`-scale in dense graphs. Practically: admissible-only `h` is a
correctness-only guarantee.

## 7. Lower Bounds

- **Output-size lower bound:** APSP must produce `Θ(V²)` numbers, so `Ω(V²)` is unavoidable. Any
  `o(V²)` APSP algorithm can only be a *query* algorithm (e.g. Hub Labels), not a precomputation.
- **Seidel (undirected, unweighted):** `O(V^{2.58})`, beating `V³`.
- **Randomised sparse APSP (Chan, 2010):** `O(V² log V)` expected — essentially optimal up to `log`.
- For a general sparse weighted graph, the conjectured optimum is `O(V² polylog V)`; no
  `o(V²)` precomputation algorithm is known, and none is expected.

## 8. Arithmetic in Practice

- `long` max ≈ `9.22·10^18`. A path with `10^5` edges of weight `10^9` totals `10^14` — fine.
- Use `INF = Long.MAX_VALUE / 4 ≈ 2.3·10^18` so `INF + w` (with `|w| ≤ 10^9`) cannot overflow.
- Johnson potentials `h ≤ 0` can be as large in magnitude as `V · |w|max` ≈ `10^14`; reweighted
  values `w' = w + h(u) − h(v)` stay bounded by `2·V·|w|max + |w|max` — still far from `long`
  overflow for realistic parameters. **For adversarial input (`w = −10^15` on a `10^3`-vertex
  path) use `BigInteger` or check for overflow explicitly.**

## 9. Summary

| Method | Time | Space | Negative `w` | Negative cycles |
|--------|------|-------|--------------|-----------------|
| FW | `Θ(V³)` | `Θ(V²)` | yes | detects (`D[i][i]<0`) |
| FW on DAG | `Θ(V·E)` | `Θ(V²)` | yes | impossible |
| Bitset closure | `Θ(V³/64)` ops | `Θ(V²/64)` words | n/a | n/a |
| `V ×` Dijkstra | `Θ(V·E log V)` | `Θ(V²)` | **no** | never reported |
| Johnson | `Θ(V·E log V)` | `Θ(V²)` | yes | BF reports |
| A\* per query | `O(E + V log V)` | `O(V + E)` | no | never reported |