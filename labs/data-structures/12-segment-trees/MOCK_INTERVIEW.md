# Mock Interview: Segment Trees

## Q1 — Range Sum Query (LC 307)

**Problem.** Support point updates and range-sum queries.
**Key insight.** Iterative tree in a size-power-of-two array: leaves at N+i, parents hold child sums; a query climbs merging O(log n) nodes. **Complexity.** O(log n) query/update, O(n) space.

```java
public class SegTreeQ1 {
    public static void main(String[] args) {
        int N = 8; int[] t = new int[16];
        int[] a = {1, 3, 5, 7, 9};
        for (int i = 0; i < 5; i++) t[N + i] = a[i];
        for (int i = N - 1; i > 0; i--) t[i] = t[2 * i] + t[2 * i + 1];
        int l = N + 1, r = N + 3, s = 0;
        while (l <= r) { if ((l & 1) == 1) s += t[l++]; if ((r & 1) == 0) s += t[r--]; l /= 2; r /= 2; }
        System.out.println(s);
    }
}
```

Output:

```
15
```

## Q2 — Range Maximum with Point Update

**Problem.** Query range maximum with single-position updates.
**Key insight.** Same skeleton as range sum; only the merge operator changes (max instead of +). Any associative operator works. **Complexity.** O(log n), O(n) space.

```java
public class SegTreeQ2 {
    static int[] t = new int[20];
    static int q(int v, int l, int r, int L, int R) {
        if (L > r || R < l) return Integer.MIN_VALUE;
        if (L <= l && r <= R) return t[v];
        int m = (l + r) / 2; return Math.max(q(2 * v, l, m, L, R), q(2 * v + 1, m + 1, r, L, R));
    }
    static void u(int v, int l, int r, int i, int x) {
        if (l == r) { t[v] = x; return; }
        int m = (l + r) / 2; if (i <= m) u(2 * v, l, m, i, x); else u(2 * v + 1, m + 1, r, i, x); t[v] = Math.max(t[2 * v], t[2 * v + 1]);
    }
    static void b(int[] a, int v, int l, int r) {
        if (l == r) { t[v] = a[l]; return; }
        int m = (l + r) / 2; b(a, 2 * v, l, m); b(a, 2 * v + 1, m + 1, r); t[v] = Math.max(t[2 * v], t[2 * v + 1]);
    }
    public static void main(String[] args) {
        b(new int[]{2, 8, 1, 9, 4}, 1, 0, 4);
        int before = q(1, 0, 4, 0, 2); u(1, 0, 4, 1, 0);
        System.out.println(before + " / " + q(1, 0, 4, 0, 2));
    }
}
```

Output:

```
8 / 2
```

## Q3 — Lazy Propagation Idea

**Problem.** Range-add updates would touch O(n) leaves naively. How does laziness fix it?
**Key insight.** Stash a pending add at fully covered nodes; push it only when a child is visited. Both range-add and point query then cost O(log n). **Complexity.** O(log n), O(n) space.

```java
public class SegTreeQ3 {
    static int[] t = new int[16], lz = new int[16];
    static void push(int v) { t[2 * v] += lz[v]; lz[2 * v] += lz[v]; t[2 * v + 1] += lz[v]; lz[2 * v + 1] += lz[v]; lz[v] = 0; }
    static void add(int v, int l, int r, int ql, int qr, int x) {
        if (ql > r || qr < l) return;
        if (ql <= l && r <= qr) { t[v] += x; lz[v] += x; return; }
        push(v); int m = (l + r) / 2; add(2 * v, l, m, ql, qr, x); add(2 * v + 1, m + 1, r, ql, qr, x);
    }
    static int get(int v, int l, int r, int i) {
        if (l == r) return t[v];
        push(v); int m = (l + r) / 2; return i <= m ? get(2 * v, l, m, i) : get(2 * v + 1, m + 1, r, i);
    }
    public static void main(String[] args) {
        add(1, 0, 3, 0, 3, 5); System.out.println(get(1, 0, 3, 2));
    }
}
```

Output:

```
5
```
