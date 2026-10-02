# Exercises — Breadth-First Search (BFS)

## Beginner

1. **Implement BFS on an adjacency list**
   - Write a method `bfs(int start, List<List<Integer>> graph)` that returns the visitation order.
   - Test on a graph with 5 nodes and verify level-by-level traversal.

2. **Find shortest path length in unweighted graph**
   - Given a graph and start/target nodes, return the minimum number of edges.
   - Return -1 if target is unreachable.

3. **Level-order traversal of a binary tree**
   - Given a `TreeNode`, return `List<List<Integer>>` where each inner list is a level.
   - Use a queue with size tracking to separate levels.

## Intermediate

4. **Bidirectional BFS for Word Ladder**
   - Implement LeetCode 127 (Word Ladder) using bidirectional BFS.
   - Compare performance against standard BFS on large dictionaries.

5. **Connected components using BFS**
   - Given an undirected graph, count the number of connected components.
   - Return a list of component sizes.

5. **Shortest path in a binary matrix**
   - LeetCode 1091: Find shortest path from (0,0) to (n-1,n-1) in a grid with 0/1 cells.
   - 8-directional movement allowed. Return -1 if blocked.

## Advanced

7. **Minimum knight moves on infinite chessboard**
   - Given source and target coordinates, find minimum knight moves.
   - Use bidirectional BFS with symmetry optimizations.

8. **Multi-source BFS: Rotting Oranges**
   - LeetCode 994: Given a grid with fresh/rotten oranges, find minutes until all rot.
   - Rotten oranges spread to 4-directional neighbors each minute.

9. **BFS with state: Cheapest Flights with K Stops (Dijkstra variant)**
   - Implement LeetCode 787 using Dijkstra with (node, stops) state.
   - Compare with Bellman-Ford solution.

10. **Bidirectional BFS with pattern matching**
    - LeetCode 126: Word Ladder II — find ALL shortest transformation sequences.
    - Use bidirectional BFS to build the transformation graph, then DFS to enumerate paths.