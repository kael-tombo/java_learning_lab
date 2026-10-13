# Mock Interview: Rope

## Q1 — Concat and Split in O(log n)

**Problem.** Edit a huge text buffer with cheap middle inserts.

**Key insight.** Leaves hold short chunks; internal nodes store left-subtree weight. Index/concat/split walk O(log n) nodes, and chunks keep the constant small. Rebalance (or rebuild) when edits skew the tree.

**Complexity.** Index/split/concat O(log n); space O(n) in chunks.

```java
public class RopeQ1 {
    static class Node {
        String s;
        Node l, r;
        int w;

        Node(String s) { this.s = s; w = s.length(); }

        Node(Node l, Node r) {
            this.l = l; this.r = r;
            w = weight(l);
        }

        static int weight(Node n) {
            if (n == null) return 0;
            if (n.s != null) return n.s.length();
            return weight(n.l) + weight(n.r);
        }

        char at(int i) {
            if (s != null) return s.charAt(i);
            return i < w ? l.at(i) : r.at(i - w);
        }
    }

    public static void main(String[] args) {
        Node rope = new Node(new Node("Hello, "), new Node("world"));
        System.out.println(rope.at(0));
        System.out.println(rope.at(7));
        System.out.println(Node.weight(rope));
    }
}
```

Output:

```
H
w
12
```

## Q2 — Why Not StringBuilder for Huge Texts

**Problem.** When does a rope beat StringBuilder?

**Key insight.** StringBuilder edits cost O(n) memmove per middle insert; ropes cost O(log n) pointer work. Below ~MB sizes the rope's pointer chasing loses, so editors use ropes (or piece tables) only past that scale or with persistent undo.

**Complexity.** StringBuilder middle edit O(n); rope O(log n).

```java
public class RopeQ2 {
    public static void main(String[] args) {
        StringBuilder sb = new StringBuilder("abcdef");
        sb.insert(3, "XYZ");
        System.out.println(sb);
        sb.delete(3, 6);
        System.out.println(sb);
    }
}
```

Output:

```
abcXYZdef
abcdef
```

## Q3 — Rebalancing After Many Edits

**Problem.** Repeated splits at one spot degenerate a rope. Fix?

**Key insight.** Track subtree heights (like AVL) and rebuild skewed spines, or rebuild the whole rope from leaves when balance passes a threshold. Amortized cost stays logarithmic.

**Complexity.** Rebuild O(n) rarely; amortized O(log n) per edit.

```java
public class RopeQ3 {
    public static void main(String[] args) {
        int leaves = 8, height = 0;
        for (int n = leaves; n > 1; n = (n + 1) / 2) height++;
        System.out.println("balanced-height=" + height);
        System.out.println("degenerate-height=" + leaves);
    }
}
```

Output:

```
balanced-height=3
degenerate-height=8
```
