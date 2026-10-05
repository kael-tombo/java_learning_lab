# THEORY — Depth-First Search (DFS)
> Mechanics + invariants + complexity proof sketch for DFS.

## 1. Problem Statement
- Input: graph `G=(V,E)`, source(s); directed or undirected.
- Output: discovery/finish times, parent forest, cycle flag, components/order.
- Success: full traversal `O(V+E)`, correct colors, iterative + recursive forms.
- Contrast: BFS gives distance; DFS gives structure (paths, topo, SCC base).

## 2. Algorithm Mechanics
- Colors: WHITE unvisited, GRAY on stack, BLACK finished.
- Recursive: `visit(u): color=GRAY; for v∈Adj[u]: if WHITE visit(v); color=BLACK; time++`.
- Iterative: explicit stack of `(node, iterator-index)` to simulate finish times.
- Preorder (enter) vs postorder (exit) — topo uses reverse postorder on DAGs.
- Back edge (`GRAY→GRAY`) = cycle (directed); undirected needs parent check.
- Forest: outer loop launches `visit` per WHITE vertex (disconnected graphs).
- Edge classification: tree/back/forward/cross from times (directed).

## 3. Invariants
- I1 (stack = path): GRAY nodes form current root→current path exactly.
- I2 (finished safe): BLACK `u` has all descendants explored; `finish[u]` final.
- I3 (parenthesis): intervals `[disc,fin]` nested or disjoint — never partial overlap.
- Init: all WHITE, empty stack — holds.
- Maintenance: pushing grays extends path; popping blackens with complete subtree.
- Termination: no WHITE reachable from stack → pop; global WHITE empty → done.
- Cycle theorem: back edge ⟺ directed cycle (GRAY target = ancestor on stack).

## 4. Worked Trace
- `1→2→3, 1→3`: visit 1(G), 2(G), 3(G→B), 2B, 1B. Postorder 3,2,1.
- Cycle `1→2→3→1`: at 3 see GRAY 1 → cycle flag.
- Disconnected `4` alone: second forest tree after first finishes.
- Undirected triangle: parent-skipping avoids false cycle on tree edge.

## 5. Complexity Proof Sketch
- Each vertex transitions WHITE→GRAY→BLACK once → `O(V)` vertex work.
- Each edge examined once from its tail (directed) / twice (undirected) → `O(E)`.
- Total `O(V+E)` adj list; `O(V²)` matrix.
- Space: colors+parent `O(V)` + stack depth `O(V)` worst (chain) — overflow risk recursive.
- Parenthesis theorem: via DFS interval nesting proof (discovery/finish counters).
- Topo claim: DAG has no back edge → reverse postorder respects all edges.

## 6. Correctness Argument
- Induction on finish order using I1–I3; cycle detection sound+complete by back-edge theorem.
- Counter-example: marking visited only at finish (no GRAY) misses cycle vs cross distinction.

## 7. When NOT to Use
- Unweighted shortest → BFS, not DFS (DFS path can be arbitrarily long).
- Very deep graphs in Java → iterative (recursion `StackOverflowError` ~10k depth).
- Shortest/level tasks → BFS; MST → Kruskal/Prim.

## 8. Java Notes
- Recursive elegant but risky; iterative `ArrayDeque<int[]>` for depth > few thousand.
- `boolean[] onStack` + `visited[]` = two-color manual scheme; or `byte[] state`.
- Adj list `List<int[]>`/`List<List<Integer>>` for cache friendliness.

## 9. Common Misconceptions
- "DFS finds shortest path" — no, arbitrary path.
- "One visited flag suffices" — need on-stack to detect cycles correctly (directed).
- "Iterative with single stack matches recursion" — needs iterator stack for postorder.

## 10. Checklist
- [ ] 3-color (or visited+onStack) implemented.
- [ ] Recursive + iterative traces match.
- [ ] Cycle test on directed vs undirected correct.
- [ ] Forest loop over all vertices present.
