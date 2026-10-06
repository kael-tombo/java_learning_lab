# Flashcards — Bipartite Matching

Format: **Q → A**.

---

| # | Question | Answer |
|---|----------|--------|
| 1 | Augmenting path | alternating path between two unmatched vertices |
| 2 | Berge's theorem | M max iff no augmenting path exists |
| 3 | Naive matching | O(V·E) |
| 4 | Hopcroft–Karp | O(E·√V) |
| 5 | HK phases | O(√V) |
| 6 | Phase work | Θ(E) |
| 7 | König's theorem | max matching = min vertex cover in bipartite graphs |
| 8 | Vertex cover ≥ matching | |C| ≥ |M| always |
| 9 | Hungarian algorithm | Θ(n³) max-weight perfect matching |
| 10 | Blossom algorithm | general (non-bipartite) matching |
| 11 | Symmetric difference M Δ M* | alternating paths and cycles |
| 12 | Alternating path | edges alternate non-matched/matched |
| 13 | HK BFS layering | distances from unmatched L-vertices |
| 14 | HK phase | vertex-disjoint shortest augmenting paths |
| 15 | NIL distance sentinel | length of shortest augmenting path this phase |
| 16 | Maximal vs maximum matching | maximal ⊭ maximum; augmenting paths bridge them |
| 17 | König construction | reachable L ∪ non-reachable R |
| 18 | Matching edge needs | a distinct cover vertex |
| 19 | Bipartite recognition test | two-colourable graph |
| 20 | Reduces to bipartite matching | worker-job, student-project, task-slot assignment |
| 21 | Not bipartite matching | pairing within one set, or mutual preferences (use stable matching) |
| 22 | Stable matching | Gale–Shapley — different problem from max matching |
| 23 | After augmenting along a path | matching size grows by exactly one |
| 24 | Shortest augmenting path lengths | strictly increase phase to phase |
| 25 | After √V phases | remaining matching needs O(√V) more augmentations |
| 26 | HK DFS from | each unmatched L-vertex, along increasing BFS layers |
| 27 | Vertex-disjoint in a phase | each vertex in at most one augmenting path of the phase |
| 28 | M Δ M* path that grows the matching | an augmenting path for M |
| 29 | M Δ M* on cycles | even alternating cycles — they do not change the size |
| 30 | Odd cycle in a matching | impossible — matchings are sets of disjoint edges |
| 31 | Bipartite graph has | no odd cycles |
| 32 | König's theorem for | bipartite graphs only |
| 33 | General vertex cover minimum | NP-hard |
| 34 | Bipartite vertex cover | polynomial via König |
| 35 | Max flow reduction of matching | source → L, L → R, R → sink, unit capacities |
| 36 | Max matching via max flow | size of max matching = value of max flow |
| 37 | Unit-capacity flow | Dinic runs in O(E·√V) — matches Hopcroft–Karp |
| 38 | Hungarian feasibility invariant | reduced costs stay non-negative |
| 39 | Hungarian relaxations | Θ(n) per matching edge, Θ(n³) total |
| 40 | Assignment problem | max-weight perfect matching in a complete bipartite graph |
| 41 | Bipartite matching is polytime | yes — via augmenting paths or max flow |
| 42 | Unweighted max matching | Hopcroft–Karp |
| 43 | Weighted max matching | Hungarian, Θ(n³) |
| 44 | Min vertex cover output | the König set, size = |M*| |
| 45 | Matching in a tree | greedy by leaves is optimal |
| 46 | Augmenting path in a tree matching | alternate matched/unmatched; unique simple path |
| 47 | Alternating cycle | even cycle of alternating edges — does not change size |
| 48 | M Δ M* when M* > M | at least one more augmenting path for M than for M* |
| 49 | Each HK phase shortens... no — lengthens | the shortest augmenting path strictly |
| 50 | Polynomial-time matching | yes, unlike general vertex cover |
| 51 | Why bipartite helps | alternating-path structure is decidable in polytime |
| 52 | Stable marriage problem | Gale–Shapley O(n²) — different optimality notion |
| 53 | College admissions | stable matching example |
| 54 | Max flow with unit capacities | Dinic O(E·√V) |
| 55 | HK practical on | large sparse bipartite graphs — the standard choice |
