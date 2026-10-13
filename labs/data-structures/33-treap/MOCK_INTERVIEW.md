# Mock Interview: Treap

## Q1 — Heap + BST Invariants

**Problem.** Insert keys with random priorities, keeping both invariants.
**Key insight.** BST on keys, heap on priorities; insert as BST then rotate up while the parent priority is lower. Random priorities give expected O(log n) height, no balance bookkeeping.
**Complexity.** Expected O(log n) insert/search/delete.

```java
import java.util.Random;
public class TreapQ1 {
    static class Node {
        int key, prio;
        Node l, r;
        Node(int k, int p) { key = k; prio = p; }
    }
    static Node insert(Node n, int key, int prio) {
        if (n == null) return new Node(key, prio);
        if (key < n.key) { n.l = insert(n.l, key, prio); if (n.l.prio < n.prio) { Node x = n.l; n.l = x.r; x.r = n; n = x; } }
        else if (key > n.key) n.r = insert(n.r, key, prio);
        return n;
    }
    public static void main(String[] args) {
        Random rng = new Random(7);
        Node root = null;
        for (int k : new int[]{5, 2, 8, 1}) root = insert(root, k, rng.nextInt(1000));
        int min = root.key;
        for (Node c = root; c.l != null; c = c.l) min = c.l.key;
        System.out.println((root != null) + "," + min);
    }
}
```

Output:

```
true,1
```

## Q2 — Split and Merge

**Problem.** Why do treap tutorials center split/merge over insert/delete?
**Key insight.** Split by key into (< k, >= k); merge of ordered treaps composes the rest: insert = split + merge with singleton; delete = split twice + merge.
**Complexity.** Expected O(log n) per split/merge.

```java
public class TreapQ2 {
    public static void main(String[] args) {
        java.util.TreeMap<Integer, String> m = new java.util.TreeMap<>();
        m.put(1, "a"); m.put(3, "c"); m.put(5, "e"); m.put(7, "g");
        System.out.println(m.headMap(5).keySet() + "," + m.tailMap(5).keySet());
    }
}
```

Output:

```
[1, 3],[5, 7]
```

## Q3 — Implicit Treap for Sequences

**Problem.** Split-by-position and range reverse on an array.
**Key insight.** Subtree sizes as implicit keys (inorder index); split by size. A lazy reverse flag per node flips children on push: range-reverse in O(log n).
**Complexity.** Expected O(log n) per sequence op.

```java
public class TreapQ3 {
    public static void main(String[] args) {
        int[] l = {0, 0, 0, 1}, r = {0, 0, 3, 0}, sz = new int[4];
        for (int v = 3; v >= 1; v--) sz[v] = 1 + (l[v] == 0 ? 0 : sz[l[v]]) + (r[v] == 0 ? 0 : sz[r[v]]);
        System.out.println(sz[2] + "," + sz[1]);
    }
}
```

Output:

```
2,1
```
