# Mock Interview: Trees

## Q1 — Maximum Depth (LC 104)

**Problem.** Compute the maximum depth of a binary tree.
**Key insight.** Depth is 1 plus the max of children's depths; empty tree is 0. **Complexity.** O(n) time, O(h) stack.

```java
public class TreesQ1 {
    static class Node {
        int v; Node l, r;
        Node(int v) { this.v = v; }
    }
    static int depth(Node n) { return n == null ? 0 : 1 + Math.max(depth(n.l), depth(n.r)); }
    public static void main(String[] args) {
        Node root = new Node(3);
        root.l = new Node(9); root.r = new Node(20); root.r.l = new Node(15);
        System.out.println(depth(root));
    }
}
```

Output:

```
3
```

## Q2 — Validate BST (LC 98)

**Problem.** Check whether a binary tree is a valid BST.
**Key insight.** Carry a (low, high) interval down: left tightens high, right tightens low. **Complexity.** O(n) time, O(h) space.

```java
public class TreesQ2 {
    static class Node {
        int v; Node l, r;
        Node(int v) { this.v = v; }
    }
    static boolean ok(Node n, long lo, long hi) {
        return n == null || (n.v > lo && n.v < hi && ok(n.l, lo, n.v) && ok(n.r, n.v, hi));
    }
    public static void main(String[] args) {
        Node g = new Node(2); g.l = new Node(1); g.r = new Node(3);
        Node b = new Node(5); b.l = new Node(1);
        b.r = new Node(4); b.r.l = new Node(3); b.r.r = new Node(6);
        System.out.println(ok(g, Long.MIN_VALUE, Long.MAX_VALUE) + " / " + ok(b, Long.MIN_VALUE, Long.MAX_VALUE));
    }
}
```

Output:

```
true / false
```

## Q3 — Level-Order Traversal (LC 102)

**Problem.** Return tree values grouped by depth.
**Key insight.** BFS snapshotting queue size per level separates levels without markers. **Complexity.** O(n) time, O(width) space.

```java
public class TreesQ3 {
    static class Node {
        int v; Node l, r;
        Node(int v) { this.v = v; }
    }
    public static void main(String[] args) {
        Node root = new Node(3);
        root.l = new Node(9); root.r = new Node(20);
        java.util.List<java.util.List<Integer>> lv = new java.util.ArrayList<>();
        java.util.Deque<Node> q = new java.util.ArrayDeque<>();
        q.add(root);
        while (!q.isEmpty()) {
            int n = q.size();
            java.util.List<Integer> row = new java.util.ArrayList<>();
            for (int i = 0; i < n; i++) { Node c = q.poll(); row.add(c.v); if (c.l != null) q.add(c.l); if (c.r != null) q.add(c.r); }
            lv.add(row);
        }
        System.out.println(lv);
    }
}
```

Output:

```
[[3], [9, 20]]
```
