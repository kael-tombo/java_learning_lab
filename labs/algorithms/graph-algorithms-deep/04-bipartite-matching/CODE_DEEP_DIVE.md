# Code Deep Dive — Bipartite Matching

A compact but complete Java implementation of the lab's core algorithm(s), with the pitfalls annotated.

```java
import java.util.*;

public final class HopcroftKarp {
    final int nL, nR; final List<List<Integer>> adj;
    HopcroftKarp(int nL, int nR) { this.nL = nL; this.nR = nR; adj = new ArrayList<>(); for (int i=0;i<nL;i++) adj.add(new ArrayList<>()); }
    void edge(int u, int v) { adj.get(u).add(v); }

    /** Returns the matching size; matchL[u] = v or -1. */
    public int maxMatching() {
        int[] matchL = new int[nL]; int[] matchR = new int[nR]; Arrays.fill(matchL,-1); Arrays.fill(matchR,-1);
        int dist[] = new int[nL]; int total = 0;
        while (bfs(matchL, matchR, dist)) {
            for (int u = 0; u < nL; u++) if (matchL[u] == -1 && dfs(u, matchL, matchR, dist)) total++;
        }
        return total;
    }

    boolean bfs(int[] mL, int[] mR, int[] dist) {
        Queue<Integer> q = new ArrayDeque<>();
        for (int u = 0; u < nL; u++) { dist[u] = mL[u] == -1 ? 0 : -1; if (dist[u] == 0) q.add(u); }
        boolean found = false;
        while (!q.isEmpty()) {
            int u = q.poll();
            for (int v : adj.get(u)) {
                int w = mR[v];
                if (w == -1) found = true;
                else if (dist[w] == -1) { dist[w] = dist[u] + 1; q.add(w); }
            }
        }
        return found;
    }

    boolean dfs(int u, int[] mL, int[] mR, int[] dist) {
        for (int v : adj.get(u)) {
            int w = mR[v];
            if (w == -1 || (dist[w] == dist[u] + 1 && dfs(w, mL, mR, dist))) { mL[u] = v; mR[v] = u; return true; }
        }
        dist[u] = -1; return false;
    }
}
```

## Pitfalls

- Applying Hopcroft–Karp to a non-bipartite graph — use Edmonds' blossom algorithm there.
- Running one augmenting path at a time — that is the O(V·E) method; HK batches shortest paths per phase.
- Forgetting the NIL sentinel in the layered BFS — the DFS then cannot detect when the current shortest-path length is complete.
- Treating a maximal matching as maximum — augmenting paths are the difference.
- Confusing bipartite matching with stable matching when both sides have preferences.
- Using max flow with a poor max-flow algorithm — Dinic on unit capacities recovers the O(E·√V) bound.

## Why the bounds hold

- **Augmenting path (per phase)**: Θ(E) time, Θ(1) — one BFS/DFS.
- **Naive matching**: O(V·E) time, Θ(1) — one augmentation per pass.
- **Hopcroft–Karp**: Θ(E·√V) time, Θ(V) — O(√V) phases × Θ(E) per phase.
- **Hungarian (weighted)**: Θ(n³) time, Θ(n²) — feasible potentials.
- **Min vertex cover from matching**: Θ(V+E) post-processing time, Θ(V) — König construction.

## Takeaway

# Theory — Bipartite Matching
