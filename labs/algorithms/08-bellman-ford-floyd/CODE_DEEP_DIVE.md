# CODE_DEEP_DIVE — Bellman-Ford + Floyd-Warshall
> Java implementation with complexity annotations + pitfalls.

## 1. Complete Implementation
```java
import java.util.Arrays;
public final class ShortestNeg { // BF O(VE); FW O(V³)
    static final long INF = Long.MAX_VALUE / 4;  // +w safe
    public static long[] bellmanFord(int n, int[][] edges, int s) { // edges {u,v,w}
        long[] d = new long[n]; Arrays.fill(d, INF); d[s] = 0; // O(V)
        for (int i = 0; i < n - 1; i++) {        // V-1 passes (load-bearing count)
            boolean upd = false;                 // O(1) early-exit flag
            for (int[] e : edges) {              // O(E) relaxations per pass
                int u = e[0], v = e[1]; long w = e[2]; // O(1)
                if (d[u] != INF && d[u] + w < d[v]) { d[v] = d[u] + w; upd = true; } // O(1)
            }
            if (!upd) break;                     // O(1) still need detection pass below
        }
        for (int[] e : edges)                    // Vth detection pass O(E)
            if (d[e[0]] != INF && d[e[0]] + e[2] < d[e[1]])
                throw new IllegalStateException("negative cycle"); // signal
        return d;                                // O(1)
    }
    public static long[][] floyd(long[][] w) { // O(V³) time, O(V²) space in-place
        int n = w.length;                        // O(1)
        long[][] d = new long[n][n];             // O(V²)
        for (int i = 0; i < n; i++) d[i] = w[i].clone(); // O(V²)
        for (int k = 0; k < n; k++)              // K OUTERMOST (semantics!)
            for (int i = 0; i < n; i++) {        // O(V²) per k
                if (d[i][k] == INF) continue;    // O(1) prune + overflow guard
                for (int j = 0; j < n; j++) {    // inner O(V)
                    if (d[k][j] == INF) continue;// O(1)
                    long nd = d[i][k] + d[k][j]; // O(1)
                    if (nd < d[i][j]) d[i][j] = nd; // O(1)
                }
            }
        return d;                                // diag<0 = negative cycle
    }
}
```

## 2. Complexity Annotations
- BF: V passes × E = O(VE); space O(V). Early-exit doesn't remove worst case.
- FW: V³ inner ops Θ(V³); 2-D in-place valid by k-monotonicity.
- Detection included in stated bounds (extra pass / diag scan).

## 3. Pitfalls (5 + fixes)
1. Skipping detection pass (early-exit confusion) → missed cycle. Fix: always detect.
2. FW `i`-outer order → wrong intermediate sets. Fix: k-outer + comment.
3. `INF + w` overflow → guard `!=INF` + INF/4.
4. Undirected negative edge = 2-cycle → instantly negative; validate input.
5. `int` distances overflow on long paths → long.

## 4. Micro-Opts
- SPFA queue for typical sparse (no worst guarantee); Johnson for sparse all-pairs.

## 5. Test Snippets
```java
// s→a5,s→b6,b→a-4 => a==2; cycle a→b-1,b→a-1 => throw; FW 1→2→3 chain updates d[0][2]
```

## 6. Checklist
- [ ] V-1 + detection. [ ] k-outer. [ ] INF guards. [ ] Cycle demo.
