# Mock Interview: Linked Lists

## Q1 — Reverse a Singly Linked List (LC 206)

**Problem.** Reverse a singly linked list in place and return the new head.
**Key insight.** Walk once, redirecting each `next` to the previous node; three pointers suffice. **Complexity.** O(n) time, O(1) space.

```java
public class LinkedListQ1 {
    static class Node {
        int v; Node next;
        Node(int v) { this.v = v; }
    }
    public static void main(String[] args) {
        Node h = new Node(1); h.next = new Node(2); h.next.next = new Node(3);
        Node prev = null, cur = h;
        while (cur != null) { Node n = cur.next; cur.next = prev; prev = cur; cur = n; }
        StringBuilder sb = new StringBuilder();
        for (; prev != null; prev = prev.next) sb.append(prev.v);
        System.out.println(sb);
    }
}
```

Output:

```
321
```

## Q2 — Cycle Detection (Floyd, LC 141)

**Problem.** Determine whether a linked list contains a cycle.
**Key insight.** A 1-step and a 2-step pointer must meet inside a cycle; no extra memory. **Complexity.** O(n) time, O(1) space.

```java
public class LinkedListQ2 {
    static class Node {
        int v; Node next;
        Node(int v) { this.v = v; }
    }
    public static boolean hasCycle(Node h) {
        Node s = h, f = h;
        while (f != null && f.next != null) { s = s.next; f = f.next.next; if (s == f) return true; }
        return false;
    }
    public static void main(String[] args) {
        Node a = new Node(1), b = new Node(2);
        a.next = b; b.next = a;
        System.out.println(hasCycle(a) + " / " + hasCycle(new Node(3)));
    }
}
```

Output:

```
true / false
```

## Q3 — Merge Two Sorted Lists (LC 21)

**Problem.** Merge two sorted linked lists into one sorted list.
**Key insight.** A dummy head removes first-node special-casing; always attach the smaller head. **Complexity.** O(n + m) time, O(1) space.

```java
public class LinkedListQ3 {
    static class Node {
        int v; Node next;
        Node(int v) { this.v = v; }
    }
    public static void main(String[] args) {
        Node a = new Node(1); a.next = new Node(3);
        Node b = new Node(2); b.next = new Node(4);
        Node d = new Node(0), t = d;
        while (a != null && b != null) {
            if (a.v <= b.v) { t.next = a; a = a.next; } else { t.next = b; b = b.next; }
            t = t.next;
        }
        t.next = (a != null) ? a : b;
        StringBuilder sb = new StringBuilder();
        for (Node c = d.next; c != null; c = c.next) sb.append(c.v);
        System.out.println(sb);
    }
}
```

Output:

```
1234
```
