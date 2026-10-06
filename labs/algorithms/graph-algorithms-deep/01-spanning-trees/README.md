# 01 — Spanning Trees

<div align="center">

**Kruskal · Prim · Borůvka · Cut Property · Cycle Property · Disjoint Sets · Reverse-Delete**

</div>

---

## Learning Objectives

- State the **cut property** and the **cycle property** and use each to *prove* greedy correctness
- Implement Kruskal with union-find and prove the union-find amortised bound
- Implement Prim with a lazy and an eager (decrease-key) priority queue; compare
- Implement Borůvka for the read-mostly / memory-constrained case
- Implement reverse-delete from a spanning forest and see why it is the slowest but simplest
- Recognise when a graph has *no* spanning tree (disconnected) and when weights are negative
- Handle multi-graphs, self-loops, parallel edges, and integer overflow in weight sums
- Know which MST you are computing when weights tie (a *minimum* spanning tree, not *the* tree)

## Prerequisites

- `05-bfs`, `06-dfs` — graph traversal, adjacency lists
- Heaps / priority queues
- Union-find (disjoint set union) with path compression + union by rank
- Sorting

## Estimated Time

- **Theory**: 80 minutes
- **Practice**: 140 minutes
- **Exercises**: 70 minutes
- **Total**: 5 hours

## Key Concepts

| Concept | Statement |
|---------|-----------|
| Spanning tree | Subgraph on all `V` with exactly `V−1` edges, acyclic, connected |
| Tree ↔ `E = V−1` | A connected graph is a tree **iff** `E = V−1` |
| Cut property | For any cut, a minimum-weight edge crossing it is in *some* MST |
| Cycle property | The maximum-weight edge of any cycle is in *no* MST |
| Kruskal | Sort edges ascending, add if it doesn't create a cycle. `O(E log E)` |
| Prim | Grow one tree from a root using a heap. `O(E log V)` |
| Borůvka | Each component picks its lightest outgoing edge, merge. `O(E log V)` |
| Reverse-delete | Delete heaviest edges in cycle order. `O(E(V+E))` naive |
| `E = V−1` | Every spanning tree of a connected graph has exactly `V−1` edges |
| Weight tie | Many MSTs may exist; all have the *same* total weight |
| Self-loop | Never in any MST (it is a cycle of length 1) |
| Parallel edges | Keep the cheapest per pair, or let Kruskal's sort handle it |

## Complexity Snapshot

| Algorithm | Time | Space | Dominant cost |
|-----------|------|-------|---------------|
| Kruskal (sort) | **`O(E log E)`** | `O(V)` | sort + union-find |
| Kruskal (bucket/counting) | `O(E + W)` | `O(V + W)` | bounded integer weights |
| Prim (binary heap, lazy) | `O(E log E)` | `O(E)` | heap can hold `E` entries |
| Prim (eager, `decrease-key`) | **`O(E log V)`** | `O(V)` | heap holds at most `V` |
| Prim (Fibonacci heap) | `O(E + V log V)` | `O(V)` | amortised decrease-key `O(1)` |
| Prim (dense/adjacency matrix) | `O(V²)` | `O(V²)` | best for `E ≈ V²` |
| Borůvka | `O(E log V)` | `O(V + E)` | phases = `O(log V)` |
| Reverse-delete | `O(E(V+E))` | `O(V + E)` | needs cycle detection per deletion |
| Union-find `find` amortised | `O(α(V))` ≈ constant | `O(V)` | inverse Ackermann |

**Note on Kruskal vs Prim:** Kruskal is `O(E log E)`, which is `O(E log V)` since `E ≤ V²`.
Prim with an eager heap is `O(E log V)`. On sparse graphs both are `Θ(E log V)`. On **dense**
graphs (`E = Θ(V²)`) Kruskal is `Θ(V² log V)` while array-based Prim is `Θ(V²)` — Prim wins
when the graph is already dense.

## Algorithms Covered

### Kruskal
```
sort all edges by weight ascending
for each (u, v, w) in order:
    if find(u) != find(v):
        union(u, v);  add edge to MST;  total += w
```
Early exit when `V−1` edges are chosen. Connected components make `V−1` unreachable — the
forest then has `> 1` tree, which is the correct output ("minimum spanning forest").

### Prim
```
tree = {root};  pq = all edges from root
while pq not empty and MST not complete:
    (w, u, v) = pq.poll()
    if v not in tree: add edge; tree.add(v); push all edges from v
```
The lazy version pushes `Σ deg = O(E)` entries total (one per edge examined), giving `O(E log E)`.
The eager version keeps one entry per vertex and calls `decrease-key`, giving `O(E log V)`.

### Borůvka
```
while #components > 1:
    for each component, find its minimum-weight outgoing edge
    add all such edges (ties broken arbitrarily, but skip edge if it would close a cycle)
    recompute components
```
Number of phases: each phase at least **halves** the component count (each component connects to
its cheapest neighbour, so the "component graph" has minimum degree ≥ 1 and its connected
components are unions of pairs), hence `⌈log₂ V⌉` phases. Total `O(E log V)`.

Borůvka's real advantage: it makes only **one pass over the edges per phase** with `O(1)` extra
memory per component, so it works in cache / streaming / memory-limited settings.

## Files

| File | Purpose |
|------|---------|
| `THEORY.md` | Cut/cycle property proofs, correctness arguments, tie handling |
| `EXERCISES.md` | Implement all four + hand-trace + edge cases |
| `QUIZ.md` | 15 questions on complexity, invariants, counter-examples |
| `FLASHCARDS.md` | ~60 rapid-recall rows |
| `MATH_FOUNDATION.md` | Union-find amortised bound, Kruskal phase analysis, `#trees = (Σ c_i)/n` |
| `CODE_DEEP_DIVE.md` | Annotated Java (4 algorithms) + pitfalls |
| `DIAGRAMS/` | Cut/cycle diagrams, Borůvka phase halving |