# CODE_DEEP_DIVE — DFS
> Java implementation with complexity annotations + pitfalls.

## 1. Complete Implementation
```java
import java.util.*;
public final class DFS { // O(V+E) adj-list; O(V) space + stack
    static final int W = 0, G = 1, B = 2;        // colors
    public static boolean hasCycle(List<List<Integer>> adj) { // directed cycle via GRAY
        int n = adj.size(); int[] c = new int[n]; // O(V)
        for (int u = 0; u < n; u++)              // O(V) forest
            if (c[u] == W && dfs(u, adj, c)) return true; // O(E) total edges
        return false;                            // O(1)
    }
    private static boolean dfs(int u, List<List<Integer>> adj, int[] c) { // O(1+deg) each
        c[u] = G;                                // push: on-stack path
        for (int v : adj.get(u)) {               // Σ deg = O(E)
            if (c[v] == G) return true;          // back edge = cycle
            if (c[v] == W && dfs(v, adj, c)) return true; // recurse
        }
        c[u] = B; return false;                  // pop: subtree done
    }
    public static List<Integer> order(List<List<Integer>> adj) { // iterative preorder
        int n = adj.size(); boolean[] vis = new boolean[n]; // O(V)
        List<Integer> out = new ArrayList<>();   // O(V)
        ArrayDeque<Integer> st = new ArrayDeque<>(); // O(V) explicit stack
        for (int s = 0; s < n; s++) {            // forest O(V+E)
            if (vis[s]) continue;                // O(1)
            st.push(s); vis[s] = true;           // O(1)
            while (!st.isEmpty()) {              // each popped once
                int u = st.pop(); out.add(u);    // O(1)
                for (int v : adj.get(u)) if (!vis[v]) { vis[v] = true; st.push(v); } // O(E)
            }
        }
        return out;                              // note: preorder; postorder needs idx-stack
    }
}
```

## 2. Complexity Annotations
- 3-color DFS: each vertex W→G→B once; edges once (directed) → O(V+E).
- Iterative preorder O(V+E) but postorder needs `(node,idx)` stack (two-slot).
- Recursion depth = longest path; chain V=10⁵ overflows — iterative mandatory.

## 3. Pitfalls (5 + fixes)
1. Single visited flag (no GRAY) → cross vs back conflated. Fix: 3 colors / onStack.
2. Undirected without parent check → false cycle on tree edge. Fix: skip parent.
3. Single-source only → misses components. Fix: forest loop.
4. Naive iterative stack ≠ postorder → topo wrong. Fix: iterator-index stack.
5. Deep recursion → StackOverflowError. Fix: explicit ArrayDeque.

## 4. Micro-Opts
- `byte[]` colors; adjacency `int[][]` for cache; reserve ArrayList(n).

## 5. Test Snippets
```java
// 1→2→3→1 => hasCycle true; 1→2→3 => false; disconnected 4 alone => forest covers
// undirected triangle with parent-skip => no false positive (separate method)
```

## 6. Checklist
- [ ] 3-color + back-edge comment. [ ] Forest loop. [ ] Directed vs undirected noted.
- [ ] Postorder caveat documented.
