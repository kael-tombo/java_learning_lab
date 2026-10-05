# QUIZ — Graph Algorithms Deep Track
> 15 questions with answers. Track `graph-algorithms-deep`.

1. Kruskal bound? → O(E log E) sort-dominated; DSU near-O(1) each.
2. Cut property? → Lightest edge crossing any cut is in some MST.
3. Dijkstra precondition? → Nonnegative weights; else Bellman-Ford.
4. Dijkstra heap bound? → O((V+E) log V) binary heap.
5. Why skip stale heap entries? → A shorter path already settled that node.
6. Bellman-Ford bound? → O(VE); extra pass detects negative cycles.
7. Floyd-Warshall? → O(V³) all-pairs; handles negatives (no neg cycles).
8. Dinic bound? → O(V²E) general; faster on unit networks.
9. Residual back edge? → Allows undo; carries pushed flow back.
10. Min-cut certificate? → Reachable set from s in final residual = min cut.
11. Hopcroft-Karp? → O(E√V) via layered batch augments.
12. Topo needs DAG? → Yes; Kahn leftover count signals cycle.
13. Undirected cycle via DSU? → Union endpoints; already-connected = cycle.
14. HLD query cost? → O(log² n) path via chains + segment tree.
15. When push-relabel over Dinic? → Dense graphs; gap/highest-label variants.

## Scoring
- 13-15: expert. 10-12: practitioner. < 10: revisit THEORY + flashcards.

## Follow-ups
- Prove one bound on paper; implement one variant from memory.
