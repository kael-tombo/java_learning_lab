# QUIZ — Data Structures Track
> 15 questions with answers. Track `data-structures`.

1. BFS/DFS time? → O(V+E) with adjacency lists.
2. BFS first-visit property? → Distance equals shortest path (unweighted).
3. DFS gray-to-gray edge means? → Back edge → cycle present.
4. Topo sort requires? → DAG; reverse finish order works.
5. Adjacency list vs matrix? → List O(V+E) sparse; matrix O(1) edge test, O(V²) space.
6. DSU amortized cost? → O(α(n)) with union-by-size + compression.
7. Heap insert/extract? → Both O(log n) via sift.
8. BST worst case? → O(n) degenerate; balanced trees give O(log n).
9. Segment tree query/update? → O(log n); build O(n).
10. Trie lookup cost? → O(L) key length, independent of n.
11. Why ArrayDeque for BFS? → O(1) FIFO without sync overhead.
12. Iterative vs recursive DFS? → Recursive risks stack overflow on deep graphs.
13. Detect bipartite? → BFS 2-coloring; conflict = odd cycle.
14. When is DSU better than BFS for connectivity? → Online unions + queries, near-O(1) each.
15. Heap vs sorted array for k-way merge? → Heap O(n log k) beats repeated sorting.

## Scoring
- 13-15: expert. 10-12: practitioner. < 10: revisit THEORY + flashcards.

## Follow-ups
- Prove one bound on paper; implement one variant from memory.
