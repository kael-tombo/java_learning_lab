# JMM Foundations — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.
Every snippet asserts a *guaranteed* outcome (JMM edges), never a race —
races are the thing being avoided, not demonstrated.

## 1. Start Edge: Writes Before start() Are Visible

```java
public class StartEdge {
    static class Data {
        int[] values = new int[1000];
        long checksum;
    }

    public static void main(String[] args) throws Exception {
        Data d = new Data();
        long expect = 0;
        for (int i = 0; i < d.values.length; i++) {
            d.values[i] = i * 3 + 1;
            expect += d.values[i];
        }
        long[] seen = {0};
        Thread t = new Thread(() -> {   // start() hb everything below
            long s = 0;
            for (int v : d.values) s += v;
            d.checksum = s;
            seen[0] = s;
        });
        t.start();
        t.join();
        System.out.println("expected checksum = " + expect);
        System.out.println("thread observed = " + seen[0]);
        System.out.println("start edge delivers all writes: " + (seen[0] == expect));
    }
}
```

Expected output:
```
expected checksum = 1499500
thread observed = 1499500
start edge delivers all writes: true
```

JLS: `t.start()` happens-before the thread's first action — the 1000
element writes (program-ordered before `start`) are transitively visible.
No `volatile`, no lock, no luck: the edge is structural.

## 2. Join Edge: Worker's Writes Are Visible After join()

```java
public class JoinEdge {
    public static void main(String[] args) throws Exception {
        int[] result = new int[500];
        Thread worker = new Thread(() -> {
            for (int i = 0; i < result.length; i++) result[i] = i * i;
        });
        worker.start();
        worker.join();   // worker's last action hb join()'s return
        long sum = 0;
        for (int v : result) sum += v;
        long expect = 0;
        for (int i = 0; i < 500; i++) expect += (long) i * i;
        System.out.println("sum = " + sum + " (expected " + expect + ")");
        System.out.println("join edge delivers worker writes: " + (sum == expect));
    }
}
```

Expected output:
```
sum = 41541750 (expected 41541750)
join edge delivers worker writes: true
```

The mirror image of snippet 1: the worker's last action hb's the `join()`
return, so everything it wrote is visible after. `join()` is a
synchronization action in both directions (joiner→joinee via start,
joinee→joiner via join) — the two edges compose a full round trip.

## 3. Monitor Edge: Lock-Protected Counter Is Exact

```java
public class LockEdge {
    static final Object LOCK = new Object();
    static long count;

    public static void main(String[] args) throws Exception {
        int threads = 8, perThread = 250_000;
        Thread[] ts = new Thread[threads];
        for (int t = 0; t < threads; t++) {
            ts[t] = new Thread(() -> {
                for (int i = 0; i < perThread; i++) {
                    synchronized (LOCK) { count++; }   // unlock hb next lock
                }
            });
            ts[t].start();
        }
        for (Thread t : ts) t.join();
        long expect = (long) threads * perThread;
        System.out.println("count = " + count + " (expected " + expect + ")");
        System.out.println("monitor edge: no lost updates: " + (count == expect));
    }
}
```

Expected output:
```
count = 2000000 (expected 2000000)
monitor edge: no lost updates: true
```

Each unlock hb's the next lock of `LOCK`, chaining all 2M increments into
one total order — mutual exclusion plus visibility in a single mechanism.
(Contrast the `volatile++` race in concurrency-deep/03: same threads, no
edge, millions lost.)

## 4. Library Edge: Latch Publication

```java
import java.util.concurrent.CountDownLatch;

public class LatchEdge {
    static class Config {
        String url;
        int timeout;
        int[] ports;
    }

    public static void main(String[] args) throws Exception {
        Config cfg = new Config();
        CountDownLatch ready = new CountDownLatch(1);
        boolean[] ok = {false};
        Thread writer = new Thread(() -> {
            cfg.url = "https://example.com";
            cfg.timeout = 5000;
            cfg.ports = new int[]{80, 443};
            ready.countDown();   // hb the await() return below (j.u.c. rule)
        });
        Thread reader = new Thread(() -> {
            try {
                ready.await();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return;
            }
            ok[0] = "https://example.com".equals(cfg.url)
                    && cfg.timeout == 5000
                    && cfg.ports[0] == 80 && cfg.ports[1] == 443;
        });
        reader.start();
        writer.start();
        writer.join();
        reader.join();
        System.out.println("latch-published graph fully visible: " + ok[0]);
    }
}
```

Expected output:
```
latch-published graph fully visible: true
```

`countDown()` hb's the return from `await()` — the concurrent package
extends happens-before across threads without locks or volatiles in user
code. Every queue handoff, future completion, and barrier trip carries an
equivalent documented edge; `CountDownLatch` is the minimal exhibit.

## 5. Causality Floor: Values Always Come From Somewhere

```java
import java.util.concurrent.atomic.AtomicInteger;

public class CausalityFloor {
    public static void main(String[] args) throws Exception {
        // Racy publication: the reader may see stale ORDER, but never invented VALUES.
        // writer writes x=1 then x=2 (plain); reader samples twice into a set.
        int[] box = {0};
        java.util.Set<Integer> seen = java.util.Collections.synchronizedSet(
                new java.util.HashSet<>());
        AtomicInteger weird = new AtomicInteger(0);
        Thread writer = new Thread(() -> {
            for (int i = 1; i <= 100_000; i++) box[0] = i;
        });
        Thread reader = new Thread(() -> {
            for (int i = 0; i < 100_000; i++) {
                int v = box[0];
                if (v < 0 || v > 100_000) weird.incrementAndGet();
                seen.add(v);
            }
        });
        writer.start();
        reader.start();
        writer.join();
        reader.join();
        boolean inRange = seen.stream().allMatch(v -> v >= 0 && v <= 100_000);
        System.out.println("distinct values observed: " + seen.size());
        System.out.println("out-of-thin-air values: " + weird.get());
        System.out.println("every value in [0, 100000] (causality floor): "
                + (inRange && weird.get() == 0));
    }
}
```

Expected output (distinct count varies — elided):
```
...
out-of-thin-air values: 0
every value in [0, 100000] (causality floor): true
```

The reader runs fully racy (no edge at all) — it may see stale values,
repeats, and skips in any order. But every observed value was *written by
someone*: 0 (initial) through 100000, never −1, never 10⁹. Causality
(JLS §17.4.8) forbids invention while permitting every reordering — the
floor below which the JMM never sinks, even for racy code.

## Common Pitfalls Encountered Here

- **Assuming visibility without an edge** — plain-flag spins, half-built
  objects: no hb, no guarantee (snippets 1–4 show the four cheapest edges
  that fix each case).
- **Confusing race-freedom with determinism** — DRF buys sequential
  *consistency* (some interleaving explains it), not a *particular*
  interleaving.
- **Treating causality as ordering** — racy reads still scramble;
  causality only bans invented values (snippet 5).
- **Forgetting library edges** — latches/queues/futures carry hb; hand-rolled
  flag protocols reinvent them badly (snippet 4).
- **Locking for visibility but mutating outside** — the edge covers what
  happens *inside* the critical sections; touching the guarded state
  unlocked re-opens the race (snippet 3's `count++` must stay inside).
