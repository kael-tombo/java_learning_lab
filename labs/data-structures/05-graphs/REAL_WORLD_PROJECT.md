# Transit Router and Build-Graph Doctor

Two graphs, one engine. The first is a transit network where stops are
vertices and timed rides are weighted edges; travelers ask for the
fewest-hop or fastest route. The second is a build-dependency graph where
modules are vertices and imports are directed edges; engineers ask what
broke the build and in which order to rebuild.

Representation. Adjacency lists with sorted neighbor arrays: BFS/DFS stay
O(V + E), edge insert stays amortized O(1), and neighbor scans stay
cache-kind. A reverse adjacency copy exists only for the dependency side,
where reverse reachability answers "who depends on this."

Traveler side. BFS for fewest hops, Dijkstra for fastest arrival, and an
island check (connected components) that names disconnected stops. A
route response lists stops, transfers, and total weight; unreachable
pairs return a named no-route answer with the component ids of both ends.

Build side. Cycle detection with the actual cycle path printed, topo
order for rebuild sequencing, and a blame query: given a failed module,
the reverse reachable set is the suspect list. Self-loops and duplicate
edges are rejected at ingest with line numbers.

Scale plan. Transit fixture at 5k stops / 40k edges; dependency fixture
at 20k modules / 80k edges. Dijkstra with a binary heap; BFS with an
array deque; iterative DFS everywhere so deep chains cannot overflow.

Trust. Every shortest path is cross-checked against a Floyd-Warshall
oracle on small graphs and a second Dijkstra implementation on large
ones. Topo orders are validated edge by edge. Cycle reports are replayed
by an independent checker that walks the printed path.

Rotten cases. Disconnected queries, midnight edge weights of zero,
self-dependent module, 10k-deep import chain, and a lockfile with a
three-cycle. Each has a golden file with the exact expected output.

Credit. Routing accuracy plus oracle agreement 12, cycle/blame quality
10, scale behavior with honest timings 8.
