# Mock Interview: Cache-Oblivious Structures

## Q1 — Van Emde Boas Layout for Search Trees

**Problem.** Lay out a binary search tree so every block size enjoys locality, without tuning for a specific cache.

**Key insight.** Recursively split the tree at half height: top subtree plus bottom subtrees stored contiguously. Any cache line then holds a useful subtree regardless of line size, giving O(log_B n) block transfers optimally.

**Complexity.** Search O(log_B n) transfers; no cache parameter anywhere.

```java
public class CacheOblivQ1 {
    static int height(int n) {
        return 32 - Integer.numberOfLeadingZeros(n);
    }

    public static void main(String[] args) {
        int n = 1023;
        System.out.println("bst-height=" + height(n));
        System.out.println("transfers-B64~" + (height(n) / 6));
    }
}
```

Output:

```
bst-height=10
transfers-B64~1
```

## Q2 — Tiled (Blocked) Matrix Multiply

**Problem.** Multiply matrices with good cache behavior at every level.

**Key insight.** Process B x B tiles so each tile stays in cache during its inner products; the same code is near-optimal for L1, L2, and TLB simultaneously because blocking helps every level. Naive ijk order streams rows against the cache.

**Complexity.** Same O(n^3) flops; block transfers drop toward the lower bound.

```java
public class CacheOblivQ2 {
    public static void main(String[] args) {
        int[][] a = {{1, 2}, {3, 4}};
        int[][] b = {{5, 6}, {7, 8}};
        int[][] c = new int[2][2];
        int B = 1;
        for (int ii = 0; ii < 2; ii += B) {
            for (int jj = 0; jj < 2; jj += B) {
                for (int kk = 0; kk < 2; kk += B) {
                    for (int i = ii; i < ii + B; i++) {
                        for (int j = jj; j < jj + B; j++) {
                            for (int k = kk; k < kk + B; k++) {
                                c[i][j] += a[i][k] * b[k][j];
                            }
                        }
                    }
                }
            }
        }
        System.out.println(c[0][0] + "," + c[0][1]);
        System.out.println(c[1][0] + "," + c[1][1]);
    }
}
```

Output:

```
19,22
43,50
```

## Q3 — Funnelsort / Cache-Oblivious Sorting Idea

**Problem.** Why can't you just tune mergesort's merge width once?

**Key insight.** Any fixed tuning fits one cache level. Funnelsort uses a recursive k-merger whose buffers are sized by the recursion itself, so every level of the memory hierarchy gets a fitting merge width automatically.

**Complexity.** Optimal O((n/B) log_{M/B}(n/B)) transfers; mergesort with one tuned width is optimal for one level only.

```java
public class CacheOblivQ3 {
    public static void main(String[] args) {
        int n = 1 << 20, B = 64;
        double transfers = (n / (double) B) * (Math.log(n / (double) B) / Math.log(2));
        System.out.printf("%.1f%n", transfers);
        System.out.println("tuned-once=suboptimal-elsewhere");
    }
}
```

Output:

```
229376.0
tuned-once=suboptimal-elsewhere
```
