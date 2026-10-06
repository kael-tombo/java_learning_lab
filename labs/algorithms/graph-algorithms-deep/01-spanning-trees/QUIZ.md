# QUIZ — Spanning Trees

1. State the cut property precisely.
2. State the cycle property precisely, including the tie condition.
3. What does Kruskal output when the input graph is disconnected?
4. Why does Kruskal's `find(u) != find(v)` test exactly implement "does not create a cycle"?
5. Give the time complexity of Kruskal with union-find, and identify the dominant term.
6. Give the time complexity of Prim with a lazy `PriorityQueue` versus an eager `decrease-key` heap.
7. State the invariant that makes the lazy Prim heap correct.
8. For `E = Θ(V²)` (dense), which MST algorithm is asymptotically faster and why?
9. With negative edge weights, does Kruskal still return a correct MST? Explain.
10. Are self-loops ever part of an MST, and what is the one-line reason?
11. Borůvka's per-phase scan is `O(E)`. Why are there exactly `⌈log₂ V⌉` phases (at most)?
12. What real-world setting makes Borůvka the best of the four, and why?
13. Reverse-delete deletes an edge only when doing so preserves connectivity. Which property justifies this, and what must be true about the deletion order?
14. Union-find with union by rank AND path compression gives what amortised bound per operation, and what does `α` stand for?
15. Give a concrete edge set where two different MSTs have identical total weight but different edge sets. Then explain what "the MST" means for such a graph.

---

## Answers

1. Let `(S, V∖S)` be any cut of the graph and let `e` be a minimum-weight edge crossing that cut.
   Then `e` belongs to **at least one** minimum spanning tree. Note: *minimum*, not *uniquely*
   minimum — and *some* MST, not every MST.
2. Let `C` be any cycle and `e` the maximum-weight edge on `C`. If `e` is the **unique**
   maximum on `C`, then `e` is in **no** MST. If the maximum is tied, `e` is merely *not required*
   — it may still belong to some MST. Proof sketch: `T − e` splits into two components; `C`
   contains another edge `f` joining them with `w(f) ≤ w(e)`; `T − e + f` is a spanning tree with
   weight `≤ w(T)`, hence equal, hence an MST without `e`. Uniqueness is what excludes `e` from
   every MST.
3. A **minimum spanning forest** — one MST per connected component, with `V − k` edges where `k`
   is the number of components. Detection: the count of accepted edges never reaches `V − 1`.
   This is the correct, useful output; "there is no spanning tree" is a degenerate phrasing.
4. An edge set is acyclic iff it is a forest, and `e = (u,v)` merges two distinct trees without
   creating a cycle **exactly** when `u` and `v` are currently in different components of the
   partial solution. Union-find maintains precisely those components, so `find(u) != find(v)` is a
   complete and sound cycle test — not a heuristic.
5. `O(E log E)` for the sort, plus `O(E·α(V))` for the union-find operations. The dominant term
   is the sort: since `E ≤ V²`, `log E = O(log V)`, so `Θ(E log V)`. With bounded integer weights
   you can bucket-sort to get `O(E + W)`.
6. Lazy: `O(E log E)` — up to `O(E)` heap entries are pushed (one per edge examined) and the heap
   grows to `O(E)`. Eager (`decrease-key`, one entry per vertex): `O(E log V)` with the heap
   bounded at `O(V)`. With a Fibonacci heap the eager version is `O(E + V log V)` amortised since
   `decrease-key` is `O(1)`.
7. The heap holds, for every vertex not yet in the tree, the weight of the cheapest edge
   discovered that connects it to the tree. Consequently extract-min yields the minimum-weight
   edge crossing the cut `(tree, V∖tree)`. Stale entries (whose key no longer matches `key[v]`)
   are detected on pop and skipped, which is why correctness survives the lazy heap's duplicates.
8. **Array-based Prim, `O(V²)`, beats `O(E log V) = Θ(V² log V)`.** The gap is the `log V` factor
   from the heap: when the graph is already dense there are only `V` extract-mins to perform, so
   a linear scan over `V` keys (total `V²`) beats `V` heap operations plus `E` heap pushes
   (`V² log V`). The crossover is where `V² ≈ E log V`.
9. **Yes.** MST requires no non-negativity. The greedy arguments use only *comparisons* of weights,
   not addition of weights to a running count or the "prefix sums are non-negative" assumption
   that greedy correctness often needs. Kruskal sorts ascending including negatives, and every
   accepted edge is still a minimum-weight crossing edge of some cut. (Contrast: Dijkstra *does*
   require non-negative weights, because it uses the "settled vertices have final distance"
   invariant.)
10. **No.** A self-loop `e = (u,u)` is a cycle of length 1, and `e` is trivially its own maximum,
    so the cycle property excludes it. Operationally, `find(u) == find(v)` for a self-loop, so
    Kruskal rejects it automatically. Prim can still *examine* it while relaxing `u`'s key — it
    just never improves anything, since `w(u,u) ≥ key[u]`.
11. Because each phase at least **halves** the component count. Consider the component graph `H`
    (nodes = current components, edges = original edges between them). Every component picks its
    cheapest outgoing edge, so every node of `H` has degree ≥ 1 in the selected subgraph — there
    are no isolated nodes. Hence every connected component of `H` has ≥ 2 nodes, so the count
    halves or better. Starting from `V` components, after `k` phases there are `≤ V/2^k`, and
    `k ≥ log₂ V` phases are needed to reach 1.
12. **Read-mostly / streaming or memory-constrained settings**, and distributed MST. Each Borůvka
    phase is one *sequential* pass over the edge array with `O(1)` work per edge and `O(V)` extra
    memory (one cheapest-edge record per component), versus Kruskal's sort (which needs `Θ(E)`
    memory for the sort buffer and random access) and Prim's heap (`O(E)` entries). If edges
    arrive from a stream or live on disk, one linear scan per phase is far cheaper than sorting.
13. **The cycle property**, with the essential ordering constraint: edges must be processed in
    **descending** weight order. At the moment of deletion, `e` is the heaviest edge on the cycle
    it lies on (all heavier edges were already deleted, so the cycle's other edges are `≤ e`).
    Delete in ascending order and `e` is not the maximum on its cycle, so the argument fails and
    the result need not be minimum.
14. `O(α(V))` amortised per `find`/`union` (and `O(α(V))` amortised for a whole `union`-of-two-
    `find`s sequence), where `α` is the **inverse Ackermann function**, defined as
    `α(n) = min{k : A(k) ≥ n}` with `A(0)=1, A(k+1) = 2^{A(k)}`. It grows so slowly that
    `α(2^65536) = 5`, so for any realistic `V ≤ 2^64` you can read it as "practically constant".
    The *proven* bound needs **both** union by rank/size and path compression; either alone gives
    `O(log V)` amortised (or `O(log V)` worst case without compression).
15. **Triangle `K₃` with all edges weight 1** (or `ab=5, bc=5, ca=1`). There are three spanning
    trees, each with 2 edges and total weight 2 (respectively 6). So "the MST" is wrong
    terminology — a graph may have **many** minimum spanning trees of equal total weight. The
    unique object is the **minimum total weight** `OPT(G)`, not a particular edge set. If you need
    determinism, sort by `(weight, u, v)` or by a unique edge id to force a canonical tie-break.