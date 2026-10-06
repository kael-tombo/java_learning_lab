# 03 — Max-Flow / Min-Cut

<div align="center">

**Ford–Fulkerson · Edmonds–Karp · Dinic · Push–Relabel · Residual Graphs · Bipartite Matching · Gomory–Hu**

</div>

---

## Learning Objectives

- Define the flow network formally and derive the **max-flow min-cut theorem** by construction
- Explain the residual graph and why back-edges are essential to optimality
- Implement Ford–Fulkerson, Edmonds–Karp (`O(V·E²)`), and Dinic (`O(V²E)`)
- Implement push–relabel with gap heuristic and global relabelling (`O(V³)`)
- Extract the min cut from a *finished* max flow (reachable set in the residual graph)
- Reduce bipartite matching, bipartite vertex cover (König), and edge-disjoint paths to max-flow
- State Gomory–Hu trees and how they answer "min cut between every pair" in `V−1` max-flows
- Diagnose integer overflow in capacity sums and `∞` edge capacities

## Prerequisites

- BFS and DFS (`05-bfs`, `06-dfs`)
- Graph connectivity and residual reasoning
- `04-bipartite-matching` (or do it after — the reductions run both ways)

## Estimated Time

- **Theory**: 95 minutes
- **Practice**: 160 minutes
- **Exercises**: 80 minutes
- **Total**: 5.5 hours

## Key Concepts

| Concept | Statement |
|---------|-----------|
| Flow network | directed graph with `cap(u,v) ≥ 0`, source `s`, sink `t` |
| Flow | `0 ≤ f(u,v) ≤ cap(u,v)`, conservation at all `v ∉ {s,t}` |
| Value | `|f| = Σ f(s,v) − Σ f(v,s)` |
| Residual capacity | `res(u,v) = cap(u,v) − f(u,v) + f(v,u)` |
| Augmenting path | `s → t` path of edges with positive residual capacity |
| Cut | partition `(S, T)` with `s ∈ S, t ∈ T`; capacity `Σ_{u∈S, v∈T} cap(u,v)` |
| Weak duality | `|f| ≤ cap(S,T)` for **every** flow and every cut — the core bound |
| Max-flow min-cut | max flow value = min cut capacity |
| Dinic BFS phase | level graph from residual `BFS`; blocking flow inside it |
| Blocking flow | flow with no `s→t` path in the level graph; `O(V·E)` per phase |
| Dinic bound | `O(V²E)`; `O(E√V)` on unit-capacity unit networks |
| Push–relabel | local excess `e(x)`; discharge pushes surplus to reachable nodes |
| Gap heuristic | nodes with gap `> n` are dead → prune |
| Global relabel | periodic BFS from `t` to recompute exact distances |
| Integer capacities | Dinic is strongly polynomial: `O(V²E)` regardless of capacity magnitude |

## Complexity Snapshot

| Algorithm | Time | Space | Notes |
|-----------|------|-------|-------|
| Ford–Fulkerson (DFS) | `O(E·F)` | `O(V+E)` | **depends on `F`** — pseudo-polynomial |
| Edmonds–Karp (BFS) | **`O(V·E²)`** | `O(V+E)` | polynomial; short augmenting paths |
| Dinic | **`O(V²E)`** | `O(V+E)` | best practical general algorithm |
| Dinic, unit capacities | `O(E√V)` | `O(V+E)` | bipartite matching, unit networks |
| Dinic, unit networks | `O(E√V)` | `O(V+E)` | e.g. bipartite matching |
| Push–relabel (FIFO) | `O(V³)` | `O(V+E)` | good for dense graphs |
| Push–relabel (highest-label + gap) | `O(V²√E)` practical | `O(V+E)` | **the practical champion** on big instances |
| Goldberg–Tarjan (generic) | `O(V²E)` | `O(V+E)` | |
| Orlin (`V = O(√E)`) | `O(VE)` | `O(V+E)` | fastest theoretical APSP-matching bound |
| Bipartite matching via Dinic | `O(E√V)` | | = Hopcroft–Karp |
| Min cut for all pairs (Gomory–Hu) | `V−1` max-flows | `O(V²)` | + `O(V)` per query |

**The key theoretical point:** Ford–Fulkerson is *pseudo-polynomial* in the capacity values, so
it is exponentially bad in the input bit-size. Edmonds–Karp fixed that at `O(VE²)` by insisting on
**shortest** (fewest-edges) augmenting paths. Dinic improved it further by doing *many* augmenting
paths per BFS phase.

## Algorithms Covered

### Ford–Fulkerson
Repeatedly find any `s→t` residual path, push `min` residual capacity along it. Terminates with a
max flow. **Correct always, fast only when capacities are small.**

### Edmonds–Karp
Same, but BFS ⇒ shortest augmenting path in *edge count*. Max `V` phases of `O(E)` each ⇒
`O(V·E²)`.

### Dinic
```
while BFS builds a non-empty level graph from s:
    blocking = true
    while blocking:
        blocking = false
        for each edge (u,v) admissible in the level graph (level[v] = level[u]+1, res>0):
            push the max possible; if res becomes 0, blocking = false
```
Per phase: the level graph's `s→t` paths all have exactly `level[t]` edges, so the number of
augmentations is bounded by `E`; each DFS is `O(V)` ⇒ `O(VE)` per phase. Between phases, `level[t]`
strictly increases ⇒ `≤ V` phases ⇒ **`O(V²E)`**.

### Push–relabel
```
h[s] = V, all other h = 0
while a vertex with positive excess exists:
    discharge it: while e(v) > 0: relabel/push
```
Push–relabel *starts from the max flow* and works backwards, ending at the *max pre-flow*. Its
advantage is that the high-level structure allows the global-relabel and gap heuristics, which
give near-linear practical behaviour on very large instances.

## Reductions

| From | To | Construction | Sizes |
|------|----|--------------|-------|
| Max bipartite matching | Max flow | `s → U` (cap 1), `U → V` (cap 1 per edge), `V → t` (cap 1) | `V+2` nodes, `E + |U| + |V|` arcs |
| Bipartite vertex cover | Max flow | Hopcroft–Karp, or König: cover from cut | — |
| Min s-t cut | Max flow | **identical by theorem** | — |
| All-pairs min cut | Gomory–Hu tree | `V−1` max-flow computations | `O(V²)` |
| Edge-disjoint paths | Unit capacities | max flow = number of disjoint paths | |
| Node-disjoint paths | Node splitting | split each `v` into `v_in → v_out` (cap 1) | `2V` nodes |
| Project selection | Min cut | maximise `Σ profit − Σ penalty` | |
| Reliability / max concurrent flow | Max flow | capacities = capacities | |

**Min-cut from max flow:** after a max flow, let `S` = set of nodes reachable from `s` in the
**residual** graph. Then `(S, V∖S)` is a minimum cut. This is a theorem, not a heuristic.

## Files

| File | Purpose |
|------|---------|
| `THEORY.md` | Weak duality, max-flow min-cut proof, Dinic bound, cut extraction |
| `EXERCISES.md` | Implement FF/EK/Dinic, hand-trace, hit overflow and `∞` cases |
| `QUIZ.md` | 15 questions on invariants, complexity, counter-examples |
| `FLASHCARDS.md` | ~60 rapid-recall rows |
| `MATH_FOUNDATION.md` | MFM-cut proof, Dinic `O(V²E)`, Hopcroft–Karp `O(√V E)`, Gomory–Hu |
| `CODE_DEEP_DIVE.md` | Annotated Java (EK, Dinic, push–relabel, matching) + pitfalls |
| `DIAGRAMS/` | Residual graphs, level graphs, cut extraction |