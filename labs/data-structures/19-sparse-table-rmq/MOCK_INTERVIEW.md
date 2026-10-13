# Mock Interview: Sparse Table (RMQ)

## Q1 — O(1) Range Minimum on Static Arrays

**Problem.** Answer many range-minimum queries on an array that never changes.

**Key insight.** Precompute min over intervals of length 2^j. Any query [l, r] of length len is covered by two overlapping blocks of size 2^floor(log2 len); min is idempotent so overlap is harmless.

**Complexity.** Build O(n log n), query O(1), space O(n log n).

```java
public class SparseTableQ1 {
    public static void main(String[] args) {
        int[] a = {7, 2, 9, 1, 5};
        int n = a.length, K = 3;
        int[][] st = new int[n][K];
        for (int i = 0; i < n; i++) st[i][0] = a[i];
        for (int j = 1; j < K; j++) {
            for (int i = 0; i + (1 << j) <= n; i++) {
                st[i][j] = Math.min(st[i][j - 1], st[i + (1 << (j - 1))][j - 1]);
            }
        }
        int l = 1, r = 3, len = r - l + 1;
        int j = 31 - Integer.numberOfLeadingZeros(len);
        System.out.println(Math.min(st[l][j], st[r - (1 << j) + 1][j]));
    }
}
```

Output:

```
1
```

## Q2 — Precomputed Logarithms

**Problem.** Why does every sparse-table tutorial precompute a log table?

**Key insight.** Query needs floor(log2 len) in O(1); Math.log per query works but a `lg[i] = lg[i/2] + 1` table is exact, branch-free, and documents the block sizing.

**Complexity.** O(n) table build, O(1) lookup.

```java
public class SparseTableQ2 {
    public static void main(String[] args) {
        int n = 10;
        int[] lg = new int[n + 1];
        for (int i = 2; i <= n; i++) lg[i] = lg[i / 2] + 1;
        System.out.println(lg[1] + " " + lg[3] + " " + lg[8] + " " + lg[10]);
    }
}
```

Output:

```
0 1 3 3
```

## Q3 — Sparse Table vs Segment Tree

**Problem.** When is a sparse table the wrong choice?

**Key insight.** Sparse tables are static: any point update costs O(n log n) to rebuild, while a segment tree updates in O(log n). They also only support idempotent ops (min/max/gcd); range sum needs disjoint coverage, so use a segment tree or Fenwick tree.

**Complexity.** Static RMQ: sparse table wins queries O(1) vs O(log n); dynamic: segment tree wins updates.

```java
public class SparseTableQ3 {
    public static void main(String[] args) {
        int n = 100000;
        int levels = 32 - Integer.numberOfLeadingZeros(n);
        long cells = (long) n * levels;
        System.out.println("levels=" + levels);
        System.out.println("cells=" + cells);
        System.out.println("static-only=" + true);
    }
}
```

Output:

```
levels=17
cells=1700000
static-only=true
```
