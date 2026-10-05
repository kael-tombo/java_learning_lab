# CODE_DEEP_DIVE — BFS
> Java implementation with complexity annotations + pitfalls.

## 1. Complete Implementation
```java
import java.util.*;
public final class BFS { // O(V+E) adj-list; O(V) space
    public static int[] bfs(List<List<Integer>> adj, int s) { // dist[], -1 = unreached
        int n = adj.size();                       // O(1)
        int[] dist = new int[n]; Arrays.fill(dist, -1); // O(V)
        ArrayDeque<Integer> q = new ArrayDeque<>(); // O(1)
        dist[s] = 0; q.add(s);                   // O(1) init; mark ON ENQUEUE
        while (!q.isEmpty()) {                   // each vertex dequeued ≤ once → O(V)
            int u = q.poll();                    // O(1)
            for (int v : adj.get(u)) {           // Σ deg = O(E) total
                if (dist[v] == -1) {             // O(1) unvisited check
                    dist[v] = dist[u] + 1;       // O(1) level+1
                    q.add(v);                    // O(1) amortized
                }
            }
        }
        return dist;                             // O(1)
    }
    public static List<List<Integer>> levels(List<List<Integer>> adj, int s) { // layer lists
        int n = adj.size(); boolean[] vis = new boolean[n]; // O(V)
        List<List<Integer>> out = new ArrayList<>(); // O(1)
        ArrayDeque<Integer> q = new ArrayDeque<>(); q.add(s); vis[s] = true; // O(1)
        while (!q.isEmpty()) {                   // O(V) dequeues
            int sz = q.size(); List<Integer> lv = new ArrayList<>(sz); // O(1)
            for (int i = 0; i < sz; i++) {       // level width sum = O(V)
                int u = q.poll(); lv.add(u);     // O(1)
                for (int v : adj.get(u)) if (!vis[v]) { vis[v] = true; q.add(v); } // O(E) total
            }
            out.add(lv);                         // O(1)
        }
        return out;                              // O(1)
    }
}
```

## 2. Complexity Annotations
- Outer while O(V) dequeues; inner for total O(E) edge visits (undirected ×2).
- `dist`+`vis`+queue O(V). Matrix would be O(V²) (row scan per pop).
- Level variant same bound; `sz` snapshot preserves layering.

## 3. Pitfalls (5 + fixes)
1. Mark-on-dequeue → duplicates/explosion. Fix: mark on enqueue (both dist+vis).
2. No forest loop → misses components. Fix: outer for over all V for full cover.
3. `LinkedList` queue → slower; use `ArrayDeque`.
4. Recursion for BFS → wrong tool; iterative only.
5. Weighted edges → BFS wrong (1-hop ≠ min-weight); use Dijkstra.

## 4. Micro-Opts
- `int[]` queue ring buffer for 10⁶+ nodes (avoid boxing).
- BitSet visited for dense ids; adjacency `int[][]` for cache.

## 5. Test Snippets
```java
// line s-A-B + s-C: dist s=0,A=1,C=1,B=2 — assert levels [[s],[A,C],[B]]
// disconnected node stays -1; self-loop ignored (dist unchanged)
```

## 6. Checklist
- [ ] Mark-on-enqueue. [ ] Forest loop (if full cover). [ ] Weighted counter-example.
- [ ] Level snapshot (`sz`) correct.
