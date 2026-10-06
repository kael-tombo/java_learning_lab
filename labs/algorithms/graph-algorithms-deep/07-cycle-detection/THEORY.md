# Theory — Cycle Detection

A cycle is a directed path from a vertex back to itself. The detection
algorithms differ by what they optimise for: directed vs undirected, explicit
graph vs implicit (a function iteration), and whether they must *locate* the
cycle or merely prove its existence.

## Three-colour DFS (directed graphs)

Colour each vertex white (unvisited), grey (on the current recursion stack),
or black (finished). A back edge — an edge to a grey vertex — is exactly a
cycle: the grey vertex is an ancestor of the current vertex, so the path down
to it plus the back edge closes a cycle. Every edge in a DFS falls into one
of four classes (tree, back, forward, cross); only back edges indicate
cycles. A forward or cross edge goes to a black vertex and cannot close a
cycle. Θ(V+E) time, Θ(V) space.

## Union-Find (undirected graphs)

Process edges one at a time; maintain a disjoint-set over vertices. When
examining edge (u,v), if find(u) == find(v), then u and v are already
connected, so adding (u,v) closes a cycle. Otherwise union them. Each edge
costs an almost-constant α(V) amortised, so the whole scan is Θ(E·α(V)).
This is simpler than DFS for the undirected case and is why Kruskal's MST
algorithm is built on it.

## Floyd's tortoise and hare (functional graphs)

Given a function f on a finite set and a start, iterate x_{i+1} = f(x_i).
Because the set is finite, the walk eventually enters a cycle. Advance a
*slow* pointer by one step and a *fast* pointer by two steps; they must meet,
because once both are inside the cycle the fast one gains one position per
step and laps the slow one. Let the meeting point be μ, the cycle length be L,
and the tail length be t. The meeting happens after k slow-steps where k is a
multiple of L and k ≥ t. To find the cycle *entry*, restart one pointer at
the start and move both one step at a time; they meet at the entry. The proof:
the slow pointer is at position k ≡ 0 (mod L) inside the cycle; moving it by
t from the cycle entry brings it to the same point mod L. Θ(t+L) time, Θ(1)
space — the celebrated trade of time for memory.

## Cycles and SCCs

A directed graph is acyclic iff every strongly connected component is a
singleton with no self-loop. Tarjan's or Kosaraju's SCC decomposition
therefore doubles as a cycle detector: any non-trivial SCC (size > 1, or a
self-loop) is a cycle. Tarjan runs in Θ(V+E) and produces the SCCs in
reverse topological order.

## Directed vs undirected pitfalls

In an undirected graph, the edge back to the *parent* is not a cycle — every
undirected edge appears as (u,v) and (v,u). The three-colour rule must ignore
the parent edge (or, with Union-Find, the first visit is the union). In a
directed graph, *any* edge to a grey vertex is a cycle, including a
self-loop.

## Cycle detection as deadlock detection

In a wait-for graph (threads waiting on resources), a cycle is a deadlock.
In a dependency graph, a cycle is an infeasible build. In a call graph, a
cycle is recursion. The same Θ(V+E) algorithm answers all three — the
modelling is what differs.

## Pitfalls

- Treating the parent edge in an undirected graph as a cycle.
- Using two-colour DFS (visited/unvisited) for *directed* cycle detection —
  you need the third grey state to distinguish a back edge from a cross edge.
- Reporting "cycle exists" without locating it: keep the recursion stack to
  recover the cycle when needed.
- Floyd's algorithm on a non-functional graph (branching factor > 1) — it
  assumes a single successor per node.
