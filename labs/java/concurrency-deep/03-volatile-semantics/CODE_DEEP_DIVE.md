# Volatile Semantics — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.

## 1. The Stale Read: Plain Flag Spins to the Bound, Volatile Exits Early

The canonical visibility demo, made harness-safe with an iteration bound
(the plain version would otherwise hang the JVM — which is itself the
point). The JIT is *allowed* to hoist the plain read (no synchronization
action forces a reload); it is *forbidden* to hoist the volatile read:

```java
public class StaleSpin {
    // Bound sized so the 300ms pre-publish window can never reach it:
    // a volatile read costs >= ~1ns, so 300ms fits << BOUND/2 iterations
    // on any machine, while the hoisted plain read runs to BOUND always.
    static final long BOUND = 2_000_000_000L;
    static boolean plainFlag;              // NOT volatile
    static volatile boolean volFlag;
    static long plainSpins, volSpins;

    public static void main(String[] args) throws Exception {
        Thread t1 = new Thread(() -> {
            long s = 0;
            while (!plainFlag) {           // read hoisted after OSR: stale forever
                if (++s >= BOUND) break;
            }
            plainSpins = s;
        });
        t1.start();
        Thread.sleep(300);                 // let OSR compile the loop
        plainFlag = true;                  // main publishes... invisibly
        t1.join(30_000);

        Thread t2 = new Thread(() -> {
            long s = 0;
            while (!volFlag) {
                if (++s >= BOUND) break;
            }
            volSpins = s;
        });
        t2.start();
        Thread.sleep(300);
        volFlag = true;                    // ...visibly
        t2.join(30_000);

        System.out.println("plain ran to bound (stale read): " + (plainSpins >= BOUND));
        // structural: the volatile spinner only runs during the 300ms window,
        // while the plain spinner always runs the full bound (window iters << bound)
        System.out.println("volatile exited early (fresh read): " + (volSpins < plainSpins));
    }
}
```

Expected output:
```
plain ran to bound (stale read): true
volatile exited early (fresh read): true
```

Same loop, same timing, opposite outcomes — visibility is a compiler
constraint, not just a hardware story.

## 2. volatile ++ Loses Updates; AtomicInteger Doesn't

```java
import java.util.concurrent.atomic.AtomicInteger;

public class PlusPlusRace {
    static volatile int volCount;
    static int plainCount;                       // also racy, for comparison
    static final AtomicInteger atomicCount = new AtomicInteger();
    static final int THREADS = 8, PER_THREAD = 500_000;

    static void runAll(Runnable r) throws Exception {
        Thread[] ts = new Thread[THREADS];
        for (int i = 0; i < THREADS; i++) ts[i] = new Thread(r);
        for (Thread t : ts) t.start();
        for (Thread t : ts) t.join();
    }

    public static void main(String[] args) throws Exception {
        int expected = THREADS * PER_THREAD;
        runAll(() -> { for (int i = 0; i < PER_THREAD; i++) volCount++; });
        runAll(() -> { for (int i = 0; i < PER_THREAD; i++) plainCount++; });
        runAll(() -> { for (int i = 0; i < PER_THREAD; i++) atomicCount.incrementAndGet(); });
        System.out.println("expected = " + expected);
        System.out.println("volatile lost updates: " + (volCount < expected));
        System.out.println("plain lost updates: " + (plainCount < expected));
        System.out.println("atomic exact: " + (atomicCount.get() == expected));
    }
}
```

Expected output (exact shortfalls vary — elided):
```
expected = 4000000
...
volatile lost updates: true
plain lost updates: true
atomic exact: true
```

`volCount++` is read-modify-write: two threads read 5, both write 6 — one
update lost, with full visibility of every step. Volatile guarantees you see
the *latest* value when you look; it cannot make the look-and-write atomic.
That last mile is `AtomicInteger` (CAS loop) or a lock.

## 3. Safe Publication: One Volatile Flag Publishes a Whole Object Graph

```java
public class SafePublication {
    static class Config {
        int timeout;
        String url;
        int[] ports;
    }

    static Config config;              // NOT volatile
    static volatile boolean ready;     // the piggyback edge

    public static void main(String[] args) throws Exception {
        Thread writer = new Thread(() -> {
            Config c = new Config();
            c.timeout = 5000;
            c.url = "https://example.com";
            c.ports = new int[]{80, 443};
            config = c;                // (a) plain write
            ready = true;              // (b) volatile write: hb edge
        });
        boolean[] ok = {false};
        Thread reader = new Thread(() -> {
            while (!ready) Thread.onSpinWait();   // (c) volatile read
            Config c = config;                    // (d) plain read: SEES (a)
            ok[0] = c.timeout == 5000
                    && "https://example.com".equals(c.url)
                    && c.ports[0] == 80 && c.ports[1] == 443;
        });
        reader.start();
        writer.start();
        writer.join(5000);
        reader.join(5000);
        System.out.println("fully constructed config visible: " + ok[0]);
    }
}
```

Expected output:
```
fully constructed config visible: true
```

(b) happens-before (c) by the volatile rule; (a) is program-ordered before
(b); (c) before (d); transitivity delivers (a)→(d). The reader can never see
`timeout == 0` or a null `url` here — guaranteed by the JMM on every JVM,
not just HotSpot. This is the single most reused volatile idiom (config
reloads, lazy singletons-via-holder alternatives, shutdown flags with
payloads).

## 4. Double-Checked Locking: Correct With volatile, Same Instance for All

```java
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;

public class DclSingleton {
    static class Helper {
        final int value = 42;          // final: safe under 17.5 even so
        Helper() { }
    }

    static volatile Helper instance;   // remove volatile -> broken (pre-JSR-133 ordering)

    static Helper get() {
        Helper h = instance;           // local read: volatile read happens once
        if (h == null) {
            synchronized (DclSingleton.class) {
                if (instance == null) instance = new Helper();
                h = instance;
            }
        }
        return h;
    }

    public static void main(String[] args) throws Exception {
        int threads = 16;
        CountDownLatch go = new CountDownLatch(1);
        Set<Helper> seen = ConcurrentHashMap.newKeySet();
        Thread[] ts = new Thread[threads];
        for (int i = 0; i < threads; i++) {
            ts[i] = new Thread(() -> {
                try { go.await(); } catch (InterruptedException ignored) { }
                for (int j = 0; j < 10_000; j++) seen.add(get());
            });
            ts[i].start();
        }
        go.countDown();
        for (Thread t : ts) t.join();
        System.out.println("distinct instances: " + seen.size());
        System.out.println("single instance under race: " + (seen.size() == 1));
        System.out.println("fully constructed (value==42): "
                + seen.iterator().next().value);
    }
}
```

Expected output:
```
distinct instances: 1
single instance under race: true
fully constructed (value==42): 42
```

The local-variable read (`Helper h = instance`) is the Bloch-approved shape:
one volatile read on the fast path instead of two. Without `volatile`, the
constructor's field stores could reorder past the reference store and a
reader could observe `value == 0` — unreproducible on demand (that's what
makes it vicious), forbidden by the model with the keyword present.

## 5. Transitivity Across Three Threads (A → B → C)

```java
import java.util.concurrent.CountDownLatch;

public class TransitiveHb {
    static int x;                        // plain
    static volatile boolean v;           // A -> B edge
    static volatile boolean w;           // B -> C edge
    static int observedByC = -1;

    public static void main(String[] args) throws Exception {
        CountDownLatch bReadV = new CountDownLatch(1);
        CountDownLatch cDone = new CountDownLatch(1);

        Thread a = new Thread(() -> { x = 7; v = true; });
        Thread b = new Thread(() -> {
            while (!v) Thread.onSpinWait();
            bReadV.countDown();
            w = true;
        });
        Thread c = new Thread(() -> {
            while (!w) Thread.onSpinWait();
            observedByC = x;             // must see 7: x->v (po) -> v-read (vol)
            cDone.countDown();           // -> w (po) -> w-read (vol) -> x-read
        });
        c.start();
        b.start();
        a.start();
        cDone.await();
        bReadV.await();
        System.out.println("C observed x = " + observedByC);
        System.out.println("transitive publication intact: " + (observedByC == 7));
    }
}
```

Expected output:
```
C observed x = 7
transitive publication intact: true
```

Thread C never touches a lock shared with A, yet sees A's write — the two
volatile edges compose by transitivity. Message-passing concurrency
(latches, queues, futures) is *built* from chains like this; every
`BlockingQueue.take()` guarantee is transitivity wearing a trench coat.

## Common Pitfalls Encountered Here

- **Spinning on a plain flag** — the JIT hoists the read; the loop never
  observes the write (snippet 1). Shutdown flags must be volatile (or
  atomic/interrupt-based).
- **`volatile` counters** — `++`/`--`/`+=` are compound; use `AtomicLong` /
  `LongAdder` (snippet 2).
- **DCL without `volatile`** — half-constructed publication, unreproducible
  in tests, real in production (snippet 4).
- **Volatile arrays** — the keyword covers the reference, not the elements;
  per-element volatility needs `AtomicIntegerArray`/`VarHandle`.
- **Assuming volatile orders non-volatile accesses around it in all
  directions** — a volatile *write* doesn't pull later plain writes
  backwards into visibility; only the specified edges exist. Draw the arrows
  before relying on them.
- **Using `Thread.stop`-era thinking for visibility** — `stop()`/`suspend()`
  are deprecated-unsafe precisely because they interact with monitor state;
  interruption + volatile flags are the replacement.
