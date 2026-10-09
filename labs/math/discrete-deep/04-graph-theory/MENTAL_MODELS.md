# Mental Models: Graph Theory

## 1. A Graph Is Just a Binary Relation

A directed graph on V is a subset E ⊆ V × V — a table of "which pairs are related." Everything else (paths, connectivity, trees) is what you can build from that relation. When a problem gives you "users follow users," "modules import modules," or "cities connect to cities," you have already chosen the relation; the rest of the work is deciding which questions about it matter (reachability? cheapest chain? can it be linearized?).

## 2. Paths Are Proofs

"u can reach v" is witnessed by a concrete sequence of edges — a path is a *proof object*. Algorithms either produce the witness (parent pointers give you the path) or prove absence (an unreached node after exhaustive BFS is proof of non-reachability, because BFS explores everything it can). This is why BFS/DFS must be exhaustive: an early stop invalidates the negative conclusion.

## 3. BFS = Layered Expansion; DFS = Commitment

BFS grows a frontier uniformly: when it first reaches a node, it has provably done so with the fewest edges — think ripples on a pond. DFS dives down one branch and backtracks only when stuck — think exploring a maze by always taking the leftmost unvisited corridor and marking your trail. Choose BFS for distance/level structure, DFS for ordering, cycle detection, and component exploration.

## 4. Weights Change Everything

Unweighted graphs measure hop counts; weights turn paths into *optimization over sums*. The model must say which: "shortest" = fewest edges (BFS), "cheapest" = minimum weight sum (Dijkstra for nonnegative, Bellman–Ford for negative), "widest" = maximum bottleneck capacity (maximize the minimum edge — replace + with min in Dijkstra). If you can't say which, the model isn't finished.

## 5. The Cut Lens

A cut partitions V into (S, V∖S). Many theorems become "the cheapest/highest thing crossing *some* cut is safe to take": MST's light edge crossing a cut belongs to some MST; max-flow = min-cut says the bottleneck of the network is a specific cut's capacity. When stuck, imagine where the boundary is.

## 6. DAG = Dependency Order

A DAG is a partial order drawn as arrows: topological order is any linear extension — a legal sequence for doing things whose prerequisites are arrows. Scheduling, build systems, "course prerequisites," and spreadsheet recalculation are all topological sorts. The presence of a cycle means the dependency is circular and *no* order exists — that's not an algorithm failure, it's the answer.

## 7. Tree = Minimally Connected; The Cycle as Redundancy

A spanning tree keeps V−1 edges and connectivity; every extra edge creates exactly one cycle, i.e., redundancy. Union–find, Kruskal, and "remove the edge closing the cycle in a graph with one extra edge" (finding an arbitrary cycle in a graph) all exploit the identity: **edges − vertices + components = cyclomatic number** (the number of independent cycles).

## 8. Graph as State Machine

Nodes = states, directed edges = allowed transitions. Then language recognition, protocol handshakes, and game positions are graphs, and their questions (does a deadlock cycle exist? can the attacker reach admin from user?) are graph questions. Reachability in the *attack graph* is privilege escalation; a cycle in the *wait-for graph* is deadlock — the same DFS, different vocabulary.
