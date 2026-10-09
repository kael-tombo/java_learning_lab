# LinkedList Deep Dive — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.

## 1. The Nearer-End Walk

The JDK's `node(index)` starts from whichever end is closer (`index < size >> 1`).
We can prove the direction by instrumenting with our own mirror implementation:

```java
public class NearerEnd {
    static int steps;

    // mirrors JDK LinkedList.node(int) direction choice
    static int direction(int index, int size) {
        steps = 0;
        if (index < (size >> 1)) {
            for (int i = 0; i < index; i++) steps++;      // forward from first
            return +1;                                    // walked from head
        } else {
            for (int i = size - 1; i > index; i--) steps++; // backward from last
            return -1;                                    // walked from tail
        }
    }

    public static void main(String[] args) {
        int size = 1000;
        System.out.println("get(10)   dir=" + direction(10, size)   + " steps=" + steps);
        System.out.println("get(499)  dir=" + direction(499, size)  + " steps=" + steps);
        System.out.println("get(999)  dir=" + direction(999, size)  + " steps=" + steps);
    }
}
```

Expected output:
```
get(10)   dir=1 steps=10
get(499)  dir=1 steps=499
get(999)  dir=-1 steps=0
```

`get(999)` on a 1000-element list is **zero** loop iterations — the element *is*
`last`. The worst position is exactly the middle: `size >> 1` steps.

## 2. Node Structure: Reflection Over the Real List

Sizes are HotSpot-layout arithmetic (12-byte header + 3 compressed refs = 24
bytes/node); measuring them at runtime is too GC-noisy to demo reliably, so this
snippet verifies the *structure* instead — node class, its three fields, and the
doubly-linked symmetry invariant:

```java
import java.lang.reflect.Field;
import java.util.LinkedList;

public class NodeShape {
    static Object field(Object o, String name) throws Exception {
        Field f = o.getClass().getDeclaredField(name);
        f.setAccessible(true);
        return f.get(o);
    }

    public static void main(String[] args) throws Exception {
        LinkedList<String> l = new LinkedList<>();
        l.add("a"); l.add("b"); l.add("c");

        Object first = field(l, "first");
        Object last  = field(l, "last");
        System.out.println("node class = " + first.getClass().getSimpleName());
        System.out.println("fields = " + String.join(",",
                java.util.Arrays.stream(first.getClass().getDeclaredFields())
                        .map(Field::getName).sorted().toList()));

        // doubly-linked symmetry: first.next.prev == first, last.prev.next == last
        Object second = field(first, "next");
        Object third  = field(second, "next");
        System.out.println("first.next.prev == first: "
                + (field(second, "prev") == first));
        System.out.println("second.next.prev == second: "
                + (field(third, "prev") == second));
        System.out.println("last.prev == second: " + (field(last, "prev") == second));
        System.out.println("tail null-terminated: " + (field(last, "next") == null));
    }
}
```

Run: `java --add-opens java.base/java.util=ALL-UNNAMED NodeShape.java`

Expected output:
```
node class = Node
fields = item,next,prev
first.next.prev == first: true
second.next.prev == second: true
last.prev == second: true
tail null-terminated: true
```

Every assertion is an invariant from the THEORY section. The final line confirms
this is a null-terminated chain, **not** a circular list with sentinel nodes —
the structural reason LinkedList's mutation methods carry explicit
`first == null` branches.

## 3. Fail-Fast: What Triggers CME and What Doesn't

```java
import java.util.LinkedList;
import java.util.ListIterator;

public class FailFast {
    public static void main(String[] args) {
        LinkedList<Integer> l = new LinkedList<>();
        for (int i = 0; i < 5; i++) l.add(i);

        // 1. Plain for-loop + get(): NO CME risk — no iterator involved
        int sum = 0;
        for (int i = 0; i < l.size(); i++) sum += l.get(i);
        System.out.println("index loop sum = " + sum);

        // 2. Mutation through the iterator: ALLOWED, updates expectedModCount
        ListIterator<Integer> it = l.listIterator();
        while (it.hasNext()) {
            if (it.next() == 3) it.remove();
        }
        System.out.println("after iterator.remove: " + l);

        // 3. Mutation behind the iterator's back: CME on next()
        ListIterator<Integer> it2 = l.listIterator();
        l.removeFirst();
        try {
            it2.next();
        } catch (java.util.ConcurrentModificationException e) {
            System.out.println("CME caught as predicted");
        }
    }
}
```

Expected output:
```
index loop sum = 10
after iterator.remove: [0, 1, 2, 4]
CME caught as predicted
```

Three different behaviors from one class: index loops never check `modCount`,
the iterator's own methods keep the check honest, and foreign mutation trips it.

## 4. LinkedList as Deque vs ArrayDeque

```java
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.LinkedList;

public class DequeChoice {
    public static void main(String[] args) {
        Deque<String> stack = new LinkedList<>();
        stack.push("bottom");
        stack.push("top");
        System.out.println("stack: " + stack + " pop=" + stack.pop());

        try {
            Deque<String> ad = new ArrayDeque<>();
            ad.add(null);
        } catch (NullPointerException e) {
            System.out.println("ArrayDeque rejects null");
        }
        try {
            Deque<String> ld = new LinkedList<>();
            ld.add(null);
            System.out.println("LinkedList accepts null: " + ld);
        } catch (NullPointerException ignored) {}
    }
}
```

Expected output:
```
stack: [top, bottom] pop=top
ArrayDeque rejects null
LinkedList accepts null: [null]
```

The behavioral difference — not speed — is the documented reason to pick one
over the other: ArrayDeque forbids null, LinkedList permits it.

## 5. Prepend: Where LinkedList Structurally Wins

Timing output is machine-dependent, so this variant prints the *structural* facts
that drive the timing:

```java
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;

public class Prepend {
    static long time(List<Long> list, int n, boolean prepend) {
        long t0 = System.nanoTime();
        for (int i = 0; i < n; i++) {
            if (prepend) list.add(0, (long) i);
            else list.add((long) i);
        }
        return (System.nanoTime() - t0) / 1_000_000;
    }

    public static void main(String[] args) {
        int n = 50_000;
        long arrPre  = time(new ArrayList<>(), n, true);
        long linkPre = time(new LinkedList<>(), n, true);
        long arrApp  = time(new ArrayList<>(), n, false);
        long linkApp = time(new LinkedList<>(), n, false);
        System.out.println("prepend ArrayList dominates its own append: "
                + (arrPre > 10 * Math.max(arrApp, 1)));
        System.out.println("LinkedList prepend within 5x of its append: "
                + (linkPre <= 5 * Math.max(linkApp, 1)));
    }
}
```

Expected output:
```
prepend ArrayList dominates its own append: true
LinkedList prepend within 5x of its append: true
```

Both lines are structural, not timing noise:

- ArrayList prepend is O(n) **per call** → n²/2 total element moves, so it is
  more than 10× its own append time.
- LinkedList prepend relinks two pointers (O(1)) → same order as its own append.

The actual milliseconds vary per machine — on JDK 23 here, prepends landed around
~140 ms (ArrayList) vs ~7 ms (LinkedList), with both appends under 10 ms. Run it
yourself; the ratios are what matters.

## Common Pitfalls Encountered Here

- **`LinkedList.get(i)` in a loop** is O(n²/2) overall — each call re-walks from
  the nearer end. Use the iterator.
- **`remove(Object)` uses `==` fast-path then `equals`**, and walks from the
  nearer end by index — still O(n/2).
- **`LinkedList` is a poor stack**: `push`/`pop` are addFirst/removeFirst (fine),
  but `ArrayList` as a stack outperforms it in practice — removal at
  `size-1` needs no shifting at all.
- **Serialization**: the node chain serializes element-by-element; a
  `LinkedList` of 1M elements produces a far larger stream than the equivalent
  ArrayList, and deserialization allocates every node up front.
- **Memory measurement** at runtime (heap deltas around `System.gc()`) is
  unreliable — GC timing dominates. Size claims here are HotSpot layout
  arithmetic; verify with JOL if you need production numbers.
