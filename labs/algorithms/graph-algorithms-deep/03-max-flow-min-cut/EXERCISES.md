# EXERCISES — Max-Flow / Min-Cut

## Level 1 — Hand Traces

### 1.1 Ford–Fulkerson trace
Network: `s→a = 3, s→b = 2, a→b = 2, a→t = 2, b→t = 3`.

- Path `s→a→t`: `δ = min(res(s,a), res(a,t)) = min(3, 2) = 2`. Push 2.
- Path `s→b→t`: `δ = min(2, 3) = 2`. Push 2.
- Path `s→a→b→t`: `res(s,a)=1, res(a,b)=2, res(b,t)=1` ⇒ `δ = 1`. Push 1.

Final flow: `f(s,a)=3, f(a,t)=2, f(s,b)=2, f(b,t)=3, f(a,b)=1`.
Check conservation: at `a`, in `= 3`, out `= 2 + 1 = 3` ✓. At `b`, in `= 2 + 1 = 3`, out `= 3` ✓.
**`f* = f(s,a) + f(s,b) = 3 + 2 = 5`.**

Residual: `res(s,a)=0, res(s,b)=0, res(a,t)=0, res(b,t)=0`, `res(a,b)=1`,
`res(b,a)=f(a,b)=1` (backward), `res(t,a)=f(a,t)=2`, `res(t,b)=f(b,t)=3`.
No `s→t` residual path ⇒ the flow is maximum.

**Min cut:** residual-reachable from `s` is `{s}` alone (both `s`-arcs saturated). `S = {s}`,
`T = {a,b,t}`. `cap(S,T) = c(s,a) + c(s,b) = 3 + 2 = 5 = f*` ✓ MFM-cut holds.

**Trace lesson:** a blocking flow is a *sum* of pushes, not one push. Verify conservation and
`|f|` at every intermediate state before moving on.

### 1.2 Edmonds–Karp trace
Same network; BFS picks fewest-*arc* paths: `s→a→t` (2 arcs, `δ=2`), `s→b→t` (2 arcs, `δ=2`),
`s→a→b→t` (3 arcs, `δ=1`). Same result `f* = 5`, three augmentations.

**Construct a network where DFS order and BFS order diverge.** Take `s→a=1, s→b=1, a→x=1,
b→y=5, x→t=5, y→t=1, a→y=1`. DFS (first arc first) may take `s→a→x→t` (`δ=1`), then
`s→b→y→t` (`δ=1`) ⇒ 2. BFS takes both 3-arc paths, also 2. To force a divergence you need the
*short* path to be capacity-limited while a *long* path is abundant:
`s→a=1, a→t=1, s→b=1, b→c=1, c→d=10, d→t=10, a→c=10`.
DFS takes `s→a→t` (`δ=1`), then is stuck on `a→t` and must discover `s→b→c→d→t` (`δ=1`) ⇒ 2.
BFS takes `s→a→t` then `s→b→c→d→t` too ⇒ 2. The real divergence shows up in the **augmentation
count**, not the value: build a graph where DFS wastes many unit-capacity augmentations on a long
detour that BFS avoids in one shot. Count augmentations for both on `V = 8`, random unit-capacity
graphs — BFS consistently needs fewer, which is exactly the `O(VE)` augmentation bound.

### 1.3 Dinic trace with level graphs
Network: `s→a=3, s→b=3, a→b=1, a→t=2, b→t=3`.

- **BFS phase 1:** `level[s]=0, level[a]=1, level[b]=1, level[t]=2`.
  Level-graph arcs (need `res>0` **and** `level[v] = level[u]+1`): `s→a`, `s→b`, `a→t`, `b→t`.
  (`a→b` is **excluded**: `level[b] = 1 = level[a]`, not `level[a] + 1`.)
  Blocking flow: `s→a→t` pushes `min(3,2) = 2`; `s→b→t` pushes `min(3,3) = 3`.
  **Phase total = 2 + 3 = 5.**
- **BFS phase 2:** residual out of `s`: `res(s,a)=1`, `res(s,b)=0`. From `a`: `res(a,t)=0`,
  `res(a,b)=1` ⇒ `level[b]=2`; from `b`: `res(b,t)=0`, `res(b,a)=f(a,b)=0` ⇒ nothing new.
  So `level[t] = ∞` ⇒ **no level graph ⇒ terminate.**
- **`f* = 5`.**

Note `level[t]` went from 2 to `∞` rather than incrementing by one — the "shortest path length
strictly increases" claim bounds the phase *count* by `V−1`, not forces a specific sequence.

### 1.4 Cut extraction from a finished flow
From 1.3 the final flow is `f(s,a)=2, f(a,t)=2, f(s,b)=3, f(b,t)=3, f(a,b)=0`.
Residual: `res(s,a)=1, res(s,b)=0, res(a,t)=0, res(a,b)=1, res(b,t)=0`.

Residual BFS from `s`: reach `s`; `s→a` has residual 1 ⇒ reach `a`; from `a`: `a→t` residual 0,
`a→b` residual 1 ⇒ reach `b`; from `b`: `b→t` residual 0, `b→a` residual `f(a,b) = 0` ⇒ nothing.
**`S = {s, a, b}`, `T = {t}`.**

`cap(S,T) = c(a,t) + c(b,t) = 2 + 3 = 5 = f*` ✓

Verify both theorems from THEORY §6:
- every `δ⁺` arc (`a→t`, `b→t`) is **saturated**: `f = c` ✓
- every `δ⁻` arc (none here — nothing leaves `T`) carries **zero** flow ✓

**Trap to practise:** compute the cut capacity from `initialCapacity`, not from residual capacity.
Using residual here gives `0 + 0 = 0 ≠ 5` — silently wrong, no exception.

### 1.5 Enumerate all min cuts
Small network: `s→a=1, a→t=1, s→b=1, b→t=1`, and no `a→b` arc.
Min cut value `2`, and **two** minimum cuts: `({s}, {a,b,t})` and `({s,a,b}, {t})`.
Brute-force all `2^(V−2)` partitions to confirm exactly these two are minimal.
Menger + integrality guarantees *a* min cut exists; it does **not** guarantee uniqueness.

## Level 2 — Implementations

### 2.1 Residual-graph structure
Build a Dinic-style edge-array structure (flat `int[] to`, `long[] cap`, `int[] next`, plus a
reverse-edge index `e ^ 1`). Write `push(u, e, δ)` and assert the invariant
`res(u,v) + res(v,u) = c(u,v) + c(v,u)` after every push. This single assertion catches most flow
bugs immediately, and the `e ^ 1` indexing (forward edge `2k`, reverse edge `2k+1`) removes all
`reverseIndex` bookkeeping bugs.

### 2.2 Edmonds–Karp
Implement and cross-validate against Dinic on random graphs (`V ≤ 30`, `E ≤ 100`). Then benchmark
on a dense graph (`V = 200, E = 10 000`), where EK's `O(VE²)` should hurt badly versus Dinic.

### 2.3 Dinic
Implement with `level[]` and `it[]`. Instrument: number of BFS phases, number of DFS calls, max
`it[]` index reached. Verify empirically that `phases ≤ V−1` on 10 000 random instances — a
violation means the level graph is being reused incorrectly.

### 2.4 Blocking flow: DFS-loop vs "distribute"
Implement the blocking flow two ways: (a) `while (dfs(s, INF) > 0) ;` and (b) a "distribute"
version `distribute(s, INF)` that tries to satisfy all demands in one descent. Compare on
`V = 2000, E = 20 000`. (b) usually wins: it makes fewer redundant re-descents because it does not
restart from `s` after each augmentation.

### 2.5 Push–relabel
Implement FIFO push–relabel with global relabel (every `c·E` operations), the gap heuristic, and
highest-label selection. Benchmark on `V = 5000, E = 200 000` against Dinic — push–relabel with
all three heuristics should win by 1–2 orders of magnitude.

### 2.6 The `∞` capacity convention
Implement `infiniteCapacity(n, maxFiniteCap)` returning `(long) n * maxFiniteCap + 1`, and prove
it never binds: no `s→t` flow can exceed the total capacity out of `s`, which is `≤ n·maxCap`.
Then show the failure mode with `Integer.MAX_VALUE` and `maxFiniteCap = 3·10^9`: two "infinite"
arcs sum to `6·10^9 > Integer.MAX_VALUE` ⇒ overflow ⇒ a negative residual ⇒ the flow loop thinks
it found capacity. For bipartite matching the tight `∞` is `min(|U|, |V|)`.

## Level 3 — Matching Reductions

### 3.1 Bipartite matching via max flow
Build the standard reduction (`s→u` cap 1, `u→v` cap 1 per edge, `v→t` cap 1).
Verify on `U = {u1,u2,u3}`, `V = {v1,v2}`, edges `{(u1,v1),(u1,v2),(u2,v1),(u3,v2)}`
⇒ max flow `2`. **Trace the Dinic phases** and confirm the `O(E√V)` behaviour on random
bipartite graphs with `|U| = |V| = n`, `|E| ≈ 3n`.

### 3.2 König: min vertex cover from the cut
For the same instance, extract `S` from the residual and compute `cover = (U ∩ T) ∪ (V ∩ S)`.
Verify `|cover| = 2` and that it covers every edge.

### 3.3 Hopcroft–Karp equivalence
Implement Hopcroft–Karp and confirm it matches Dinic-based matching *in size* on random bipartite
graphs. Note the actual matchings may differ (many maximum matchings exist).

### 3.4 Node-disjoint paths via node splitting
Given a graph, split each internal `v` into `v_in → v_out` with capacity 1, rewire incoming arcs
to `v_in` and outgoing from `v_out`. Verify the max flow equals the Menger vertex-disjoint path
count on a hand example where the vertex cut is smaller than the edge cut.

## Level 4 — Cut Extraction

### 4.1 Extract and verify
After every run, extract the cut and assert `cutCapacity == flowValue`. Free, very strong check.

### 4.2 Assert the two cut theorems
Programmatically assert (i) every `δ⁺` arc has `f == c`, and (ii) every `δ⁻` arc has `f == 0`.
Both are theorems, so a violation is a guaranteed bug.

### 4.3 Enumerate all min cuts
On `V ≤ 10`, brute-force all `2^(V−2)` partitions, filter to min capacity, and verify how many
tie. Use this to demonstrate that **min cuts are not unique** and that cut-extraction returns
*one* of them.

### 4.4 Weighted vs unweighted min cut
Explain why the cut capacity counts only `S → T` arcs (never `T → S`) and what that implies for
undirected inputs. Verify on a 3-cycle with capacities 1 each: min cut `2`, and check your
extraction never includes the reverse direction.

## Level 5 — Edge Cases (all must pass)

| Input | Expected | Trap |
|-------|----------|------|
| `s` has no outgoing arc | flow 0, cut 0 | `INF` sentinel paths |
| `t` unreachable | flow 0; `S` = everything residual-reachable from `s` | cut = Σ of `s`-arcs |
| `cap = 0` arcs | never used | must be filtered, or the level graph must check `res > 0` |
| Parallel arcs | both usable | residual formula must account for both |
| Antiparallel arcs `u→v`, `v→u` | `res(u,v) = c(u,v) − f(u,v) + f(v,u)` | using only `c − f` is the #1 bug |
| Self-loop `u→u` | never on an augmenting path | breaks the "simple path" assumption |
| `V = 2` | only the direct `s→t` arc | tests init |
| `V = 1` (`s == t`) | invalid | guard explicitly; the loop never terminates |
| Total flow > `Integer.MAX_VALUE` | `long` | overflow ⇒ negative flow, silently |
| Huge `∞` capacity | `(long) n * maxCap + 1` | overflow on summing two `∞` arcs |
| Zero-capacity source | flow 0 | |
| Equal-length augmenting paths | BFS order changes *which* opt flow, not the value | tests determinism only |

## Level 6 — Proof Obligations

6.1 Prove weak duality in full: decompose `|f|` across the cut, showing interior arcs cancel by
      conservation.
6.2 Prove that a maximal flow (no augmenting residual `s→t` path) is maximum, using weak duality.
6.3 Prove min-cut extraction: `δ⁺` saturated and `δ⁻` zero, hence `cap(S,T) = |f|`.
6.4 Prove Dinic's `O(V²E)`: blocking flow `O(VE)` per phase, at most `V` phases.
6.5 Prove `O(E√V)` for unit networks (the bipartite-matching case).
6.6 Prove König's theorem from weak duality plus the cut-extraction formula.
6.7 Prove push–relabel validity: the height function stays valid, so when all excess is zero there
      is no augmenting residual `s→t` path (validity `h(u) ≤ h(v)+1` plus `h(s) = V`, `h(t) = 0`
      force `V ≤ 0`, a contradiction).

## Level 7 — Stretch

7.1 **Gomory–Hu tree** for an undirected graph: implement, verify every tree edge weight equals the
    corresponding min-cut value, then answer "min cut between `a` and `b`" in `O(V)` by a tree
    traversal.
7.2 **Min-cost flow**: successive shortest paths with Johnson potentials and SPFA for the init.
    Verify it reduces to max flow when all costs are 0.
7.3 **Sparse/cactus graphs**: show that max flow on a cactus decomposes into independent per-cycle
    problems, giving `O(V)`. Implement and compare on generated cactus graphs.
7.4 **Global min cut** (Stoer–Wagner, `O(V³)`): implement, then verify against per-pair max flows
    on small instances (`V ≤ 8`).
7.5 **Multicommodity flow**: state why single-commodity integrality fails, and give a fractional
    LP counterexample — two commodities each wanting `1` unit between the same `s` and `t`, with two
    parallel `s→t` paths of capacity 1 each: any integral solution gives total 1, but the fractional
    optimum is `2` (`0.5` down each path for each commodity). Hence no integral theorem exists.
7.6 **Push–relabel correctness invariant**: assert `h(u) ≤ h(v) + 1` for every residual arc after
    every relabel. A violation proves the relabel step is wrong.