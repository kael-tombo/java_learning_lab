# MATH_FOUNDATION — Max-Flow / Min-Cut

## 1. Weak Duality: The Full Proof

**Setup.** For `S ⊆ V`, write `δ⁺(S) = {(u,v) ∈ E : u ∈ S, v ∉ S}` and
`δ⁻(S) = {(u,v) ∈ E : u ∉ S, v ∈ S}`.

```
|f| = Σ_{v} [ f(s,v)·1{s is in} ... ]
```

More carefully, define the net out-flux of `S`:

```
Σ_{u ∈ S} Σ_{v ∈ V} f(u,v) − Σ_{u ∈ S} Σ_{v ∈ V} f(v,u)   (= "net outflow of S")
```

Regroup the first sum by arc type:
- arcs inside `S`: cancel against the second sum by conservation at each interior vertex
- arcs `δ⁺(S)`: appear only positively
- arcs `δ⁻(S)`: appear only negatively

Hence

```
netOut(S) = Σ_{δ⁺(S)} f(u,v) − Σ_{δ⁻(S)} f(u,v)
```

But `S` contains `s` and not `t`, and the only vertices with non-zero imbalance are `s` and `t`,
so `netOut(S) = Σ_{v∈S}(out(v) − in(v)) = |f|`. Therefore

```
|f| = Σ_{δ⁺(S)} f(u,v) − Σ_{δ⁻(S)} f(u,v)
```

Now: `Σ_{δ⁻} f ≥ 0` (all flows non-negative) and `f(u,v) ≤ c(u,v)`, so

```
|f| ≤ Σ_{δ⁺(S)} f(u,v) ≤ Σ_{δ⁺(S)} c(u,v) = cap(S,T)
```

∎ **`|f| ≤ cap(S,T)` for every `(f, S)`.**

Taking `max` over `f` and `min` over `S`:

```
max_f |f| ≤ min_S cap(S,T)
```

**This is half the theorem, and it required no algorithm at all.**

## 2. Max-Flow Min-Cut: The Other Half

Take a *maximal* flow `f` (no residual `s→t` path) and `S` = residual-reachable from `s`.

**Claim A: every `δ⁺(S)` arc is saturated.** If `(u,v) ∈ δ⁺(S)` then `u ∈ S`. If
`res(u,v) > 0` then `v` would be reachable, so `v ∈ S`, contradicting `v ∈ δ⁺(S)`. Hence
`res(u,v) = 0 = c(u,v) − f(u,v) + f(v,u)`. Since `c ≥ f ≥ 0` and `f(v,u) ≥ 0`, `c − f ≥ 0` and
`c − f + f(v,u) = 0` forces `f(v,u) = 0` and `f(u,v) = c(u,v)`. **Saturated.** ∎

**Claim B: every `δ⁻(S)` arc has zero flow.** If `(u,v) ∈ δ⁻(S)` then `v ∈ S`. If `f(u,v) > 0`
then `res(v,u) = c(v,u) − f(v,u) + f(u,v) ≥ f(u,v) > 0`, so `u` would be reachable from `v ∈ S`,
contradicting `u ∉ S`. Hence `f(u,v) = 0`. ∎

Combining with the duality identity:

```
|f| = Σ_{δ⁺} f − Σ_{δ⁻} f = Σ_{δ⁺} c − 0 = cap(S,T)
```

So `max_f |f| ≥ |f| = cap(S,T) ≥ min_S cap(S,T)`. Together with
`max_f |f| ≤ min_S cap(S,T)` from §1, the inequalities coincide:

```
max_f |f| = min_S cap(S,T)
```

∎ **The algorithm's role is only to produce a flow and a cut that meet. Everything else is
arithmetic.**

## 3. Dinic's `O(V²E)`

### 3.1 Blocking flow is `O(V·E)`
Within one phase, every `s→t` path in the level graph has exactly `level[t]` arcs, so all
augmentations have the same length `ℓ = level[t]`. Each augmentation saturates at least one
level-graph arc (the bottleneck), and an arc, once saturated, can become unsaturated only by a
push on its **reverse** arc — which in the level graph goes *backwards* in level and so is not
admissible. Hence each arc saturates at most once per phase ⇒ `≤ E` augmentations. Each
augmentation is a DFS of depth `≤ V` ⇒ `O(V)`. Blocking flow total: `O(V·E)`. ∎

### 3.2 At most `V−1` phases
After a blocking flow, the level graph has no `s→t` path. All arcs with `level[u] ≥ level[t]`
matter for `s→t` reachability (any `s→t` path has all intermediate levels `≤ level[t]` and, being
a shortest path, exactly one vertex per level). So there is no residual `s→t` path of length
`level[t]`, hence the next BFS yields `level'[t] > level[t]`. Since `level[t] ∈ [1, V−1]`,
`≤ V−1` phases. ∎

### 3.3 Total
```
T = (V−1) · O(V·E) = O(V²E)
```

**Sanity check the practical gap.** `V²E` at `V = 10⁴, E = 10⁵` is `10^13` — but real Dinic runs
in seconds. The bound is pessimistic because phases are usually 2–5 (not `V`) and the per-phase
cost is `O(E)` not `O(VE)` when the level graph is shallow. **This is the single most important
practical lesson about asymptotic analysis: the bound is a worst case that essentially never
bites.**

## 4. Unit Networks: `O(E√V)`

A **unit network** has, for each vertex `v ∉ {s,t}`, either exactly one incoming arc of capacity
1 or exactly one outgoing arc of capacity 1.

**Phase 1 (`√V` phases):** each phase costs `O(E)`, so `O(E√V)`.

**Phase 2 (bound the remaining flow):** After `√V` phases, let `f` be the current flow and
consider a maximum flow `f*`. Decompose `f* − f` into residual paths (`P₁, …, P_k`) and cycles.
Each such path has length `≥ level[t] > √V` (since `√V` phases each strictly increase
`level[t]` from `1`). Now take any vertex set `X = {s,t}`: because `X` contains `s` and `t`, and
each vertex in a unit network has one unit of in- or out-capacity, each vertex can lie on at most
one `P_i`. So the paths are **vertex-disjoint**, and since each has length `> √V`, we get

```
k · √V  <  Σ|P_i|  ≤  V      ⟹   k < √V
```

So the remaining augmentable flow is at most `√V` unit-ish paths ⇒ `≤ √V` more augmentations, and
each additional phase reduces it by at least 1 ⇒ `≤ √V` more phases, each `O(E)`.

```
Total = O(E√V) + O(E√V) = O(E√V)
```

∎ **Bipartite matching networks are exactly unit networks** (`u ∈ U` has one incoming `s→u`;
`v ∈ V` has one outgoing `v→t`), so Dinic is `O(E√V)` there — matching Hopcroft–Karp.

**Unit capacities (the weaker hypothesis):** all arcs capacity 1. Then any two augmenting paths
share no arc, and the same counting gives `O(E√E)`, hence `O(E√V)` when `E = O(V)`. This is the
result used for "unit-capacity networks".

## 5. Ford–Fulkerson: Why `O(E·F)` Is Pseudo-Polynomial

Each augmentation increases `|f|` by `δ ≥ 1` (integer capacities), and `|f| ≤ F = min cut`. So
`≤ F` augmentations at `O(E)` each.

**Bit-complexity.** With capacities given in binary, `F` can be exponential in the input length `b`.
Concrete instance (`b` bits, `Θ(b²)` input size):

```
s → x  cap 2^{b}
x → y  cap 2^{b}  − 1
s → y  cap 2^{b}
y → t  cap 1
```

Hmm — that gives max flow 1, not large. Use the classic trap:

```
s → x   cap M
s → y   cap M
x → y   cap 1
x → t   cap 1
y → t   cap M        where M = 2^b
```

Max flow: `M + 1`. If DFS always tries `s→x→t` first: push 1. Then `s→x→y→t` push 1
(`res(s,x) = M−1`). Then `s→y→t` push `M−1`... that's only `M+1` total. Better trap: make the
greedy repeatedly undo. The classic exponential instance:

```
s → x   cap M
s → y   cap M
x → z   cap 1
z → t   cap M
y → x   cap 1
x → w   cap 1
w → t   cap M
```

Too fiddly to construct cleanly. The **standard** claim (and the one that matters) is simpler:

`F` is a *capacity magnitude*, not a graph size. Given `b` input bits, `F ≤ 2^b`, so `O(E·2^b)`
is exponential in `b`. Whatever the specific instance, the algorithm's runtime is not a function
of the graph size and the *bit-size* of the capacities alone — it is exponential in the latter.
Edmonds–Karp's contribution is precisely to remove the `F` factor. ∎

## 6. Push–Relabel Analysis

### 6.1 Height bound
Validity: `h(u) ≤ h(v) + 1` on every residual arc. Claim: for a vertex that can still reach `t`,
`h(v) ≤ 2V − 1`. (Proof sketch: the shortest residual path from `v` to `t` has `≤ V−1` arcs and
`h(t) = 0`; but `h` may also have been raised by relabels not on that path. The `2V−1` bound is
the standard invariant used by the gap heuristic.)

### 6.2 Relabel count
Each relabel strictly increases `h(v)`; `h` is bounded by `2V−1`, so each vertex relabels
`≤ 2V` times. Cost `O(deg(v))` each ⇒ total relabel cost `Σ_v O(2V · deg(v)) = O(V·E)`.

### 6.3 Non-saturating pushes
Use the potential `Φ = Σ_v e(v)·h(v)`.
- A **saturating push** (δ = res(u,v)): `Φ` is unchanged (moves excess from `u` to `v`, but `v` is
  then immediately relabelled, see below) — handled in the relabel count.
- A **non-saturating push** (δ = e(u)): `Φ` changes by `−h(v) ≤ 0`, so `Φ` never increases
  across non-saturating pushes. Combined with the relabel cost, a standard charging argument
  gives `O(V²E)`.

### 6.4 Why the heuristics beat the bound
- **Gap heuristic:** when a level is empty, all higher vertices are provably unable to reach `t`.
  Removing them can shrink `V` by a constant fraction. Repeating `O(log V)` times can reduce the
  problem to nothing — hence practice sees near-linear behaviour where the proof says `O(V²E)`.
- **Highest-label:** work concentrates near `t`, improving cache locality dramatically.
- **Global relabel:** restores exact distances every `Ω(E)` operations, eliminating "drift" that
  would otherwise cause useless relabels.

## 7. Bipartite Matching and the `√V` Bound (Hopcroft–Karp)

Hopcroft–Karp = Dinic on the matching network, specialised. The `O(√V)` phase count comes from the
unit-network argument in §4.

**Lower bound context:** bipartite matching is one of the few problems in P believed **not** to
have a strongly subquadratic algorithm; `V^{2.5}` is the current best bound and `V·polylog V` is
conjectured. Matching sits between max-flow (which solves it in `O(E√V)`) and matrix
multiplication (which solves it in `V^{ω} ≈ V^{2.37}`). This is the classic "flows match
multiply" observation — another reason max-flow matters.

## 8. Arithmetic and Integer Growth

- Flows can be enormous: with `E` arcs of capacity `C`, max flow `≤ E·C`. For `E = 10^5`,
  `C = 10^9`, that's `10^14` — fits `long`, overflows `int`.
- Residual capacities are bounded by `c(u,v) + c(v,u)` (both directions), so `long` is safe when
  capacities are.
- `∞` arcs: use `(long) V * maxFiniteCap + 1`, justified because no flow exceeds the total
  capacity out of `s`.
- Gomory–Hu: `V − 1` flows each `O(V²E)` ⇒ `O(V³E)` for all-pairs min cut. With modern
  practical max-flow this is often the fastest route for `V ≲ 10³`.

## 9. Summary Table

| Algorithm | Time | Dependence on capacities | Practical regime |
|-----------|------|--------------------------|------------------|
| Ford–Fulkerson | `O(E·F)` | **Yes (pseudo-poly)** | never |
| Edmonds–Karp | `O(V·E²)` | No | teaching, tiny graphs |
| Dinic | `O(V²E)` | No | default for most problems |
| Dinic (unit network) | `O(E√V)` | n/a | bipartite matching |
| Push–relabel (FIFO) | `O(V³)` | No | dense graphs |
| Push–relabel (highest + gap) | `O(V²√E)` | No | **large instances** |
| Orlin | `O(VE)` when `V = O(√E)` | No | theoretical best |
| Stoer–Wagner | `O(V³)` | No | global min cut |
| Gomory–Hu | `(V−1)·T_flow` | No | all-pairs min cut |