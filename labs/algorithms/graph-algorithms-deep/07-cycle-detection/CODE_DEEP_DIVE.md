# Code Deep Dive — Cycle Detection

A compact but complete Java implementation of the lab's core algorithm(s), with the pitfalls annotated.

```java
import java.util.*;

public final class CycleDetect {
    /** Three-colour DFS; returns true iff the directed graph has a cycle. */
    public static boolean hasCycle(List<List<Integer>> adj, int n) {
        int[] color = new int[n];
        for (int s = 0; s < n; s++) if (color[s] == 0 && dfs(s, adj, color)) return true;
        return false;
    }
    static boolean dfs(int u, List<List<Integer>> adj, int[] color) {
        color[u] = 1;
        for (int v : adj.get(u)) {
            if (color[v] == 1) return true;
            if (color[v] == 0 && dfs(v, adj, color)) return true;
        }
        color[u] = 2; return false;
    }

    /** Floyd tortoise-hare on a functional graph f(x). */
    public static int cycleEntry(int[] f, int start) {
        int slow = f[start], fast = f[f[start]];
        while (slow != fast) { slow = f[slow]; fast = f[f[fast]]; }
        int p = start;
        while (p != slow) { p = f[p]; slow = f[slow]; }
        return p;
    }
}
```

## Pitfalls

- Treating the parent edge in an undirected graph as a cycle.
- Using a two-colour DFS for a directed graph — it cannot separate back from cross edges.
- Running Floyd's algorithm on a branching successor — it needs out-degree 1.
- Forgetting that a disconnected graph needs a DFS from every unvisited vertex.
- Concluding "DAG" from one component — the whole graph must be grey-free.
- Assuming any SCC has a cycle — a singleton without a self-loop is acyclic.

## Why the bounds hold

- **Three-colour DFS**: Θ(V+E) time, Θ(V) — directed graphs.
- **Union-Find scan**: Θ(E·α(V)) time, Θ(V) — undirected graphs.
- **Floyd tortoise-hare**: Θ(t+L) time, Θ(1) — functional graphs.
- **Tarjan SCC**: Θ(V+E) time, Θ(V) — SCCs = cycles.
- **Kosaraju SCC**: Θ(V+E) time, Θ(V) — two DFS passes.

## Takeaway

# Theory — Cycle Detection
