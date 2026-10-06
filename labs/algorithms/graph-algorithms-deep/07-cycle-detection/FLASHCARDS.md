# Flashcards — Cycle Detection

Format: **Q → A**.

---

| # | Question | Answer |
|---|----------|--------|
| 1 | Three-colour DFS | white/grey/black states |
| 2 | Back edge | to a grey vertex — a cycle |
| 3 | Forward edge | to a black descendant — no cycle |
| 4 | Cross edge | to a black vertex in another subtree — no cycle |
| 5 | Union-Find cycle test | find(u)==find(v) before adding (u,v) |
| 6 | Union-Find per-edge cost | α(V) amortised |
| 7 | Floyd tortoise-hare | slow +1, fast +2, meet in the cycle |
| 8 | Floyd entry point | restart one pointer, advance both by 1 |
| 9 | Floyd space | Θ(1) |
| 10 | Floyd time | Θ(t+L) |
| 11 | Functional graph | every vertex has out-degree 1 |
| 12 | Tail t | steps before entering the cycle |
| 13 | Cycle length L | states inside the cycle |
| 14 | Tarjan SCC time | Θ(V+E) |
| 15 | Kosaraju passes | two DFS |
| 16 | Non-trivial SCC | size > 1 — contains a cycle |
| 17 | Self-loop | a cycle of length 1 |
| 18 | Undirected parent edge | not a cycle — it is the same edge back |
| 19 | Directed self-loop | a cycle |
| 20 | Wait-for graph cycle | deadlock |
| 21 | Dependency cycle | infeasible build |
| 22 | Call graph cycle | recursion |
| 23 | Three-colour DFS time | Θ(V+E) |
| 24 | Two-colour DFS for directed cycles | insufficient — cannot separate back from cross edges |
| 25 | Recursion stack recovery | walk it from the grey target to the current vertex |
| 26 | Floyd meeting invariant | fast gains one position per step once both are in the cycle |
| 27 | Cycle length from Floyd | advance slow until it returns to the meeting point |
| 28 | Floyd entry formula | t = k - r·L for the meeting offset k |
| 29 | Tarjan low-link | earliest grey ancestor reachable from the subtree |
| 30 | Tarjan SSC condition | low-link[v] == disc[v] pops the SCC |
| 31 | Kosaraju first pass | finish order on G |
| 32 | Kosaraju second pass | DFS on Gᵀ in reverse finish order |
| 33 | Kosaraju SCC time | Θ(V+E) |
| 34 | Cycle in undirected no self-edge | simple cycle of length ≥ 3 |
| 35 | Undirected two-cycle | the same edge traversed back — not a cycle |
| 36 | Union-Find vs DFS for undirected cycle | Union-Find is simpler and matches Kruskal's use |
| 37 | DFS tree edge | to a white vertex — part of the spanning forest |
| 38 | A back edge closes | the path from the ancestor down to the current vertex |
| 39 | Cycle detection in a graph with parallel edges | a 2-cycle from the parallel pair — count carefully |
| 40 | Floyd assumes | a single successor per node — a functional graph |
| 41 | Non-functional successor | Floyd's picks one successor; branch points need search |
| 42 | Cycle entry found by | resetting one pointer to the start |
| 43 | Floyd meeting point distance from entry | equal to tail length t mod L |
| 44 | Deadlock detection via cycle | a cycle in the wait-for graph is necessary and sufficient |
| 45 | Build deadlock | circular prerequisites — no vertex can run first |
| 46 | SCCs of a DAG | all singletons, no self-loops |
| 47 | Tarjan vs Kosaraju | Tarjan one pass, Kosaraju two passes on G and Gᵀ |
| 48 | Union-Find cycle test runs in | Θ(E·α(V)) |
| 49 | Three-colour DFS in a DAG | no back edges ever — every edge is tree/forward/cross |
| 50 | Cycle ⇒ no topological order | yes |
| 51 | In a DAG every edge is | tree, forward, or cross — never back |
| 52 | A cycle is a | maximal set of mutually reachable vertices? No — an SCC; a cycle is one closed walk |
| 53 | Simple cycle | no repeated vertex except start=end |
| 54 | Floyd's tortoise-hare inventor | Robert W. Floyd |
| 55 | Functional graph iteration | must eventually repeat a state |
| 56 | Repeated state = cycle entry | for the iteration, not necessarily for Floyd's pointers |
| 57 | Slow pointer steps to meet | a multiple of L, at least t |
| 58 | Cycle length L | k slow-steps were a multiple of L |
| 59 | Cycle entry is at | distance t from the start, where t is the tail length |
| 60 | Floyd works because | the walk is eventually periodic |
| 61 | Cycle detection in a linked list | Floyd's tortoise-hare |
| 62 | Detecting a loop in a singly linked list | the classic application |
| 63 | Self-loop in Union-Find | find(u)==find(u) — trivially a cycle |
| 64 | Parallel-edge 2-cycle | two edges between u and v form a 2-cycle in a multigraph |
