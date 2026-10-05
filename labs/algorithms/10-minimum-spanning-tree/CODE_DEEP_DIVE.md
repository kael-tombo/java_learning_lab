# CODE_DEEP_DIVE — MST (Kruskal + Prim)
> Java implementation with complexity annotations + pitfalls.

## 1. Complete Implementation
```java
import java.util.*;
public final class MST { // Kruskal O(E log E); Prim O(E log V)
    static class DSU { // α(V) amortized
        int[] p, r; DSU(int n) { p = new int[n]; r = new int[n]; for (int i = 0; i < n; i++) p[i] = i; } // O(V)
        int find(int x) { while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; } return x; } // halving O(α)
        boolean union(int a, int b) { // union by rank
            a = find(a); b = find(b); if (a == b) return false; // same set → cycle edge
            if (r[a] < r[b]) { int t = a; a = b; b = t; } // rank
            p[b] = a; if (r[a] == r[b]) r[a]++; return true; // O(α)
        }
    }
    public static long kruskal(int n, int[][] edges) { // {u,v,w}
        Arrays.sort(edges, Comparator.comparingInt(e -> e[2])); // O(E log E) DOMINANT
        DSU d = new DSU(n); long tot = 0; int took = 0; // O(V)
        for (int[] e : edges) {          // O(E·α)
            if (d.union(e[0], e[1])) { tot += e[2]; if (++took == n - 1) break; } // cut edge
        }
        return tot;                      // forest sum if disconnected (took<n-1)
    }
    public static long prim(List<int[]>[] adj, int s) { // adj[u]={to,w} O(E log V)
        int n = adj.length; boolean[] in = new boolean[n]; // O(V)
        PriorityQueue<long[]> pq = new PriorityQueue<>(Comparator.comparingLong(a -> a[0])); // (w,to)
        pq.add(new long[]{0, s}); long tot = 0; int seen = 0; // O(log V)
        while (!pq.isEmpty()) {          // ≤ E pops
            long[] c = pq.poll(); long w = c[0]; int u = (int) c[1]; // O(log V)
            if (in[u]) continue;         // stale skip O(1)
            in[u] = true; tot += w; seen++; // lightest crossing (cut property)
            for (int[] e : adj[u]) if (!in[e[0]]) pq.add(new long[]{e[1], e[0]}); // O(log V)
        }
        return tot;                      // seen<n ⟺ disconnected
    }
}
```

## 2. Complexity Annotations
- Sort dominates Kruskal; DSU ~α ≈ const (Tarjan bound).
- Prim pushes ≤ E, pops ≤ E; naive V² scan better dense.
- `long tot` (sums overflow int).

## 3. Pitfalls (5 + fixes)
1. Recursive find without compression → O(n) chains. Fix: halving + rank.
2. `int` total overflow → long.
3. Disconnected assumed connected → document MSF vs throw.
4. Directed edges fed to MST → undefined; validate undirected.
5. Prim settle-on-push → wrong; settle on pop w/ stale skip.

## 4. Micro-Opts
- Counting/radix sort for small int weights; Borůvka for parallel.

## 5. Test Snippets
```java
// triangle AB1 BC2 AC3 => 3 both; square ties => 3; disconnected => forest sum + seen<n
```

## 6. Checklist
- [ ] Halving+rank. [ ] long. [ ] Forest handling. [ ] Cut comment.
