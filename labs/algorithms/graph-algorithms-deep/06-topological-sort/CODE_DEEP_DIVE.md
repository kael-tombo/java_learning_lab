# Code Deep Dive — Topological Sort

A compact but complete Java implementation of the lab's core algorithm(s), with the pitfalls annotated.

```java
import java.util.*;

public final class TopoSort {
    /** Kahn's algorithm; null means the graph has a cycle. */
    public static List<Integer> kahn(List<List<Integer>> adj, int n) {
        int[] indeg = new int[n];
        for (int u = 0; u < n; u++) for (int v : adj.get(u)) indeg[v]++;
        Queue<Integer> q = new ArrayDeque<>();
        for (int u = 0; u < n; u++) if (indeg[u] == 0) q.add(u);
        List<Integer> order = new ArrayList<>();
        while (!q.isEmpty()) {
            int u = q.poll(); order.add(u);
            for (int v : adj.get(u)) if (--indeg[v] == 0) q.add(v);
        }
        return order.size() == n ? order : null;
    }

    /** DFS reverse post-order; null means a cycle was found. */
    public static List<Integer> dfsOrder(List<List<Integer>> adj, int n) {
        int[] color = new int[n]; List<Integer> post = new ArrayList<>();
        for (int s = 0; s < n; s++) if (color[s] == 0 && !dfs(s, adj, color, post)) return null;
        Collections.reverse(post); return post;
    }
    static boolean dfs(int u, List<List<Integer>> adj, int[] color, List<Integer> post) {
        color[u] = 1;
        for (int v : adj.get(u)) {
            if (color[v] == 1) return false;
            if (color[v] == 0 && !dfs(v, adj, color, post)) return false;
        }
        color[u] = 2; post.add(u); return true;
    }
}
```

## Pitfalls

- Assuming the topological order is unique — most DAGs have many.
- Using topological sort on an undirected graph — it is a directed concept.
- Reporting "no order" without checking why — it means a cycle, not an isolated vertex.
- Relaxing edges in the wrong order — only topological order makes the single-pass DP valid.
- Forgetting that a disconnected DAG still has a topological order — run Kahn/DFS from every component.
- Confusing a topological order with a BFS layering — they agree on source distances but differ in general.

## Why the bounds hold

- **Kahn's algorithm**: Θ(V+E) time, Θ(V) — in-degree queue.
- **DFS post-order**: Θ(V+E) time, Θ(V) — reverse post-order.
- **Cycle detection via Kahn**: Θ(V+E) time, Θ(V) — unoutputted vertices.
- **DAG longest path**: Θ(V+E) time, Θ(V) — relax in topo order.
- **Dependency build order**: Θ(V+E) time, Θ(V) — the topological order itself.

## Takeaway

# Theory — Topological Sort
