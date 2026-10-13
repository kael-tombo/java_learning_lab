# Mock Interview: Immutable and Persistent Data Structures

## Q1 — Path Copying in a Persistent Stack

**Problem.** Stack where push/pop return new versions; old versions stay usable.
**Key insight.** Immutable shared nodes: push allocates one node at the old top; pop returns the stored predecessor. Nothing is ever mutated.
**Complexity.** O(1) push/pop/top, O(1) new nodes per op.

```java
public class PersistentQ1 {
    static class Stack {
        final int head;
        final Stack tail;
        final boolean empty;
        Stack() { empty = true; head = 0; tail = null; }
        Stack(int h, Stack t) { empty = false; head = h; tail = t; }
        Stack push(int x) { return new Stack(x, this); }
    }
    public static void main(String[] args) {
        Stack v0 = new Stack();
        Stack v1 = v0.push(1).push(2);
        System.out.println(v1.head + "," + v1.tail.head + "," + v0.empty);
    }
}
```

Output:

```
2,1,true
```

## Q2 — Persistent Array with Path Copying

**Problem.** Versioned point updates and reads on an array.
**Key insight.** Segment tree copying only the O(log n) update path; untouched subtrees are shared. Flat copies would cost O(n) per version.
**Complexity.** O(log n) update/read, O(log n) new nodes per update.

```java
public class PersistentQ2 {
    static class Node {
        final int v;
        final Node l, r;
        Node(int v, Node l, Node r) { this.v = v; this.l = l; this.r = r; }
    }
    static Node upd(Node n, int lo, int hi, int i, int x) {
        if (lo == hi) return new Node(x, null, null);
        int m = (lo + hi) / 2;
        return i <= m ? new Node(0, upd(n.l, lo, m, i, x), n.r) : new Node(0, n.l, upd(n.r, m + 1, hi, i, x));
    }
    static int get(Node n, int lo, int hi, int i) {
        if (lo == hi) return n.v;
        int m = (lo + hi) / 2;
        return i <= m ? get(n.l, lo, m, i) : get(n.r, m + 1, hi, i);
    }
    public static void main(String[] args) {
        Node v0 = new Node(0, new Node(1, null, null), new Node(2, null, null));
        Node v1 = upd(v0, 0, 1, 0, 9);
        System.out.println(get(v1, 0, 1, 0) + "," + get(v0, 0, 1, 0));
    }
}
```

Output:

```
9,1
```

## Q3 — Why Immutability Helps Concurrency

**Problem.** Why do persistent structures need no locks for readers?
**Key insight.** An immutable version cannot change under a reader: reads are race-free by construction; writers build new versions undisturbed. Price: allocation churn.
**Complexity.** Same asymptotics as ephemeral, modulo allocation constants.

```java
import java.util.List;
public class PersistentQ3 {
    public static void main(String[] args) {
        List<Integer> v0 = List.of(1, 2, 3);
        List<Integer> v1 = java.util.stream.Stream.concat(v0.stream(), java.util.stream.Stream.of(4)).toList();
        System.out.println(v0 + "," + v1);
    }
}
```

Output:

```
[1, 2, 3],[1, 2, 3, 4]
```
