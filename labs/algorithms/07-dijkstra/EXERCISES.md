# Exercises — Dijkstra's Algorithm

## Beginner

1. **Implement Dijkstra with binary heap**
   - Given adjacency list `List<List<int[]>> graph` where `int[] = {neighbor, weight}`, implement `dijkstra(int source)` returning `int[] dist`.
   - Handle unreachable nodes (Integer.MAX_VALUE).

2. **Shortest path to single target**
   - Modify the above to stop early when target is reached.
   - Return the path as `List<Integer>` using parent pointers.

3. **Dijkstra on matrix grid**
   - Given `int[][] grid` with positive weights, find shortest path from (0,0) to (m-1,n-1) with 4-directional moves.
   - Treat each cell as a node.

## Intermediate

4. **Network Delay Time (LeetCode 743)**
   - Implement the complete solution with test cases.
   - Verify unreachable node returns -1.

5. **Minimum Cost to Make at Least One Valid Path (LeetCode 1368)**
   - Grid with directional edges (0/1 cost). Find min cost to reach bottom-right.
   - Use 0-1 BFS (deque) for O(V + E) instead of Dijkstra's O((V+E) log V).

6. **Path with Minimum Effort (LeetCode 1631)**
   - Edge weight = absolute difference between adjacent cells.
   - Find path minimizing **maximum** edge weight (minimax path).
   - Modify Dijkstra: distance = max(current_max, edge_weight), use min-heap on this metric.

## Advanced

7. **Dijkstra with state: Cheapest Flights Within K Stops (LeetCode 787)**
   - State = (node, stops_remaining). Transitions reduce stops by 1.
   - Compare performance with Bellman-Ford solution.

8. **Second Shortest Path**
   - Find the length of the second-shortest path from source to target.
   - Track two best distances per node; only relax if new distance is between best and second-best.

9. **Minimum Spanning Tree vs Shortest Path Tree**
   - Given a graph, compute both MST (Prim's) and SPT (Dijkstra from node 0).
   - Compare total weights and structure. When are they identical?

10. **Dijkstra on implicit graph: Swim in Rising Water (LeetCode 778)**
    - Grid where you can move to adjacent cell at time = max(current_time, cell_height).
    - Find minimum time to reach bottom-right.
    - Edge weight depends on max of current path and next cell.