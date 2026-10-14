# Mock Interview: Graph Coloring and Cliques
> Three questions on coloring versus cliques. Quote the Delta+1 bound and the clique lower bound first.
## Q1: greedy coloring, fixed order
Problem: color a 5-vertex graph visiting vertices 0..4, always taking the smallest free color.
Key insight: greedy never uses more than Delta + 1 colors (4 here) and the output uses 3; quality depends entirely on the visit order.
Complexity: O(V + E) time, O(V) memory.
```java
import java.util.*;
public class L37Q1 {
    public static void main(String[] a){
        int n = 5, used[][] = new int[][]{};
        List<Set<Integer>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new HashSet<>());
        for (int[] x : new int[][]{{0,1},{0,2},{1,2},{1,3},{2,4},{3,4}}){ adj.get(x[0]).add(x[1]); adj.get(x[1]).add(x[0]); }
        int[] col = new int[n]; Arrays.fill(col, -1);
        for (int v = 0; v < n; v++){ boolean[] seen = new boolean[n]; for (int u : adj.get(v)) if (col[u] != -1) seen[col[u]] = true; int c = 0; while (seen[c]) c++; col[v] = c; }
        System.out.println("colors=" + Arrays.toString(col));
    }
}
```
Observed output:
```
colors=[0, 1, 2, 0, 1]
```
Follow-up: construct an ordering that forces greedy to waste colors.
## Q2: Welsh-Powell ordering
Problem: recolor the same graph visiting vertices in descending degree.
Key insight: high-degree vertices constrain the most, so coloring them first is a cheap heuristic; here it also reaches 3 colors.
Complexity: O(V log V + E) time, O(V) memory.
```java
import java.util.*;
public class L37Q2 {
    public static void main(String[] a){
        List<Set<Integer>> adj = new ArrayList<>();
        for (int i = 0; i < 5; i++) adj.add(new HashSet<>());
        for (int[] x : new int[][]{{0,1},{0,2},{1,2},{1,3},{2,4},{3,4}}){ adj.get(x[0]).add(x[1]); adj.get(x[1]).add(x[0]); }
        Integer[] ord = {0,1,2,3,4};
        Arrays.sort(ord, (x,y) -> adj.get(y).size() - adj.get(x).size());
        int[] col = new int[5]; Arrays.fill(col, -1);
        for (int v : ord){ boolean[] seen = new boolean[5]; for (int u : adj.get(v)) if (col[u] != -1) seen[col[u]] = true; int c = 0; while (seen[c]) c++; col[v] = c; }
        System.out.println("order=" + Arrays.toString(ord) + " colors=" + Arrays.toString(col));
    }
}
```
Observed output:
```
order=[1, 2, 0, 3, 4] colors=[2, 0, 1, 1, 0]
```
Follow-up: where does degree order still fail, motivating DSATUR?
## Q3: Bron-Kerbosch max clique
Problem: enumerate maximal cliques with bitmask sets and report the largest.
Key insight: R/P/X recursion with bit operations finds clique {0,1,2} of size 3, so chromatic number >= 3; with the 3-coloring above, chi = 3 exactly.
Complexity: O(3^(n/3)) worst case, tiny on this graph.
```java
public class L37Q3 {
    static int[] nb; static int best, bestSet;
    public static void main(String[] a){
        nb = new int[5];
        for (int[] x : new int[][]{{0,1},{0,2},{1,2},{1,3},{2,3},{3,4}}){ nb[x[0]] |= 1<<x[1]; nb[x[1]] |= 1<<x[0]; }
        bk(0, 0b11111, 0);
        System.out.println("max_clique_size=" + best + " mask=" + Integer.toBinaryString(bestSet));
    }
    static void bk(int R, int P, int X){
        if (P == 0 && X == 0){ if (Integer.bitCount(R) > best){ best = Integer.bitCount(R); bestSet = R; } return; }
        for (int v = 0; v < 5; v++) if ((P & (1<<v)) != 0){ bk(R|(1<<v), P&nb[v], X&nb[v]); P &= ~(1<<v); X |= (1<<v); }
    }
}
```
Observed output:
```
max_clique_size=3 mask=111
```
Follow-up: what does pivoting change in the recursion?
## Pass checklist
- [ ] Verify no edge in Q1 shares a color at both ends.
- [ ] Check the clique vertices are pairwise adjacent in the edge list.
- [ ] Explain why omega <= chi pins the answer at 3 here.
