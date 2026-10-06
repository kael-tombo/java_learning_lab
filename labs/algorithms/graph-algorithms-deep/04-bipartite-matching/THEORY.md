# THEORY — Bipartite Matching

## 1. Definitions

A graph `G = (V, E)` is **bipartite** if `V = U ⊔ V'` (a disjoint union) and every edge has one
endpoint in each part. Equivalently, `G` is 2-colourable.

A **matching** `M ⊆ E` is a set of edges with pairwise disjoint endpoints. Write `ν(G) = max|M|`.

- **Maximum matching:** largest possible size.
- **Perfect matching:** matches every vertex. Exists only if `|V|` is even (and needs `ν = |V|/2`).
- **Maximum *weight* matching:** maximises `Σ w(e)` — a different problem, needs different tools.

The two structural facts that make bipartite matching tractable:
1. **No odd cycles.** This is what makes alternating-path reasoning clean (see §5).
2. **Every vertex has a well-defined side.** Algorithm state can be split by side.

## 2. Augmenting Paths

Let `M` be a matching. An `M`-**alternating path** alternates between edges *in* `M` and edges
*not in* `M`:

```
v₀ -[∉M]- v₁ -[∈M]- v₂ -[∉M]- v₃ -[∈M]- ... -[∈M]- v_{k-1} -[∉M]- v_k
```

It is **augmenting** if `v₀` and `v_k` are both unmatched (`M`-free). Symmetrically, the first and
last edges are outside `M` and the interior edges are inside `M`.

**The augmenting move.** Given an augmenting path `P = (v₀, …, v_k)`:
```
M' = M △ (E(P))
```
(`△` = symmetric difference — remove the `M`-edges of `P`, add the non-`M` edges of `P`.)
Then `M' ∪ M` is a matching and `|M'| = |M| + 1`. *Proof:* the interior vertices of `P` each lose
one `M`-edge and gain one non-`M`-edge; the endpoints each gain one. No endpoint collides. ∎

## 3. Berge's Theorem

> **Theorem (Berge, 1959).** A matching `M` is maximum **if and only if** there is no augmenting
> path with respect to `M`.

**Proof (⇒ direction contrapositive).** If `M` is not maximum there exists `M'` with
`|M'| > |M|`. Consider `M △ M'`, which decomposes into connected components, each of which is:
- an **alternating even cycle**, or
- an alternating **even path** with both endpoints unmatched in `M` only (`M'`-alternating),
- an alternating **odd path** with one endpoint `M`-free and the other `M'`-free,
- an isolated vertex.

Since `|M'| > |M|`, some component contributes more edges to `M'` than to `M`. That component must be
a path starting *and* ending with an `M'`-edge, i.e. a path whose endpoints are unmatched in `M` and
whose edges alternate starting and ending outside `M` — exactly an **augmenting path** for `M`. ∎

**Proof (⇐ direction).** If `M` is not maximum then by the above there is an augmenting path. So
"no augmenting path" ⟹ maximum. (This direction is the contrapositive of the same argument.) ∎

**Key consequence:** the algorithm shape is now clear. Start with `M = ∅` (or greedy); repeatedly
find an augmenting path and augment. Terminate when none exists. This is Ford–Fulkerson's shape
applied to matching — and the `O(E√V)` improvement comes from finding *many* augmenting paths per
layer, exactly as Dinic batches augmentations per level graph.

## 4. Kuhn's Algorithm (the baseline)

```
M = ∅
for each u in U:
    seen[] = fresh          // MUST be reset for every u
    if dfs(u):  |M|++
dfs(u):
    if seen[u]: return false
    seen[u] = true
    for v in adj[u]:
        if matchR[v] == -1 or dfs(matchR[v]):
            matchR[v] = u
            return true
    return false
```

**Correctness.** `dfs(u)` succeeds iff an augmenting path starting at (the new) free left vertex `u`
exists (standard DFS reachability in the alternating structure). Processing every `u` once: after
processing `u_1..u_k`, `M` is maximum **on the subgraph induced by `{u_1..u_k} ∪ V'`** — an
induction using Berge restricted to that subgraph. After all `u`, `M` is maximum on `G`. ∎

**Complexity.** `|U|` DFS searches, each `O(E)` ⇒ **`O(V·E)`**. Each search visits each left vertex
at most once (via `seen[]`) and scans each adjacency list at most once.

**The `seen[]` reset is essential.** Without it, `dfs` short-circuits across different starting
vertices and the algorithm returns non-maximal matchings — silently.

## 5. Why Bipartite Is Special

Consider the alternating structure of a general (non-bipartite) graph. Start an alternating walk
at an unmatched vertex. The sequence of "in-`M` / not-in-`M`" edges determines where you can go.

**In a bipartite graph**, the walk stays on alternating sides: starting at a free `u ∈ U`, the path
`u →(∉M) v ∈ V' →(∈M) u' ∈ U → ...` always has `U`-vertices at even indices and `V'`-vertices at
odd indices. It can only end at a free `V'`-vertex, and any odd cycle would require returning to
the same side — impossible in a bipartite graph. **So an augmenting path always has a clean
"free left → free right" shape and parity is fixed.**

**In a general graph**, the walk can return to the same side, and an **odd cycle** can appear in
the middle of what would be an augmenting path. Even though the path itself is simple (odd cycles
in a path would be separate), the *blossom* structure — an odd cycle reachable from an
alternating tree root — breaks the simple "free start → free end" reasoning. Concretely: an
augmenting path might need to pass through `u₀ ∈ U`, `v₁ ∈ V'`, `u₂ ∈ U`, `v₃ ∈ V'`, `u₁ ∈ U` —
returning to `U` — which in a bipartite graph is impossible.

**Blossom algorithms (Edmonds, 1965)** handle this by *contracting* odd alternating cycles
("blossoms") into single vertices, recursively solving, then *expanding* to recover which edges
belong to the matching. The recursion makes the algorithm `O(V³)`.

## 6. Hopcroft–Karp: `O(E√V)`

**Layering.** Let `F` = the set of unmatched vertices of `U`. BFS from all of `F` in the alternating
structure, computing `dist[u]` for each left vertex (the number of `M`-edges traversed so far).
Left vertex `u` is *free-reaching* if `dist[u] = 0`; vertex `v ∈ V'` at alternating depth `d` is
*nearest* if `dist[matchR[v]] = d+1`; `t` is *nearest* if `matchR[v] = -1`.

**Phase.** Find a maximal set of **vertex-disjoint shortest augmenting paths** using a DFS that
follows only `dist`-increasing edges and **deletes used vertices from the layers**.

**Why `O(√V)` phases.** Let `√V` phases have run. Standard argument: either (a) the remaining
augmenting path has length `> √V`, or (b) at least `√V` vertex-disjoint augmenting paths remain.
Either way, the total remaining increase is `O(√V)` — hence `O(√V)` more phases. Total
`O(√V · E) = O(E√V)`. ∎

**Equivalence to Dinic.** Build the flow network (`s→u` cap 1, `u→v` cap 1 per edge, `v→t` cap 1).
- BFS on the residual graph = HK's layering BFS (levels measured in matched/unmatched arc pairs).
- Blocking flow = maximal set of vertex-disjoint shortest augmenting paths.
- The network is a **unit network**, so Dinic's `O(E√V)` theorem applies verbatim.

**So "use Dinic for bipartite matching" and "use Hopcroft–Karp" are the same algorithm with
different constant factors.** HK wins on constants because it avoids the generic machinery.

## 7. König's Theorem

> **Theorem (König, 1936).** In a bipartite graph `G`, `max matching size = min vertex cover size`.

Recall a **vertex cover** is a set `C ⊆ V` with at least one endpoint in `C` for every edge.
(In a general graph `τ(G) ≥ ν(G)` — König's theorem says equality holds for bipartite graphs, and
it is **false** in general: a triangle has `ν = 1` but `τ = 2`.)

### Proof via max-flow min-cut
Build the standard reduction. Let `M` be maximum, `f` the induced flow with `|f| = |M|`, and
`(S, T)` the min cut.

**Step 1: every `u ∈ U ∩ S` is unmatched.** If `u` were matched, `f(s,u) = 1`, so
`res(s,u) = 0`, so `u ∉ S` (not residual-reachable from `s`). Contrapositive: `u ∈ U ∩ S ⟹ u` unmatched. ∎

**Step 2: every `v ∈ V' ∩ T` is unmatched.** If `v` were matched, `f(v,t) = 1`, so `res(v,t) = 0`
and `res(t,v) = 1`, meaning `t` has residual capacity *into* `v`. But that is about `t`, not `v`.
Correct argument: if `v` is matched to `u` then `f(u,v) = 1` and `f(v,t) = 1`. Conservation at `v`
forces `f(v,t) = 1 > 0`, hence `res(t,v) ≥ 1`. Since `t ∉ S` (max flow), `res(t,v) > 0` does not
put `v` in `S`. Now: if `v ∈ S`, then the arc `v→t` crosses the cut (`v ∈ S, t ∈ T`), but all `δ⁺`
arcs are saturated and carry `1`, so `f(v,t) = 1`; conservation then gives `f(u,v) = 1`, and the
arc `s→u` carries `1`, so `res(s,u) = 0` so `u ∉ S`; but `u → v` is a cut arc with `u ∉ S, v ∈ S`,
i.e. `δ⁻(S)`, and all `δ⁻(S)` arcs carry zero flow — contradiction. Hence `v ∉ S`, i.e. `v ∈ T`. ∎

Hmm — Step 2 as written needs care. The clean version: **if `v ∈ V' ∩ S`, then `v` is matched.**
Proof: `v ∈ S` means residual-reachable. If `v` were unmatched, `res(v,t) = 1 > 0`, so `t` would
be reachable from `v` — but `t ∉ S`. Contradiction. So `v` matched. Equivalently,
**unmatched `v` implies `v ∈ T`**. ∎

**Step 3: the cover.** Set `C = (U ∩ T) ∪ (V' ∩ S)`.
- *It covers every edge:* take an edge `(u, v)`. If `u ∈ U ∩ S`, then by Step 1's contrapositive... —
  more directly: if neither endpoint were in `C`, then `u ∈ S` and `v ∈ T`, so `(u,v) ∈ δ⁺(S)`, so
  `f(u,v) = c(u,v) = 1`; conservation at `u` then gives `f(s,u) = 1` so `u` is matched, and `u ∈ S`
  with `f(s,u) = 1` means `res(s,u) = 0`, contradicting `u ∈ S`. ✓
- *Its size is `|M|`:* conservation at the cut boundary gives
  `|M| = Σ_{(u,v) ∈ δ⁺(S), u∈U} f(u,v) + Σ_{v ∈ V'} f(v,t) − [arcs T→S]`
  and since `δ⁻(S)` flows are zero,
  `|M| = (number of matched `v` in `T`) + (number of saturated `s→u` with `u ∉ S)`
       = |V' ∩ S ∩ matched| + |U ∩ T ∩ matched|
       = |V' ∩ S| + |U ∩ T| = |C|`
  (using Steps 1–2: matched vertices of `U` are exactly `U ∖ S`, and matched vertices of `V'` are
  exactly `V' ∩ S`.) ∎

## 8. Minimum Weight Matching

Different problem: maximise `Σ w(e)` subject to matching constraints.

### 8.1 Bipartite — Hungarian algorithm
Given a cost matrix `c[i][j]` (`n × n`, `n` on each side), find a perfect matching minimising total
cost. `O(n³)` time (dense), `O(n²)` space.

The classical implementation maintains a dual solution (`u[i]`, `v[j]` potentials) satisfying
**complementary slackness**: for every matched `(i,j)`, `u[i] + v[j] = c[i][j]`; for every
unmatched `(i,j)`, `u[i] + v[j] ≤ c[i][j]`. Feasibility (`u[i] + v[j] ≤ c[i][j]`) makes the
potential solution a lower bound on the optimum; complementary slackness makes it exact.
The algorithm maintains an **alternating tree** rooted at the free rows, growing it by relabelling
potentials until a free column is reachable — exactly an augmenting-path search with dual updates.

Jonker–Volgenant's variant uses shortest-path computation on the reduced costs and is the
standard in production assignment solvers (scipy's `linear_sum_assignment`, LAP solvers).

### 8.2 Sparse bipartite — min-cost max-flow
Successive shortest paths with potentials (Johnson) or SPFA gives `O(F·E log V)` where `F` is the
flow value. Preferred when `E ≪ n²`.

### 8.3 General graph — Edmonds' blossom with weights
`O(V³)`. Substantially harder; rarely needed outside specialised solvers.

## 9. General (Non-Bipartite) Matching

**Blossom algorithm (Edmonds).**
```
repeat:
    grow an alternating forest from every unmatched vertex, via BFS on the alternating structure
    whenever an odd cycle (a "blossom") is found, CONTRACT it to a single node and continue
    whenever an even alternating path joins two trees (or reaches another free vertex),
        augment along it
until no augmenting path exists
```
- `O(V³)` time, `O(V²)` space (naive) or `O(E√V)` with Micali–Vazirani's improvement.
- The contraction/unexpansion bookkeeping is the hard part — expansion must decide, using an
  `m`-parity label, which specific edge of each blossom belongs to the matching.

**Tutte's theorem.** `G` has a perfect matching **iff** for every `S ⊆ V`, the number of
odd-order connected components of `G − S` is at most `|S|`.

**Tutte–Berge formula.**
```
ν(G) = ( n − max_{S ⊆ V} o(G − S) ) / 2
```
where `o(G−S)` = number of odd components. The formula is exact but requires maximising over
`2^n` subsets — informative, not algorithmic.

## 10. Dulmage–Mendelsohn Decomposition

The bipartite graph decomposes into four regions based on alternating reachability from free
vertices:
- **D** (deficient) — reachable from a free `U` vertex via `U→V`
- **A** (allowed) — reachable from a free `V` vertex via `V→U`
- **C** (constrained) — reachable from `D`
- **B** (balanced) — everything else

This tells you **which vertices can be unmatched in some maximum matching** (exactly `D ∪ A`),
which is the foundation of scheduling and of "which courses can be left without a timetabling
conflict" style analyses. Computable in `O(E)`.

## 11. Complexity Landscape (2026 view)

| Method | Bound |
|--------|-------|
| Hopcroft–Karp | `O(E√V)` |
| Blossom | `O(V³)` |
| Micali–Vazirani | `O(√V·E)` (deterministic); randomised `O(m√n log n)` |
| Matching via matrix multiplication | `O(n^{ω}) ≈ n^{2.37}` |
| **Conjectured optimum** | `O(n^{2+ε})` — polynomial, and matching is likely the easiest such problem |

Bipartite matching sits at `O(E√V)` while general matching can be done in `O(n^{2.37})` — so the
"harder" problem has the *better* worst-case asymptotic bound, because general matching includes
bipartite matching and the `n^{2.37}` bound holds for the harder problem. **Asymptotic worst-case
bounds do not track perceived difficulty.**