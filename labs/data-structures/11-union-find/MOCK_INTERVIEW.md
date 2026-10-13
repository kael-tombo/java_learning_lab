# Mock Interview: Union-Find (Disjoint Set Union)

## Q1 — Union by Rank + Path Compression

**Problem.** Implement DSU with near-constant amortized union/find.
**Key insight.** Attach shorter trees under taller ones; flatten paths on find. Together: amortized near-alpha(n).
**Complexity.** Amortized near-alpha(n); space O(n).

```java
public class UnionFindQ1 {
    static int[] p, r;
    static int find(int x) { return p[x] == x ? x : (p[x] = find(p[x])); }
    static void union(int a, int b) {
        a = find(a); b = find(b);
        if (a == b) return;
        if (r[a] < r[b]) p[a] = b; else if (r[a] > r[b]) p[b] = a; else { p[b] = a; r[a]++; }
    }
    public static void main(String[] args) {
        p = new int[]{0, 1, 2, 3, 4}; r = new int[5];
        union(0, 1); union(3, 4); union(1, 4);
        System.out.println(find(0) == find(3));
        System.out.println(find(0) == find(2));
    }
}
```

Output:

```
true
false
```

## Q2 — Kruskal's MST

**Problem.** Where does union-find fit in Kruskal's algorithm?
**Key insight.** Sort edges by weight; accept an edge iff endpoints are in different components. DSU makes the cycle test near-O(1).
**Complexity.** O(E log E) sort; DSU ops near-alpha(n).

```java
import java.util.Arrays;
public class UnionFindQ2 {
    public static void main(String[] args) {
        int[][] e = {{0, 1, 4}, {1, 2, 1}, {0, 2, 3}};
        Arrays.sort(e, (a, b) -> a[2] - b[2]);
        int[] p = {0, 1, 2};
        int total = 0;
        for (int[] x : e) {
            int a = x[0], b = x[1];
            while (p[a] != a) a = p[a];
            while (p[b] != b) b = p[b];
            if (a != b) { p[a] = b; total += x[2]; }
        }
        System.out.println(total);
    }
}
```

Output:

```
4
```

## Q3 — Number of Provinces (LC 547)

**Problem.** Count connected components in an adjacency matrix.
**Key insight.** Union every connected pair, then count distinct roots.
**Complexity.** Time O(n^2 * alpha(n)), space O(n).

```java
public class UnionFindQ3 {
    public static void main(String[] args) {
        int[][] c = {{1, 1, 0}, {1, 1, 0}, {0, 0, 1}};
        int[] p = {0, 1, 2};
        for (int i = 0; i < 3; i++) for (int j = i + 1; j < 3; j++) if (c[i][j] == 1) {
            int a = i; while (p[a] != a) a = p[a];
            int b = j; while (p[b] != b) b = p[b];
            if (a != b) p[a] = b;
        }
        int roots = 0;
        for (int i = 0; i < 3; i++) if (p[i] == i) roots++;
        System.out.println(roots);
    }
}
```

Output:

```
2
```
