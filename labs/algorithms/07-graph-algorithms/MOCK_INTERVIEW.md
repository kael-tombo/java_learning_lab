# Mock Interview: Graph Algorithms: BFS, DFS, Dijkstra
> Three worked questions on graph traversal and shortest paths. Each answer is complete runnable Java; outputs below were observed.

## Q1: Print BFS order on a fixed 5-node graph.
Key insight: A queue gives level order: nodes are first reached along a shortest-edge path, so BFS distances from the source are exact in unweighted graphs. The seen-set at enqueue time (not dequeue) prevents duplicate work.
Complexity: Time O(V + E); space O(V).
```java
import java.util.ArrayDeque;
import java.util.Queue;
public class L07Q1Bfs {
    public static void main(String[] args) {
        int[][] g = {{1, 2}, {0, 3}, {0, 3}, {1, 2, 4}, {3}};
        boolean[] seen = {true, false, false, false, false};
        Queue<Integer> q = new ArrayDeque<>();
        q.add(0);
        String s = "";
        while (!q.isEmpty()) {
            int u = q.poll();
            s += u + " ";
            for (int v : g[u]) if (!seen[v]) { seen[v] = true; q.add(v); }
        }
        System.out.println("bfs=" + s.trim());
    }
}
```
Observed output: `bfs=0 1 2 3 4`
Follow-up: Why must nodes be marked when enqueued rather than when dequeued?

## Q2: Print iterative DFS order with an explicit stack.
Key insight: A stack explores one path to its end before backtracking, which is exactly what recursion does implicitly. Pushing neighbors in reverse keeps the visit order identical to the recursive version.
Complexity: Time O(V + E); space O(V).
```java
import java.util.ArrayDeque;
import java.util.Deque;
public class L07Q2Dfs {
    public static void main(String[] args) {
        int[][] g = {{1, 2}, {0, 3}, {0, 3}, {1, 2, 4}, {3}};
        boolean[] seen = new boolean[5];
        Deque<Integer> st = new ArrayDeque<>();
        st.push(0);
        String s = "";
        while (!st.isEmpty()) {
            int u = st.pop();
            if (seen[u]) continue;
            seen[u] = true;
            s += u + " ";
            for (int i = g[u].length - 1; i >= 0; i--) if (!seen[g[u][i]]) st.push(g[u][i]);
        }
        System.out.println("dfs=" + s.trim());
    }
}
```
Observed output: `dfs=0 1 3 2 4`
Follow-up: How does DFS classify edges (tree, back, cross), and which class detects a cycle in a directed graph?

## Q3: Compute single-source shortest paths with Dijkstra on a weighted graph.
Key insight: Dijkstra repeatedly finalizes the unsettled node with the smallest tentative distance; with non-negative weights no later path can beat it. This compact version scans for the minimum; a binary heap makes each extraction logarithmic.
Complexity: Time O(V^2) for this array version, O((V + E) log V) with a binary heap; space O(V + E).
```java
import java.util.Arrays;
public class L07Q3Dijkstra {
    public static void main(String[] args) {
        int[][] e = {{0, 1, 4}, {0, 2, 1}, {2, 1, 2}, {1, 3, 1}, {2, 3, 5}, {3, 4, 3}};
        int[] d = {0, 999, 999, 999, 999};
        boolean[] done = new boolean[5];
        for (int k = 0; k < 5; k++) {
            int u = -1;
            for (int i = 0; i < 5; i++) if (!done[i] && (u < 0 || d[i] < d[u])) u = i;
            done[u] = true;
            for (int[] x : e) if (x[0] == u && d[x[1]] > d[u] + x[2]) d[x[1]] = d[u] + x[2];
        }
        System.out.println("dist=" + Arrays.toString(d));
    }
}
```
Observed output: `dist=[0, 3, 1, 4, 7]`
Follow-up: Give a 3-node graph with one negative edge where Dijkstra returns the wrong distance.

## Checklist
- State the key insight before coding; name the loop invariant.
- Derive time and space bounds from the code structure, not from memory.
