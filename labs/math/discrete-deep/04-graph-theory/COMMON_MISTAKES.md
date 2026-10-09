# Common Mistakes: Graph Theory

## 1. Forgetting the `visited` Mark (or Marking It Too Late)

In BFS, mark a node when you *enqueue* it, not when you dequeue it. Marking on dequeue lets the same node be enqueued from two neighbors → duplicated work and, with parent tracking, a wrong "shortest" tree. In DFS the mark must happen before recursion. Symptom: infinite loop on any cycle, or a queue that never empties.

## 2. Assuming Dijkstra Works With Negative Weights

Dijkstra's invariant — "settled nodes have final distances" — is destroyed by a negative edge discovered *after* a node is settled. Counterexample graph: s→a (1), s→b (4), a→b (−3): Dijkstra settles a with dist 1, then b via s at 4, missing s→a→b = −2. Use Bellman–Ford O(V·E) when negatives exist (and detect negative cycles), Dijkstra only for nonnegative weights.

## 3. Mixing Up Directed and Undirected Storage

An undirected edge {u,v} must be inserted in *both* adjacency lists (or once in a matrix cell symmetrized `mat[u][v] = mat[v][u] = w`). Forgetting one direction makes traversal one-way: BFS from u reaches v but not vice versa — a bug that shows up only for certain start nodes. Conversely, storing an undirected edge once and then running algorithms that expect symmetry (degree counting, flow) silently halves degrees.

## 4. Confusing Path Length With Edge Count

Unweighted BFS distance counts edges; weighted distance sums weights. Running BFS on a weighted graph returns fewest-edges paths, not cheapest — "shortest path" is ambiguous unless you name the metric.

## 5. De Morgan-Style Cut Errors

min-cut = max-flow is about *capacity*, not *number of edges*: the minimum cut by edge count is a different problem (and for undirected graphs relates to edge connectivity). Also the cut is a set of edges whose removal disconnects s from t — forgetting that cut edges are counted with multiplicity in a directed graph (parallel arcs both ways) changes the capacity.

## 6. Ignoring Disconnected Components

Single-source algorithms reach only the component containing s; distances to other components stay ∞. Loops that compute "the average shortest path" then crash on ∞ or divide by zero. Either run the algorithm from each component's source or filter unreachable pairs explicitly.

## 7. Off-by-One on Vertex Indices

Graphs given as 1-based edge lists (common in problem statements) loaded into 0-based arrays write out of bounds or silently alias vertex n to vertex 0. Fix at parse time: decide once whether ids are 0-based and convert on ingest; assert `0 <= u && u < V` for every edge.

## 8. Tree vs Graph in Recursion (Revisiting in DAGs)

Topological sort and DAG-DP require processing a node only when all predecessors are done. Running plain DFS and appending on finish works for a *DAG*; on a cyclic graph it produces a "topological order" that violates an edge — always detect cycles (white/gray/black coloring: a back edge to a gray node is a cycle) instead of assuming acyclicity.

## 9. Self-Loops and Parallel Edges in Matrices

`mat[v][v] = w` makes a self-loop look like a "path of weight w staying put," corrupting degree (adds 2 or 1 arbitrarily) and min/max computations. Parallel edges in an adjacency matrix collapse to the single stored value — if you need all of them (e.g., max flow with multiple arcs), use adjacency lists or sum capacities explicitly.
