# Mock Interview: Network Flow: Max-Flow, Bipartite Matching, Min-Cut
> Three worked questions on flows and cuts. Each answer is complete runnable Java; outputs below were observed.

## Q1: Compute max flow on a 4-node network with Edmonds-Karp.
Key insight: Every augmentation pushes flow along a shortest residual path and updates forward/backward residual edges; the loop stops exactly when the sink is unreachable, at which point max-flow min-cut says the flow is optimal.
Complexity: Time O(V*E^2) for Edmonds-Karp; general Ford-Fulkerson is O(E*|f|). Space O(V^2) here.
```java
import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.Queue;
public class L17Q1MaxFlow {
    public static void main(String[] args) {
        int[][] cap = {{0, 3, 2, 0}, {0, 0, 1, 2}, {0, 0, 0, 3}, {0, 0, 0, 0}};
        int flow = 0, f;
        int[] par = new int[4];
        for (;;) {
            Arrays.fill(par, -1); par[0] = 0;
            Queue<Integer> q = new ArrayDeque<>(); q.add(0);
            while (!q.isEmpty() && par[3] < 0) {
                int u = q.poll();
                for (int v = 0; v < 4; v++) if (par[v] < 0 && cap[u][v] > 0) { par[v] = u; q.add(v); }
            }
            if (par[3] < 0) break;
            f = 99; for (int v = 3; v != 0; v = par[v]) f = Math.min(f, cap[par[v]][v]);
            for (int v = 3; v != 0; v = par[v]) { cap[par[v]][v] -= f; cap[v][par[v]] += f; }
            flow += f;
        }
        System.out.println("maxflow=" + flow);
    }
}
```
Observed output: `maxflow=5`
Follow-up: Why does Ford-Fulkerson cost O(E*|f|), and which capacity choice makes that bound hurt?

## Q2: Match 3 workers to 3 jobs with augmenting-path (Kuhn) search.
Key insight: Bipartite matching reduces to flow (source to workers, jobs to sink, unit capacities); Kuhn's DFS finds augmenting paths directly and rematches displaced workers recursively. The match array doubles as the proof of who got which job.
Complexity: Time O(V*E); space O(V).
```java
import java.util.Arrays;
public class L17Q2Bipartite {
    static boolean[][] g = {{true, true, false}, {true, false, false}, {false, true, true}};
    static int[] mt = {-1, -1, -1};
    static boolean[] seen = new boolean[3];
    static boolean kuhn(int u) {
        for (int v = 0; v < 3; v++) {
            if (!g[u][v] || seen[v]) continue; seen[v] = true;
            if (mt[v] < 0 || kuhn(mt[v])) { mt[v] = u; return true; }
        }
        return false;
    }
    public static void main(String[] args) {
        int n = 0;
        for (int u = 0; u < 3; u++) { seen = new boolean[3]; if (kuhn(u)) n++; }
        System.out.println("matching=" + n + " " + Arrays.toString(mt));
    }
}
```
Observed output: `matching=3 [1, 0, 2]`
Follow-up: Trace which worker gets rematched when worker 1 steals job 0, and why the recursion terminates.

## Q3: Verify max-flow min-cut equality by enumerating all s-t cuts.
Key insight: Any s-t cut's capacity upper-bounds every flow; enumerating all 4 cuts of the Q1 network shows the minimum cut equals the computed max flow of 5. The equality certificate is the point, not the enumeration.
Complexity: Enumeration is O(2^V * V^2) - a check for tiny graphs only; real min-cut comes from the residual reachable set.
```java
public class L17Q3MinCut {
    public static void main(String[] args) {
        int[][] cap = {{0, 3, 2, 0}, {0, 0, 1, 2}, {0, 0, 0, 3}, {0, 0, 0, 0}};
        int best = 99; String cut = "";
        for (int m = 0; m < 4; m++) {
            boolean[] inS = {true, (m & 1) != 0, (m & 2) != 0, false};
            int c = 0;
            for (int u = 0; u < 4; u++) for (int v = 0; v < 4; v++) if (inS[u] && !inS[v]) c += cap[u][v];
            if (c < best) { best = c; cut = (inS[1] ? "1" : "") + (inS[2] ? "2" : ""); }
        }
        System.out.println("mincut=" + best + " S={0" + cut + "}");
    }
}
```
Observed output: `mincut=5 S={0}`
Follow-up: How do you read the minimum cut off the residual graph instead of enumerating, and which set is S?

## Checklist
- State the key insight before coding; name the loop invariant.
- Derive time and space bounds from the code structure, not from memory.
