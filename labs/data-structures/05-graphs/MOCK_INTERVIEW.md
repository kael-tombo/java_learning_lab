# Mock Interview: Graphs

## Q1 — BFS Shortest Path (unweighted)

**Problem.** Shortest path length between two vertices in an unweighted graph.
**Key insight.** BFS visits vertices in increasing distance order; first visit to target is optimal. **Complexity.** O(V + E) time, O(V) space.

```java
public class GraphsQ1 {
    public static void main(String[] args) {
        int n = 3;
        java.util.List<java.util.List<Integer>> g = new java.util.ArrayList<>();
        for (int i = 0; i < n; i++) g.add(new java.util.ArrayList<>());
        for (int[] e : new int[][]{{0, 1}, {1, 2}, {0, 2}}) { g.get(e[0]).add(e[1]); g.get(e[1]).add(e[0]); }
        int[] dist = {-1, -1, -1};
        java.util.Deque<Integer> q = new java.util.ArrayDeque<>();
        q.add(0); dist[0] = 0;
        while (!q.isEmpty()) {
            int u = q.poll();
            for (int v : g.get(u)) if (dist[v] == -1) { dist[v] = dist[u] + 1; q.add(v); }
        }
        System.out.println(dist[2]);
    }
}
```

Output:

```
1
```

## Q2 — Cycle Detection (undirected)

**Problem.** Report whether an undirected graph contains a cycle.
**Key insight.** DFS with parent tracking: a visited neighbor that is not the parent is a back edge. **Complexity.** O(V + E) time, O(V) space.

```java
public class GraphsQ2 {
    static boolean dfs(java.util.List<java.util.List<Integer>> g, boolean[] seen, int u, int p) {
        seen[u] = true;
        for (int v : g.get(u)) {
            if (!seen[v]) { if (dfs(g, seen, v, u)) return true; }
            else if (v != p) return true;
        }
        return false;
    }
    public static void main(String[] args) {
        java.util.List<java.util.List<Integer>> g = new java.util.ArrayList<>();
        for (int i = 0; i < 3; i++) g.add(new java.util.ArrayList<>());
        for (int[] e : new int[][]{{0, 1}, {1, 2}, {2, 0}}) { g.get(e[0]).add(e[1]); g.get(e[1]).add(e[0]); }
        System.out.println(dfs(g, new boolean[3], 0, -1));
    }
}
```

Output:

```
true
```

## Q3 — Topological Sort (Kahn, LC 207)

**Problem.** Decide whether all courses finish given prerequisites (is the digraph acyclic?).
**Key insight.** Repeatedly remove zero-in-degree vertices; removing all proves acyclicity. **Complexity.** O(V + E) time, O(V + E) space.

```java
public class GraphsQ3 {
    static boolean canFinish(int n, int[][] pre) {
        java.util.List<java.util.List<Integer>> g = new java.util.ArrayList<>();
        for (int i = 0; i < n; i++) g.add(new java.util.ArrayList<>());
        int[] in = new int[n];
        for (int[] p : pre) { g.get(p[1]).add(p[0]); in[p[0]]++; }
        java.util.Deque<Integer> q = new java.util.ArrayDeque<>();
        for (int i = 0; i < n; i++) if (in[i] == 0) q.add(i);
        int done = 0;
        while (!q.isEmpty()) { int u = q.poll(); done++; for (int v : g.get(u)) if (--in[v] == 0) q.add(v); }
        return done == n;
    }
    public static void main(String[] args) {
        System.out.println(canFinish(2, new int[][]{{1, 0}}) + " / " + canFinish(2, new int[][]{{1, 0}, {0, 1}}));
    }
}
```

Output:

```
true / false
```
