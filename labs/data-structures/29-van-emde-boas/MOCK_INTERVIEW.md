# Mock Interview: van Emde Boas Trees

## Q1 — Successor in O(log log U)

**Problem.** Support successor/predecessor on integers from a bounded universe {0..U-1} faster than a BST.

**Key insight.** Recurse on sqrt(U)-sized clusters with a summary structure: each level takes the square root of the universe, so depth is O(log log U). Min/max are cached for O(1) access.

**Complexity.** All ops O(log log U), space O(U).

```java
import java.util.TreeSet;

public class VebQ1 {
    public static void main(String[] args) {
        TreeSet<Integer> s = new TreeSet<>();
        int[] keys = {2, 5, 8, 11};
        for (int k : keys) s.add(k);
        System.out.println(s.higher(5));
        System.out.println(s.lower(5));
        System.out.println(s.first() + "," + s.last());
    }
}
```

Output:

```
8
2
2,11
```

## Q2 — Why Universe Size Matters

**Problem.** When is vEB worth its O(U) space?

**Key insight.** vEB beats comparison structures only for small universes (e.g. 16-bit ports, bounded IDs): log log 2^16 = 4. For 64-bit keys the space is impossible and hashing/BSTs win. Universe size is the deciding question.

**Complexity.** Compare log log U against log n with real constants and memory.

```java
public class VebQ2 {
    public static void main(String[] args) {
        for (int bits : new int[]{8, 16, 32}) {
            long u = 1L << bits;
            double ops = Math.log(Math.log(u) / Math.log(2)) / Math.log(2);
            System.out.printf("U=2^%d levels~%.1f%n", bits, ops);
        }
    }
}
```

Output:

```
U=2^8 levels~3.0
U=2^16 levels~4.0
U=2^32 levels~5.0
```

## Q3 — Proto-vEB on a Tiny Universe

**Problem.** Sketch the cluster/summary recursion on U = 4.

**Key insight.** Split {0..3} into 2 clusters of 2 plus a 2-bit summary. Successor checks the home cluster first, then the summary's next non-empty cluster. The demo below models exactly this two-level structure.

**Complexity.** Two array probes per op at this size; recursion generalizes it.

```java
public class VebQ3 {
    public static void main(String[] args) {
        boolean[][] clusters = {{true, false}, {true, true}};
        boolean[] summary = {true, true};
        int x = 1;
        int hi = x / 2, lo = x % 2;
        Integer succ = null;
        for (int i = lo + 1; i < 2; i++) if (clusters[hi][i]) succ = hi * 2 + i;
        if (succ == null) {
            for (int c = hi + 1; c < 2; c++) {
                if (summary[c]) {
                    for (int i = 0; i < 2; i++) {
                        if (clusters[c][i]) { succ = c * 2 + i; break; }
                    }
                    break;
                }
            }
        }
        System.out.println(succ);
        System.out.println(clusters[0][0] && summary[0]);
    }
}
```

Output:

```
2
true
```
