# QUIZ — Max-Flow / Min-Cut

1. State the capacity constraint and the conservation condition for a flow.
2. State weak duality and explain why it is the key to everything else.
3. Give the residual capacity formula, and explain where the second term comes from.
4. Why are backward residual arcs essential? Give the network where omitting them breaks Ford–Fulkerson.
5. State the max-flow min-cut theorem and outline the proof in two sentences.
6. How do you extract a minimum cut from a finished maximum flow, and what two properties does the extracted cut satisfy?
7. Give Ford–Fulkerson's time complexity and explain why it is *pseudo-polynomial*.
8. State Edmonds–Karp's bound and the structural reason for it.
9. What is a level graph, and what is a blocking flow?
10. Why are there at most `V−1` Dinic phases, and what is the per-phase cost?
11. Give Dinic's complexity on unit-capacity networks and explain which problem it makes fast.
12. What is the residual-graph formulation of the min vertex cover in bipartite graphs (König)?
13. Why does the min-cut capacity sum only arcs from `S` to `T`, never `T` to `S`?
14. State the gap heuristic for push–relabel and explain why it is sound.
15. What is a Gomory–Hu tree, how many max-flow computations does it need, and what is its caveat for directed graphs?

---

## Answers

1. **Capacity:** `0 ≤ f(u,v) ≤ c(u,v)` for every arc. **Conservation:** for every `v ∉ {s,t}`,
   `Σ_u f(u,v) = Σ_u f(v,u)` (total in-flow equals total out-flow). The flow **value** is
   `|f| = Σ_v f(s,v) − Σ_v f(v,s)`; `s` and `t` are the only vertices exempted from conservation
   because their imbalance *is* the value.
2. **Weak duality:** for every flow `f` and every cut `(S,T)` with `s ∈ S, t ∈ T`,
   **`|f| ≤ cap(S,T)`**. *Why it is the key:* it gives `max_f |f| ≤ min_(S,T) cap(S,T)` immediately,
   i.e. a feasible flow and a feasible cut always bound each other. Every algorithm below is
   justified by producing a flow and a cut that **meet** — MFM-cut is then a corollary, not a
   separate theorem. The proof: decompose `|f|` across the cut; interior arcs cancel by
   conservation; the `S→T` term is bounded by `c` and the `T→S` term is `≤ 0`.
3. **`res(u,v) = c(u,v) − f(u,v) + f(v,u)`.** The first term `c − f` is the **forward residual**
   (how much more can be pushed along `u→v`). The second term `f(v,u)` is the **backward residual**
   (how much of the flow already on `v→u` can be cancelled), which becomes available residual
   capacity in the direction `u→v`. When both `u→v` and `v→u` exist in the network, this single
   formula captures both. In code you store `capacity = initialCapacity − flow` per arc, so
   `res(u,v) = capacity[u→v]` and `res(v,u) = flow[u→v]`, and a push updates both directions.
4. **Because a maximum flow may require *cancelling* flow that an earlier augmentation pushed,
   and cancelling is only possible along a residual backward arc.**

   **Clean counter-example (the standard bipartite reduction).** U = {u1,u2}, V = {v1,v2},
   edges u1-v1, u1-v2, u2-v1. Network: s->u1 = 1, s->u2 = 1, u1->v1 = 1, u1->v2 = 1,
   u2->v1 = 1, v1->t = 1, v2->t = 1. The **maximum matching is 2** ({u1-v2, u2-v1}), so
   max flow = 2.

   Greedy takes the first available path s -> u1 -> v1 -> t, pushing 1. Now v1 -> t is saturated.
   A **forward-only** search then finds s -> u2 -> v1 and dead-ends at v1 (no residual forward
   arc to t), so it stops with **flow = 1**, which is *not* maximum.

   With residual backward arcs the augmenting path exists:
   s -> u2 -> v1 -> (backward arc, res = f(u1,v1) = 1) -> u1 -> v2 -> t, pushing 1. Final flow
   = 2 = maximum. Dropping the + f(v,u) term from res(u,v) is exactly what loses this path, and
   the failure is *silent* -- the algorithm reports a valid-looking flow of value 1.

5. **`f* = min cut`**: in every flow network the maximum achievable flow value equals the minimum,
   over all cuts `(S,T)`, of `cap(S,T)`. *Proof in two sentences:* Weak duality gives
   `max flow ≤ min cut`; if `f` has no augmenting residual `s→t` path, let `S` be the vertices
   residual-reachable from `s` — then every `δ⁺(S)` arc is saturated and every `δ⁻(S)` arc carries
   zero flow, so `cap(S,T) = |f|`, hence `min cut ≤ max flow`, and the two inequalities coincide.
6. **BFS/DFS from `s` over arcs with `res > 0`; `S` = reached vertices, `T = V∖S`; the cut is the
   original arcs `(u,v)` with `u ∈ S, v ∈ T`.** Two properties: (i) **every `δ⁺` arc is
   saturated** (`f(u,v) = c(u,v)`) — otherwise `res(u,v) > 0` would make `v` reachable;
   (ii) **every `δ⁻` arc carries zero flow** (`f(u,v) = 0`) — otherwise `res(v,u) > 0` would make
   `u` reachable. Property (ii) is what rules out the second case in weak duality's proof and is
   therefore load-bearing, not cosmetic.
7. **`O(E·|f*|)`** — each augmentation increases the flow by at least 1 (integer capacities) and the
   flow never exceeds the max, so there are `≤ |f*|` augmentations, each `O(E)`.
   **Pseudo-polynomial** because `|f*|` is a *value*, not a size: with capacities given in binary,
   `|f*|` can be `2^b` for `b` input bits, so the algorithm is exponential in the input **bit
   length** while looking polynomial in the numeric capacity. That is the definition of
   pseudo-polynomial. Edmonds–Karp was the result that removed this dependency.
8. **`O(V·E²)`.** BFS finds a residual `s→t` path with the **fewest arcs**, so after each augmentation
   the shortest residual path length (in arcs) **strictly increases**. That length is at most `V−1`,
   so there are at most `V−1` distinct lengths; within one length, at most `O(E)` augmentations
   (each saturates at least one arc, and only `E` arcs exist); each BFS costs `O(E)`.
   `V · E · E = V·E²`. The result is **strongly polynomial** — independent of capacity magnitudes.
9. **Level graph:** the subgraph of the residual graph containing only arcs `(u,v)` with
   `res(u,v) > 0` and `level[v] = level[u] + 1`, where `level[]` comes from a BFS from `s` in the
   residual graph. Every `s→t` path in it has exactly `level[t]` arcs. **Blocking flow:** a flow
   that is valid in the original network and leaves **no** `s→t` path in the level graph — i.e. it
   is maximal within one layer structure. It is found with a current-arc-pointer DFS
   (`while (dfs(s, INF) > 0)`).
10. **At most `V−1` phases** because after a blocking flow, no `s→t` path of length `level[t]`
    remains in the level graph, so the next BFS must produce a strictly larger `level[t]`; and
    `level[t] ∈ [1, V−1]`. **Per phase `O(V·E)`**: within a phase every augmenting path has the
    same length `level[t]`, so at most `O(E)` augmentations occur (each saturates an arc), and each
    is found by a DFS of `O(V)`. Total `O(V · V·E) = O(V²E)`.
11. **`O(E√V)`** for **unit-capacity networks** (and `O(E√V)` for *unit networks*, i.e. every
    vertex except `s,t` has exactly one incoming or one outgoing unit-capacity arc). The argument:
    after `√V` phases, `√V·√V = V` residual augmentations have been applied, and the standard
    vertex-disjointness argument bounds the *remaining* flow by `E/√V`, so at most `√V` more phases
    suffice — total `O(√V)` phases. **This makes bipartite matching fast**, since a matching flow
    network *is* a unit network (`s→u` and `u→v` and `v→t` give each `u` one incoming and each `v`
    one outgoing unit arc). Dinic therefore matches Hopcroft–Karp's `O(E√V)`.
12. **`cover = (U ∩ T) ∪ (V ∩ S)`.** No edge is uncovered: if `u ∈ U ∖ cover` and `v ∈ V ∖ cover`
    then `u ∈ S` and `v ∈ T`, so the arc `u→v` crosses the min cut — but all `δ⁺` arcs are
    saturated with capacity 1, so a saturated cut arc means the edge is in the matching, and
    König's identity `|cover| = |max matching|` closes the argument. Equivalently, an edge
    `(u,v)` in the matching has `f(u,v) = 1`; if it crossed the cut then `v ∈ T` and `u ∈ S`;
    conservation at `u` then forces `u`'s only incoming arc (`s→u`) to be saturated, i.e. `u` is
    matched *away* from `s`… The clean statement: every `u ∈ U ∩ S` is unmatched (its `s→u` arc is
    saturated only if it carries flow, and a saturated `s→u` implies `f(u,v)=0` for all `v`,
    forcing `u ∉ U ∩ S`), and every `v ∈ V ∩ T` is unmatched — so `U ∩ T` and `V ∩ S` together
    contain `|matching|` vertices covering all edges.
13. **Because a cut's capacity is a capacity to *move flow forward***, and only forward arcs can
    increase `|f|`. In the weak-duality proof, `|f| ≤ Σ_{δ⁺} f + Σ_{δ⁻}(−f) ≤ Σ_{δ⁺} f ≤ Σ_{δ⁺} c`;
    the `δ⁻` term appears with a **negative** sign, so it can only *reduce* the bound, and dropping
    it stays valid. Equivalently, flow crossing `T → S` is flow that has left the "downstream" side
    and would have to be re-earned to reach `t`. For undirected input graphs, each edge is modelled
    as **two** arcs of equal capacity, and a cut counts whichever direction goes `S → T` — which is
    why an undirected min cut is `min over partitions of Σ crossing edges` with no sign.
14. **The gap heuristic:** maintain the count `cnt[h] = #{v : height(v) = h}`. If `cnt[h] == 0`
    (a "gap"), then no vertex has height `> h` either — because validity (`h(u) ≤ h(v)+1` on every
    residual arc) means a vertex at height `> h` would need a chain of valid heights reaching down
    to `h`, which must pass through every intermediate level, contradicting the gap. So every vertex
    with `height > h` can never reach `t`, and may be reset to `V+1` and removed from further
    consideration. **Sound** because it only prunes vertices provably unable to send flow to `t`;
    it never removes a vertex that participates in the optimum, and it preserves validity (moving
    a vertex *up* to `V+1` keeps `h(u) ≤ h(v)+1` for arcs into it, since `V+1` is maximal).
    It is the single biggest practical speedup for push–relabel.
15. **A Gomory–Hu tree** is a weighted tree `T` on the same vertex set where the weight of edge
    `{a,b}` equals the value of the minimum `a`–`b` cut in the original graph. It needs exactly
    **`V − 1` max-flow computations** (instead of `V(V−1)/2` pairwise flows) plus the re-parenting
    step; after construction, "min cut between `a` and `b`" is answered in `O(V)` by traversing
    the tree path `a → b` and taking the **minimum edge weight** along it. **Caveat for directed
    graphs:** the theorem requires **undirected** input (capacities in both directions, which must
    be equal). The Gomory–Hu construction applied to a directed graph produces a tree whose edge
    weights equal the min cuts of the *symmetric* capacity assignment, not the directed min cuts —
    the tree "solves" a different problem. For directed min cuts you need the
    Karger–Raghavan–Thompson construction, which is `O(V)` flows but only guarantees cut
    *values* in expectation (no single tree reproduces all directed cuts).