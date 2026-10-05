# EXERCISES — Graph Algorithms Deep Track
> Implement + trace + edge cases (Java templates). Track `graph-algorithms-deep`.

## E1. Kruskal + DSU
```java
import java.util.*;
public class E1 {
    // TODO: sort edges by w; union endpoints; sum chosen
    // Cut property: lightest crossing edge is safe
    // Edge: disconnected (forest), equal weights, 1 node
}
```

## E2. Dijkstra with lazy heap
```java
import java.util.*;
public class E2 {
    public static long[] dijkstra(List<int[]>[] adj, int s) {
        long[] dist = new long[adj.length];
        Arrays.fill(dist, Long.MAX_VALUE); dist[s] = 0;
        PriorityQueue<long[]> pq = new PriorityQueue<>(Comparator.comparingLong(a -> a[0]));
        pq.add(new long[]{0, s});
        while (!pq.isEmpty()) {
            long[] cur = pq.poll();
            if (cur[0] != dist[(int) cur[1]]) continue; // stale skip
            for (int[] e : adj[(int) cur[1]]) {
                long nd = cur[0] + e[1];
                if (nd < dist[e[0]]) { dist[e[0]] = nd; pq.add(new long[]{nd, e[0]}); }
            }
        }
        return dist;
    }
}
```
- Edge: unreachable (INF), zero weights OK, negative (reject).

## E3. Bellman-Ford + negative cycle
```java
public class E3 {
    // TODO: V-1 relaxations; one more pass => negative cycle flag
    // Edge: disconnected component cycle, self-loop negative
}
```

## E4. Dinic max-flow
```java
public class E4 {
    // TODO: level BFS; ptr DFS blocking flow; residual add-edge pairs
    // Edge: zero capacity, parallel edges, s==t (reject)
}
```

## E5. Hopcroft-Karp matching
```java
public class E5 {
    // TODO: BFS layer NIL-dist; DFS multi-augment; count
    // Edge: empty side, isolated vertices, non-bipartite (reject/validate)
}
```

## E6. Topo + cycle + HLD query
```java
public class E6 {
    // TODO: Kahn indegrees + queue; leftover count => cycle
    // TODO: HLD parent/depth/heavy/head/pos + segtree path query
    // Edge: multi-component, chain tree (one heavy path)
}
```

## Edge-case checklist
- [ ] Disconnected/unreachable. [ ] Negative weights policy.
- [ ] s==t / empty side. [ ] long distances.

## Trace template
| step | state | decision | invariant holds? |
|---|---|---|---|
| 1 | init | base | yes |

## Review rubric
- [ ] All 6 compile + pass fixtures. [ ] Trace tables filled.
- [ ] Complexity stated per exercise. [ ] One pitfall noted each.
