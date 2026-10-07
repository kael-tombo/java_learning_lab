# Code Deep Dive — Deep Collections Engineering (collections-deep)

Six runnable snippets for the `collections-deep` lab: hash spreading and tree bins, red-black balance in `TreeMap`, atomic updates in `ConcurrentHashMap`, snapshot iteration in `CopyOnWriteArrayList`, the difference between immutable copies and unmodifiable views, and the ordering guarantees of `Deque`, `PriorityQueue` and bounded queues. Each snippet is one file for Java 21 using only JDK classes. Output blocks were pasted from runs on JDK 23.0.1; where a number depends on threads or JVM state the section says so.

## Snippet 1: hash spreading & bins

Because the table length is a power of two, the bucket index uses only the low bits of the hash, so `HashMap` XORs the upper 16 bits into the lower 16 first; hashes that differ only above bit 15 would otherwise all land in bucket 0. When one bin collects 8 or more entries and the table has at least 64 slots, `HashMap` converts the chain into a red-black tree (JEP 180); below 64 slots it resizes instead. Tree bins order by hash and then by `compareTo` when the key class implements `Comparable` of itself, so Comparable keys keep lookups logarithmic while other keys force a search through both subtrees.

Save as `HashSpreadCollisions.java`, then:

```bash
javac --release 21 -proc:none -d out HashSpreadCollisions.java
java -cp out HashSpreadCollisions
```

```java
import java.util.HashMap;
import java.util.Map;

public class HashSpreadCollisions {
    static int spread(int h) { return h ^ (h >>> 16); }

    // Every key has the same hashCode, so all of them land in one bin.
    static final class ComparableKey implements Comparable<ComparableKey> {
        static long equalsCalls, compareCalls;
        final int id;
        ComparableKey(int id) { this.id = id; }
        @Override public int hashCode() { return 42; }
        @Override public boolean equals(Object o) {
            equalsCalls++;
            return o instanceof ComparableKey k && k.id == id;
        }
        @Override public int compareTo(ComparableKey o) {
            compareCalls++;
            return Integer.compare(id, o.id);
        }
    }

    static final class PlainKey {
        static long equalsCalls;
        final int id;
        PlainKey(int id) { this.id = id; }
        @Override public int hashCode() { return 42; }
        @Override public boolean equals(Object o) {
            equalsCalls++;
            return o instanceof PlainKey k && k.id == id;
        }
    }

    public static void main(String[] args) {
        // 1. Why spreading exists: two hashes that differ only above bit 15
        //    map to the same bucket of a 16-slot table unless the high bits are folded in.
        int h1 = 0x10000, h2 = 0x20000, mask = 16 - 1;
        System.out.println("no spreading:   " + (h1 & mask) + " and " + (h2 & mask));
        System.out.println("with spreading: " + (spread(h1) & mask) + " and " + (spread(h2) & mask));

        // 2. Same-hash keys: a Comparable key lets a treeified bin binary-search.
        final int n = 1000;
        Map<ComparableKey, Integer> comparable = new HashMap<>();
        Map<PlainKey, Integer> plain = new HashMap<>();
        for (int i = 0; i < n; i++) {
            comparable.put(new ComparableKey(i), i);
            plain.put(new PlainKey(i), i);
        }

        ComparableKey.equalsCalls = 0;
        ComparableKey.compareCalls = 0;
        comparable.get(new ComparableKey(n - 1));
        System.out.println("Comparable key, one get among " + n + " collisions: equals calls="
                + ComparableKey.equalsCalls + ", compareTo calls=" + ComparableKey.compareCalls);

        PlainKey.equalsCalls = 0;
        plain.get(new PlainKey(n - 1));
        System.out.println("Non-Comparable key, one get among " + n + " collisions: equals calls="
                + PlainKey.equalsCalls);
    }
}
```

Observed output (JDK 23.0.1). The call counts are exact counts of `equals`/`compareTo` invocations. The 357 for the non-Comparable key was identical in three consecutive runs here, but it depends on how the tree was shaped by identity-hash tie-breaking, so treat it as "hundreds", not as a constant.

```text
no spreading:   0 and 0
with spreading: 1 and 2
Comparable key, one get among 1000 collisions: equals calls=18, compareTo calls=15
Non-Comparable key, one get among 1000 collisions: equals calls=357
```

**Pitfall.** A key class with a weak `hashCode` (a constant, or a value with few distinct bits) that is also not `Comparable` makes every lookup in the crowded bin scan a large part of it: the run shows 357 `equals` calls for a single `get` among 1000 colliding keys against 18 plus 15 for the Comparable version. You notice it as `HashMap$TreeNode.find` or `HashMap.getNode` dominating a CPU profile while the map is not even large. The same effect is the basis of hash-flooding denial-of-service attacks on maps keyed by untrusted strings.

## Snippet 2: red-black trees

`TreeMap` is a red-black tree: every node is red or black and the colouring rules guarantee that the longest root-to-leaf path is at most twice the shortest, so height stays at most about 2·log2(n+1) even when keys arrive in sorted order. Each `get` or `put` therefore costs a comparator call per level visited. `subMap`, `headMap` and `tailMap` return live views of the same tree restricted to a key range: writes go through in both directions and a write outside the range is rejected.

Save as `TreeMapBalance.java`, then:

```bash
javac --release 21 -proc:none -d out TreeMapBalance.java
java -cp out TreeMapBalance
```

```java
import java.util.Comparator;
import java.util.NavigableMap;
import java.util.TreeMap;

public class TreeMapBalance {
    static int calls;

    public static void main(String[] args) {
        Comparator<Integer> counting = (a, b) -> { calls++; return Integer.compare(a, b); };
        TreeMap<Integer, String> map = new TreeMap<>(counting);

        // Ascending inserts turn an unbalanced BST into a linked list; a red-black tree rebalances.
        int n = 1023;
        for (int i = 1; i <= n; i++) {
            map.put(i, "v" + i);
        }

        int worst = 0;
        for (int i = 1; i <= n; i++) {
            calls = 0;
            map.get(i);
            worst = Math.max(worst, calls);
        }
        int log2 = 32 - Integer.numberOfLeadingZeros(n + 1) - 1; // log2(1024) = 10
        System.out.println("entries=" + n + " worst-case compare calls for get=" + worst
                + " (red-black height bound 2*log2(n+1)=" + 2 * log2 + ", linked list would need " + n + ")");

        // Navigation and live range views.
        System.out.println("floorKey(500)=" + map.floorKey(500) + " higherKey(500)=" + map.higherKey(500));
        NavigableMap<Integer, String> window = map.subMap(10, true, 12, true);
        System.out.println("subMap [10..12]: " + window);
        window.put(11, "changed");
        map.remove(12);
        System.out.println("backing map sees 11 -> " + map.get(11) + "; view after remove(12): " + window);
        try {
            window.put(99, "outside");
        } catch (IllegalArgumentException e) {
            System.out.println("put outside the view's range: " + e.getMessage());
        }

        // A comparator that returns 0 for different keys makes them the SAME key.
        TreeMap<String, Integer> ci = new TreeMap<>(String.CASE_INSENSITIVE_ORDER);
        ci.put("Key", 1);
        ci.put("KEY", 2);
        System.out.println("case-insensitive map: " + ci + " size=" + ci.size());
    }
}
```

Observed output (JDK 23.0.1). Deterministic: the comparator-call counts depend only on the tree shape that 1023 ascending inserts produce.

```text
entries=1023 worst-case compare calls for get=18 (red-black height bound 2*log2(n+1)=20, linked list would need 1023)
floorKey(500)=500 higherKey(500)=501
subMap [10..12]: {10=v10, 11=v11, 12=v12}
backing map sees 11 -> changed; view after remove(12): {10=v10, 11=changed}
put outside the view's range: key out of range
case-insensitive map: {Key=2} size=1
```

**Pitfall.** A comparator that returns 0 for keys you consider distinct makes them one key. With `String.CASE_INSENSITIVE_ORDER`, `put("KEY", 2)` finds the node holding `"Key"`, replaces its value and keeps the old key object, so the output shows `{Key=2}` with size 1. There is no error, just lost data, and it surfaces later as missing entries. Also remember that mutating a key in a way that changes its ordering corrupts the tree's invariants without any exception.

## Snippet 3: ConcurrentHashMap

`ConcurrentHashMap` reads without locking and updates a bin by CAS-ing into an empty slot or by synchronizing on the first node of a non-empty bin (JDK 8 and later). `merge`, `compute` and `computeIfAbsent` run their function atomically for that key while its bin is locked. A `get` followed by a `put` is two separate atomic operations with a gap between them, and other threads can update the key in that gap.

Save as `MapUpdateRace.java`, then:

```bash
javac --release 21 -proc:none -d out MapUpdateRace.java
java -cp out MapUpdateRace
```

```java
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;
import java.util.function.Consumer;

public class MapUpdateRace {
    static final int THREADS = 8, PER_THREAD = 10_000;

    static int runWith(Consumer<ConcurrentHashMap<String, Integer>> update) throws InterruptedException {
        ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
        map.put("hits", 0);
        CountDownLatch start = new CountDownLatch(1);
        Thread[] ts = new Thread[THREADS];
        for (int t = 0; t < THREADS; t++) {
            ts[t] = new Thread(() -> {
                try {
                    start.await();
                } catch (InterruptedException e) {
                    return;
                }
                for (int i = 0; i < PER_THREAD; i++) {
                    update.accept(map);
                }
            });
            ts[t].start();
        }
        start.countDown();
        for (Thread t : ts) {
            t.join();
        }
        return map.get("hits");
    }

    public static void main(String[] args) throws InterruptedException {
        int expected = THREADS * PER_THREAD;

        // Each call is thread-safe, but get-then-put is two calls: updates are lost.
        int checkThenAct = runWith(m -> m.put("hits", m.get("hits") + 1));
        // merge runs the whole read-modify-write atomically for that key.
        int merged = runWith(m -> m.merge("hits", 1, Integer::sum));
        // compute is the general form of the same guarantee.
        int computed = runWith(m -> m.compute("hits", (k, v) -> v + 1));

        System.out.println("expected  = " + expected);
        System.out.println("get + put = " + checkThenAct + " (lost " + (expected - checkThenAct) + ")");
        System.out.println("merge     = " + merged);
        System.out.println("compute   = " + computed);

        // mappingCount() is the long-valued, documented-as-estimate variant of size().
        ConcurrentHashMap<Integer, Integer> small = new ConcurrentHashMap<>();
        for (int i = 0; i < 5; i++) {
            small.put(i, i);
        }
        System.out.println("quiescent size=" + small.size() + " mappingCount=" + small.mappingCount());
    }
}
```

Observed output (JDK 23.0.1). Nondeterministic. The `get + put` total varies every run (this run lost 52340 of 80000 updates; expect a different loss each time but almost certainly a loss). The `merge` and `compute` rows are always 80000.

```text
expected  = 80000
get + put = 27660 (lost 52340)
merge     = 80000
compute   = 80000
quiescent size=5 mappingCount=5
```

**Pitfall.** The race loses updates with no exception, so the only symptom is counters, totals or caches that are lower than they should be, and only under concurrency, which makes it hard to reproduce in a single-threaded test. A second trap lives in the atomic methods themselves: the function passed to `compute`/`computeIfAbsent` runs while the bin is locked, so it must be short and must not update the same map; the `ConcurrentHashMap` javadoc warns that such recursive updates may block other writers, and some JDK versions throw `IllegalStateException`.

## Snippet 4: CopyOnWriteArrayList

Every mutator of `CopyOnWriteArrayList` takes a lock, copies the backing array with the change applied, and publishes the new array through a volatile field. An iterator holds a reference to the array that existed when it was created, so it never throws `ConcurrentModificationException`, never sees later writes, and cannot support `remove()`. Reads need no lock at all.

Save as `SnapshotIteration.java`, then:

```bash
javac --release 21 -proc:none -d out SnapshotIteration.java
java -cp out SnapshotIteration
```

```java
import java.util.ArrayList;
import java.util.ConcurrentModificationException;
import java.util.Iterator;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

public class SnapshotIteration {
    public static void main(String[] args) {
        List<String> plain = new ArrayList<>(List.of("a", "b", "c"));
        try {
            for (String s : plain) {
                if (s.equals("a")) {
                    plain.add("d");
                }
            }
        } catch (ConcurrentModificationException e) {
            System.out.println("ArrayList: " + e.getClass().getSimpleName());
        }

        CopyOnWriteArrayList<String> cow = new CopyOnWriteArrayList<>(List.of("a", "b", "c"));
        StringBuilder seen = new StringBuilder();
        for (String s : cow) {                 // iterator captured the array as it was here
            seen.append(s);
            if (s.equals("a")) {
                cow.add("d");                  // writes build a fresh array
            }
        }
        System.out.println("COW iteration saw: " + seen + ", list now: " + cow);

        Iterator<String> it = cow.iterator();
        it.next();
        try {
            it.remove();
        } catch (UnsupportedOperationException e) {
            System.out.println("COW iterator.remove(): UnsupportedOperationException");
        }

        // Snapshot semantics: an iterator created before a write never sees it.
        Iterator<String> before = cow.iterator();
        cow.add("e");
        int count = 0;
        while (before.hasNext()) {
            before.next();
            count++;
        }
        System.out.println("iterator made before add(\"e\") saw " + count + " elements; list has " + cow.size());

        // addIfAbsent is an atomic check-then-add on the array copy.
        System.out.println("addIfAbsent(\"a\")=" + cow.addIfAbsent("a") + " addIfAbsent(\"z\")=" + cow.addIfAbsent("z"));
    }
}
```

Observed output (JDK 23.0.1). Deterministic: all of the mutation here happens on one thread.

```text
ArrayList: ConcurrentModificationException
COW iteration saw: abc, list now: [a, b, c, d]
COW iterator.remove(): UnsupportedOperationException
iterator made before add("e") saw 4 elements; list has 5
addIfAbsent("a")=false addIfAbsent("z")=true
```

**Pitfall.** Because each `add` copies the whole array, using it as a general-purpose list under frequent writes costs O(n) per write and allocates garbage proportional to the list size, so n adds copy O(n²) elements overall. You notice it as high allocation rates and CPU in `Arrays.copyOf` while the list is not large. To judge whether it fits your read/write ratio, benchmark with JMH using the `-prof gc` profiler; do not assume it from the snapshot behaviour shown above.

## Snippet 5: immutable collections

`Collections.unmodifiableList` is a wrapper that forwards reads to the original, so later changes to the source are visible through it. `List.copyOf`, `List.of`, `Set.of` and `Map.of` build their own immutable structures, reject `null`, and the set and map factories also reject duplicate elements or keys. `Set.of` and `Map.of` iterate in an order that is randomized per JVM instance on purpose, and immutability is shallow: it covers the structure, not the elements.

Save as `ImmutableViews.java`, then:

```bash
javac --release 21 -proc:none -d out ImmutableViews.java
java -cp out ImmutableViews
```

```java
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class ImmutableViews {
    public static void main(String[] args) {
        List<String> source = new ArrayList<>(List.of("x", "y"));

        List<String> view = Collections.unmodifiableList(source); // a window onto source
        List<String> copy = List.copyOf(source);                  // an independent immutable copy
        source.add("z");
        System.out.println("unmodifiableList sees later change: " + view);
        System.out.println("List.copyOf does not:               " + copy);

        try {
            copy.add("w");
        } catch (UnsupportedOperationException e) {
            System.out.println("copy.add -> UnsupportedOperationException");
        }

        try {
            List.of("a", null);
        } catch (NullPointerException e) {
            System.out.println("List.of(.., null) -> NullPointerException");
        }
        try {
            Set.of("a", "a");
        } catch (IllegalArgumentException e) {
            System.out.println("Set.of duplicates -> " + e.getMessage());
        }
        try {
            Map.of("k", 1).containsKey(null);
        } catch (NullPointerException e) {
            System.out.println("Map.of(..).containsKey(null) -> NullPointerException");
        }

        // The elements themselves are not frozen: immutability is shallow.
        List<StringBuilder> shallow = List.of(new StringBuilder("hi"));
        shallow.get(0).append("!");
        System.out.println("shallow immutability: " + shallow);

        // Implementation behaviour, not a documented guarantee: copyOf of an immutable list can return it as-is.
        System.out.println("List.copyOf(copy) == copy: " + (List.copyOf(copy) == copy));

        // Set.of iteration order is deliberately randomized per JVM run: do not depend on it.
        System.out.println("Set.of order in this run: " + Set.of("a", "b", "c", "d", "e"));
    }
}
```

Observed output (JDK 23.0.1). Deterministic except the last line: the `Set.of` order differs between JVM runs (here `[d, c, b, a, e]`).

```text
unmodifiableList sees later change: [x, y, z]
List.copyOf does not:               [x, y]
copy.add -> UnsupportedOperationException
List.of(.., null) -> NullPointerException
Set.of duplicates -> duplicate element: a
Map.of(..).containsKey(null) -> NullPointerException
shallow immutability: [hi!]
List.copyOf(copy) == copy: true
Set.of order in this run: [d, c, b, a, e]
```

**Pitfall.** Returning `Collections.unmodifiableList(internalList)` from a getter gives callers a live view, not a snapshot. The output shows the view printing `[x, y, z]` after the owner added `z`; a reader iterating that view while the owner mutates it can hit `ConcurrentModificationException`. If the caller must see a stable list, return `List.copyOf(internalList)`, and remember that mutable elements such as the `StringBuilder` above still change underneath either one.

## Snippet 6: Deque & queues

`ArrayDeque` is a circular array: `push`/`pop` work at the head, `offer`/`poll` add at the tail and remove from the head, and `null` is forbidden because `poll` and `peek` return `null` to mean "empty". `PriorityQueue` is a binary min-heap stored in an array that guarantees only that index 0 is the smallest element, so its `toString` shows the heap layout, not sorted order. A bounded `ArrayBlockingQueue` has several failure modes on a full queue: `offer` returns `false`, `add` throws `IllegalStateException("Queue full")`, and a timed `offer` waits then returns `false`.

Save as `QueueBehaviors.java`, then:

```bash
javac --release 21 -proc:none -d out QueueBehaviors.java
java -cp out QueueBehaviors
```

```java
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.NoSuchElementException;
import java.util.PriorityQueue;
import java.util.Queue;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.TimeUnit;

public class QueueBehaviors {
    public static void main(String[] args) throws InterruptedException {
        Deque<Integer> stack = new ArrayDeque<>();
        stack.push(1);
        stack.push(2);
        stack.push(3);   // push = addFirst
        System.out.println("stack after push 1,2,3: " + stack + " pop=" + stack.pop());

        Queue<Integer> fifo = new ArrayDeque<>();
        fifo.offer(1);
        fifo.offer(2);
        fifo.offer(3);   // offer = addLast
        System.out.println("fifo poll=" + fifo.poll() + " peek=" + fifo.peek());

        try {
            new ArrayDeque<String>().add(null);
        } catch (NullPointerException e) {
            System.out.println("ArrayDeque rejects null (poll() uses null for 'empty')");
        }
        System.out.println("poll on empty: " + new ArrayDeque<String>().poll());
        try {
            new ArrayDeque<String>().remove();
        } catch (NoSuchElementException e) {
            System.out.println("remove on empty: NoSuchElementException");
        }

        // A PriorityQueue is a binary heap in an array: only the head is ordered.
        PriorityQueue<Integer> pq = new PriorityQueue<>();
        for (int v : new int[] {5, 3, 8, 1, 9, 2}) {
            pq.offer(v);
        }
        System.out.println("heap array / toString: " + pq);
        StringBuilder polled = new StringBuilder();
        while (!pq.isEmpty()) {
            polled.append(pq.poll()).append(' ');
        }
        System.out.println("poll order:            " + polled.toString().trim());

        BlockingQueue<String> bounded = new ArrayBlockingQueue<>(2);
        System.out.println("offer 1: " + bounded.offer("a") + ", offer 2: " + bounded.offer("b")
                + ", offer 3: " + bounded.offer("c"));
        try {
            bounded.add("d");
        } catch (IllegalStateException e) {
            System.out.println("add on full queue: " + e.getMessage());
        }
        System.out.println("offer with 50 ms timeout on full queue: "
                + bounded.offer("e", 50, TimeUnit.MILLISECONDS));
    }
}
```

Observed output (JDK 23.0.1). Deterministic; the timed `offer` waits 50 ms before returning `false`.

```text
stack after push 1,2,3: [3, 2, 1] pop=3
fifo poll=1 peek=2
ArrayDeque rejects null (poll() uses null for 'empty')
poll on empty: null
remove on empty: NoSuchElementException
heap array / toString: [1, 3, 2, 5, 9, 8]
poll order:            1 2 3 5 8 9
offer 1: true, offer 2: true, offer 3: false
add on full queue: Queue full
offer with 50 ms timeout on full queue: false
```

**Pitfall.** Printing or iterating a `PriorityQueue` and assuming the sequence is sorted is a real bug: the run prints the heap layout `[1, 3, 2, 5, 9, 8]` while `poll` yields `1 2 3 5 8 9`. Code that logs the queue, copies it into a list, or streams it sees the heap order and the output looks "almost sorted", which hides the mistake. Drain with `poll`, or copy into a list and sort it, when you need ordered output.
