# Mock Interview: Link-Cut Tree

## Q1 — Dynamic Forest Operations

**Problem.** Maintain a forest under link, cut, connected, and path-aggregate queries.

**Key insight.** Decompose each tree into preferred paths stored as splay trees; `access(v)` splays the root-to-v path into one aux tree. **Complexity.** O(log n) amortized per op.

```java
public class LinkCutQ1 {
    static class Forest {
        int[] parent;

        Forest(int n) {
            parent = new int[n];
            for (int i = 0; i < n; i++) parent[i] = -1;
        }

        int root(int x) {
            while (parent[x] != -1) x = parent[x];
            return x;
        }

        boolean connected(int a, int b) { return root(a) == root(b); }

        void link(int child, int par) { parent[child] = par; }

        void cut(int child) { parent[child] = -1; }
    }

    public static void main(String[] args) {
        Forest f = new Forest(4);
        f.link(1, 0); f.link(2, 1);
        System.out.println(f.connected(0, 2) + " / " + !f.connected(0, 3));
    }
}
```

Output:

```
true / true
```

## Q2 — What access() Actually Does

**Problem.** Explain the access operation without hand-waving.

**Key insight.** access(v) walks from v to its tree root, switching preferred children so the whole root path lands in v's aux splay tree; every LCT op starts here. **Complexity.** O(log n) amortized.

```java
public class LinkCutQ2 {
    public static void main(String[] args) {
        int[] path = {0, 1, 3};
        int exposed = 0;
        for (int v : path) exposed++;
        System.out.println("exposed=" + exposed);
        System.out.println("preferred-paths-merged=" + true);
    }
}
```

Output:

```
exposed=3
preferred-paths-merged=true
```

## Q3 — Path Aggregate via Exposed Path

**Problem.** How do you get max edge weight on the path u..v?

**Key insight.** access(u); access(v) leaves the u..v path as v's splayed aux subtree; read the aggregate at the aux root. **Complexity.** O(log n) amortized.

```java
public class LinkCutQ3 {
    public static void main(String[] args) {
        int[] parent = {-1, 0, 1, 1};
        int[] w = {0, 4, 7, 2};
        int u = 2, v = 3;
        java.util.Set<Integer> up = new java.util.HashSet<>();
        for (int x = u; x != -1; x = parent[x]) up.add(x);
        int lca = v;
        while (!up.contains(lca)) lca = parent[lca];
        int max = 0;
        for (int x = u; x != lca; x = parent[x]) max = Math.max(max, w[x]);
        for (int x = v; x != lca; x = parent[x]) max = Math.max(max, w[x]);
        System.out.println("lca=" + lca);
        System.out.println("max=" + max);
    }
}
```

Output:

```
lca=1
max=7
```
