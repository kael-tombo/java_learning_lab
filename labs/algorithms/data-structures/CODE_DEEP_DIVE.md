# CODE_DEEP_DIVE — Data Structures Track
> Java implementation + pitfalls. Track `data-structures`.

## Canonical: adjacency + BFS/DFS + DSU
```java
import java.util.*;
public final class Structures {
    public static List<Integer>[] graph(int n, int[][] edges) {
        List<Integer>[] adj = new List[n];
        for (int i = 0; i < n; i++) adj[i] = new ArrayList<>();
        for (int[] e : edges) { adj[e[0]].add(e[1]); adj[e[1]].add(e[0]); }
        return adj;
    }
    public static boolean hasCycle(List<Integer>[] adj) {
        int[] color = new int[adj.length];
        for (int s = 0; s < adj.length; s++)
            if (color[s] == 0 && dfs(adj, s, -1, color)) return true;
        return false;
    }
    static boolean dfs(List<Integer>[] adj, int u, int parent, int[] color) {
        color[u] = 1;
        for (int v : adj[u]) {
            if (color[v] == 1 && v != parent) return true;
            if (color[v] == 0 && dfs(adj, v, u, color)) return true;
        }
        color[u] = 2; return false;
    }
    public static final class DSU {
        final int[] p, sz;
        public DSU(int n) {
            p = new int[n]; sz = new int[n];
            for (int i = 0; i < n; i++) { p[i] = i; sz[i] = 1; }
        }
        public int find(int x) {
            while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; }
            return x;
        }
        public void union(int a, int b) {
            a = find(a); b = find(b);
            if (a == b) return;
            if (sz[a] < sz[b]) { int t = a; a = b; b = t; }
            p[b] = a; sz[a] += sz[b];
        }
    }
}
```

## Heap + segment sketches
```java
// Heap: ArrayList<Integer> h; siftUp(i): while i>0 && h[parent]>h[i] swap
// siftDown(i): pick min child; swap while violated. Pitfall: 0- vs 1-index math.
// Segment: tree[4n]; build(node,l,r); query(node,l,r,ql,qr); update point.
// Pitfall: half-open vs closed intervals — pick one, test boundaries.
```

## Pitfalls table
| Pitfall | Symptom | Fix |
|---|---|---|
| Recursive DFS deep graph | StackOverflowError | iterative stack or bigger limit + test |
| Matrix for sparse graph | OOM | adjacency list |
| Forgetting visited set | infinite loop | color/visited array |
| Undirected cycle false positive | always-true | skip parent edge |
| Stale heap entries | wrong min | lazy deletion + version check |
| == on boxed Integer | wrong equality | equals() / intValue |
| Heap index math | off-by-one | parent=(i-1)/2; children 2i+1,2i+2 |
| DSU without compression | TLE | halving + union by size |
| Trie memory blowup | OOM | map children / compress |
| Concurrent modification | CME in traversal | copy or iterator discipline |

## Testing
- Fuzz DSU vs BFS connectivity on random graphs.
- Fuzz heap vs sort on random arrays.
- Segment tree vs brute range sum on 1k random queries.

## Performance notes
- ArrayList adjacency beats LinkedList (cache locality).
- ArrayDeque beats Stack/LinkedList for BFS/DFS.
- Size DSU arrays int[], not boxed.

## Review checklist
- [ ] Cycle logic parent-aware. [ ] Compression present. [ ] Fuzz green.
- [ ] Interval convention tested. [ ] No recursion risk.
