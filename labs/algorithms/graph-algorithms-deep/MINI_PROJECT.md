# MINI_PROJECT — Graph Algorithms Deep Track
> Core-plus-advanced graph kit: shortest paths (Dijkstra/Bellman-Ford/Floyd), SCC, bridges/articulation, LCA, and max flow with cross-verified oracles.

## Inputs
- Fixed 6-node weighted graph (documented in code) with a negative edge but no negative cycle; disconnected pair for component tests.
- Random graphs (n = 100/1k, fixed seeds) for timing; small flow network with known max flow 23-style reference (state the exact reference value in code from your hand computation).

## Build steps
1. Implement Dijkstra (binary heap, O(E log V)) and Bellman-Ford (O(VE)); assert agreement on non-negative instances, Bellman-Ford alone on the negative edge.
2. Implement Floyd-Warshall O(V^3) with path reconstruction on the fixed graph; cross-check all-pairs against repeated Dijkstra.
3. Implement Tarjan SCC (or Kosaraju, labeled) plus bridges/articulation via discovery/low times; verify on the fixed graph by hand-counted components.
4. Implement LCA by binary lifting; verify 200 queries against naive climbing.
5. Implement Edmonds-Karp (O(VE^2)) max flow; verify the reference value and min-cut edge set.

## Acceptance criteria
1. Dijkstra/Bellman-Ford agreement test passes on all non-negative instances; negative-edge instance solved by Bellman-Ford with distances hand-verified.
2. Floyd all-pairs matches repeated Dijkstra on the fixed graph with one reconstructed path shown.
3. SCC/bridge/articulation outputs match hand counts recorded in the test file.
4. LCA agrees with naive climbing on all 200 queries.
5. Max-flow value matches the hand-computed reference with the min cut listed.
6. Timing table (100/1k) from real runs with machine/JDK noted; heap-vs-array Dijkstra choice justified from the numbers.

## Analysis prompts
1. Where does Bellman-Ford's extra cost show, and what does it buy (negative edges + cycle detection)?
2. Which fixed-graph vertex is an articulation point, and which edge is a bridge — why?
3. How does Edmonds-Karp time scale from your two sizes, and what would Dinic change?

## Non-goals
- Dinic/push-relabel implementations (see 28-push-relabel-flow), dynamic graph algorithms, and geometric graphs.

## Hand-verified anchors
- Fixed-graph distances hand-verified, including the negative edge that only Bellman-Ford may touch.
- Articulation points, bridges, SCC count, and max-flow value with min cut all recorded from hand computation first.

## Stretch
- Implement Dinic with level graphs and compare flow time against Edmonds-Karp on a layered network.
- Add Johnson's algorithm (reweight + Dijkstra) and verify all-pairs against Floyd on the negative-edge graph.
