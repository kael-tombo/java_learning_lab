# THEORY — Spanning Trees

## 1. Definitions

A **spanning tree** of a connected graph `G = (V, E)` is a subgraph `T ⊆ G` with:
- all of `V` (it *spans*),
- `V − 1` edges,
- connected and acyclic (hence a tree).

**Theorem.** For any connected undirected graph, `E = V − 1` **iff** the graph is a tree.
*Proof.* (⇐) By induction: a tree has a leaf `v` with `deg(v) = 1` (else follow paths forever on
the finite vertex set to build a cycle). Remove `v`: the remainder is a tree on `V−1` vertices
with `V−2` edges, and re-adding `v` gives `V−1`. (⇒) A connected graph with `V−1` edges has
exactly one path between any two vertices — a second would form a cycle, and a cycle plus the
existing path would need an extra edge. ∎

**Consequence:** every spanning tree has exactly `V−1` edges, so *any* algorithm that adds edges
without creating cycles and stops at `V−1` edges has found a spanning tree.

## 2. The Two Properties (the whole theory in two statements)

### Cut property
> Let `(S, V∖S)` be any cut of the graph and let `e` be a minimum-weight edge crossing it.
> Then `e` belongs to **at least one** MST.

*Proof.* Let `T` be an MST not containing `e`. Adding `e` to `T` creates a unique cycle `C`,
because `T` is a tree. `C` crosses the cut at least twice (it enters and leaves `S`), and `e` is
one crossing, so there is another edge `f ∈ C` crossing the cut with `f ≠ e`. Since `e` is a
minimum-weight crossing edge, `w(e) ≤ w(f)`. Now `T' = T + e − f` is a spanning tree with
`w(T') = w(T) + w(e) − w(f) ≤ w(T) = OPT`. Since `T` was already minimum, `w(T') = OPT`, so `T'`
is an MST containing `e`. ∎

### Cycle property
> Let `C` be any cycle and `e` the **maximum**-weight edge on `C`. Then `e` belongs to **no** MST.

*Proof.* Suppose `T` is an MST containing `e`. Remove `e` from `T`: the result is a spanning
*forest* with two components, `A` and `B`. The cycle `C` must contain another edge `f` joining
`A` and `B` (because `C` is a cycle, removing any one edge leaves a path spanning `C`'s vertices,
which connects the two components). `f ≠ e` and `w(e) ≥ w(f)` since `e` is the maximum on `C`.
Then `T − e + f` is a spanning tree with `w(T) − w(e) + w(f) ≤ w(T)`. Minimality of `T` forces
`w(T) − w(e) + w(f) ≥ w(T)`, i.e. `w(f) ≥ w(e)`. Together: `w(f) = w(e)`, so `T − e + f` is *also*
an MST not containing `e`. So there always exists an MST excluding `e` — but does that mean `e`
is in **no** MST? No: the conclusion proved is "there exists an MST without `e`", i.e. `e` is not
*required*. The stronger claim "in no MST" holds when `e` is the **unique** maximum on `C`.
∎

**Precise statement:** `e` is in *some* MST iff `e` is not the unique maximum-weight edge of any
cycle. The `≥` vs `>` distinction matters — this is exactly where ties come from.

### Why the properties justify the greedy algorithms
- **Kruskal** processes edges in ascending order. When it adds edge `e`, the set of edges
  already chosen defines a partition; the "endpoints of `e` in different components" condition
  means `e` crosses some cut, and every earlier (hence `≤`) edge has already been considered, so
  `e` is a minimum-weight crossing edge of *some* cut → cut property → safe.
- **Prim** maintains a growing vertex set `S`. It picks the minimum-weight edge crossing `(S, V∖S)`
  → cut property applied to that specific cut → safe.
- **Reverse-delete** processes edges in *descending* order, deleting an edge if it lies on a
  cycle. Equivalently it deletes the maximum edge of a cycle → cycle property → safe.

**General theorem (greedy paradigm).** A greedy algorithm is correct if *every* choice it makes
can be shown to extend to an optimal solution. Both properties give exactly that.

## 3. Kruskal

```
1. Sort E ascending by weight.
2. Initialise union-find (each vertex its own component).
3. For each (u,v,w) in order:
       if find(u) ≠ find(v):  union(u,v);  add to MST;  total += w
4. If |MST| < V−1 the graph was disconnected → return a minimum spanning FOREST.
```

**Invariant.** The chosen edge set is acyclic (we add `e` only when it joins two distinct
components, which is exactly the definition of not creating a cycle) and is a subset of some MST.

**Correctness.** By the cut property argument above, each accepted edge is safe. Since we accept
exactly `V−1` edges on a connected graph, the result is a spanning tree, and safety at every step
implies it is minimum. ∎

**Complexity.** Sort `O(E log E)`. Union-find: `V−1` successful `union`s and up to `E` `find`
pairs. With path compression + union by rank, each `find`/`union` is `O(α(V))` amortised, so
`O(E·α(V))`. Total **`O(E log E)`** dominated by the sort.

**Early exit.** Once `V−1` edges are chosen, stop — the remaining edges are irrelevant. On graphs
where `E ≫ V` (e.g. complete graphs) this saves most of the `find` calls.

**Ties.** Sorting is not stable across equal weights unless you make it so, and different tie
orders can yield different (but equally minimum) spanning trees. If the problem demands a
*canonical* MST, sort by `(weight, u, v)`.

## 4. Prim

```
1. Start from any vertex r; treeKeys[r] = 0, else ∞.
2. Extract-min vertex u from the heap.
3. If u's key is ∞ → graph disconnected; stop.
4. Add (parent[u], u) to MST.
5. For each neighbour v of u not in the tree: if w(u,v) < key[v], update and set parent[v] = u.
```

**Invariant.** At every step the heap contains exactly one candidate entry per tree-adjacent
vertex not yet in the tree, keyed by the cheapest edge connecting it. So extract-min yields the
minimum edge crossing the cut `(tree, V∖tree)`.

**Correctness.** Cut property on the cut `(tree, V∖tree)`. The extracted edge is its minimum.
∎

**Two implementations, two complexities.**
- **Lazy** (push a new entry on every improvement, skip stale entries on pop): pushes `O(E)`
  entries, heap size `O(E)`, so `O(E log E)`.
- **Eager** (`decrease-key`, one entry per vertex): heap size `O(V)`, `O(E)` extract/decrease
  ops → `O(E log V)`. A binary heap's `decrease-key` is `O(log V)`; a Fibonacci heap's is
  `O(1)` amortised, giving `O(E + V log V)`.
- **Array-based** (linear scan for the min): `O(V)` per extraction → `O(V²)` total. Best when
  `E = Θ(V²)` (dense), where `V² < E log V`.

## 5. Borůvka

```
components = union-find with every vertex separate
while #components > 1:
    best = array of (cheapest outgoing edge per component), init ∞
    for each edge (u,v,w):          // ONE pass over all edges
        if find(u) != find(v):
            ru = find(u); rv = find(v)
            if w < best[ru].w: best[ru] = (u,v,w)
            if w < best[rv].w: best[rv] = (u,v,w)
    for each component c with best[c] ≠ ∞:
        if find(c) is still the current root:  union(...)   // skip if already merged
```

**Phase-halving lemma.** Each phase at least halves the number of components.
*Proof.* Consider the *component graph* `H`: nodes = current components, and there is an edge
between two components if the original graph has an edge between them. Every component chooses
its cheapest outgoing edge, so every node of `H` has degree ≥ 1 in the chosen subgraph. Hence
`H` contains a spanning forest covering all `k` nodes with no isolated node, so every connected
component of `H` has at least 2 nodes. Therefore the number of components **halves or better**.
∎

Since each phase halves, there are `⌈log₂ V⌉` phases, each costing `O(E·α(V))` for the edge scan,
so total **`O(E log V)`**.

**Borůvka's real niche:** each phase is a single sequential pass over the edge array with `O(1)`
work per edge. That makes it cache-friendly and — crucially — usable in **streaming / external
memory** settings where random access to the edge array is expensive but one sequential scan is
cheap. It is also the basis of distributed MST algorithms, where each node holds a local MST.

## 6. Reverse-Delete

```
1. Sort E descending by weight.
2. for each (u,v,w) in order:
       if removing e keeps G connected:  remove e
3. The remaining V−1 edges form an MST.
```

**Correctness.** `e` is deleted only when it lies on a cycle (deleting it keeps the graph
connected, and the graph was connected before, so there was an alternative path = a cycle
through `e`). Being processed in descending order, `e` is the maximum-weight edge on that cycle
at the moment of deletion. By the cycle property, deleting it preserves *some* MST. ∎

**Complexity.** Connectivity test after each deletion is `O(V+E)` with BFS, giving
`O(E(V+E))`. Faster variants maintain a dynamic connectivity structure (ETT, Holm–de Lichtenberg–
Thorup) to get `O(E log n)`. Reverse-delete exists mainly because it is trivially *obviously*
correct from the cycle property — it is the reference implementation and the pedagogical baseline.

## 7. Existence, and Disconnection

- A spanning tree exists **iff** the graph is connected.
- On a disconnected graph the algorithms naturally return a **minimum spanning forest**: one MST
  per connected component. Kruskal's `|MST| < V−1` test detects this.
- If the graph is directed, "spanning tree" is not even well defined (you need an arborescence,
  which has its own algorithm — Chu–Liu/Edmonds for minimum cost).

## 8. Special Cases

| Situation | Handling |
|-----------|----------|
| Self-loop `e = (u,u)` | Never in an MST — it is a cycle of length 1. Skip explicitly. |
| Parallel edges `(u,v)` with different weights | Keep the cheapest; Kruskal handles it naturally. |
| Negative weights | Fine! MST works with any real weights, including negatives. |
| Integer overflow on `total` | Use `long`; `|total|` can exceed `int` for large `V`. |
| Infinite/`NaN` weights | Kruskal's ordering is undefined. Reject up front. |
| `V = 0` | Empty MST, `total = 0`. Guard the `V−1` early exit (which would be `−1`). |
| `V = 1` | MST is the single vertex, `total = 0`, zero edges. |

## 9. Which Algorithm When?

| Situation | Pick |
|-----------|------|
| Generic sparse graph, simplest correct code | **Kruskal** |
| Need the tree edges as a set (skip en masse) | **Kruskal** |
| Dense graph `E = Θ(V²)` | **Prim (array)** |
| Want a single growing tree / cut queries | **Prim** |
| Read-mostly, low memory, or streaming edges | **Borůvka** |
| Distributed / partitioned graph | **Borůvka** |
| Teaching / proof baseline | **Reverse-delete** |
| Weights are small integers `0..W` | **Kruskal with bucket sort, `O(E + W)`** |