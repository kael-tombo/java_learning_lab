# CODE_DEEP_DIVE — Topological Sort (Kahn + DFS)
> Java implementation with complexity annotations + pitfalls.

## 1. Complete Implementation
```java
import java.util.*;
public final class Topo { // Kahn O(V+E); DFS O(V+E); PQ variant O((V+E) log V)
    public static List<Integer> kahn(int n, List<List<Integer>> adj) { // returns partial if cycle
        int[] indeg = new int[n];            // O(V)
        for (List<Integer> us : adj)         // O(V+E) indegree pass
            for (int v : us) indeg[v]++;     // O(1) each
        ArrayDeque<Integer> q = new ArrayDeque<>(); // FIFO; PQ for lexicographic
        for (int i = 0; i < n; i++) if (indeg[i] == 0) q.add(i); // O(V) sources
        List<Integer> out = new ArrayList<>(n); // O(V)
        while (!q.isEmpty()) {               // each vertex once → O(V)
            int u = q.poll(); out.add(u);    // O(1)
            for (int v : adj.get(u))         // each edge once → O(E)
                if (--indeg[v] == 0) q.add(v); // O(1)
        }
        return out;                          // size<n ⟺ cycle
    }
    static final int W=0,G=1,B=2;
    public static List<Integer> dfsTopo(int n, List<List<Integer>> adj) { // null if cycle
        int[] c = new int[n];                // O(V)
        LinkedList<Integer> out = new LinkedList<>(); // prepend O(1)
        for (int s = 0; s < n; s++)          // forest O(V+E)
            if (c[s] == W && !dfs(s, adj, c, out)) return null; // back edge
        return out;                          // reverse postorder
    }
    private static boolean dfs(int u, List<List<Integer>> adj, int[] c, LinkedList<Integer> out) {
        c[u] = G;                            // on-stack
        for (int v : adj.get(u)) {           // O(deg)
            if (c[v] == G) return false;     // back edge = cycle
            if (c[v] == W && !dfs(v, adj, c, out)) return false;
        }
        c[u] = B; out.addFirst(u); return true; // finish → prepend
    }
}
```

## 2. Complexity Annotations
- Kahn: indeg O(V+E) + queue O(V) + decrements O(E).
- DFS: colors O(V) + edges once + prepend O(1) each.
- PQ-Kahn adds log V per vertex (ordering cost).

## 3. Pitfalls (5 + fixes)
1. Mutating caller indeg → copy first (done above via fresh array from adj).
2. Parallel edges double-decrement → guard multiset or dedupe.
3. Single-source DFS → misses forest; outer loop required.
4. Preorder mistaken for topo → must be reverse postorder (prepend on finish).
5. Self-loop `u→u` is cycle: Kahn leaves u stranded; DFS sees GRAY self — both flag.

## 4. Micro-Opts
- `int[]` queue ring for 10⁶ DAGs; level-batch for semester counting.

## 5. Test Snippets
```java
// diamond 0→1,0→2,1→3,2→3: valid ABCD/ACBD; cycle 0→1→2→0: kahn.size()<3, dfs null
```

## 6. Checklist
- [ ] Cycle verdict both. [ ] Forest loop. [ ] Tie-break documented.
