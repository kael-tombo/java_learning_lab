# QUIZ — Topological Sort (15Q + Answers)
> Complexity, invariants, counter-examples. Answers at end — attempt first.

## Questions (2 pts each)
1. Topo order exists ⟺ graph is ___? (A) connected (B) DAG (C) weighted (D) dense
2. Kahn's first step: (A) DFS (B) compute indegrees, queue zeros (C) sort edges (D) transpose
3. Invariant: emitted prefix has ___ incoming edge from remainder. (A) no (B) one (C) all (D) heavy
4. Complexity Kahn (adj list): (A) O(V+E) (B) O(V²) (C) O(E log V) (D) O(VE)
5. DFS topo uses: (A) preorder (B) reverse postorder (C) BFS order (D) sorted labels
6. Cycle `A→B→C→A`: Kahn ends with order size ___. (A) 3 (B) 0 (C) 1 (D) undefined crash
7. Counter-example: topo on ___ graph is meaningless. (A) DAG (B) undirected cyclic (C) empty (D) singleton
8. Lexicographically smallest needs: (A) FIFO (B) PriorityQueue (C) stack (D) random
9. DAG always has: (A) source (indeg-0) (B) Hamiltonian path (C) negative edge (D) bridge
10. Edge `u→v` in DFS DAG satisfies: (A) fin[v]<fin[u] (B) fin[u]<fin[v] (C) equal (D) unrelated
11. `k`-outer loop belongs to: (A) Kahn (B) Floyd-Warshall (C) DFS (D) Prim — sanity distractor, answer B.
12. True/False: partial Kahn output (size<V) proves a cycle.
13. True/False: unique topo order ⟺ DAG has Hamiltonian path.
14. Which detects cycle via back edge? (A) Kahn (B) DFS colors (C) Union-Find (D) PQ
15. Semester batches = ___ BFS layering of Kahn. (A) level (B) greedy (C) random (D) reverse

## Answers
1-B (DAG characterization). 2-B. 3-A (core invariant).
4-A (each vertex/edge once). 5-B. 6-B (no source to start).
7-B (order constraint directed only). 8-B. 9-A (source lemma).
10-A. 11-B (distractor check). 12-True. 13-True.
14-B (→GRAY = ancestor). 15-A.
- Scoring: 26–30 mastery; 20–25 review cycle proofs; <20 redo THEORY §4 + E3.

## Follow-ups
- Prove DAG-has-source lemma in 3 lines. Give 2 valid orders for diamond DAG.
