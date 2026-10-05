# QUIZ — Minimum Spanning Tree (15Q + Answers)
> Complexity, invariants, counter-examples. Answers at end.

## Questions
1. Cut property: lightest crossing edge belongs to ___. (A) no MST (B) some MST (C) all paths (D) longest path
2. Kruskal sorts by: (A) weight asc (B) weight desc (C) label (D) degree
3. Kruskal invariant: taken set ⊆ ___. (A) some MST (B) shortest path (C) max cut (D) cycle
4. Complexity Kruskal: (A) O(E log E) (B) O(V) (C) O(VE) (D) O(V³)
5. Prim grows from: (A) heaviest edge (B) tree fringe min (C) random node (D) all at once
6. Prim+PQ complexity: (A) O(E log V) (B) O(VE) (C) O(2ⁿ) (D) O(V+E)
7. Union-Find per-op amortized: (A) O(log n) worst (B) ~α(V) (C) O(n) (D) O(1) worst
8. Counter-example: MST on ___ needs different algorithm. (A) undirected (B) directed (C) negative weights (D) ties
9. Heaviest edge on any cycle is: (A) always in MST (B) never needed (C) always unique (D) shortest
10. Distinct weights ⇒ MST is ___. (A) non-unique (B) unique (C) empty (D) cyclic
11. Disconnected graph yields: (A) exception only (B) MSF (C) single tree (D) no output
12. True/False: negative weights break Kruskal.
13. True/False: Prim stale fringe entries must be skipped.
14. DSU needs: (A) path compression + union by rank (B) hashing only (C) sorting only (D) BFS
15. Triangle AB1 BC2 AC3 MST weight = ___. (A) 3 (B) 4 (C) 6 (D) 5

## Answers
1-B. 2-A. 3-A. 4-A (sort dominates). 5-B. 6-A. 7-B.
8-B (directed → arborescence). 9-B (cycle property). 10-B. 11-B.
12-False (cycles only matter, weights arbitrary). 13-True. 14-A. 15-A (1+2).
- Scoring: 26–30 mastery; 20–25 review cut proof; <20 redo E1–E2 traces.

## Follow-ups
- State cycle property. Give tied-weight graph with 3 distinct MSTs.
