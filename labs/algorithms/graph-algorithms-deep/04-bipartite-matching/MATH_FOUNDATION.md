# Math Foundation — Bipartite Matching

Derivations, applicability, and counter-examples for the formulas this lab relies on.

---

## Berge's theorem

If M is not maximum, take M* larger. M Δ M* is a union of alternating paths and even cycles. The size difference |M*| - |M| = (number of augmenting paths in M Δ M*) - (number of augmenting paths in M Δ M* in the other direction) > 0, so at least one M Δ M* component is an augmenting path for M.

The converse is direct: an augmenting path for M can be flipped to enlarge M.

## Hopcroft–Karp phase bound

Let d_i be the length of the shortest augmenting path before phase i. After a phase, d_{i+1} > d_i (each phase augments along a maximal set of shortest disjoint paths). After √V phases, d > √V, so any remaining augmenting path uses > √V distinct L-vertices, meaning at most |M*|/d ≤ V/d < √V augmentations remain.

Hence at most O(√V) phases each of cost O(E) — total O(E·√V).

## König's theorem

Let M* be max and define: U = unmatched L-vertices, Z = L ∪ R reachable from U by alternating paths, C = (L\Z) ∪ (R ∩ Z). C is a vertex cover: any L-edge from L\Z must go to R\Z, but then it would be reachable... any R in R∩Z is in C, and any L in L\Z is in C. |C| = |M*| by construction, since each cover vertex is matched. Hence min cover ≤ |M*| ≤ max matching ≤ min cover.

The middle inequality min vertex cover ≥ max matching is the trivial direction, so all are equal.

## Symmetric difference structure

Edges of M Δ M* form vertex-disjoint alternating paths and even cycles because every vertex has degree ≤ 2 in M Δ M* (at most one M-edge and one M*-edge) and the edges alternate by construction.

Each component is a path, an even cycle, or a single edge; size change comes only from augmenting M-paths.

## Max flow reduction

Add source s → every L-vertex (capacity 1), every R-vertex → sink t (capacity 1), and L→R for each original edge (capacity 1). A unit of flow uses one s→L→R→t path, giving a matching edge; integrality of max flow makes the correspondence exact.

The max-flow value equals the matching size, so polytime max flow gives polytime matching.
