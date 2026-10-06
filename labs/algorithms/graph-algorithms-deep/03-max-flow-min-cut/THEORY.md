# THEORY — Max-Flow / Min-Cut

## 1. Definition

A **flow network** is a directed graph `G = (V, E)` with a capacity `c(u,v) ≥ 0` on each arc, and
two distinguished vertices `s` (source) and `t` (sink).

A **flow** `f` assigns `f(u,v)` to each arc such that:
1. **Capacity constraint:** `0 ≤ f(u,v) ≤ c(u,v)`
2. **Conservation:** for every `v ∉ {s, t}`, `Σ_{u} f(u,v) = Σ_{u} f(v,u)`

The **value** is `|f| = Σ_v f(s,v) − Σ_v f(v,s)`.

The **cut** `(S, T)` is a partition of `V` with `s ∈ S`, `t ∈ T`. Its capacity is

```
cap(S, T) = Σ_{u ∈ S, v ∈ T} c(u,v)
```

Only arcs **from `S` to `T`** count. Arcs from `T` back to `S` are irrelevant — which is why the
theorem is about a *directed* cut even for undirected input (where each edge gets capacity in
both directions).

## 2. Weak Duality (the fundamental inequality)

**Theorem.** For every flow `f` and every cut `(S, T)`, `|f| ≤ cap(S, T)`.

*Proof.* Let `δ⁺(S) = {(u,v) ∈ E : u ∈ S, v ∈ T}`.
Write
```
|f| = Σ_{u∈S} Σ_{v∈V} f(u,v) − Σ_{u∈S} Σ_{v∈V} f(v,u)
    = Σ_{(u,v) ∈ δ⁺(S)} f(u,v) − Σ_{(u,v) ∈ δ⁻(S)} f(u,v)
```
where `δ⁻(S) = {(u,v) ∈ E : u ∈ T, v ∈ S}`. The interior arcs cancel because every `v ∈ S\{s}`
has equal in- and out-flow (conservation), and `s`'s imbalance *is* `|f|`.

Drop the (non-positive) `δ⁻(S)` term:
```
|f| ≤ Σ_{(u,v) ∈ δ⁺(S)} f(u,v) ≤ Σ_{(u,v) ∈ δ⁺(S)} c(u,v) = cap(S,T)
```
using the capacity constraint in the second step. ∎

**Why this is the whole theory.** It says: no flow can ever exceed any cut. So
`max_f |f| ≤ min_(S,T) cap(S,T)`. All that remains is to prove equality.

## 3. Residual Graphs

For a flow `f`, the residual graph has the arcs

```
res(u,v) = c(u,v) − f(u,v) + f(v,u)
```

`c(u,v) − f(u,v)` is the **forward residual**: how much more can be pushed. `f(v,u)` is the
**backward residual**: how much can be cancelled. If `u → v` and `v → u` are both arcs of the
original network, `res(u,v) = c(u,v) − f(u,v) + f(v,u)` accounts for both.

**Representation in code:** store only the forward arcs, but give each arc an `initialCapacity`
and maintain `capacity = initialCapacity − flow`. Then
`res(u,v) = capacity` and `res(v,u) = flow`, which is exactly the formula. Pushing `δ` forward:
`capacity -= δ; flow += δ; capacity_rev += δ; flow_rev -= δ`.

**Invariant.** A residual graph with no `s → t` path certifies optimality. Combined with weak
duality: if `f` is a flow and `(S,T)` is the set reachable from `s` in the residual graph, then
`cap(S,T) = |f|`, so by weak duality `f` is maximum **and** `(S,T)` is minimum. **That is the
max-flow min-cut theorem, proved.**

## 4. Augmenting Path Algorithms

```
residual R = residual graph of the current flow f
while R has an s→t path P:
    δ = min over (u,v) in P of res(u,v)
    push δ along P; update f and R
```

**Correctness of one step.** Pushing `δ ≤ min res` keeps every capacity constraint satisfied;
`P` is a simple `s→t` path, so conservation is preserved at all internal vertices (one unit in,
one unit out); `|f|` increases by exactly `δ`. ∎

**Termination and optimality.** Each augmentation increases `|f|` by `δ ≥ 1` (integer capacities)
and `|f| ≤ min cut`, so the loop terminates in at most `(min cut)` iterations. On termination,
`(S,T)` = residual-reachable set from `s` is a cut, no residual `s→t` path crosses it, so
`cap(S,T) = |f|` by the invariant above; weak duality then forces `|f| = min cut`. ∎

### 4.1 Ford–Fulkerson — and why it is dangerous
Any path works. Complexity `Θ(E·|f*|)`. With capacities in *bits*, `|f*|` can be `2^b`, so this is
**exponential in the input size**.

**The classic counter-example** (`s→a = 1, s→b = 2, a→b = 1, b→t = 2, a→t = 2`, DFS always
picks `s→a→t`): push 1, then `s→b→t` push 2 → total 3 (optimum is 3, fine). Modify so the first
path is bad: `s→a=1, a→t=1; s→b=1, b→t=1; a→b=1`. DFS picks `s→a→t` (1), then `s→b→t` (1) — total 2,
optimum 2. Now the real trap: `s→a = 1, a→t = 1, s→b = 1, b→a = 1, a→t = 2`. Push 1 on
`s→a→t`. Now `a→t` is saturated, so the next DFS goes `s→b→a→t` but `a→t` has no residual — must
**backtrack via the residual arc `t→a`?** No: it must use the residual arc `a→s`. Correct FF needs
the backward residual to undo the first choice. Get this right and FF is correct; **get it wrong
and FF returns a non-maximal flow with no error.**

### 4.2 Edmonds–Karp — shortest (fewest-edges) paths
BFS finds the path with the fewest arcs. The classic bound: after each BFS phase, the shortest
residual path length **increases**, so there are at most `V−1` phases; each phase costs `O(V·E)`
(worst case for all augmentations) ⇒ **`O(V·E²)`**. Polynomial in the input size — this is the
result that made max-flow a respectable tool.

### 4.3 Dinic — level graphs and blocking flows
```
while (level = BFS(residual)) has level[t] < INF:
    it[] = 0 for all vertices
    while (pushed = dfs(s, INF)) > 0: ;      // current-arc DFS finds a blocking flow
```
- **Level graph:** arcs with `level[v] = level[u] + 1` and `res(u,v) > 0`. Every `s→t` path in it
  has exactly `level[t]` arcs.
- **Blocking flow:** a flow with **no** `s→t` path in the level graph.
- **Current-arc pointer `it[]`:** each arc is examined at most once per phase except when it is
  re-examined after gaining residual capacity (back-arcs to the same level), giving the `O(VE)`
  per-phase bound.

**Why `O(V)` phases:** after a blocking flow, the residual graph has no `s→t` path using only
level-`level[t]` arcs; the next BFS must therefore produce `level[t] > ` the previous value. Since
`level[t] ∈ [1, V−1]`, at most `V−1` phases. `O(V·VE) = O(V²E)`. ∎

**Practical bound.** Dinic runs in roughly `O(E)` time per phase on typical networks, and the phase
count is usually tiny (2–5), giving near-linear practical performance.

**Special cases:**
- **Unit capacities** (every `c(u,v) = 1`): augmentations per phase `≤ E`, and total augmentations
  `≤ √V·E`, giving **`O(E√V)`**.
- **Unit networks** (each vertex except `s,t` has exactly one incoming or one outgoing arc of
  capacity 1): also `O(E√V)`. **This covers bipartite matching**, which is why Dinic matches
  Hopcroft–Karp.

## 5. Push–Relabel

Push–relabel reverses the perspective: instead of building flow from nothing, it starts with a
**pre-flow** `|f|` artificially large and "returns" the excess to `s`.

State per vertex: `height h(v)`, `excess e(v) ≥ 0`, and residual capacities. Validity condition:
`h(s) = V`, and every residual arc `(u,v)` satisfies `h(u) ≤ h(v) + 1` (a *valid height function*).

```
h(s) = n; all other h = 0
for all (s,v): push saturating amount, e[v] += c, e[s] -= c
while ∃ v ≠ s,t with e(v) > 0:
    discharge(v):
      while e(v) > 0 and v has an admissible arc (res>0 and h(v) = h(res_neighbour)+1):
          push δ = min(e(v), res(u,v))
      if e(v) > 0:
          relabel(v) = min over residual neighbours of (h(neighbour) + 1)
          current[v] = first neighbour
```

**Termination.** Relabelling raises `h(v)`; validity bounds `h(v) ≤ 2V−1`, so each vertex relabels
`O(V)` times, and each relabel costs `O(deg(v))`. Total `O(V·E)`. Pushes: an argument using a
potential function gives `O(V²E)`.

**Why push–relabel wins in practice on huge instances:** three heuristics.
- **Highest-label rule:** discharge the vertex with maximum `h` first. Reduces "wasted" work on
  short paths to the sink.
- **Gap heuristic:** if no vertex has height `k`, then no vertex can have height `> k` either
  (validity propagates). Reset all heights `> k` to `V+1` and mark those nodes unreachable —
  they can never reach `t`, so drop them entirely. This is the single biggest practical win.
- **Global relabel:** every `Ω(E)` operations, run one reverse BFS from `t` to recompute exact
  distances and reset heights and current-arc pointers. Dramatically improves locality.

**Empirical note:** on dense graphs push–relabel with highest-label + gap + global relabel beats
Dinic by 1–2 orders of magnitude for `V > 10^4`. The reason is structural: Dinic's BFS phases
touch the whole graph, while push–relabel's relabels are local until global relabel resynchronises.

**Blocking-flow view:** an equivalent formulation pushes a whole blocking flow from `v` before
moving on, which is "FIFO push–relabel". It has better theoretical guarantees but similar practice.

## 6. Min Cut Extraction

After any max flow `f`:
1. Build the residual graph.
2. BFS/DFS from `s` over residual arcs with `res > 0`.
3. `S` = reached vertices; `T = V∖S`.
4. `(S, T)` is a **minimum** cut, and the min cut consists of the original arcs
   `(u,v)` with `u ∈ S, v ∈ T`.

**Why it's minimum (proof).** Because `s ∈ S` and `t ∈ T`, `(S,T)` is a legal cut. Every
`δ⁺(S)` arc is *saturated* — if `(u,v) ∈ δ⁺(S)` had `res(u,v) = c − f + f(v,u) > 0`, then `v`
would be reachable from `u ∈ S`, contradiction. And every `δ⁻(S)` arc has zero flow — if
`f(u,v) > 0` for `(u,v) ∈ δ⁻(S)` then `res(v,u) > 0` and `v ∈ S` would make `u ∈ S`, contradiction.
Therefore
```
cap(S,T) = Σ_{δ⁺} c(u,v) = Σ_{δ⁺} f(u,v) = |f|
```
(the middle equality by conservation). Weak duality gives `min cut ≥ |f|`, so `|f| = min cut`. ∎

## 7. Reductions

### 7.1 Bipartite matching
`G = (U ∪ V, E)` bipartite. Build `s → u` with `c = 1` for each `u ∈ U`; `u → v` with `c = 1`
for each edge; `v → t` with `c = 1` for each `v`. Then `max flow = maximum matching size`, and an
integral flow decomposes into `|f|` paths `s → u → v → t`, one per matched pair. **Integrality
matters:** the capacities are integers, so an integral maximum flow exists (and every Dinic
augmentation is integral). Use Dinic ⇒ `O(E√V)`.

### 7.2 Minimum vertex cover (König's theorem)
For bipartite graphs, `min vertex cover size = max matching size`. Given a max flow `f` and the
min-cut `(S,T)`:
```
cover = (U ∩ T) ∪ (V ∩ S)
```
**Verification.** No edge `(u,v)` has both endpoints outside the cover: if `u ∈ S` and `v ∈ T`,
the arc `u → v` would cross the cut uncrossed — impossible since all `δ⁺` arcs are saturated and
all carry 1 unit. ✓ And `|cover| = |max flow|` by conservation. ∎

### 7.3 Edge-disjoint and node-disjoint paths
- **Edge-disjoint:** give each edge capacity 1. Max flow = maximum number of edge-disjoint
  `s → t` paths (Menger's edge version, via flow integrality).
- **Node-disjoint:** split each internal `v` into `v_in → v_out` with capacity 1 and rewire all
  incoming arcs to `v_in` and all outgoing from `v_out`. Menger's vertex version.

### 7.4 Gomory–Hu trees
`V−1` max-flow computations produce a **tree** `T` on `V` whose edge `s–t` has weight equal to the
minimum `s–t` cut in the original graph. Any min `a–b` cut can then be read off by a single
`O(V)` tree traversal. For **undirected** graphs, this is exactly "answer all `V²/2` min-cut
queries in `V−1` max-flows".

**Gomory–Hu construction sketch:** compute `f_i` = max flow between `i` and parent(`i`); let
`(S_i, T_i)` be the min cut; then *swap* `i` and the parent if `i ∈ S_i`, and re-parent every
child whose cut-side matches. The subtle re-parenting step is the entire difficulty.

**Directed graphs:** the cut defined by deleting one edge of the Gomory–Hu tree is a *minimum cut
on undirected versions of the arcs*, not necessarily the directed min cut — a real caveat.

## 8. Complexity Summary

| Algorithm | Time | Dependence on capacities? |
|-----------|------|---------------------------|
| Ford–Fulkerson | `O(E·F)` | **Yes** — pseudo-polynomial |
| Edmonds–Karp | `O(V·E²)` | No |
| Dinic | `O(V²E)` | No |
| Dinic (unit caps) | `O(E√V)` | n/a |
| Push–relabel (generic) | `O(V²E)` | No |
| Push–relabel (FIFO) | `O(V³)` | No |
| Push–relabel + highest label | `O(V²√E)` | No |
| Orlin | `O(VE)` when `V = O(√E)` | No |

All of Edmonds–Karp, Dinic, and push–relabel are **strongly polynomial**: their running time
depends only on `V` and `E`, never on the magnitude of the capacities. This is the whole point of
moving past Ford–Fulkerson.

## 9. Practical Diagnosis

| Symptom | Likely cause |
|---------|--------------|
| Flow value wrong | backward residual arcs not maintained (cancel pushes) |
| Infinite loop | residual not restored on the reverse arc; or `it[]` not advanced on saturation |
| Cut capacity ≠ flow value | cut extracted with `capacity` instead of `initialCapacity` |
| `int` overflow | total flow can exceed `int` — use `long` |
| Slow on dense graphs | use push–relabel with gap + global relabel |
| `∞` capacity given as `Integer.MAX_VALUE` | sum of capacities can overflow; use `long` or `V·maxCap` |

**The `∞` capacity convention:** when a "capacity-`∞`" arc is needed (e.g. "any number of
matchings"), set it to `sum of all other capacities + 1` (or `V · maxFiniteCap`), never
`Integer.MAX_VALUE`. For bipartite matching the right `∞` is `min(|U|, |V|)`, which is tight and
provably never binding.