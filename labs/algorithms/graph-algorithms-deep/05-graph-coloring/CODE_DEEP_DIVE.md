# Code Deep Dive — Graph Coloring

A compact but complete Java implementation of the lab's core algorithm(s), with the pitfalls annotated.

```java
import java.util.*;

public final class GreedyColoring {
    /** First-fit greedy colouring in any vertex order. */
    public static int[] color(List<List<Integer>> adj) {
        int n = adj.size(); int[] color = new int[n]; Arrays.fill(color, -1);
        for (int v = 0; v < n; v++) {
            boolean[] used = new boolean[n];
            for (int u : adj.get(v)) if (color[u] != -1) used[color[u]] = true;
            int c = 0; while (used[c]) c++;
            color[v] = c;
        }
        return color;
    }

    /** BFS 2-colouring; -1 means the graph is not bipartite. */
    public static int[] twoColor(List<List<Integer>> adj) {
        int n = adj.size(); int[] color = new int[n]; Arrays.fill(color, -1);
        for (int s = 0; s < n; s++) if (color[s] == -1) {
            color[s] = 0; Queue<Integer> q = new ArrayDeque<>(); q.add(s);
            while (!q.isEmpty()) {
                int v = q.poll();
                for (int u : adj.get(v)) {
                    if (color[u] == -1) { color[u] = color[v] ^ 1; q.add(u); }
                    else if (color[u] == color[v]) return null;
                }
            }
        }
        return color;
    }
}
```

## Pitfalls

- Treating greedy as optimal — a bad vertex order uses far more than χ.
- Off-by-one on the Δ+1 bound: Δ counts neighbours, not colours used.
- Forgetting Brooks' exceptions — K_{Δ+1} and odd cycles need Δ+1.
- Under-building the conflict graph in scheduling — a missing edge under-constrains the colouring.
- Assuming 3-colourability is tractable — it is NP-complete.
- Confusing vertex colouring with edge colouring — Vizing gives χ' ∈ {Δ, Δ+1} instead.

## Why the bounds hold

- **Greedy colouring**: Θ(V+E) time, Θ(V+E) — any fixed order.
- **DSATUR**: Θ((V+E)·log V) with a heap time, Θ(V) — saturation-degree order.
- **Bipartite test**: Θ(V+E) time, Θ(V) — BFS 2-colouring.
- **χ computation**: NP-hard time, — — 3-colourability is NP-complete.
- **Interval-graph greedy**: Θ(E log V) time, Θ(V) — optimal for interval graphs.

## Takeaway

# Theory — Graph Coloring
