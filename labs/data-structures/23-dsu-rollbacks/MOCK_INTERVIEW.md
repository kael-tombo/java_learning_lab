# Mock Interview: DSU with Rollbacks

## Q1 — Undoable Union (no path compression)

**Problem.** Support union, find, snapshot, and rollback.
**Key insight.** Skip path compression (not undoable); union by size plus a change stack gives O(log n) finds and exact rollback to a recorded height.
**Complexity.** Union/find O(log n); snapshot O(1); rollback O(changes undone).

```java
import java.util.ArrayDeque;
import java.util.Deque;
public class DsuRollbackQ1 {
    static int[] parent, size;
    static Deque<int[]> hist = new ArrayDeque<>();
    static int find(int x) { while (parent[x] != x) x = parent[x]; return x; }
    static void union(int a, int b) {
        a = find(a); b = find(b);
        if (a == b) { hist.push(new int[]{-1}); return; }
        if (size[a] < size[b]) { int t = a; a = b; b = t; }
        hist.push(new int[]{b, parent[b], a, size[a]});
        parent[b] = a; size[a] += size[b];
    }
    static void rollback(int snap) {
        while (hist.size() > snap) { int[] e = hist.pop(); if (e[0] != -1) { parent[e[0]] = e[1]; size[e[2]] = e[3]; } }
    }
    public static void main(String[] args) {
        parent = new int[]{0, 1, 2, 3}; size = new int[]{1, 1, 1, 1};
        union(0, 1);
        int s = hist.size();
        union(1, 2);
        System.out.println(find(0) == find(2));
        rollback(s);
        System.out.println(find(0) == find(2));
    }
}
```

Output:

```
true
false
```

## Q2 — Offline Dynamic Connectivity

**Problem.** Edges added/removed over time; answer connectivity at each step.
**Key insight.** Insert each edge's active interval into a segment tree over time; DFS applying unions, rolling back on exit. Rollback DSU makes it sound.
**Complexity.** O((E + Q) log Q); each edge united O(log Q) times.

```java
public class DsuRollbackQ2 {
    public static void main(String[] args) {
        int[][] life = {{0, 2}, {1, 3}, {2, 4}};
        int total = 0;
        for (int[] e : life) total += e[1] - e[0];
        System.out.println("intervals=" + life.length + ",apps=" + total + ",queries=5");
    }
}
```

Output:

```
intervals=3,apps=6,queries=5
```

## Q3 — Why Path Compression Breaks Rollback

**Problem.** Why not just log compression changes too?
**Key insight.** One find can compress many pointers, inflating op and rollback costs unpredictably. Union-by-size alone already bounds finds at O(log n), so little is lost.
**Complexity.** Without compression: O(log n); with it near-alpha(n) but not undoable.

```java
public class DsuRollbackQ3 {
    public static void main(String[] args) {
        int depth = 0;
        for (int x = 1024; x > 1; x /= 2) depth++;
        System.out.println("union-by-size-depth<=" + depth + ",compression=off");
    }
}
```

Output:

```
union-by-size-depth<=10,compression=off
```
