# Flashcards — Depth-First Search (DFS)

- Q: DFS time complexity (graph)? → A: O(V + E)
- Q: DFS space complexity (recursive)? → A: O(V) — recursion stack
- Q: DFS shortest path guarantee? → A: No — does NOT guarantee shortest path
- Q: DFS vertex colors (CLRS)? → A: WHITE=undiscovered, GRAY=in stack, BLACK=finished
- Q: Back edge in directed graph? → A: Edge to ancestor in DFS tree → indicates CYCLE
- Q: Why sink grid in Number of Islands? → A: O(1) space vs O(m×n) visited array
- Q: Union-Find time for Number of Islands? → A: O(m × n × α(m×n)) ≈ O(m × n)
- Q: Topological sort requirement? → A: Graph must be a DAG (no cycles)
- Q: Topological sort via DFS? → A: Reverse post-order (reverse of finish times)
- Q: Recursive vs iterative DFS? → A: Iterative avoids stack overflow, more control
- Q: DFS vs BFS for cycle detection? → A: DFS detects cycles naturally via GRAY back edges
- Q: Tree edge, forward edge, cross edge? → A: Tree=edge in DFS tree; Forward=descendant (non-tree); Cross=between subtrees
- Q: When to use DFS over BFS? → A: Path existence, topological sort, cycle detection, maze solving, less memory for deep graphs
- Q: DFS on directed vs undirected cycle detection? → A: Directed: back edge to GRAY = cycle. Undirected: edge to visited non-parent = cycle
- Q: Kosaraju's algorithm for SCC? → A: 1) DFS for finish times 2) Reverse graph 3) DFS in reverse finish order