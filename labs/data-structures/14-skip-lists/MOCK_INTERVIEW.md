# Mock Interview: Skip Lists

## Q1 — Randomized Levels

**Problem.** Why does skip list search cost O(log n) expected?
**Key insight.** Promotion with p = 1/2 puts ~n/2^k nodes on level k; search takes a few steps per level over ~log_2 n levels.
**Complexity.** Expected O(log n); worst O(n) with vanishing probability.

```java
import java.util.Random;
public class SkipListQ1 {
    public static void main(String[] args) {
        Random rng = new Random(42);
        long total = 0;
        for (int i = 0; i < 10000; i++) { int l = 1; while (rng.nextDouble() < 0.5 && l < 16) l++; total += l; }
        System.out.printf("%.2f%n", total / 10000.0);
    }
}
```

Output:

```
1.98
```

## Q2 — Ordered Insert and Search

**Problem.** Implement layered forward pointers with search and insert.
**Key insight.** Search top-down (right while next key is smaller, then drop); insert splices the new tower into recorded predecessors.
**Complexity.** Expected O(log n).

```java
public class SkipListQ2 {
    static class Node {
        int v; Node[] fwd;
        Node(int v, int l) { this.v = v; fwd = new Node[l]; }
    }
    static Node head = new Node(Integer.MIN_VALUE, 4);
    static void add(int x, int lvl) {
        Node[] up = new Node[4];
        Node c = head;
        for (int l = 3; l >= 0; l--) { while (c.fwd[l] != null && c.fwd[l].v < x) c = c.fwd[l]; up[l] = c; }
        Node n = new Node(x, lvl);
        for (int l = 0; l < lvl; l++) { n.fwd[l] = up[l].fwd[l]; up[l].fwd[l] = n; }
    }
    static boolean contains(int x) {
        Node c = head;
        for (int l = 3; l >= 0; l--) while (c.fwd[l] != null && c.fwd[l].v < x) c = c.fwd[l];
        return c.fwd[0] != null && c.fwd[0].v == x;
    }
    public static void main(String[] args) {
        add(3, 2); add(1, 1); add(5, 3);
        System.out.println(contains(3));
        System.out.println(contains(4));
    }
}
```

Output:

```
true
false
```

## Q3 — Skip List vs Balanced BST

**Problem.** When is a skip list preferable to a red-black tree?
**Key insight.** Same expected asymptotics but no rotations: concurrent variants lock only local towers, simplifying lock-free design. Cost: pointer overhead + randomness.
**Complexity.** Expected O(log n); ~2n pointers for p = 1/2.

```java
import java.util.concurrent.ConcurrentSkipListMap;
public class SkipListQ3 {
    public static void main(String[] args) {
        ConcurrentSkipListMap<Integer, String> m = new ConcurrentSkipListMap<>();
        m.put(3, "c"); m.put(1, "a"); m.put(2, "b");
        System.out.println(m.firstKey() + "=" + m.firstEntry().getValue() + "," + m.size());
    }
}
```

Output:

```
1=a,3
```
