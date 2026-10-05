# FLASHCARDS — Topological Sort (~60)
> Rapid recall: front → back. Cover recurrence, complexity, when-to-use.

| # | Front | Back |
|---|-------|------|
| 1 | Exists iff? | DAG |
| 2 | Kahn step 1? | indegrees + queue zeros |
| 3 | Kahn invariant? | emitted prefix has no incoming from remainder |
| 4 | Kahn time? | O(V+E) |
| 5 | Kahn space? | O(V) + graph |
| 6 | DFS method? | reverse postorder |
| 7 | DFS cycle signal? | edge →GRAY (back edge) |
| 8 | Partial output means? | cycle |
| 9 | Undirected topo? | meaningless (directed only) |
| 10 | Lexicographic? | PQ-Kahn |
| 11 | DAG has? | source (indeg-0) |
| 12 | Finish order DAG edge u→v? | fin[v]<fin[u] |
| 13 | Unique order iff? | Hamiltonian path in DAG |
| 14 | Semester batches? | level-by-level Kahn |
| 15 | Self-loop? | cycle |
| 16 | Parallel edges risk? | double decrement; guard |
| 17 | Forest needed? | yes, loop all V |
| 18 | Validate order how? | all edges forward |
| 19 | Kahn vs DFS cross-check? | both valid (may differ) |
| 20 | Use case? | build systems / task DAGs |
| 21 | Weighted costs? | topo + DP critical path |
| 22 | Dynamic graph? | incremental needed |
| 23 | Queue type default? | ArrayDeque FIFO |
| 24 | Indeg mutate whose? | copy, not caller array |
| 25 | Diamond orders? | ABCD or ACBD both valid |
| 26 | Cycle example? | A→B→C→A → size 0 |
| 27 | Disconnected node? | anywhere valid |
| 28 | Recursion risk? | deep DAG overflow; iterative |
| 29 | Preorder for topo? | no, postorder |
| 30 | Back vs cross? | GRAY=back; BLACK=cross/forward |
| 31 | Lower bound? | Ω(V+E) must inspect all |
| 32 | `n=0`? | [] |
| 33 | `n=1`? | [0] |
| 34 | Leftover nodes =? | cyclic core + dependents |
| 35 | Course Schedule maps to? | Kahn + cycle flag |
| 36 | Kahn early? | queue empty early = cycle |
| 37 | DFS outer loop skips? | misses components |
| 38 | Tie-break documented? | FIFO vs PQ |
| 39 | Reverse graph? | for dependents query |
| 40 | Topo + shortest? | relax in topo order O(V+E) |
| 41 | Longest path DAG? | topo + DP (NP-hard generally) |
| 42 | SCC first? | Kosaraju uses finish order |
| 43 | Indeg zero mid-run? | enqueue immediately |
| 44 | Java PQ cost? | O(log V) per op |
| 45 | Space graph? | O(V+E) adj list |
| 46 | Matrix topo time? | O(V²) |
| 47 | Empty graph edges? | any order valid |
| 48 | Single edge 0→1? | [0,1] only |
| 49 | Two sources 0,1→2? | [0,1,2] or [1,0,2] |
| 50 | Prepend vs append DFS? | prepend on finish |
| 51 | Colors meaning? | W unvisited/G on-stack/B done |
| 52 | B→B edge? | forward/cross, no cycle |
| 53 | G→G? | back = cycle |
| 54 | W→W? | tree edge |
| 55 | Kahn stable? | FIFO ≈ level order |
| 56 | When NOT topo? | cyclic workflow |
| 57 | Alt for cycles? | report cycle + SCC |
| 58 | Test count? | empty/single/dag/cycle/self-loop |
| 59 | Recurrence? | none (linear scan, not divide) |
| 60 | One-line summary? | linearize DAG or prove cyclic |
