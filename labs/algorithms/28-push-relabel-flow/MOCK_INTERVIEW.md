# Mock Interview: Push-Relabel Max Flow

Test graph for all three questions (s=0, t=3): 0->1:3, 0->2:2, 1->2:1, 1->3:2, 2->3:3. Max flow is 5.

## Q1: Compute max flow with Edmonds-Karp

Key insight: augment along BFS shortest paths in the residual graph until the sink is unreachable. Complexity: O(V E^2) time; BFS is what makes it polynomial.

```java
public class MaxFlowEKDemo {
    public static void main(String[] a) {
        int n = 4, s = 0, t = 3, flow = 0;
        int[][] res = {{0, 3, 2, 0}, {0, 0, 1, 2}, {0, 0, 0, 3}, {0, 0, 0, 0}};
        int[] par = new int[n];
        for (;;) {
            java.util.Arrays.fill(par, -1); par[s] = s;
            java.util.Queue<Integer> q = new java.util.ArrayDeque<>(java.util.List.of(s));
            while (!q.isEmpty() && par[t] < 0) {
                int u = q.poll();
                for (int v = 0; v < n; v++) if (par[v] < 0 && res[u][v] > 0) { par[v] = u; q.add(v); }
            }
            if (par[t] < 0) break;
            int add = Integer.MAX_VALUE;
            for (int v = t; v != s; v = par[v]) add = Math.min(add, res[par[v]][v]);
            for (int v = t; v != s; v = par[v]) { res[par[v]][v] -= add; res[v][par[v]] += add; }
            flow += add;
        }
        System.out.println("maxflow=" + flow);
    }
}
```

Output:

```text
maxflow=5
```

## Q2: Compute the same flow with generic push-relabel

Key insight: saturate the source edges into a preflow, then push excess downhill in height or relabel stuck nodes upward. Complexity: O(V^3) generic bound; the gap heuristic speeds practice.

```java
public class PushRelabelDemo {
    static int n = 4, s = 0, t = 3; static int[] h = new int[n], ex = new int[n];
    static int[][] cap = {{0, 3, 2, 0}, {0, 0, 1, 2}, {0, 0, 0, 3}, {0, 0, 0, 0}};
    public static void main(String[] a) {
        h[s] = n; // source starts at height n; saturate its edges: preflow
        for (int v = 0; v < n; v++) { ex[v] += cap[s][v]; ex[s] -= cap[s][v]; cap[v][s] += cap[s][v]; cap[s][v] = 0; }
        for (;;) {
            int u = -1;
            for (int i = 0; i < n; i++) if (i != s && i != t && ex[i] > 0) { u = i; break; }
            if (u < 0) break;
            boolean moved = false;
            for (int v = 0; v < n && ex[u] > 0; v++)
                if (cap[u][v] > 0 && h[u] == h[v] + 1) {
                    int d = Math.min(ex[u], cap[u][v]);
                    cap[u][v] -= d; cap[v][u] += d; ex[u] -= d; ex[v] += d; moved = true;
                }
            if (ex[u] > 0 && !moved) { // relabel above lowest residual neighbor
                int m = Integer.MAX_VALUE;
                for (int v = 0; v < n; v++) if (cap[u][v] > 0) m = Math.min(m, h[v]);
                h[u] = m + 1;
            }
        }
        System.out.println("maxflow=" + ex[t]);
    }
}
```

Output:

```text
maxflow=5
```

## Q3: Show the initial preflow heights and excesses

Key insight: initialization sets source height to n and floods its edges, so neighbors start active while conservation is restored later. Complexity: O(V) time; digits below are per-node values for nodes 0-3.

```java
public class PreflowDemo {
    public static void main(String[] a) {
        int n = 4, s = 0; int[][] cap = {{0, 3, 2, 0}, {0, 0, 1, 2}, {0, 0, 0, 3}, {0, 0, 0, 0}};
        int[] h = new int[n], ex = new int[n]; h[s] = n; // source at height n
        for (int v = 0; v < n; v++) { ex[v] += cap[s][v]; ex[s] -= cap[s][v]; cap[v][s] += cap[s][v]; cap[s][v] = 0; }
        System.out.println("h=" + h[0] + h[1] + h[2] + h[3] + " ex=" + ex[0] + ex[1] + ex[2] + ex[3]);
    }
}
```

Output:

```text
h=4000 ex=-5320
```
