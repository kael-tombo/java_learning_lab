# CODE_DEEP_DIVE — Graph Algorithms (Traversal Core)
> Java implementation with complexity annotations + pitfalls.

## 1. Complete Implementation
```java
import java.util.*;
public final class Graphs { // BFS+DFS O(V+E); Dijkstra O((V+E) log V)
    public static List<Integer> bfsOrder(List<List<Integer>> adj, int s) { // O(V+E)
        boolean[] vis = new boolean[adj.size()]; // O(V)
        List<Integer> out = new ArrayList<>();   // O(V)
        ArrayDeque<Integer> q = new ArrayDeque<>(); q.add(s); vis[s] = true; // mark-on-enqueue
        while (!q.isEmpty()) {                   // O(V) dequeues
            int u = q.poll(); out.add(u);        // O(1)
            for (int v : adj.get(u))             // O(E) total
                if (!vis[v]) { vis[v] = true; q.add(v); } // O(1)
        }
        return out;                              // level order
    }
    public static int components(List<List<Integer>> adj) { // O(V+E) forest count
        boolean[] vis = new boolean[adj.size()]; int c = 0; // O(V)
        for (int s = 0; s < adj.size(); s++) {   // forest loop (load-bearing)
            if (vis[s]) continue;                // O(1)
            c++; ArrayDeque<Integer> st = new ArrayDeque<>(); st.push(s); vis[s] = true;
            while (!st.isEmpty()) {              // DFS component flood O(V+E) total
                int u = st.pop();                // O(1)
                for (int v : adj.get(u)) if (!vis[v]) { vis[v] = true; st.push(v); }
            }
        }
        return c;                                // O(1)
    }
    public static boolean isBipartite(List<List<Integer>> adj) { // 2-color O(V+E)
        int[] col = new int[adj.size()]; Arrays.fill(col, -1); // O(V)
        for (int s = 0; s < adj.size(); s++) {   // forest
            if (col[s] != -1) continue;           // O(1)
            col[s] = 0; ArrayDeque<Integer> q = new ArrayDeque<>(); q.add(s);
            while (!q.isEmpty()) {               // BFS color
                int u = q.poll();                // O(1)
                for (int v : adj.get(u)) {       // O(E)
                    if (col[v] == -1) { col[v] = col[u] ^ 1; q.add(v); }
                    else if (col[v] == col[u]) return false; // odd cycle
                }
            }
        }
        return true;                             // O(1)
    }
}
```

## 2. Complexity Annotations
- Each method: vertices once, edges ≤twice → O(V+E) adj-list; matrix → O(V²).
- Forest loop adds no order (still each vertex once).
- Space O(V) colors/queues + O(V+E) graph.

## 3. Pitfalls (5 + fixes)
1. Missing forest loop → wrong components/bipartite on disconnected. Fix: outer for.
2. Mark-on-dequeue → duplicates. Fix: mark on push/enqueue.
3. Directed vs undirected confusion → document edge symmetry.
4. Recursion depth → iterative stacks/queues.
5. Weighted shortest via BFS → wrong; dispatch to Dijkstra.

## 4. Micro-Opts
- `int[][]` adjacency; reuse buffers across queries; early-exit bipartite on conflict.

## 5. Test Snippets
```java
// triangle bipartite? false (odd cycle); square true; two isolated => components 2+
```

## 6. Checklist
- [ ] Forest loops. [ ] Mark-on-enqueue. [ ] Bipartite conflict test.
