# Mock Interview: Fenwick Tree (Binary Indexed Tree)

## Q1 — Prefix Sums and Point Updates

**Problem.** Maintain an array under point updates with frequent prefix-sum queries.
**Key insight.** Partial sums keyed by `i - (i & -i)` ranges; adding/removing the lowest set bit walks the O(log n) covering cells.
**Complexity.** Update/query O(log n), space O(n); smaller constant than a segment tree.

```java
public class FenwickQ1 {
    static int[] bit = new int[6];
    static void add(int i, int d) { for (i++; i <= 5; i += i & -i) bit[i] += d; }
    static int sum(int i) { int s = 0; for (i++; i > 0; i -= i & -i) s += bit[i]; return s; }
    public static void main(String[] args) {
        for (int i = 0; i < 5; i++) add(i, i + 1);
        System.out.println(sum(2));
        add(1, 10);
        System.out.println(sum(2));
    }
}
```

Output:

```
6
16
```

## Q2 — Range Sum from Two Prefixes

**Problem.** Answer sum(l, r) using only prefix queries.
**Key insight.** sum(l, r) = prefix(r) - prefix(l - 1). No separate range structure needed.
**Complexity.** O(log n) per range query.

```java
public class FenwickQ2 {
    public static void main(String[] args) {
        int[] bit = new int[6];
        int[] a = {2, 4, 6, 8, 10};
        for (int i = 0; i < 5; i++) for (int j = i + 1; j <= 5; j += j & -j) bit[j] += a[i];
        int r = 0, l = 0;
        for (int j = 4; j > 0; j -= j & -j) r += bit[j];
        for (int j = 1; j > 0; j -= j & -j) l += bit[j];
        System.out.println(r - l);
    }
}
```

Output:

```
18
```

## Q3 — Counting Inversions

**Problem.** Count pairs i < j with a[i] > a[j].
**Key insight.** Scan left to right over compressed coordinates; a BIT suffix count per element gives prior greater elements in O(log n).
**Complexity.** Time O(n log n), space O(n).

```java
import java.util.Arrays;
public class FenwickQ3 {
    static int[] bit;
    static void add(int i) { for (; i < bit.length; i += i & -i) bit[i]++; }
    static int sum(int i) { int s = 0; for (; i > 0; i -= i & -i) s += bit[i]; return s; }
    public static void main(String[] args) {
        int[] a = {3, 1, 2}, vals = a.clone();
        Arrays.sort(vals);
        bit = new int[a.length + 1];
        long inv = 0;
        int seen = 0;
        for (int x : a) { int r = Arrays.binarySearch(vals, x) + 1; inv += seen - sum(r); add(r); seen++; }
        System.out.println(inv);
    }
}
```

Output:

```
2
```
