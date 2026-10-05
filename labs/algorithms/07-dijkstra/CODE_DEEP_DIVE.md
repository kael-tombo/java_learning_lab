# CODE_DEEP_DIVE — Dijkstra
> Java implementation with complexity annotations + pitfalls.

## 1. Complete Implementation
```java
import java.util.*;
public final class Dijkstra { // O((V+E) log V) binary-heap; O(V) space
    static final long INF = Long.MAX_VALUE / 4;  // overflow-safe (allows +w)
    public static long[] shortest(List<int[]>[] adj, int s) { // adj[u] = {to,w}
        int n = adj.length;                      // O(1)
        long[] dist = new long[n]; Arrays.fill(dist, INF); // O(V)
        dist[s] = 0;                             // O(1)
        PriorityQueue<long[]> pq = new PriorityQueue<>(Comparator.comparingLong(a -> a[0])); // (d,v)
        pq.add(new long[]{0, s});                // O(log V)
        while (!pq.isEmpty()) {                  // ≤ E pops (lazy duplicates)
            long[] cur = pq.poll(); long d = cur[0]; int u = (int) cur[1]; // O(log V)
            if (d != dist[u]) continue;          // O(1) STALE SKIP (no decrease-key)
            for (int[] e : adj[u]) {             // Σ deg = O(E) relaxations
                int v = e[0]; long nd = d + e[1]; // O(1); long avoids overflow
                if (nd < dist[v]) { dist[v] = nd; pq.add(new long[]{nd, v}); } // O(log V) push
            }
        }
        return dist;                             // INF = unreachable
    }
    public static List<Integer> path(int[] prev, int t) { // O(length)
        List<Integer> p = new ArrayList<>();     // O(1)
        for (int c = t; c != -1; c = prev[c]) p.add(c); // back-chain
        Collections.reverse(p); return p;        // O(length)
    }
}
```

## 2. Complexity Annotations
- Pops ≤ E (lazy), pushes ≤ E → O(E log V); extracts settled once each.
- Early exit for target: stop at pop (final by invariant) — saves drain.
- Naive array-scan variant O(V²): better when E≈V² (no PQ overhead).

## 3. Pitfalls (5 + fixes)
1. Negative edge → silent wrong answer. Fix: assert w≥0; route to Bellman-Ford.
2. Settle-on-push (visited at push) → wrong; settle on pop with stale check.
3. `int` dist + INF overflow on `+w` → long + INF/4.
4. No stale skip → still correct but slower; duplicates pile to E.
5. `prev` unmaintained → path broken; update prev alongside dist.

## 4. Micro-Opts
- Adjacency `int[][]` flat; stop-at-target; bidirectional for single-pair (meet).

## 5. Test Snippets
```java
// s→A4, s→B2, B→A1, A→T1: dist[T]==4 via B; stale (4,A) skipped after (3,A)
// unreachable stays INF; negative single edge demo must be routed away
```

## 6. Checklist
- [ ] w≥0 asserted. [ ] Stale skip. [ ] long + INF/4. [ ] Early-exit noted.
