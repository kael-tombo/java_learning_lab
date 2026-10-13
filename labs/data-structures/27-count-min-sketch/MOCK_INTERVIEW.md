# Mock Interview: Count-Min Sketch

## Q1 — Overestimate-Only Counting

**Problem.** Estimate frequencies in a stream using sublinear memory.

**Key insight.** Keep d rows of w counters; each item increments one counter per row. Collisions only add, so the minimum across rows overestimates but never underestimates. More rows drive the failure probability down exponentially.

**Complexity.** Update/query O(d), space O(d * w).

```java
public class CmsQ1 {
    public static void main(String[] args) {
        int d = 3, w = 7;
        int[][] table = new int[d][w];
        String[] stream = {"a", "b", "a", "c", "a", "b"};
        for (String s : stream) {
            for (int i = 0; i < d; i++) {
                int h = Math.floorMod(s.hashCode() * (31 + i * 17), w);
                table[i][h]++;
            }
        }
        int est = Integer.MAX_VALUE;
        for (int i = 0; i < d; i++) {
            est = Math.min(est, table[i][Math.floorMod("a".hashCode() * (31 + i * 17), w)]);
        }
        System.out.println("true=3 est=" + est);
        System.out.println(est >= 3);
    }
}
```

Output:

```
true=3 est=3
true
```

## Q2 — Sizing from (epsilon, delta) Guarantees

**Problem.** Size a sketch for error at most epsilon * N with probability 1 - delta.

**Key insight.** Textbook bounds: w = ceil(e / epsilon) controls the error scale, d = ceil(ln(1/delta)) controls confidence. Error applies to the overestimate gap, not the raw count.

**Complexity.** Memory O((1/epsilon) log(1/delta)).

```java
public class CmsQ2 {
    public static void main(String[] args) {
        double eps = 0.01, delta = 0.01;
        int w = (int) Math.ceil(Math.E / eps);
        int d = (int) Math.ceil(Math.log(1 / delta));
        System.out.println("w=" + w + " d=" + d);
        System.out.println("counters=" + (w * d));
    }
}
```

Output:

```
w=272 d=5
counters=1360
```

## Q3 — CMS vs Exact HashMap

**Problem.** When does a sketch beat a HashMap counter?

**Key insight.** HashMap is exact but stores every distinct key: O(u) memory for u distinct items. CMS uses fixed O(d*w) memory regardless of cardinality, at the price of one-sided error. High-cardinality streams (IPs, endpoints) favor the sketch.

**Complexity.** HashMap exact O(1)/O(u); CMS bounded error O(d)/O(d*w).

```java
import java.util.HashMap;
import java.util.Map;

public class CmsQ3 {
    public static void main(String[] args) {
        Map<String, Integer> exact = new HashMap<>();
        String[] stream = {"x", "y", "x", "z", "y", "x"};
        for (String s : stream) exact.put(s, exact.getOrDefault(s, 0) + 1);
        System.out.println(exact);
        System.out.println(exact.size());
    }
}
```

Output:

```
{x=3, y=2, z=1}
3
```
