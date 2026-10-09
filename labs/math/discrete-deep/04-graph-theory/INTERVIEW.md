# Interview: Graph Theory

## Conceptual Questions

**Q: BFS vs DFS — when do you use which?**
A: BFS when edges are unweighted and you need fewest edges (shortest paths, level structure, bipartite coloring, neighbor explosion with a depth budget). DFS when you need order and structure: topological sort, cycle detection (back edge to gray), strongly connected components, articulation points. Rule of thumb: distances → BFS; dependencies/cycles → DFS.

**Q: Why does Dijkstra fail with negative weights? Give a counterexample.**
A: Once a node is settled the algorithm assumes no later discovery can improve it; a negative edge can. Graph: s→a weight 1, s→b weight 4, a→b weight −3. Dijkstra settles a (1), then pops b at 4 via s, but the true distance s→a→b is −2, which was found after b settled. Bellman–Ford (O(V·E)) handles negatives and detects negative cycles; SPFA/DAG shortest paths are alternatives in restricted cases.

**Q: What's the complexity of BFS and what does it assume?**
A: O(V + E) time, O(V) space — assuming adjacency lists. With an adjacency matrix, neighbor scan costs Θ(V) per vertex so it becomes O(V²). Each vertex is enqueued at most once (if marked on push) and each edge examined once (twice for undirected).

**Q: Prove or explain max-flow = min-cut.**
A: For any s–t cut, flow ≤ capacity of the cut (flow conservation forces net flow out of S to be ≤ sum of capacities leaving S). So max flow ≤ min cut. Conversely, when Ford–Fulkerson finds no augmenting path, the set of nodes reachable from s in the residual graph defines a cut whose saturated forward edges carry exactly the flow value — flow = cut capacity. Equal bounds force equality.

**Q: What is Hall's theorem and when do you use it?**
A: A bipartite graph (X, Y) has a matching covering X iff for every S ⊆ X, |N(S)| ≥ |S|. Use it to prove an assignment exists (or that it fails, by exhibiting a squeezed subset S). It underpins scheduling/assignment problems and gives a characterization rather than just an algorithm.

**Q: How many spanning trees does a labeled graph on n vertices have (Cayley)? Give an example count.**
A: nⁿ⁻² for the complete graph Kₙ (Cayley, 1857). For n = 4: 4² = 16. General graphs: Kirchhoff's matrix–tree theorem = any cofactor of the Laplacian L = D − A.

## Applied / Coding Questions

**Q: Trace Dijkstra's invariant. Where exactly does "mark on enqueue" vs "on dequeue" matter?**
A: Dijkstra: the invariant is on *pop order* — skip stale entries (`if (d != dist[v]) continue`). BFS: marking must happen at enqueue; marking at dequeue lets two parents enqueue the same node → duplicate queue entries and incorrect parent pointers. For weighted graphs, lazy re-insertion replaces decrease-key; the stale-skip line is what makes it correct.

**Q: Detect whether a directed graph has a cycle, in O(V+E).**
A: Kahn's algorithm: compute in-degrees, push zeros, decrement successors; if fewer than V nodes are emitted, the remainder is a cycle. Or DFS three-coloring: any edge to a gray node is a back edge → cycle. Both O(V + E).

**Q: Your BFS stack overflows on a large input. Fix it.**
A: Recursion depth is O(V) on a chain-shaped graph. Convert to an explicit `ArrayDeque` stack/queue (iterative BFS/DFS), or raise `-Xss` as a stopgap. Also ensure you're not re-enqueueing (the missing-visited bug inflates depth/queue size).

**Q: Choose a representation for: (1) web crawl frontier, (2) road network with 5M intersections, (3) 100-node network with all-pairs queries.**
A: (1) Sparse, dynamic, huge → adjacency lists with a hash-based frontier; CSR once frozen. (2) E ≈ 3V (streets) → primitive adjacency arrays; A*/Dijkstra with heuristics; matrix impossible (2.5×10¹³ cells). (3) V = 100, dense queries → Floyd–Warshall precompute O(V³) = 10⁶ ops, then O(1) lookups; matrix storage is 10⁴ cells.

**Q: Kruskal vs Prim — when?**
A: Equivalent complexity: Kruskal O(E log E) (dominated by sort; union–find is ~O(E)), Prim O(E log V). Kruskal wins with edge-list/sparse input and stops early on disconnected graphs (forest); Prim wins when you already have an adjacency structure and a dense graph — its O(V²) array form beats the heap form when E ≈ V². Correctness of both rests on the cut property.

**Q: How would you test a graph library?**
A: Golden fixture (the lab's 6-node graph → distances 0,3,2,8,10,13, MST weight 13); cross-algorithm oracle (Dijkstra vs Floyd–Warshall vs brute-force path enumeration for V ≤ 6); property tests on random graphs (flow ≤ cut always, flow = min cut at termination; BFS dist ≤ weighted Dijkstra on positive weights; Kruskal weight = Prim weight); and adversarial cases: cycle-only graphs, self-loops, parallel edges, disconnected components, all-equal weights, and a negative edge that must be rejected by Dijkstra.
