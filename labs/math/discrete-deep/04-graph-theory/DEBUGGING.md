# Debugging: Graph Theory Code

## Symptom: Infinite Loop on a Cyclic Graph

Most common cause: the `visited` check happens after the neighbor is enqueued/pushed, or is missing on one of two code paths (e.g., you guard the queue but not the neighbor scan). Fix: `if (!visited[n]) { visited[n] = true; queue.add(n); }` as one indivisible step. Write a three-node cycle test (A→B→C→A) — it hangs immediately if the guard is wrong, so run it first with a timeout.

## Symptom: BFS Finds a Longer Path Than Expected

Check whether you weighted anything. BFS guarantees minimum *edge count*; on weighted graphs use Dijkstra. Also verify you stop at dequeue distance: with lazy-deletion Dijkstra, stale queue entries must be skipped (`if (d != dist[v]) continue;`) or you propagate outdated distances.

## Symptom: Priority Queue Keeps Returning Outdated Entries

`PriorityQueue` in Java has no `decreaseKey`. The standard workaround is re-insertion: pushing (newDist, v) again and skipping stale pops on read. If you skip that skip, nodes settle with old values — the classic "Dijkstra gives wrong answer" bug. Diagnostic: print `(poppedDist, currentDist[v])`; any mismatch is a stale entry being processed.

## Symptom: The Queue Keeps Returning the Same Node (Checklist)

Diagnose duplicate/again-processed nodes in order:

1. Smallest repro: three nodes in a cycle; set a step counter and fail at 10·V steps ("progress guarantee": BFS enqueues ≤ V nodes if marked on push).
2. Dump `queue` contents each iteration — a repeated node means the mark is missing or applied to a different object (e.g., `Integer` vs `int` boxing comparison, or a node wrapper without proper `equals`).
3. Verify edges are what you think: print the adjacency list before running; a parse bug (off-by-one, wrong delimiter) is the second most common cause.

## Symptom: Works on Small Graphs, Wrong on Large Ones

Prime suspect: **integer overflow in the distance sum**. Path weights summed in `int` exceed 2,147,483,647 whenever total weight is large (e.g., 3 edges of 10⁹); distances then wrap negative and Dijkstra's ordering inverts. Use `long` for all accumulated weights. Second suspect: recursion depth — DFS on a chain of 10⁵ nodes overflows the JVM stack; convert to an explicit `ArrayDeque` stack or raise `-Xss`.

## Symptom: The "Spanning Tree" Has a Cycle or Misses Nodes

Kruskal's union–find must check `find(u) != find(v)` *before* union; skipping the check adds the cycle-closing edge. Prim must start from a node in the component you want. Assert after the algorithm: `edgesSelected == V - components` and `|vertices reached| == V` for connected graphs.

## Symptom: Topological Order Violates an Edge

Wait — *violates* an edge: a dependency u→v appears with v before u. Either the graph has a cycle (Kahn's algorithm detects it when the queue empties before processing V nodes — assert that count) or you inserted the edge backwards at parse time. Print `indegree[v]` right after parsing; an unexpected 0 means the incoming edge never got registered.

## Test Oracle for Small Graphs

For V ≤ 8, compute all-pairs shortest paths by Floyd–Warshall O(V³) (works with negatives if no negative cycle) and compare against Dijkstra-from-every-node and BFS. Any disagreement isolates: Dijkstra vs Floyd → negative weight or stale PQ entry; BFS vs Floyd → weight/edge-count metric mix-up. Also enumerate all paths for V ≤ 6 and brute-force the minimum — slow, definitive.
