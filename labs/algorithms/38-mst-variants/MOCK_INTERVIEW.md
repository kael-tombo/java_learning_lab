# Mock Interview: MST Variants
> Three questions on minimum spanning trees. State the cut property before coding.
## Q1: Kruskal with union-find
Problem: MST of a 5-vertex 7-edge graph by ascending edge weight with path-compressed union-find.
Key insight: the cut property certifies each added edge: the lightest edge crossing any cut belongs to some MST, and union-find detects the cycles.
Complexity: O(E log E) time, O(V) memory.
```java
import java.util.*;
public class L38Q1 {
    public static void main(String[] a){
        int[][] e = {{0,1,4},{0,2,3},{1,2,1},{1,3,2},{2,3,4},{3,4,2},{2,4,5}};
        Arrays.sort(e, (x,y) -> x[2]-y[2]);
        int[] p = {0,1,2,3,4}; int w = 0, used = 0;
        for (int[] x : e){ int r1=find(p,x[0]), r2=find(p,x[1]); if (r1 != r2){ p[r1]=r2; w += x[2]; used++; } }
        System.out.println("mst_weight=" + w + " edges=" + used);
    }
    static int find(int[] p, int x){ return p[x]==x ? x : (p[x]=find(p,p[x])); }
}
```
Observed output:
```
mst_weight=8 edges=4
```
Follow-up: why does sorting dominate the running time?
## Q2: Prim dense version
Problem: grow the MST from vertex 0 with the O(V^2) Prim loop on the same graph.
Key insight: Prim maintains the lightest connection from the grown tree outward, which is the same cut argument from the tree side; weight 8 matches Kruskal.
Complexity: O(V^2) time, O(V) memory; heap version is O(E log V).
```java
public class L38Q2 {
    public static void main(String[] a){
        int n = 5, INF = 999, total = 0;
        int[][] w = {{0,4,3,INF,INF},{4,0,1,2,INF},{3,1,0,4,5},{INF,2,4,0,2},{INF,INF,5,2,0}};
        boolean[] in = new boolean[n]; int[] d = {0,INF,INF,INF,INF};
        for (int i = 0; i < n; i++){
            int u = -1; for (int v = 0; v < n; v++) if (!in[v] && (u == -1 || d[v] < d[u])) u = v;
            in[u] = true; total += d[u];
            for (int v = 0; v < n; v++) d[v] = Math.min(d[v], w[u][v]);
        }
        System.out.println("prim_weight=" + total);
    }
}
```
Observed output:
```
prim_weight=8
```
Follow-up: when is the heap version actually faster?
## Q3: second-best MST
Problem: reuse the weight-8 tree and evaluate every non-tree edge as a swap.
Key insight: adding a non-tree edge creates one cycle, and swapping out its heaviest tree edge gives the best tree using that edge; the minimum over swaps is 9.
Complexity: O(E*V) with BFS per swap, O(V + E) memory.
```java
import java.util.*;
public class L38Q3 {
    public static void main(String[] a){
        int[][] mst = {{1,2,1},{1,3,2},{3,4,2},{0,2,3}}; // weight 8, matches Q1/Q2 output
        Map<Integer,List<int[]>> t = new HashMap<>();
        for (int i = 0; i < 5; i++) t.put(i, new ArrayList<>());
        for (int[] x : mst){ t.get(x[0]).add(new int[]{x[1],x[2]}); t.get(x[1]).add(new int[]{x[0],x[2]}); }
        int second = 999;
        for (int[] x : new int[][]{{0,1,4},{2,3,4},{2,4,5}}) second = Math.min(second, 8 + x[2] - maxEdge(t, x[0], x[1]));
        System.out.println("second_best=" + second);
    }
    static int maxEdge(Map<Integer,List<int[]>> t, int s, int d){
        int[] par = new int[5], pw = new int[5]; boolean[] vis = new boolean[5];
        Queue<Integer> q = new ArrayDeque<>(); q.add(s); vis[s] = true; par[s] = -1;
        while (!q.isEmpty()){ int u = q.poll(); for (int[] nb : t.get(u)) if (!vis[nb[0]]){ vis[nb[0]] = true; par[nb[0]] = u; pw[nb[0]] = nb[1]; q.add(nb[0]); } }
        int mx = 0; for (int c = d; c != s; c = par[c]) mx = Math.max(mx, pw[c]); return mx;
    }
}
```
Observed output:
```
second_best=9
```
## Pass checklist
- [ ] Confirm both algorithms report weight 8 on the same graph.
- [ ] Trace one swap in Q3: added edge, cycle, removed edge.
- [ ] State the cut property in one sentence from memory.
