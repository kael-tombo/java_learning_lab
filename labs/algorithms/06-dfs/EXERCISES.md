# Exercises — Depth-First Search (DFS)

## Beginner

1. **Implement recursive DFS on adjacency list**
   - Write `dfs(int start, List<List<Integer>> graph, boolean[] visited)` returning visitation order.
   - Test on a graph with cycles and verify no infinite recursion.

2. **Implement iterative DFS with explicit stack**
   - Convert the recursive version to use `Deque<Integer>` stack.
   - Compare traversal order with recursive version.

3. **Count connected components in undirected graph**
   - Given an adjacency list, return number of connected components.
   - Use either recursive or iterative DFS.

## Intermediate

4. **Cycle detection in directed graph**
   - Implement `hasCycle(List<List<Integer>> graph)` using GRAY/BLACK colors.
   - Return the cycle path if one exists.

5. **Topological sort via DFS**
   - Given a DAG, return a valid topological ordering.
   - Test on a task scheduling graph with prerequisites.

6. **Number of Islands (LeetCode 200) — DFS solution**
   - Implement the "sink and flood" approach on a char[][] grid.
   - Verify with multiple test cases including edge cases.

## Advanced

7. **Number of Islands — Union-Find solution**
   - Implement Union-Find with path compression and union by rank.
   - Compare performance with DFS on large grids (1000×1000).

8. **Strongly Connected Components — Kosaraju's Algorithm**
   - Implement the two-pass algorithm for finding SCCs.
   - Return list of components (each as a list of vertices).

9. **Tarjan's Algorithm for SCCs (Single-pass)**
   - Implement Tarjan's algorithm using low-link values.
   - Single DFS pass, O(V + E) time.

10. **DFS with memoization: Longest path in DAG**
    - Given a weighted DAG, find the longest path from source to all nodes.
    - Use DFS + DP (memoization) for O(V + E) solution.