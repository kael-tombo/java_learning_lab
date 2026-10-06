# Theory — Graph Coloring

A proper k-colouring of a graph assigns one of k colours to each vertex so
that adjacent vertices get different colours. The chromatic number χ(G) is
the smallest k for which a k-colouring exists. Computing χ is NP-hard; the
practical algorithms either colour greedily with a good order, exploit a
special class, or accept an approximation.

## Greedy colouring and the Δ+1 bound

Process vertices in any order; assign each the smallest colour not used by
its already-coloured neighbours. A vertex has at most Δ neighbours, so at
most Δ forbidden colours; one of the first Δ+1 colours is always available.
Hence every graph is (Δ+1)-colourable. The bound is tight — complete graphs
K_{Δ+1} need Δ+1 colours — but it is often very loose. The order of the
greedy pass decides how close you get; a bad order can use far more than the
chromatic number.

## Brooks' theorem

Every connected graph with maximum degree Δ is Δ-colourable, *unless* it is a
complete graph or an odd cycle, in which case χ = Δ+1. This is the
structural refinement of the Δ+1 bound: the only graphs that saturate it are
the complete graphs and the odd cycles.

## Bipartite graphs are exactly the 2-colourable graphs

A graph is bipartite iff its vertices split into two sets with no edges
within a set — i.e. exactly a 2-colouring. And a graph is bipartite iff it
has no odd cycle: a BFS 2-colouring succeeds iff every back edge connects
same-level vertices at even distance. So testing bipartiteness is the same
as testing 2-colourability, and both are Θ(V+E).

## DSATUR: ordering by saturation

DSATUR (Brélaz, 1979) improves greedy by colouring the most constrained
vertex next: the vertex whose *coloured* neighbours use the most distinct
colours (the "saturation degree"). Ties break by the classic greedy degree.
The intuition is that a vertex with many coloured neighbours has fewer
colours available, so it should be decided early — the opposite of the
"largest degree first" heuristic. DSATUR is exact on several special classes
and is the standard practical greedy method.

## Special classes with exact colouring

- Trees: 2 colours.
- Bipartite: 2 colours.
- Cycles: 2 if even, 3 if odd.
- Complete graphs K_n: n colours.
- Interval graphs: the greedy left-to-right order is optimal; χ = clique
  number (these are *perfect* graphs).
- Planar graphs: 4 colours suffice (the Four-Colour Theorem), but no
  polynomial-time 4-colouring algorithm is simple.

## When colouring is NP-hard

Deciding whether a graph is 3-colourable is NP-complete, even for planar
graphs of maximum degree 4. So no polynomial exact χ computation is expected.
The practical responses: use DSATUR or another greedy order for a
heuristic; use an exact exponential algorithm for small graphs; or recognise
the special class and apply the exact rule.

## Pitfalls

- Treating greedy colouring as optimal — it is a heuristic, often by a wide
  margin.
- Off-by-one on the Δ+1 bound: Δ counts *neighbours*, not colours already
  used.
- Forgetting Brooks' exceptions: K_n and odd cycles genuinely need Δ+1.
- Scheduling conflicts model: the graph must be built with an edge for each
  *pair* of tasks that cannot share a slot — missing edges under-constrain
  the colouring.
