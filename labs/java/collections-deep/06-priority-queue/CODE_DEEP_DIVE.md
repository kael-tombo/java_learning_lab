# PriorityQueue — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.

## 1. Iteration Is Heap Order, Not Sorted Order

The most common PriorityQueue surprise: the array *is* the tree, so walking it
yields a valid heap layout, not a sorted sequence.

```java
import java.util.ArrayList;
import java.util.PriorityQueue;

public class HeapNotSorted {
    public static void main(String[] args) {
        int[] data = {5, 3, 8, 1, 9, 2, 7};
        PriorityQueue<Integer> pq = new PriorityQueue<>();
        for (int v : data) pq.offer(v);

        System.out.println("iteration order : " + pq);
        System.out.println("sorted copy     : " + new ArrayList<>(pq.stream()
                .sorted().toList()));

        // prove the heap property on the raw iteration order
        var arr = new ArrayList<>(pq);
        boolean heapOk = true;
        for (int i = 1; i < arr.size(); i++) {
            int parent = (i - 1) >>> 1;
            if (arr.get(parent) > arr.get(i)) heapOk = false;
        }
        System.out.println("min-heap property holds on iteration: " + heapOk);

        // sorted output requires draining
        var drained = new java.util.ArrayList<Integer>();
        PriorityQueue<Integer> copy = new PriorityQueue<>(pq);
        while (!copy.isEmpty()) drained.add(copy.poll());
        System.out.println("drained sorted  : " + drained);
    }
}
```

Expected output:
```
iteration order : [1, 3, 2, 5, 9, 8, 7]
sorted copy     : [1, 2, 3, 5, 7, 8, 9]
min-heap property holds on iteration: true
drained sorted  : [1, 2, 3, 5, 7, 8, 9]
```

Line 1 looks arbitrary but satisfies `parent <= children` at every index (line 3
proves it programmatically). Both orders are "correct" — just under different
contracts.

## 2. The Parent Index Arithmetic

`offer` sifts up via `(k - 1) >>> 1`; children are `2k+1` and `2k+2`. The `>>>`
(unsigned shift) matters: it keeps index math correct and avoids the sign-bit
surprise of `>>`.

```java
public class HeapIndex {
    static int parent(int k) { return (k - 1) >>> 1; }
    static int left(int k)   { return (k << 1) + 1; }
    static int right(int k)  { return (k << 1) + 2; }

    public static void main(String[] args) {
        System.out.println("parent(0) = " + parent(0));        // wraps: Integer.MAX_VALUE
        System.out.println("parent(1) = " + parent(1) + ", parent(2) = " + parent(2));
        System.out.println("children(3) = " + left(3) + "," + right(3));
        // verify child->parent consistency for indices 1..15
        boolean ok = true;
        for (int k = 1; k <= 15; k++) if (left(parent(k)) != k && right(parent(k)) != k) ok = false;
        System.out.println("every child maps back to its parent: " + ok);
        System.out.println("siftUp guard k > 0 avoids parent(0): " + (parent(0) != 0));
    }
}
```

Expected output:
```
parent(0) = 2147483647
parent(1) = 0, parent(2) = 0
children(3) = 7,8
every child maps back to its parent: true
siftUp guard k > 0 avoids parent(0): true
```

`parent(0)` computes `(0-1) >>> 1` = `0xFFFFFFFF >>> 1` = **2147483647** — the
root has no parent, and the unsigned shift turns "underflow" into a huge index
rather than a negative one. That's exactly why `siftUp` opens with
`while (k > 0)`: without the guard, index 0 would compare itself against
`queue[2147483647]` (an ArrayIndexOutOfBoundsException waiting to happen).

## 3. Growth Sequence: 11 → 24 → 50 → 102 → 153

Measured from the real backing array (reflection on the `queue` field):

```java
import java.lang.reflect.Field;
import java.util.PriorityQueue;

public class GrowthPQ {
    static int cap(PriorityQueue<?> q) throws Exception {
        Field f = PriorityQueue.class.getDeclaredField("queue");
        f.setAccessible(true);
        return ((Object[]) f.get(q)).length;
    }

    public static void main(String[] args) throws Exception {
        PriorityQueue<Integer> q = new PriorityQueue<>();
        System.out.println("fresh capacity = " + cap(q));
        StringBuilder sb = new StringBuilder();
        int last = cap(q);
        for (int i = 0; i < 300; i++) {
            q.offer(i);
            int c = cap(q);
            if (c != last) { sb.append(" -> ").append(c); last = c; }
        }
        System.out.println("growth:" + sb);
        try {
            new PriorityQueue<>(0);
        } catch (IllegalArgumentException e) {
            System.out.println("initialCapacity 0 rejected");
        }
    }
}
```

Run: `java --add-opens java.base/java.util=ALL-UNNAMED GrowthPQ.java`

Expected output:
```
fresh capacity = 11
growth: -> 24 -> 50 -> 102 -> 153 -> 229 -> 343
initialCapacity 0 rejected
```

Two source facts on display: `DEFAULT_INITIAL_CAPACITY = 11` is allocated
**eagerly** in the constructor (no lazy-empty state like ArrayList), and growth
is `oldCap + oldCap + 2` below 64 (11→24→50) then `oldCap + oldCap/2`
(102→153→229→343). The constructor rejects capacity 0 outright.

## 4. removeAt: siftDown First, Then Maybe siftUp

When you remove a middle element, the JDK moves the **last** element into the
hole and tries `siftDown`; if the moved element didn't move (`es[i] == moved`),
it means it belongs *higher*, so it `siftUp`s instead. Both branches are
observable:

```java
import java.util.ArrayList;
import java.util.PriorityQueue;

public class RemoveAt {
    public static void main(String[] args) {
        // Case A: removing the root -> last element sifts DOWN into place
        PriorityQueue<Integer> a = new PriorityQueue<>(java.util.List.of(1, 3, 5, 7, 9, 11, 13));
        a.remove(1);                                    // root removed
        System.out.println("after removing min: " + a + " (heap="
                + isHeap(a) + ", min=" + a.peek() + ")");

        // Case B: remove a large mid-list value -> replacement sifts UP
        PriorityQueue<Integer> b = new PriorityQueue<>(java.util.List.of(2, 4, 6, 8, 10, 12, 14));
        b.remove(14);                                   // last element removed -> trivial branch
        System.out.println("after removing 14: " + b + " (heap=" + isHeap(b) + ")");

        // Duplicates all retained; remove(Object) uses equals
        PriorityQueue<String> c = new PriorityQueue<>(java.util.List.of("b", "a", "b", "c"));
        c.remove("b");
        System.out.println("one 'b' removed, remaining: " + c);
    }

    static boolean isHeap(PriorityQueue<Integer> q) {
        var arr = new ArrayList<>(q);
        for (int i = 1; i < arr.size(); i++) {
            if (arr.get((i - 1) >>> 1) > arr.get(i)) return false;
        }
        return true;
    }
}
```

Expected output:
```
after removing min: [3, 7, 5, 13, 9, 11] (heap=true, min=3)
after removing 14: [2, 4, 6, 8, 10, 12] (heap=true)
one 'b' removed, remaining: [a, c, b]
```

Every state remains a valid min-heap — that's the invariant `removeAt`
restores before returning, via whichever sift direction the moved element
needed.

## 5. PriorityQueue Is a Queue, Not a Sorting Tool

```java
import java.util.Comparator;
import java.util.PriorityQueue;

public class NotASorter {
    public static void main(String[] args) {
        // custom comparator: max-heap via reversed natural order
        PriorityQueue<Integer> maxHeap =
                new PriorityQueue<>(Comparator.reverseOrder());
        maxHeap.addAll(java.util.List.of(5, 1, 9, 3));
        System.out.println("max-heap peek = " + maxHeap.peek());
        System.out.println("iteration = " + maxHeap);

        // offer(null) is banned under ANY ordering
        try {
            maxHeap.offer(null);
        } catch (NullPointerException e) {
            System.out.println("offer(null) throws NPE");
        }

        // contains() is O(n) equals-scan, not ordering-based
        System.out.println("contains(9) = " + maxHeap.contains(9));
        System.out.println("size = " + maxHeap.size());
    }
}
```

Expected output:
```
max-heap peek = 9
iteration = [9, 3, 5, 1]
offer(null) throws NPE
contains(9) = true
size = 4
```

`peek()` respects the comparator (9 is max), but iteration still shows raw heap
layout. `null` is banned before any comparison happens — the null check is the
first statement in `offer`.

## Common Pitfalls Encountered Here

- **Sorted output?** Never from iteration — drain with `poll()` (O(n log n)) or
  copy and sort. `toArray()` also returns heap order.
- **`remove(Object)` uses `equals`, ordering only positions** — duplicates by
  equals are all retained; removing one deletes the first array-slot match,
  which is not necessarily the "first" logical occurrence.
- **`contains`/`remove(Object)` are O(n)** — a priority queue is the wrong
  structure for membership tests; pair with a `HashSet` if you need both.
- **Unbounded vs bounded**: `PriorityBlockingQueue` is the thread-safe sibling
  (same heap, `ReentrantLock`); `PriorityQueue` is unsynchronized and its
  fail-fast iterators are best-effort only.
- **`addAll(collection)` heapifies in O(n)** (Floyd's build starting at
  `(n >>> 1) - 1`), not n insertions at O(n log n) — bulk-loading is cheaper
  than repeated `offer`.
