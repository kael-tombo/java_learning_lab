# ConcurrentHashMap — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies. Single-file
programs: `java SnippetName.java`.

## 1. The Null Ban

```java
import java.util.concurrent.ConcurrentHashMap;

public class NullBan {
    public static void main(String[] args) {
        ConcurrentHashMap<String, Integer> m = new ConcurrentHashMap<>();
        try {
            m.put(null, 1);
        } catch (NullPointerException e) {
            System.out.println("null key rejected: " + e.getMessage());
        }
        try {
            m.put("k", null);
        } catch (NullPointerException e) {
            System.out.println("null value rejected: " + e.getMessage());
        }
        System.out.println("get absent = " + m.get("missing"));   // unambiguous
    }
}
```

Expected output:
```
null key rejected: null
null value rejected: null
get absent = null
```

Both puts throw before touching the table — the checks are the first lines of
`putVal`. The trailing `get` shows why: with nulls banned, one probe answers
"absent" definitively.

## 2. get() Is Lock-Free While the Bucket Monitor Is Held

CHM writers do `synchronized (f)` on the **first node of the bucket** (JDK source,
`putVal`). This snippet grabs that node with reflection and holds it, then races a
reader and a writer against it:

```java
import java.lang.reflect.Field;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;

public class LockFreeRead {
    public static void main(String[] args) throws Exception {
        ConcurrentHashMap<Integer, String> m = new ConcurrentHashMap<>();
        m.put(0, "A0");

        // spread(0)=0 -> bucket 0; spread(16)=16 -> also bucket 0 at capacity 16
        Field tf = ConcurrentHashMap.class.getDeclaredField("table");
        tf.setAccessible(true);
        Object[] table = (Object[]) tf.get(m);
        Object bucketHead = table[0];

        AtomicBoolean readerDone = new AtomicBoolean();
        AtomicBoolean writerDone = new AtomicBoolean();
        AtomicReference<String> readVal = new AtomicReference<>();
        Thread reader = new Thread(() -> {
            readVal.set(m.get(0));      // reads take no monitor
            readerDone.set(true);
        });
        Thread writer = new Thread(() -> {
            m.put(16, "B16");           // same bucket -> needs synchronized(head)
            writerDone.set(true);
        });

        synchronized (bucketHead) {
            reader.start();
            writer.start();
            reader.join(1000);
            writer.join(1000);
            System.out.println("bucket head class: " + bucketHead.getClass().getSimpleName());
            System.out.println("reader done while bucket locked: " + readerDone.get()
                    + " -> " + readVal.get());
            System.out.println("writer done while bucket locked: " + writerDone.get());
        }
        writer.join(1000);
        System.out.println("writer done after release: " + writerDone.get());
    }
}
```

Run: `java --add-opens java.base/java.util=ALL-UNNAMED --add-opens java.base/java.util.concurrent=ALL-UNNAMED LockFreeRead.java`

Expected output:
```
bucket head class: Node
reader done while bucket locked: true -> A0
writer done while bucket locked: false
writer done after release: true
```

The asymmetry is the design: `get` never touches a monitor, `put` to that bucket
must wait for it — bucket monitors serialize writers only.

## 3. Weakly Consistent Iteration Under Concurrent Writes

```java
import java.util.concurrent.ConcurrentHashMap;

public class WeakIterate {
    public static void main(String[] args) throws Exception {
        ConcurrentHashMap<Integer, Integer> m = new ConcurrentHashMap<>();
        for (int i = 0; i < 1000; i++) m.put(i, i);

        Thread writer = new Thread(() -> {
            for (int i = 1000; i < 3000; i++) m.put(i, i);
        });
        writer.start();

        int seen = 0;
        boolean cme = false;
        try {
            // NEVER throws ConcurrentModificationException, never blocks
            for (Integer k : m.keySet()) seen++;
        } catch (java.util.ConcurrentModificationException e) {
            cme = true;
        }
        writer.join();
        System.out.println("CME thrown: " + cme);
        System.out.println("saw at least the original 1000: " + (seen >= 1000));
        System.out.println("final size = " + m.size());
    }
}
```

Expected output:
```
CME thrown: false
saw at least the original 1000: true
final size = 3000
```

The raw count inside the loop varies run to run (2048 in one run on JDK 23) —
that *is* the contract: weakly consistent, no CME, reflects whatever prefix of
concurrent work the iterator happened to observe.

## 4. Approximate size() Under Contention

```java
import java.util.concurrent.ConcurrentHashMap;

public class ApproxSize {
    public static void main(String[] args) throws Exception {
        ConcurrentHashMap<Integer, Integer> m = new ConcurrentHashMap<>();
        Thread[] ts = new Thread[8];
        for (int t = 0; t < 8; t++) {
            ts[t] = new Thread(() -> {
                for (int i = 0; i < 100_000; i++) m.put(i, i);
            });
            ts[t].start();
        }
        for (Thread t : ts) t.join();
        System.out.println("size after all writers done = " + m.size());
    }
}
```

Every thread writes the same 100_000 keys, so the settled value is exact — but
only *after* joins. Read `size()` mid-flight and the CounterCell sums can lag;
the JDK documents it as an estimate for exactly this reason.

Expected output:
```
size after all writers done = 100000
```

## 5. putIfAbsent / compute: The Atomic Primitives

```java
import java.util.concurrent.ConcurrentHashMap;

public class AtomicOps {
    public static void main(String[] args) {
        ConcurrentHashMap<String, Integer> m = new ConcurrentHashMap<>();
        m.putIfAbsent("votes", 0);
        System.out.println("first  = " + m.putIfAbsent("votes", 1));  // 0 (existing)
        m.computeIfAbsent("hits", k -> 0);
        m.compute("hits", (k, v) -> v + 1);
        System.out.println("hits   = " + m.get("hits"));
        m.merge("hits", 5, Integer::sum);
        System.out.println("merged = " + m.get("hits"));
    }
}
```

Expected output:
```
first  = 0
hits   = 1
merged = 6
```

Each lambda runs **while holding the bucket lock**, and re-entrancy into the same
map inside the lambda is permitted (the lock is a monitor) — but blocking work
inside `compute` stalls every other writer to that bucket.

## Common Pitfalls Encountered Here

- **Never call `size()` for logic** (rate limiting, quota): it is a racing
  snapshot. Track your own counter or use `LongAdder` outside the map.
- **Blocking inside `compute`/`merge`** freezes one bucket for all threads —
  the callback must be short and must not block.
- **Iterators don't CME** — that silence is not "safe to modify", it means "you
  may be seeing a stale view".
- **`concurrencyLevel` is ignored** since Java 8; passing a big value costs
  nothing but does nothing. Size by `initialCapacity` instead.
- **`get` returning null needs `containsKey` only if nulls were possible** —
  they aren't, so a single `get` is a complete presence test.
