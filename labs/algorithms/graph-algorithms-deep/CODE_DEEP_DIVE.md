# CODE_DEEP_DIVE — Graph Algorithms Deep Track
> Java implementation + pitfalls. Track `graph-algorithms-deep`.

## Canonical: Dijkstra + Kahn + DSU-MST
```java
import java.util.*;
public final class Graphs {
    public static long[] dijkstra(List<int[]>[] adj, int s) {
        long[] dist = new long[adj.length];
        Arrays.fill(dist, Long.MAX_VALUE); dist[s] = 0;
        PriorityQueue<long[]> pq = new PriorityQueue<>(Comparator.comparingLong(a -> a[0]));
        pq.add(new long[]{0, s});
        boolean[] done = new boolean[adj.length];
        while (!pq.isEmpty()) {
            long[] cur = pq.poll(); int u = (int) cur[1];
            if (done[u]) continue; done[u] = true;   // settle invariant
            for (int[] e : adj[u]) {
                long nd = cur[0] + e[1];
                if (nd < dist[e[0]]) { dist[e[0]] = nd; pq.add(new long[]{nd, e[0]}); }
            }
        }
        return dist;
    }
    public static List<Integer> topo(List<Integer>[] adj) {
        int n = adj.length; int[] indeg = new int[n];
        for (List<Integer> l : adj) for (int v : l) indeg[v]++;
        Queue<Integer> q = new ArrayDeque<>();
        for (int i = 0; i < n; i++) if (indeg[i] == 0) q.add(i);
        List<Integer> order = new ArrayList<>();
        while (!q.isEmpty()) {
            int u = q.poll(); order.add(u);
            for (int v : adj[u]) if (--indeg[v] == 0) q.add(v);
        }
        return order.size() == n ? order : null;  // null = cycle
    }
}
```

## Dinic sketch
```java
// Edge{to,rev,cap}; addEdge(u,v,c) pairs forward/back.
// bfsLevel(); dfsFlow(u,t,f) blocking; loop while level[t] reachable.
// Pitfall: int cap overflow on sums → long caps; ptr[] current-edge opt.
```

## Pitfalls table
| Pitfall | Symptom | Fix |
|---|---|---|
| Dijkstra negative w | wrong dist | validate + BF fallback |
| int dist overflow | negative paths | long + INF=4e18 guard |
| Stale heap reuse | extra work/wrong | done[] or dist-check |
| Floyd k-inner | wrong answers | k outermost loop |
| Missing residual back | flow stuck | paired back edge |
| s==t maxflow | infinite loop | early return 0/INF policy |
| Non-bipartite to HK | crash | 2-color validate first |
| Recursion DFS deep | StackOverflow | iterative or Kahn |
| HLD off-by-one | wrong ranges | half-open + brute verify |
| Equal-weight MST test | flaky assert | check weight, not edge set |

## Testing
- Fuzz Dijkstra vs Floyd on 200 small graphs (nonneg).
- Fuzz Kruskal vs Prim weight on random graphs.
- Fuzz Dinic vs Edmonds-Karp flow value.

## Performance notes
- Adjacency ArrayList<int[]>; avoid boxed Edge in hot loops.
- Binary heap fine to 1M edges; Fibonacci rarely needed in Java.
- Dinic ptr[] optimization is the 10× difference.

## Review checklist
- [ ] Settle invariant. [ ] Cycle policy. [ ] Fuzz green.
- [ ] long caps/dist. [ ] Residual pairs.
