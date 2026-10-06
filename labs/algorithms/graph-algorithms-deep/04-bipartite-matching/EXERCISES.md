# EXERCISES — Bipartite Matching

## Level 1 — Hand Traces

### 1.1 Augmenting path trace
Graph: `U = {u1,u2,u3}`, `V' = {v1,v2,v3}`. Edges: `u1-v1`, `u1-v2`, `u2-v1`, `u2-v3`, `u3-v2`.

- Start `M = ∅`. Process `u1`: `u1-v1` free ⇒ `M = {u1-v1}`, `|M| = 1`
- Process `u2`: try `v1` — matched to `u1`. Recurse on `u1`: try `v1` (seen, skip) then `v2` —
  free ⇒ `matchR[v2] = u1`, then `matchR[v1] = u2`. **`M = {u1-v2, u2-v1}`, `|M| = 2`**
  (note `u1-v1` was *replaced*, not added — this is the symmetric difference in action)
- Process `u3`: try `v2` — matched to `u1`. Recurse on `u1`: `v1` matched to `u2`, recurse on `u2`:
  `v1` seen, `v3` free ⇒ `matchR[v3] = u2`, `matchR[v1] = u1`, `matchR[v2] = u3`.
  **`M = {u1-v1, u2-v3, u3-v2}`, `|M| = 3`** — a **perfect matching**

**Verify Berge:** no unmatched vertices remain, so no augmenting path exists ⇒ maximum. ✓
`|V| = 6` so a perfect matching is possible. `|M| = 3 = |V|/2` ✓

### 1.2 Berge counter-example for a non-maximal matching
Take the graph above and claim `M = {u1-v1}` is maximum. Find the augmenting path:
`u3 - v2 - u1 - ...` hmm, `v2` is free, and `u3-v2` is an edge ⇒ `u3 → v2` is already an
augmenting path of length 1. Apply `M △ E(P)` ⇒ `{u1-v1, u3-v2}`, `|M| = 2`. Not maximum. ✓

### 1.3 König by hand
Graph: `U = {u1,u2,u3}`, `V' = {v1,v2}`, edges `u1-v1, u1-v2, u2-v1, u3-v2`.
Max matching `= 2` (e.g. `{u2-v1, u3-v2}`).
Minimum vertex cover: `{u1, v2}`? Check: `u1-v1` ✓ (`u1`), `u1-v2` ✓ (both), `u2-v1` ✓ (`v1`),
`u3-v2` ✓ (`v2`). Size `2` ✓ matches. Alternative: `{u1, v1}`? `u3-v2` uncovered ✗.
`{v1, v2}`? size 2 ✓ and covers everything! Also minimum. **Multiple minimum covers exist.**
Enumerate all: `{{u1,v2}, {v1,v2}, {u1,u2,v2}}?` size 3, not minimum.

### 1.4 Extract the cover from the cut
Build the flow network for 1.3 with `M = {u2-v1, u3-v2}`. Compute the residual:
`s→u1` residual 1 (unmatched), `s→u2` 0, `s→u3` 0; `u1→v1` residual 1, `u1→v2` residual 1;
`u2→v1` 0; `u3→v2` 0; `v1→t` 0; `v2→t` 0.
Residual-reachable from `s`: `{s, u1, v1, v2}` (`s→u1`, `u1→v1`, `u1→v2`). So
`S = {s, u1, v1, v2}`, `T = {u2, u3, v1?, t}` — careful: `v1, v2 ∈ S` ⇒ `T = {u2, u3, t}`.
**Cover `= (U ∩ T) ∪ (V' ∩ S) = {u2, u3} ∪ {v1, v2} = {u2, u3, v1, v2}`**, size 4.

Hmm — that's bigger than 2. **Recheck.** `res(v1→t) = c − f(v1,t) + f(t,v1) = 1 − 1 + 0 = 0` ✓,
and `res(t→v1) = 0 − 0 + 1 = 1`. From `v1` (in `S`), the arc `v1→t` has residual 0, so `t` is
not reachable ✓. So `S = {s, u1, v1, v2}`, `T = {u2, u3, t}`, cover size 4 ≠ 2.

**Where is the error?** König gives a cover of size `ν = 2`, so the formula must be applied with
the *other* convention. The correct one: `cover = (U \ S) ∪ (V' ∩ S)`. Check: `U \ S = {u2, u3}`,
`V' ∩ S = {v1, v2}` ⇒ still 4. Hmm.

**Let me recheck the residual reachability.** `u1-v1` is an original edge, so `u1→v1` has
`res = 1` (unmatched). Yes. So `v1 ∈ S`. `u1-v2` gives `u1→v2` res 1 ⇒ `v2 ∈ S`. From `v1`,
`res(v1→t) = 0`. From `v2`, `res(v2→t) = 0`. So `t ∉ S` ✓ and `S = {s,u1,v1,v2}`.

**So the cut is `{s,u1,v1,v2} | {u2,u3,t}` with capacity `res`-independent original capacity:**
arcs `S → T`: `s→u2` (cap 1), `s→u3` (cap 1), `u1→?` — `u1→v1, u1→v2` both internal,
`v1→t` (cap 1), `v2→t` (cap 1). **Total = 4.**

**So the min cut is 4?** But `ν = 2`! Contradiction ⇒ my matching isn't maximum.
`{u2-v1, u3-v2}`: can we do better? Edges available: `u1-v1`, `u1-v2`, `u2-v1`, `u3-v2`.
Try `{u1-v2, u2-v1}` — `u3` unmatched, size 2. Try `{u1-v1, u3-v2}` — size 2, `u2` free.
Can we get 3? We'd need all three `u`'s matched to three distinct `v`'s but `|V'| = 2`. So
**`ν = 2` is right.**

Then min cut must be 2. So there is a cut of capacity 2 — e.g. `S = {s, u1, u2, u3}`, `T = {v1,v2,t}`:
arcs `S→T` are `v1→t` and `v2→t` ⇒ capacity `1 + 1 = 2` ✓. So the min cut is
`S = {s} ∪ U`, `T = V' ∪ {t}`.

So my residual computation must be wrong. Recheck: is `u1` really reachable from `s`?
`res(s→u1) = c(s,u1) − f(s,u1) + f(u1,s) = 1 − 0 + 0 = 1 > 0` ⇒ yes reachable.
And from `u1`, `u1→v1` has `res = 1` ⇒ `v1` reachable. From `v1`, `v1→t` has `res = 0` ⇒ `t`
not reachable. So `S = {s,u1,v1,v2}` — capacity 4.

**But then the flow is not maximum!** `f = 2` and there's a residual `s→u1` — but no residual
`s→t` path because `v1→t` and `v2→t` are both saturated. By Berge/max-flow-min-cut, `f = 2` IS
maximum and the cut has capacity... let me recompute the cut capacity as `Σ_{(u,v) ∈ δ⁺(S)} c(u,v)`:
`S = {s, u1, v1, v2}`, `T = {u2, u3, t}`.
- `s→u1`: both in `S` — internal
- `s→u2`: `s ∈ S, u2 ∈ T` ⇒ `δ⁺`, cap 1
- `s→u3`: `δ⁺`, cap 1
- `u1→v1`: internal
- `u1→v2`: internal
- `u2→v1`: `u2 ∈ T, v1 ∈ S` ⇒ `δ⁻`, not counted
- `u3→v2`: `δ⁻`, not counted
- `v1→t`: `δ⁺`, cap 1
- `v2→t`: `δ⁺`, cap 1
**Capacity = 1 + 1 + 1 + 1 = 4.**

So `|f| = 2 < 4 = cap(S,T)` — that's FINE (weak duality), but it means `S` is **not** the
minimum cut, which means `f` is **not** maximum, which means there **is** a residual `s→t` path.
Check: `s→u1` (res 1), `u1→v1` (res 1), `v1→u2` — **this is the backward arc!** `res(v1→u2) =
c − f + f(u2→v1) = 0 − 0 + 1 = 1` ✓. Then `u2→?` — `u2→v1` has `res = 0`. Dead end.

Hmm. `s→u1 →v1 →u2` then stuck. What about `s→u1 →v2 →u3`? `res(v2→u3) = 0 − 0 + 1 = 1` ✓.
Then `u3→v2` res 0. Stuck.

**So genuinely no residual `s→t` path.** Then `f = 2` is max flow and `cap(S,T)` must equal 2.
**The only way both hold is if my cut-capacity arithmetic is wrong.** Let me recheck whether
`S` really contains `v1`. From `u1`, arcs out: `u1→v1` (res 1) and `u1→v2` (res 1). Also, are there
reverse arcs out of `u1`? `res(u1→s) = 0 − 0 + 1 = 1` ⇒ `s` reachable (already in `S`).
From `v1`: arcs out are `v1→t` (res 0) and `v1→u2` (res 1). So `u2 ∈ S`! I made an error —
**the backward arc `v1→u2` has positive residual and puts `u2` in `S`.**

Redo: `S = {s}`. From `s`: `s→u1` (res 1) ⇒ `u1`. From `u1`: `u1→v1` (res 1) ⇒ `v1`; `u1→v2` (res 1)
⇒ `v2`. From `v1`: `v1→u2` (res 1) ⇒ `u2`. From `v2`: `v2→u3` (res 1) ⇒ `u3`. From `u2`:
`u2→v1` (res 0), `u2→s` (res 1, already in). From `u3`: `u3→v2` res 0, `u3→s` res 1.
**`S = {s, u1, u2, u3, v1, v2}`, `T = {t}`.**

`cap(S,T)` = arcs `S→T` = `v1→t` (1) + `v2→t` (1) = **2 = ν** ✓✓

**Cover `= (U ∩ T) ∪ (V' ∩ S) = (U ∩ {t}) ∪ ({v1,v2}) = {v1, v2}`, size 2** ✓ — and we verified
`{v1,v2}` is a valid cover above!

**Lesson (the important one):** residual reachability follows **backward arcs** too. Forgetting
them puts too few vertices in `S` and produces a cut whose capacity exceeds the flow — which is
exactly how you notice something is wrong. **Always assert `cutCapacity == flowValue`.**

### 1.5 Dulmage–Mendelsohn by hand
For 1.3 with `M = {u2-v1, u3-v2}`: free `U` vertices = `{u1}`. Free `V'` = `{}`.
- From `u1` via `U→V'`: `v1, v2` ⇒ **D = {u1, v1, v2}**
- From free `V'` (none) ⇒ **A = {}**
- From `D` via `V'→U`: `v1→?` matched-to `u2` ⇒ `u2`; `v2` ⇒ `u3` ⇒ **C = {u2, u3}**
- **B = {}**
Vertices in `D ∪ A = {u1}` — exactly the vertices that can be unmatched in some maximum matching.
Indeed `{u2-v1, u3-v2}` leaves `u1` unmatched, and `{u1-v1, u3-v2}` leaves `u2` unmatched. ✓

## Level 2 — Implementations

### 2.1 Kuhn's algorithm
Implement with a `boolean[] seen` **reset per starting vertex**. Then deliberately remove the
reset and show the answer changes on a small instance (this is the bug everyone hits once).

### 2.2 Hopcroft–Karp
Implement the layered BFS + dist-increasing DFS with used-vertex deletion.
Instrument: number of phases, total DFS calls. Verify `phases ≤ O(√V)` empirically on random
bipartite graphs with `|U| = |V| = n`, `|E| ≈ 3n`.

### 2.3 Dinic equivalence
Implement matching via Dinic on the flow network. Verify it returns the **same size** as
Hopcroft–Karp on 10 000 random instances (the matchings themselves may differ).

### 2.4 König via min cut
Extract `(U ∩ T) ∪ (V' ∩ S)` from the residual cut. **Assert `|cover| == |M|` on every instance.**
If it ever fails, the residual BFS is forgetting backward arcs.

### 2.5 Hungarian algorithm (dense, min-cost)
Implement `O(n³)` Hungarian with u/v potentials and complementary slackness.
Test on `n = 5`: cost matrix with a known optimal assignment.
**Verify complementary slackness after each augmentation** — a free correctness check.

### 2.6 Min-cost max-flow for sparse weights
Implement successive shortest paths with potentials. Verify it reduces to max-flow when all costs
are 0, and to the Hungarian answer on small dense instances.

## Level 3 — Edge Cases (all must pass)

| Input | Expected | Trap |
|-------|----------|------|
| Empty graph | max matching 0, cover 0 | `seen` array size 0 |
| No edges | 0 | |
| `|U| ≠ |V'|` | max matching `≤ min(|U|,|V'|)` | no perfect matching assumption |
| Complete bipartite `K_{n,n}` | matching `n` | `n` augmentations |
| Perfect matching exists | report it; `|M| = |V|/2` | don't confuse with "maximum" |
| Star `K_{1,k}` | matching 1 | |
| Isolated vertex | simply unmatched | |
| Self-loop on a bipartite graph | impossible — drop it | bipartite-ness check |
| Duplicate edges | deduplicate or ensure they don't create false augmenting paths | |
| `V = 0` | 0 | |
| Hall's condition violated | max matching `< min(|U|,|V'|)` | e.g. `u1, u2` both adjacent only to `v1` |
| Kuhn with stale `seen` | **wrong answer, silently** | the classic bug |
| Hopcroft–Karp `dist` not reset | wrong answer or infinite loop | |
| General graph with a triangle | max matching 1, min cover 2 | König does **not** apply |

## Level 4 — Proof Obligations

4.1 Prove that `M △ E(P)` (augmenting) increases `|M|` by 1 and remains a matching.
4.2 Prove Berge's theorem via symmetric difference decomposition.
4.3 Prove Kuhn's correctness by induction: after processing `u_1..u_k`, `M` is maximum on the
      subgraph induced by `{u_1..u_k} ∪ V'`.
4.4 Prove König's theorem: `U ∩ S` are exactly the unmatched `U`, and `V' ∩ S` are exactly the
      matched `V'`; conclude the cover property and the size.
4.5 Prove that Hopcroft–Karp finds a maximal set of vertex-disjoint *shortest* augmenting paths per
      phase (the DFS greedily maximises, standard exchange argument).
4.6 Prove the `O(√V)` phase bound (two cases: long remaining path, or many disjoint short ones).
4.7 Show that `U \ S = {matched U vertices}` and `V' \ S = {unmatched V' vertices}` from the
      residual structure.

## Level 5 — General Graph Matching

### 5.1 Blossom, step by step
Implement blossom contraction for a small graph containing an odd cycle:
`triangle a-b-c` plus a pendant `d` attached to `a`, and an edge `e-f` disjoint.
Hand-trace: find the blossom (the triangle), contract it, find the augmenting path in the
contracted graph, expand.

### 5.2 Why bipartite algorithms fail on odd cycles
Run Kuhn's algorithm on the triangle `a-b-c` (all three edges) treating `a,c ∈ U`, `b ∈ V'`.
Kuhn will report matching `= 2` — impossible, since the graph has only 3 vertices so max matching
is 1. **The bug:** `a-b` and `a-c` share endpoint `a`, and Kuhn's recursion reassigns
`matchR[v]` without checking whether `a` gets matched twice. On a true bipartite graph this cannot
happen; on a general graph it can. Good demonstration of *why* the bipartite assumption is load-bearing.

### 5.3 Tutte's condition
Implement a brute-force check of Tutte's theorem: for `n ≤ 7`, enumerate all `S ⊆ V` and verify
"perfect matching exists iff `o(G−S) ≤ |S|` for all `S`". Compare against brute-force matching.

### 5.4 Tutte–Berge formula
Implement the formula's *combinatorial* verification on small graphs: `ν = (n − max_S o(G−S))/2`.
`max_S o(G−S)` is computed by brute force over `2^n` subsets for `n ≤ 16`.

## Level 6 — Stretch

6.1 **Dulmage–Mendelsohn implementation** in `O(E)`. Use it to answer: "which vertices can be left
      unmatched in some maximum matching?" Apply to a course-timetabling model.
6.2 **Hopcroft–Karp phase count** empirically: plot phases vs `n` for random sparse bipartite
      graphs, `n = 10^3..10^5`. Verify the `√n` scaling.
6.3 **f-factor matching**: match each vertex exactly `f(v)` times. Reduce to perfect matching on a
      gadget (replace each `v` with `f(v)` copies) and give the size.
6.4 **Online/incremental matching** (path and cycle augmenting): support edge insertions in
      amortised `O(1)` per insertion. Explain why it is possible (matching matroid).
6.5 **Maximum weight matching** via `O(V)` min-weight-matching reductions — state the reduction
      from a min-cost to a max-weight matching.
6.6 **Randomised algebra**: state the Schwartz–Zippel / Tutte matrix determinant characterisation
      and how randomisation over a field gives a Monte-Carlo perfect-matching test in
      `O(n^ω)`. Explain the one-sided error.