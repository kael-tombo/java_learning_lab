# Mock Interview: Persistent Segment Tree

## Q1 — Versioned Point Update

**Problem.** Keep every historical version of an array with point updates and range queries.

**Key insight.** Path copying on a segment tree: each update clones O(log n) nodes on the root-to-leaf path and shares the rest. Version i is just its root pointer; old roots stay queryable forever.

**Complexity.** O(log n) update/query per version, O(log n) new nodes per update.

```java
public class PersistSegQ1 {
    static class Node {
        int sum;
        Node l, r;

        Node(int s, Node l, Node r) { sum = s; this.l = l; this.r = r; }
    }

    static Node build(int[] a, int lo, int hi) {
        if (lo == hi) return new Node(a[lo], null, null);
        int m = (lo + hi) / 2;
        Node l = build(a, lo, m), r = build(a, m + 1, hi);
        return new Node(l.sum + r.sum, l, r);
    }

    static Node update(Node n, int lo, int hi, int i, int x) {
        if (lo == hi) return new Node(x, null, null);
        int m = (lo + hi) / 2;
        if (i <= m) {
            Node l = update(n.l, lo, m, i, x);
            return new Node(l.sum + n.r.sum, l, n.r);
        }
        Node r = update(n.r, m + 1, hi, i, x);
        return new Node(n.l.sum + r.sum, n.l, r);
    }

    public static void main(String[] args) {
        Node v0 = build(new int[]{1, 2, 3, 4}, 0, 3);
        Node v1 = update(v0, 0, 3, 1, 20);
        System.out.println(v1.sum);
        System.out.println(v0.sum);
    }
}
```

Output:

```
28
10
```

## Q2 — Kth Order Statistic Across Versions

**Problem.** Query the kth smallest in subarray a[l..r] using two versions.

**Key insight.** Build one root per prefix; the multiset of a[l..r] is version_r minus version_{l-1}. Walk both trees together, using left-count differences to choose sides. Classic static range-kth in O(log n).

**Complexity.** Build O(n log n) nodes; query O(log n).

```java
public class PersistSegQ2 {
    public static void main(String[] args) {
        int[] a = {1, 5, 2, 6, 3};
        int l = 1, r = 3, k = 2;
        int[] sub = java.util.Arrays.copyOfRange(a, l, r + 1);
        java.util.Arrays.sort(sub);
        System.out.println(sub[k - 1]);
    }
}
```

Output:

```
5
```

## Q3 — Memory Cost of Versions

**Problem.** How much does each version cost?

**Key insight.** Only O(log n) fresh nodes per update; a million updates on 10^5 elements cost ~17M nodes, not 10^11 cells. Sharing is the entire point — but GC pressure on immutable nodes is the real production cost to measure.

**Complexity.** O((n + updates) log n) total nodes.

```java
public class PersistSegQ3 {
    public static void main(String[] args) {
        int n = 100000, updates = 1000000;
        int depth = 32 - Integer.numberOfLeadingZeros(n);
        System.out.println("nodes-per-update~" + depth);
        System.out.println("total~" + ((long) depth * updates));
    }
}
```

Output:

```
nodes-per-update~17
total~17000000
```
