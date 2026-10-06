# Code Deep Dive — Heavy-Light Decomposition

A compact but complete Java implementation of the lab's core algorithm(s), with the pitfalls annotated.

```java
import java.util.*;

public final class HLD {
    final int n; final List<List<Integer>> g; final int[] parent, depth, size, heavy, head, pos;
    int cur = 0; final int[] base;
    HLD(List<List<Integer>> g) { this.g = g; n = g.size(); parent=new int[n]; depth=new int[n]; size=new int[n]; heavy=new int[n]; head=new int[n]; pos=new int[n]; base=new int[n]; Arrays.fill(heavy,-1); dfs1(0,-1); dfs2(0,0); }
    void dfs1(int v, int p) { parent[v]=p; size[v]=1; for (int u : g.get(v)) if (u!=p) { depth[u]=depth[v]+1; dfs1(u,v); size[v]+=size[u]; if (heavy[v]==-1 || size[u]>size[g.get(v).get(0)]) heavy[v]=u; } }
    void dfs2(int v, int h) { head[v]=h; pos[v]=cur; base[cur++]=v; if (heavy[v]!=-1) dfs2(heavy[v], h); for (int u : g.get(v)) if (u!=parent[v] && u!=heavy[v]) dfs2(u, u); }
    /** LCA by chain jumps in O(log n). */
    public int lca(int u, int v) {
        while (head[u] != head[v]) {
            if (depth[head[u]] > depth[head[v]]) u = parent[head[u]];
            else v = parent[head[v]];
        }
        return depth[u] < depth[v] ? u : v;
    }
}
```

## Pitfalls

- Using HLD for subtree queries — Euler-tour is simpler and faster.
- Forgetting that each chain must be contiguous in the base array — visit the heavy child first in the second DFS.
- Double-counting the LCA in a path aggregate — subtract its contribution once.
- Storing pos[] but forgetting top[] — the climb loop needs both.
- Over-decomposing: using HLD when a simple Euler-tour segment tree solves the problem.
- Treating HLD as the only tool — link-cut trees handle dynamic trees; HLD is for static ones.

## Why the bounds hold

- **HLD construction**: Θ(n) time, Θ(n) — two DFS passes.
- **Path query (HLD+segtree)**: Θ(log² n) time, Θ(log² n) — O(log n) segments × O(log n) range query.
- **LCA via HLD**: Θ(log n) time, — — chain jumps.
- **Subtree query via Euler tour**: Θ(log n) time, Θ(log n) — one range query.
- **Binary-lifting LCA (alternative)**: Θ(log n) time, — — Θ(n log n) preprocess.

## Takeaway

# Theory — Heavy-Light Decomposition
