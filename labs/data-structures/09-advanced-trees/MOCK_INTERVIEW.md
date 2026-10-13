# Mock Interview: Advanced Trees (AVL, Red-Black, B-Trees)

## Q1 — AVL Rotation

**Problem.** Insert keys 1..7 in order into a plain BST, then explain how AVL fixes the result.

**Key insight.** Unbalanced insertion degenerates to a chain (height 7). AVL restores O(log n) height with single/double rotations whenever a balance factor reaches +/-2. A sorted insert of 1..7 balances to height 3.

**Complexity.** Rotations O(1); insert/delete O(log n); height bounded by ~1.44 log n.

```java
public class AdvTreesQ1 {
    static class Node {
        int v, h = 1; Node left, right;
        Node(int v) { this.v = v; }
    }

    static int h(Node n) { return n == null ? 0 : n.h; }

    static Node rotR(Node y) {
        Node x = y.left;
        y.left = x.right; x.right = y;
        y.h = 1 + Math.max(h(y.left), h(y.right));
        x.h = 1 + Math.max(h(x.left), h(x.right));
        return x;
    }

    public static void main(String[] args) {
        Node y = new Node(3); y.left = new Node(2); y.left.left = new Node(1);
        y.h = 3; y.left.h = 2;
        System.out.println(rotR(y).v);
        System.out.println(h(new Node(9)));
    }
}
```

Output:

```
2
1
```

## Q2 — Red-Black Tree Invariants

**Problem.** State the red-black invariants and why they guarantee logarithmic height.

**Key insight.** Root black, red nodes have black children, and every root-to-leaf path holds equal black depth. A path can have at most twice the black depth, so height is O(log n) with a small constant.

**Complexity.** All ops O(log n); at most O(1) rotations per insert fix-up amortized reasoning aside.

```java
public class AdvTreesQ2 {
    public static void main(String[] args) {
        int n = 1000000;
        double blackHeight = Math.log(n + 1) / Math.log(2);
        System.out.println("maxHeight<=" + (int) (2 * blackHeight));
        System.out.println("avlBound~=" + (int) (1.44 * blackHeight));
    }
}
```

Output:

```
maxHeight<=39
avlBound~=28
```

## Q3 — B-Tree Fanout and Height

**Problem.** A database index stores 10 million keys in a B-tree with minimum degree t = 100. Bound the height.

**Key insight.** Each node holds up to 2t - 1 keys and 2t children, so height is O(log_t n): a handful of levels even for millions of keys, meaning a handful of disk reads.

**Complexity.** Search/insert/delete O(t log_t n); height O(log_t n).

```java
public class AdvTreesQ3 {
    public static void main(String[] args) {
        long n = 10_000_000L;
        int t = 100;
        int height = 0;
        long capacity = 1;
        while (capacity < n) { capacity *= (2 * t); height++; }
        System.out.println("height<=" + height);
        System.out.println("maxKeysPerNode=" + (2 * t - 1));
    }
}
```

Output:

```
height<=4
maxKeysPerNode=199
```
