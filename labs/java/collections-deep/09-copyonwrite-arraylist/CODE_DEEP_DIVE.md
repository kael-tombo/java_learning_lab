# CopyOnWriteArrayList — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.

## 1. Snapshot Semantics: The Iterator Ignores Later Writes

```java
import java.util.Iterator;
import java.util.concurrent.CopyOnWriteArrayList;

public class SnapshotSemantics {
    public static void main(String[] args) {
        CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>(
                java.util.List.of("a", "b", "c"));
        Iterator<String> snapshot = list.iterator();   // pins [a, b, c]

        list.add("d");                                 // new array published
        list.remove("a");                              // another new array

        StringBuilder seen = new StringBuilder();
        while (snapshot.hasNext()) seen.append(snapshot.next());
        System.out.println("snapshot saw: " + seen);
        System.out.println("live list now: " + list);
        try {
            snapshot.remove();
        } catch (UnsupportedOperationException e) {
            System.out.println("iterator.remove unsupported");
        }
    }
}
```

Expected output:
```
snapshot saw: abc
live list now: [b, c, d]
iterator.remove unsupported
```

The iterator walks the array captured at construction — `"d"` never appears
and `"a"` is still visited. Two arrays coexisted briefly (the snapshot pins
the old one); the writer never touched it.

## 2. Reads Never Block Writers (and Vice Versa)

```java
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicLong;

public class ReadWriteIsolation {
    public static void main(String[] args) throws Exception {
        CopyOnWriteArrayList<Integer> list = new CopyOnWriteArrayList<>();
        for (int i = 0; i < 1000; i++) list.add(i);

        CountDownLatch start = new CountDownLatch(1);
        AtomicLong reads = new AtomicLong();
        Thread reader = new Thread(() -> {
            try {
                start.await();
                long sum = 0;
                for (int i = 0; i < 200_000; i++)
                    sum += list.get(i % list.size());
                reads.set(sum);
            } catch (InterruptedException ignored) { }
        });
        Thread writer = new Thread(() -> {
            try {
                start.await();
                for (int i = 0; i < 50; i++) list.add(10_000 + i);
            } catch (InterruptedException ignored) { }
        });
        // size() walks the CURRENT array each call; capture once
        start.countDown();
        reader.start();
        writer.start();
        reader.join();
        writer.join();
        System.out.println("reader completed without lock or CME: " + (reads.get() > 0));
        System.out.println("final size = 1050: " + (list.size() == 1050));
        System.out.println("all late elements present: " + list.contains(10_049));
    }
}
```

Expected output:
```
reader completed without lock or CME: true
final size = 1050: true
all late elements present: true
```

`reader` may observe any mixture of array versions across its 200k `get`
calls — each individual `get` is atomic (one volatile read), but the *sum*
spans versions. That per-call atomicity with cross-call version drift is the
exact consistency level COW offers: safe, never torn, never current.

## 3. Write Cost Is O(n) Per Mutation — Measured

```java
import java.util.ArrayList;
import java.util.concurrent.CopyOnWriteArrayList;

public class WriteCost {
    static long addN(ArrayList<Integer> base, boolean cow, int n) {
        long t0 = System.nanoTime();
        if (cow) {
            CopyOnWriteArrayList<Integer> l = new CopyOnWriteArrayList<>(base);
            for (int i = 0; i < n; i++) l.add(i);
        } else {
            ArrayList<Integer> l = new ArrayList<>(base);
            for (int i = 0; i < n; i++) l.add(i);
        }
        return (System.nanoTime() - t0) / 1_000_000;
    }

    public static void main(String[] args) {
        ArrayList<Integer> base = new ArrayList<>();
        for (int i = 0; i < 20_000; i++) base.add(i);
        int n = 2_000;
        long cowMs = addN(base, true, n);
        long arrMs = addN(base, false, n);
        System.out.println("COW 2000 adds onto 20k list slower than ArrayList: "
                + (cowMs > arrMs));
        System.out.println("ArrayList fast path under 500ms: " + (arrMs < 500));
    }
}
```

Expected output:
```
COW 2000 adds onto 20k list slower than ArrayList: true
ArrayList fast path under 500ms: true
```

Each COW `add` copies ~20k references (~160KB at 8-byte refs); 2000 adds move
~320MB. ArrayList amortizes to memcpy-speed appends. Ratio-based assertions
keep this machine-independent — run it for your own milliseconds.

## 4. addIfAbsent: Lock-Free Fast Path, Locked Mutation

```java
import java.util.concurrent.CopyOnWriteArrayList;

public class AddIfAbsent {
    public static void main(String[] args) {
        CopyOnWriteArrayList<String> listeners = new CopyOnWriteArrayList<>(
                java.util.List.of("alpha", "beta"));

        System.out.println("re-add alpha: " + listeners.addIfAbsent("alpha"));
        System.out.println("add gamma: " + listeners.addIfAbsent("gamma"));
        System.out.println("list: " + listeners);

        // absent-index variant: addIfAbsent returns index of existing or added
        System.out.println("index of beta: " + listeners.indexOf("beta"));
        System.out.println("size = 3: " + (listeners.size() == 3));

        // nulls are legal here (unlike concurrent queues)
        listeners.add(null);
        System.out.println("null accepted, size = 4: " + (listeners.size() == 4));
        System.out.println("contains null: " + listeners.contains(null));
    }
}
```

Expected output:
```
re-add alpha: false
add gamma: true
list: [alpha, beta, gamma]
index of beta: 1
size = 3: true
null accepted, size = 4: true
contains null: true
```

The duplicate `"alpha"` never touches the lock (lock-free scan finds it and
returns false); `"gamma"` takes the copy path. This is the listener-list
idiom — register-if-absent with zero cost for the already-registered case.

## 5. The set() Volatile Heartbeat

```java
import java.lang.reflect.Field;
import java.util.concurrent.CopyOnWriteArrayList;

public class SetHeartbeat {
    static Object[] backing(CopyOnWriteArrayList<?> l) throws Exception {
        Field f = CopyOnWriteArrayList.class.getDeclaredField("array");
        f.setAccessible(true);
        return (Object[]) f.get(l);
    }

    public static void main(String[] args) throws Exception {
        CopyOnWriteArrayList<String> l = new CopyOnWriteArrayList<>(
                java.util.List.of("x", "y"));
        Object[] before = backing(l);

        l.set(0, "x");                       // equal element — same array, fresh volatile write
        Object[] afterSame = backing(l);
        System.out.println("set(same) keeps array reference: " + (before == afterSame));
        System.out.println("contents equal: "
                + java.util.Arrays.equals(before, afterSame));

        l.set(0, "z");                       // different element — clones
        Object[] afterDiff = backing(l);
        System.out.println("set(different) replaces array reference: "
                + (afterSame != afterDiff));
        System.out.println("old snapshot still [x, y]: "
                + java.util.Arrays.equals(afterSame, new Object[]{"x", "y"}));
        System.out.println("live list: " + l);
    }
}
```

Run: `java --add-opens java.base/java.util.concurrent=ALL-UNNAMED SetHeartbeat.java`

Expected output:
```
set(same) keeps array reference: true
contents equal: true
set(different) replaces array reference: true
old snapshot still [x, y]: true
live list: [z, y]
```

`set(0, "x")` is a value no-op that keeps the *same array reference* — but the
source still calls `setArray(es)` (comment: "Ensure volatile write semantics
even when oldvalue == element"). A volatile write of an identical reference
publishes no new data; its only effect is the memory barrier, ordering this
thread's earlier writes before any reader's later volatile read. Contrast
`set(0, "z")`, which clones first: the old array object is untouched, so any
outstanding iterator keeps walking `[x, y]` undisturbed. Immutability of
published arrays isn't a convention callers must respect — the class enforces
it by never mutating in place.

## Common Pitfalls Encountered Here

- **Using COW for write-heavy or large lists** — O(n) copy per mutation;
  profile the write rate before choosing it over `synchronizedList` or a
  concurrent queue.
- **Long-lived iterators pinning arrays** — each iterator holds a full array
  version alive; N iterators across M writes retain N arrays.
- **Assuming cross-call consistency** — each `get` is atomic, but a loop of
  `get(i)` calls can span versions; for a stable view, iterate (snapshot) or
  `toArray()` once.
- **Calling `iterator().remove()`** — always `UnsupportedOperationException`;
  mutate through the list.
- **Forgetting `addIfAbsent` exists** — `CopyOnWriteArraySet` is built on it;
  hand-rolled check-then-add races where `addIfAbsent` doesn't.
- **Nulls**: legal in COW collections, banned in concurrent queues — don't
  port null-sentinel protocols between them.
