# Flashcards — Heavy-Light Decomposition

Format: **Q → A**.

---

| # | Question | Answer |
|---|----------|--------|
| 1 | HLD = heavy-light | decompose a tree into heavy chains and light edges |
| 2 | Heavy child | child with largest subtree |
| 3 | Light edges per root path | ≤ log₂ n |
| 4 | Chain | maximal heavy-edge path |
| 5 | Chain head | the shallowest vertex of the chain |
| 6 | top[v] | head of v's chain |
| 7 | pos[v] | v's index in the base array |
| 8 | Base array | Euler-like order where each chain is contiguous |
| 9 | Path query with HLD | O(log n) chain segments × O(log n) range query = O(log² n) |
| 10 | LCA via HLD | climb to the same chain — O(log n) |
| 11 | Subtree query | Euler-tour segment tree — one range query |
| 12 | HLD preprocess | two DFS passes — Θ(n) |
| 13 | Light edge halves subtree | so ≤ log n light edges per path |
| 14 | Jump to chain head | the inner loop of HLD path queries |
| 15 | Why chains are contiguous | second DFS visits heavy child first |
| 16 | HLD for paths, Euler tour for subtrees | the right-structure-for-the-query rule |
| 17 | Segment tree on base array | the aggregate structure for chain segments |
| 18 | Path query decomposition | u→LCA and LCA→v side, each O(log n) segments |
| 19 | LCA is on | the chain where u and v first meet |
| 20 | Chain jump count per query | O(log n) |
| 21 | Binary lifting LCA time | O(log n) with O(n log n) preprocess |
| 22 | HLD LCA time | O(log n) with O(n) preprocess |
| 23 | Subtree of v in Euler tour | one contiguous range tin[v]..tout[v] |
| 24 | Euler tour first-visit | tin[v] — the Euler-tour index |
| 25 | Segment tree range query | O(log n) |
| 26 | HLD update a vertex value | one point update — O(log n) |
| 27 | HLD path-add query | O(log² n) with a lazy segment tree |
| 28 | HLD path aggregate | O(log² n) |
| 29 | Heavy edge from v | v → its largest child |
| 30 | Light edge from v | v → any non-largest child |
| 31 | Root of a chain | top[v] — the shallowest heavy-connected vertex |
| 32 | Chain heads count | O(n) worst case, but O(log n) per path |
| 33 | Path from root to v crosses | ≤ log n chains |
| 34 | Two vertices on the same chain when | their chain heads are equal |
| 35 | Climb loop | while top[u] != top[v]: move the deeper chain-head vertex up |
| 36 | LCA when top[u]==top[v] | the shallower of u, v |
| 37 | HLD needs | a rooted tree and a base-array segment tree |
| 38 | Online updates | HLD handles them via the segment tree |
| 39 | Path queries without HLD | binary lifting or Euler-tour RMQ for LCA only |
| 40 | When to pick HLD | path aggregates on a static tree with updates |
| 41 | When to pick Euler tour | subtree aggregates |
| 42 | When to pick binary lifting | LCA only, no path aggregates |
| 43 | HLD inventor | Sleator and Tarjan, 1983 |
| 44 | HLD in competitive programming | the standard path-query tool |
| 45 | Heavy-light on a path graph | one chain — the segment tree does everything |
| 46 | Heavy-light on a star | n chains — each leaf is its own chain |
| 47 | Star worst case for HLD | still O(log n) jumps — the bound holds |
| 48 | Path graph best case | HLD degenerates to a flat segment tree — O(log n) |
| 49 | HLD chain count | equal to the number of light edges + 1... actually number of chain heads |
| 50 | Number of light edges | O(n) — one per non-heavy child |
| 51 | Chain decomposition of a path | a single chain |
| 52 | Chain decomposition of a balanced binary tree | O(log n) chains on the deepest root path? No — O(log n) light edges on any root path, hence O(log n) chains |
| 53 | Each chain is a | contiguous interval in the base array |
| 54 | Path from u to v touches | O(log n) chains |
| 55 | Aggregate along u→v | combine O(log n) chain aggregates, each O(log n) |
| 56 | Total | O(log² n) |
| 57 | With a cleverer structure (splay/link-cut trees) | O(log n) path queries — an alternative to HLD |
| 58 | Link-cut trees | the dynamic alternative to HLD for path queries |
| 59 | ETT: Euler tour tree | another alternative — harder to implement |
| 60 | HLD vs link-cut | HLD is static-tree simpler; link-cut handles edge updates |
| 61 | HLD path update = path query | both O(log² n) with a lazy segment tree |
| 62 | Subtree path queries (path to root) | HLD handles them as a special case of u→v with v=root |
| 63 | Aggregate operator requirements | associative, with an identity — segment tree needs them |
| 64 | Commutative? Not required for path queries | directed paths need only associativity |
| 65 | LCA used in HLD path query | the climb-until-same-chain loop finds it implicitly |
| 66 | Path query includes LCA vertex once? | handle the LCA endpoint carefully — off-by-one at the junction |
| 67 | Common HLD bug | double-counting the LCA — subtract it once |
