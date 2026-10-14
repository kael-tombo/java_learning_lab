# MINI_PROJECT — MST Variants
> Build Kruskal, dense Prim, and second-best MST over one edge-list format, with cross-agreement checks.

## Inputs
- Edge-list file (`u v w` per line); reference graph with 7 edges from MOCK Q1 (expected MST weight 8, second-best 9).
- Random graphs (n = 50/200/1000, fixed seed) for timing only.

## Build steps
1. Implement Kruskal with path-compressed union-find; verify mst_weight=8 with 4 edges on the reference graph.
2. Implement dense O(V^2) Prim; verify prim_weight=8 on the same graph.
3. Implement second-best MST by max-edge-on-path swaps over the Kruskal tree; verify second_best=9.
4. Add `--check`: asserts both MST weights equal and every non-tree edge swap is evaluated; prints the swap table (added edge, removed edge, candidate).
5. Time both MST methods on the random graphs and record median ms with machine/JDK noted.

## Acceptance criteria
1. Reference graph prints weight 8 from both Kruskal and Prim.
2. Second-best prints 9 with a swap table showing each candidate and the winning swap.
3. `--check` fails loudly (nonzero exit) if the two weights ever disagree.
4. Timing table has 3 sizes x 2 methods of measured medians, no invented cells.
5. Union-find includes both path compression and union by rank/size, stated in a comment.
6. Disconnected input is rejected with the component count, not silently spanned.

## Analysis prompts
1. Which method wins at each size, and does the winner match the big-O prediction?
2. For the winning swap in Q3, trace the cycle and name the removed edge.
3. What changes if all weights tie (uniqueness and second-best definition)?

## Non-goals
- Boruvka implementation (specified conceptually), dynamic MST, and directed arborescences.

## Worked reference (verified outputs)
- Reference graph prints mst_weight=8 edges=4 from Kruskal and prim_weight=8 from dense Prim.
- Second-best prints 9; the swap table names the winning (added, removed, candidate) triple explicitly.

## Stretch
- Implement Boruvka phases and compare phase counts against Kruskal's union steps on the random graphs.
- Add edge-sensitivity: for each MST edge report the cheapest replacement (or none) from the swap data.
