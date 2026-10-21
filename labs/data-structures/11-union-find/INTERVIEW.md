# Interview Questions: Union-Find (Disjoint Set Union)

## LeetCode Problem Map
| Problem | Difficulty | Company Signal | Pattern |
|---------|-----------|----------------|---------|
| [LC 200 Number of Islands](https://leetcode.com/problems/number-of-islands/) | Medium | Amazon, Meta, Google, Microsoft, Apple | Union-Find / DFS on grid |
| [LC 547 Number of Provinces](https://leetcode.com/problems/number-of-provinces/) | Medium | Amazon, Meta, Google, Microsoft | Union-Find on adjacency matrix |
| [LC 261 Graph Valid Tree](https://leetcode.com/problems/graph-valid-tree/) | Medium | Amazon, Google, Meta, Microsoft | Union-Find cycle detection |
| [LC 323 Number of Connected Components](https://leetcode.com/problems/number-of-connected-components-in-an-undirected-graph/) | Medium | Amazon, Meta, Google, Microsoft | Union-Find counting |
| [LC 128 Longest Consecutive Sequence](https://leetcode.com/problems/longest-consecutive-sequence/) | Medium | Google, Amazon, Meta, Microsoft | Union-Find with HashMap |
| [LC 684 Redundant Connection](https://leetcode.com/problems/redundant-connection/) | Medium | Amazon, Meta, Google, Microsoft | Union-Find cycle finding |
| [LC 839 Similar String Groups](https://leetcode.com/problems/similar-string-groups/) | Hard | Google, Amazon, Meta | Union-Find with similarity check |
| [LC 721 Accounts Merge](https://leetcode.com/problems/accounts-merge/) | Medium | Amazon, Meta, Google, Microsoft | Union-Find email grouping |
| [LC 305 Number of Islands II](https://leetcode.com/problems/number-of-islands-ii/) | Hard | Amazon, Google, Meta | Online Union-Find (dynamic grid) |
| [LC 399 Evaluate Division](https://leetcode.com/problems/evaluate-division/) | Medium | Amazon, Google, Meta, Microsoft | Weighted Union-Find |
| [LC 924 Minimize Malware Spread](https://leetcode.com/problems/minimize-malware-spread/) | Hard | Google, Amazon, Meta | Union-Find with size tracking |
| [LC 990 Satisfiability of Equality Equations](https://leetcode.com/problems/satisfiability-of-equality-equations/) | Medium | Amazon, Meta, Google | Union-Find constraint propagation |
| [LC 1101 The Earliest Moment When Everyone Become Friends](https://leetcode.com/problems/the-earliest-moment-when-everyone-becomes-friends/) | Medium | Amazon, Google, Meta | Union-Find with timestamp sorting |

## NeetCode Reference
NeetCode 150: Graph category includes Number of Islands, Number of Connected Components, and Redundant Connection.

## Company-Specific Questions

### Google
- How does the Union-Find data structure work? Explain path compression and union by rank
- Design a weighted Union-Find for evaluating division ratios (LC 399)
- Implement a DSU with rollback (persistent/historical DSU for offline dynamic connectivity)
- How would you detect cycles in an undirected graph using DSU?

### Microsoft
- Number of connected components in an undirected graph (LC 323) — both DFS and DSU approaches
- Graph valid tree — why does DSU work naturally for this problem?
- Redundant connection — explain why the first edge connecting already-connected nodes creates a cycle

### Meta
- Number of islands — compare DSU vs DFS approaches; when would you prefer DSU?
- Accounts merge — how to map emails to accounts and merge using DSU
- Satisfiability of equality equations — DSU with union for ==, check for violations with !=

### Amazon
- Design a social network friend recommendation system using Union-Find
- Find the earliest time when all nodes in a graph are connected (LC 1101)
- How would you implement a Union-Find that supports component size queries?

### Apple
- How would you Union-Find to merge contacts that share phone numbers or emails?
- Design a maze generation algorithm using Union-Find (randomized Kruskal's)
- How would you implement dynamic graph connectivity (add edges, query connectivity, no deletion)?

### Oracle
- What is the inverse Ackermann function α(n) and why is it the amortized time bound for DSU?
- How would you implement DSU for a database schema migration system (dependency resolution)?
- Compare DSU path compression vs union by rank — which is more important for performance?

## Real Production Scenarios

- **Scenario 1: Social Network Friend Groups** — A social network uses Union-Find to maintain user clusters. When user A becomes friends with user B, their groups are unioned. "Mutual friend" recommendations query whether two distance-2 users belong to different groups (would-be friends).

- **Scenario 2: Image Segmentation** — An image processing pipeline segments a photo by treating each pixel as a DSU element. Adjacent pixels with similar color/ intensity are unioned. After processing all pixels, each connected component (shared root) represents a segment.

- **Scenario 3: Compiler Type Inference** — A compiler uses Union-Find for type unification in Hindley-Milner type inference. When two type variables must be equal, they are unioned. Type constraints are propagated through the DSU until a concrete type is resolved or a contradiction (cycle) is detected.

## Interview Tips

- Time: O(α(n)) per operation — effectively O(1) amortized with both path compression and union by rank
- Space: O(n) for parent and rank/size arrays
- Common edge cases: single element, self-union, unioning already-connected elements, large n (2D grid → 1D index)
- Always use both path compression AND union by rank/size for optimal performance
- For 2D grid problems: convert (row, col) → ID = row * cols + col
- DSU is monotonic — it can only merge sets, not split them (use rollbacks or persistent DSU for undo)
- DSU works for undirected graphs only; directed graphs need different cycle detection

## Java-Specific Considerations

- No standard DSU in Java — implement from scratch
- Typical implementation: `int[] parent, rank;` initialized with `parent[i] = i; rank[i] = 0;`
- Use `ArrayList<Integer>` for dynamic size DSU (add new elements on the fly)
- `Arrays.fill(parent, -1)` — use -1 to indicate root for 0-indexed elements
- For weighted DSU (LC 399): store `double[] weight` where weight[i] = value(parent[i]) / value(i)
- For 2D grid: use `int id = row * cols + col` mapping; allocate array of size `rows * cols`
- Recursive find: `int find(int x) { if (parent[x] != x) parent[x] = find(parent[x]); return parent[x]; }`
- Iterative find avoids stack overflow: `while (parent[x] != x) { int p = parent[x]; parent[x] = parent[parent[x]]; x = parent[x]; }`
- Union by size: `if (size[x] < size[y]) swap(x, y); parent[y] = x; size[x] += size[y];`
