# 04 — Bipartite Matching

<div align="center">

**Hungarian · Hopcroft–Karp · König · Minimum Weight · General Graph Matching (Blossom) · Dulmage–Mendelsohn**

</div>

---

## Learning Objectives

- Recognise a bipartite graph and the structure theorems that make matching tractable here
- Implement Kuhn's (augmenting-path) matching in `O(VE)` and Hopcroft–Karp in `O(E√V)`
- Prove the augmenting-path theorem: a matching is maximum iff no augmenting path exists
- State and prove **König's theorem**: `min vertex cover = max matching` in bipartite graphs
- Extract the min vertex cover from a max flow's min cut
- Implement the **Hungarian algorithm** for min-cost perfect matching in `O(n³)`
- Implement general (non-bipartite) matching via blossom contraction and state its complexity
- State the current complexity landscape (matching reduction to matrix multiplication, `n^{2.37}`)
- Diagnose the classic bugs: stale visited arrays, wrong side, non-perfect vs maximum matching

## Prerequisites

- `03-max-flow-min-cut` (the reduction, min-cut extraction)
- BFS/DFS
- `05-graph-coloring` for why bipartite structure matters (2-colourability is the same idea)

## Estimated Time

- **Theory**: 90 minutes
- **Practice**: 160 minutes
- **Exercises**: 80 minutes
- **Total**: 5.5 hours

## Key Concepts

| Concept | Statement |
|---------|-----------|
| Matching | Set of edges with no shared endpoints |
| Maximum matching | Largest possible matching; size `ν(G)` |
| Perfect matching | Matches **every** vertex; requires `n` even |
| Augmenting path | Alternating `M`-path with both endpoints unmatched |
| Berge's theorem | `M` maximum **iff** no augmenting path exists |
| Berge's proof | Symmetric difference of two matchings decomposes into alternating cycles/paths |
| Bipartite | Vertex set partitions into `U ∪ V`; edges only between parts |
| König's theorem | `min vertex cover = max matching` (bipartite **only**) |
| `Hopcroft–Karp` | `O(E√V)` — layered BFS/DFS augmentations, Dinic on the flow network |
| Kuhn / DFS matching | `O(VE)` — one augmenting path search per unmatched left vertex |
| Hungarian | Min-cost perfect matching on a dense cost matrix, `O(n³)` |
| Assignment problem | Hungarian's original application |
| General matching | Non-bipartite; needs blossom (odd-cycle) contraction |
| Tutte's theorem | Characterises perfect matchings via vertex deletion, general graphs |
| Tutte–Berge formula | `ν(G) = (n − max_S(o(G−S)))/2` |
| Dulmage–Mendelsohn | Decomposition of a bipartite graph into matched/unmatched regions |
| F-factor | Match each vertex exactly `f(v)` times |
| `Δ`-matroid | Abstract generalisation behind matchings (heavy) |

## Complexity Snapshot

| Algorithm | Time | Space | Applies to |
|-----------|------|-------|------------|
| Kuhn (DFS augmenting) | `O(V·E)` | `O(V)` | bipartite |
| Hopcroft–Karp | **`O(E√V)`** | `O(V)` | bipartite |
| Dinic on the flow network | `O(E√V)` | `O(V+E)` | bipartite (identical to HK) |
| Hungarian (`O(n³)`) | `O(n³)` | `O(n²)` | bipartite, dense, min-cost |
| Hungarian (`O(n³)` Jonker–Volgenant) | `O(n³)` | `O(n²)` | assignment, dense |
| Min-cost max-flow | `O(F·E log V)` | `O(V+E)` | bipartite, sparse |
| General matching (blossom) | `O(V³)` | `O(V²)` | any graph |
| General matching (Micali–Vazirani) | `O(√V·E)` | `O(V+E)` | any graph |
| Max matching via matrix mult | `O(n^{2.37})` | `O(n²)` | any graph (asymptotic best) |
| Perfect matching existence | `O(E√V)` bipartite, `O(V³)` general | | |

**Why bipartite is special:** in a bipartite graph the alternating-path structure is "clean" —
an alternating path from an unmatched left vertex can only end at an unmatched right vertex.
In a general graph it can end at the *same* side, producing an **odd cycle**, which is exactly the
obstruction blossom algorithms must handle.

## Algorithms Covered

### Kuhn's algorithm (the baseline)
```java
for each u in U:
    if (tryKuhn(u)) matched++;
boolean tryKuhn(u):
    if (seen[u]) return false
    seen[u] = true
    for v in adj[u]:
        if (matchR[v] == -1 || tryKuhn(matchR[v])) { matchR[v] = u; return true }
    return false
```
`O(V·E)` worst case. The `seen[]` array must be **reset per starting vertex** — forgetting this
is the single most common bug in this topic.

### Hopcroft–Karp
Layer the graph by distance from the free-left set (`dist[]` via BFS), then DFS along
dist-increasing edges only, finding a maximal set of **vertex-disjoint shortest** augmenting paths
per phase. `O(√V)` phases. This is *exactly* Dinic on the matching flow network — the unit-network
`O(E√V)` theorem applies directly.

### König's theorem (via min cut)
With `M` maximum and `(S, T)` the min cut of the flow network:
```
cover = (U ∩ T) ∪ (V ∩ S)
```
Proof of the cover property: if `u ∈ U ∩ S` then `u` is unmatched (its `s→u` arc carries no flow,
so it is unsaturated, so `u` is residual-reachable ⇒ `u ∈ S`). If `v ∈ V ∩ T` then `v` is
unmatched. So every edge `(u,v)` has an endpoint in the cover.
Proof of size: conservation gives `|cover| = |M|`.

## Files

| File | Purpose |
|------|---------|
| `THEORY.md` | Augmenting paths, Berge, König, blossom, complexity landscape |
| `EXERCISES.md` | Implement Kuhn/HK/Hungarian, hand-trace, edge cases |
| `QUIZ.md` | 15 questions on invariants, complexity, counter-examples |
| `FLASHCARDS.md` | ~60 rapid-recall rows |
| `MATH_FOUNDATION.md` | Berge proof, König proof, `O(√V)` phase analysis, Tutte–Berge |
| `CODE_DEEP_DIVE.md` | Annotated Java (Kuhn, HK, Hungarian, blossom sketch) + pitfalls |
| `DIAGRAMS/` | Alternating paths, blossom contraction, Dulmage–Mendelsohn |