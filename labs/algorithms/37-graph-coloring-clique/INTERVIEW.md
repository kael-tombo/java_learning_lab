# Interview Questions: Graph Coloring and Clique

## LeetCode Problem Map
| Problem | Difficulty | Company Signal | Pattern |
|---------|-----------|----------------|---------|
| LC 37 Sudoku Solver | Hard | Google, Microsoft | Constraint propagation / coloring |
| LC 22 Generate Parentheses | Medium | Google, Meta, Amazon | Catalan / backtracking |
| LC 1615 Max Network Rank | Medium | Google, Amazon | Edge count per node |
| LC 685 Redundant Connection II | Hard | Google | Union-Find / graph theory |

Note: Graph coloring and clique have limited direct LC representation but are important theoretical topics.

## NeetCode Reference
- LC 37 Sudoku Solver (NeetCode 150)

## Company-Specific Questions
### Google
- Design a graph coloring algorithm for register allocation in a compiler
- How would you check if a graph is bipartite? (2-colorable)
- Find the maximum clique in a graph using Bron-Kerbosch algorithm
- DSatur algorithm for graph coloring with minimal colors
- Design a Sudoku solver using constraint satisfaction

### Microsoft
- How does Windows scheduler use graph coloring for resource allocation?
- Design a frequency assignment algorithm for wireless networks
- Explain the relationship between graph coloring and constraint satisfaction
- Find all maximal cliques in a social network graph

### Meta
- Graph coloring for social network group detection
- Find cliques in Facebook's social graph for community detection
- How would you detect overlapping communities using coloring?
- Bipartite checking for recommendation system fairness

### Amazon
- Graph coloring for warehouse shelf assignment
- How would you assign frequencies to warehouse robots to avoid interference?
- Bron-Kerbosch for finding product bundles (cliques in co-purchase graph)
- Detect conflicting shipments using graph coloring

### Apple
- Register allocation in LLVM compiler (graph coloring)
- How would you color a map for the Maps app?
- Memory-efficient coloring algorithms for mobile
- Frequency allocation for Bluetooth/WiFi coexistence

### Oracle
- How does Oracle manage concurrent transaction conflicts (graph coloring)?
- Design a lock manager using graph coloring concepts
- Explain how databases detect deadlocks using wait-for graphs
- Concurrency control using resource allocation graphs

## Real Production Scenarios
- Scenario 1: Register allocation in compilers - using Chaitin's graph coloring algorithm to allocate CPU registers to variables in a JIT compiler, spilling to memory when insufficient registers exist
- Scenario 2: Exam scheduling - modeling course-exam timetabling as a graph coloring problem where courses sharing students must have different exam slots, minimizing total exam duration
- Scenario 3: Wireless frequency allocation - debugging a DSatur coloring algorithm that fails to find a valid 3-coloring for a cell tower network due to incorrect interference graph construction

## Interview Tips
- A graph is bipartite iff it has no odd cycles; check with BFS coloring (2 colors)
- Greedy coloring with Welsh-Powell ordering (sort by degree descending) uses at most max(degree)+1 colors
- Bron-Kerbosch for maximal cliques: pivot selection (Tomita variant) improves performance
- Common edge cases: empty graph, complete graph, bipartite vs non-bipartite, disconnected components

## Java-Specific Considerations
- Bipartite check: `int[] color` array initialized to -1; BFS assigning colors 0/1
- Greedy coloring: `int[] result` with `boolean[] available` for checking neighbor colors
- Bron-Kerbosch: `Set<Integer>` or `BitSet` for R (current), P (candidates), X (excluded) sets
- `BitSet` is preferred for Bron-Kerbosch due to efficient intersection operations
- DSatur: `PriorityQueue` ordered by degree of saturation (number of distinct neighbor colors)
- Pitfall: using adjacency matrix for large graphs (O(V^2) memory); prefer adjacency list
- Pitfall: Java recursion limit for DFS on large graphs; use iterative stack or increase stack size
