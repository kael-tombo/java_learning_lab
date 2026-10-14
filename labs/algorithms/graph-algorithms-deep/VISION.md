# VISION — Graph Algorithms Deep Track
> Direction: from BFS/DFS fluency to the full toolkit — paths, components, ancestors, cuts — each with its oracle.

## Where this sits
- Shortest paths: Dijkstra O(E log V) for non-negative, Bellman-Ford O(VE) with negatives and cycle detection, Floyd O(V^3) all-pairs, DAG O(V+E).
- Structure: SCC (Tarjan/Kosaraju), bridges/articulation (discovery/low), LCA (binary lifting O(log n) queries).
- Flow: Ford-Fulkerson idea, Edmonds-Karp O(VE^2), Dinic and push-relabel for scale (see lab 28).
- MST material lives in 38-mst-variants; this track consumes it, not rebuild it.

## 4-week direction
- Week 1: hand-run Dijkstra, Bellman-Ford, and lowlink on the fixed graph until all outputs are reproducible cold.
- Week 2: finish MINI_PROJECT; cross-verify every method against its oracle (repeated Dijkstra, naive climbing, hand counts).
- Week 3: break each method once (negative edge into Dijkstra, disconnected LCA query, oversized flow) and record the honest behavior.
- Week 4: REAL_WORLD_PROJECT review; whiteboard discovery/low timing in 10 minutes.

## Done criteria
- State each method's bound plus the input condition it requires (non-negative, DAG, size).
- Run lowlink by hand on a fresh small graph and name bridges correctly.
- Choose Dijkstra vs Bellman-Ford vs Floyd vs DAG-shortest for a given (graph, query) pair.

## Non-coverage
- This track does not implement Dinic or push-relabel (used via labeled paths, built in lab 28).
- No dynamic/connectivity-offline algorithms beyond naming (sqrt decomposition, divide-and-conquer offline).
- Geometric and planar specializations are out of scope.

## Pitfalls
- Running Dijkstra on negative edges and trusting the output.
- Quoting flow values without the min cut that certifies them.
- Forgetting version pins on snapshots and hierarchies that queries depend on.

## Adjacent tracks
- Pair with 38-mst-variants for cut thinking and 28-push-relabel-flow for flow at scale.
- Revisit after any network incident; the discovery/low and min-cut checklists are the postmortem.

## Weekly drills
- Run discovery/lowlink on a fresh 6-node graph and name bridges correctly.
- Restate Dijkstra's precondition and show the negative-edge counterexample.
- Write Edmonds-Karp's bound from the shortest-augmenting-path argument.

## Anti-roadmap
- Do not run Dijkstra where Bellman-Ford is required; check edge signs first.
- Do not quote flow without the certifying cut.
