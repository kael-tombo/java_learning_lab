# Code Deep Dive — Approximation Algorithms

A compact but complete Java implementation of the lab's core algorithm(s), with the pitfalls annotated.

```java
import java.util.*;

public final class VertexCover {
    /** Maximal-matching 2-approximation for vertex cover. */
    public static Set<Integer> approx(int[][] edges, int n) {
        boolean[] matchedEdge = new boolean[edges.length];
        boolean[] used = new boolean[n];
        Set<Integer> cover = new HashSet<>();
        // greedily extend a matching
        for (int i = 0; i < edges.length; i++) {
            int u = edges[i][0], v = edges[i][1];
            if (!used[u] && !used[v]) { cover.add(u); cover.add(v); used[u] = used[v] = true; matchedEdge[i] = true; }
        }
        return cover;
    }
}
```

## Pitfalls

- Treating an α-approximation as "almost optimal" on every instance.
- Forgetting the metric hypothesis in TSP — general TSP has no constant-factor approximation.
- Rounding values by integer division without the ε·v_max/n scaling — the guarantee evaporates.
- Reporting α < 1 for a minimisation or α > 1 for a maximisation — the convention is fixed on both sides.
- Using a maximal matching that is not also "every uncovered edge touches a chosen endpoint" — greedy maximal is fine.
- Assuming set cover greedy is exactly log n — it is H_n, which is ln n + O(1).

## Why the bounds hold

- **Greedy set cover**: Θ(|U|·|S|) time, Θ(log n) approximation — tight unless P=NP.
- **Vertex cover, matching**: Θ(V+E) time, 2-approximation — gap 2.
- **Metric TSP, MST-doubling**: Θ(E log V) time, 2-approximation — Christofides: 1.5.
- **Knapsack FPTAS**: Θ(n²/ε) time, (1-ε)-approximation — value-scaling DP.
- **Knapsack exact DP**: Θ(n·W) time, pseudo-polynomial — not polynomial in log W.
- **Set cover lower bound**: no (1-o(1))ln n time, — — unless P=NP.

## Takeaway

# Theory — Approximation Algorithms
