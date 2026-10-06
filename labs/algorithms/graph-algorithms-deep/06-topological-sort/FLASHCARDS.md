# Flashcards — Topological Sort

Format: **Q → A**.

---

| # | Question | Answer |
|---|----------|--------|
| 1 | Topological order | linear order with u before v for every u→v |
| 2 | Exists iff | the graph is a DAG |
| 3 | Kahn's | BFS in-degree reduction |
| 4 | Kahn's time | Θ(V+E) |
| 5 | DFS topo order | reverse post-order |
| 6 | Cycle + topo order | incompatible |
| 7 | Kahn leaves unoutputted ⇔ | a cycle exists |
| 8 | DFS back edge to grey vertex | a cycle |
| 9 | DAG longest path | relax in topo order |
| 10 | Every DAG has | a source (in-degree 0 vertex) |
| 11 | No source implies | a cycle |
| 12 | Cycle in requirements | circular dependency — no valid order |
| 13 | Build order is | a topological order of the dependency graph |
| 14 | DAG paths DP needs | topological order |
| 15 | Counting paths in a DAG | DP in topo order |
| 16 | Cycle detection via Kahn | unoutputted vertices |
| 17 | Post-order reversal | reverses every edge — a topological order |
| 18 | In-degree queue | Kahn's ready set |
| 19 | Edge u→v means | u before v in the order |
| 20 | Multiple topo orders | a DAG has several in general |
| 21 | Kahn output count = n | DAG; otherwise a cycle exists |
| 22 | DFS colour grey | on the current recursion stack |
| 23 | Back edge | to a grey vertex — a cycle |
| 24 | Cross/forward edge | to a black vertex — fine in a DAG |
| 25 | Longest path in a DAG | Θ(V+E) |
| 26 | Shortest path in a DAG | Θ(V+E) in topo order — no Dijkstra needed |
| 27 | Topological sort applications | build systems, task scheduling, course planning |
| 28 | Kahn's idempotence | any order of the in-degree-0 queue gives a valid topo order |
| 29 | Cycle of length k | k vertices with cyclic dependencies |
| 30 | DAG of course prerequisites | edges prerequisite→course |
| 31 | Prereq graph with a cycle | infeasible — no one can take the first course |
| 32 | Post-order of a path graph | reverse of the path |
| 33 | Reverse post-order of DFS | a topological order of a DAG |
| 34 | DFS finish time order | reverse finishing times give the topo order |
| 35 | In-degree of a source | 0 |
| 36 | Every edge relaxed once | Θ(V+E) total |
| 37 | Topological sort is for | directed graphs |
| 38 | Undirected cycle has no | topological order (it is not a DAG) |
| 39 | DAG of a textbook syllabus | chapter dependencies |
| 40 | Task scheduler input | a DAG of tasks |
| 41 | Kahn's space | Θ(V) for the queue |
| 42 | Lexicographically smallest topo order | use a min-heap of in-degree-0 vertices |
| 43 | Number of topological orders | counted by #P-complete enumeration |
| 44 | Critical path in project planning | longest path in the task DAG — topo-sort DP |
| 45 | CPM in scheduling | critical path method on a DAG |
| 46 | A vertex with no incoming edges | a source — can start |
| 47 | A vertex with no outgoing edges | a sink — no prerequisites after it |
| 48 | Topological layering | Kahn's levels — the BFS layering |
| 49 | Kahn's levels give | longest-path distance from the sources |
| 50 | Dependency cycle example | A needs B, B needs C, C needs A |
| 51 | Cycle ⇒ no valid schedule | yes — deadlock in the requirement graph |
| 52 | Kahn's algorithm is | BFS on the in-degree-0 frontier |
| 53 | DFS topo order is | reverse post-order — depth-first alternative |
| 54 | Both algorithms are | Θ(V+E) |
| 55 | Why DAG paths are easy | topological order removes the "future" edges |
| 56 | Relaxation in topo order | each edge relaxed exactly once — Θ(E) |
| 57 | Path counting in a DAG | s[v] = Σ s[u] over incoming u→v |
| 58 | Topological sort needed before | DAG shortest/longest path, path count, evaluation |
