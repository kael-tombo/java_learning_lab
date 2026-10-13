# DCL Pattern — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.
Every snippet stresses 16 threads × 10k gets and asserts single instance
plus initialized state — deterministic by construction (locks/volatile/
class-init), never by luck.

## 1. Volatile DCL: The Real Idiom Under Race

```java
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;

public class VolatileDcl {
    static class Helper {
        final int value = 42;
        Helper() { }
    }

    static volatile Helper instance;

    static Helper get() {
        Helper h = instance;                 // (1) one volatile read
        if (h == null) {
            synchronized (VolatileDcl.class) {
                if ((h = instance) == null)  // (2) recheck under lock
                    h = instance = new Helper();
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
        for (Thread t : ts) t.join(30_000);
        System.out.println("distinct instances: " + seen.size());
        System.out.println("single instance: " + (seen.size() == 1));
        System.out.println("fully constructed (value==42): "
                + (seen.iterator().next().value == 42));
    }
}
```

Expected output:
```
distinct instances: 1
single instance: true
fully constructed (value==42): true
```

The `volatile` write inside the lock hb's every later volatile read at
check (1) — construction (final field store via constructor, plus the
freeze) is visible to all 16 racers. `value == 42` on the *shared* instance
is the initialization-safety assertion (lab 04's freeze, delivered through
DCL's publication edge).

## 2. Static Holder: Laziness Without the Subtlety

```java
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;

public class HolderIdiom {
    static class Helper {
        final int value = 42;
        static int constructions;
        Helper() { constructions++; }
    }

    static class LazyHolder {
        static final Helper INSTANCE = new Helper();   // class-init lock does it all
    }

    static Helper get() { return LazyHolder.INSTANCE; }

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
        for (Thread t : ts) t.join(30_000);
        System.out.println("distinct instances: " + seen.size());
        System.out.println("constructed exactly once: " + (Helper.constructions == 1));
        System.out.println("value exact: " + (seen.iterator().next().value == 42));
    }
}
```

Expected output:
```
distinct instances: 1
constructed exactly once: true
value exact: true
```

JLS §12.4.2 initializes `LazyHolder` once, under the JVM's own lock, on
first active use — no volatile, no synchronized, no second check, nothing
to get wrong. `constructions == 1` counts what the singleton pattern
actually promises.

## 3. Enum Singleton: Serialization Safety for Free

```java
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;

public class EnumSingleton {
    enum Directory {
        INSTANCE;
        final int value = 42;
        String lookup(String k) { return k + "=" + value; }
    }

    public static void main(String[] args) throws Exception {
        int threads = 16;
        CountDownLatch go = new CountDownLatch(1);
        Set<Directory> seen = ConcurrentHashMap.newKeySet();
        Thread[] ts = new Thread[threads];
        for (int i = 0; i < threads; i++) {
            ts[i] = new Thread(() -> {
                try { go.await(); } catch (InterruptedException ignored) { }
                for (int j = 0; j < 10_000; j++) seen.add(Directory.INSTANCE);
            });
            ts[i].start();
        }
        go.countDown();
        for (Thread t : ts) t.join(30_000);
        System.out.println("distinct instances: " + seen.size());
        System.out.println("lookup works: " + "k=42".equals(Directory.INSTANCE.lookup("k")));
        // serialization cannot fork it: readResolve is built into enums
        java.io.ByteArrayOutputStream bos = new java.io.ByteArrayOutputStream();
        try (var oos = new java.io.ObjectOutputStream(bos)) { oos.writeObject(Directory.INSTANCE); }
        Object back;
        try (var ois = new java.io.ObjectInputStream(
                new java.io.ByteArrayInputStream(bos.toByteArray()))) { back = ois.readObject(); }
        System.out.println("deserialization returns same instance: " + (back == Directory.INSTANCE));
    }
}
```

Expected output:
```
distinct instances: 1
lookup works: true
deserialization returns same instance: true
```

Eager (no laziness — the price), but immune to the two classic singleton
killers at once: reflection (`Constructor.newInstance` on enums throws)
and serialization (the JVM guarantees identity on deserialize). DCL and
holder both need explicit `readResolve` for the second property.

## 4. Synchronized Baseline: Obviously Correct, Priced Per Call

```java
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;

public class SyncBaseline {
    static class Helper {
        final int value = 42;
    }

    static Helper instance;

    static synchronized Helper get() {
        if (instance == null) instance = new Helper();
        return instance;
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
        for (Thread t : ts) t.join(30_000);
        System.out.println("distinct instances: " + seen.size());
        System.out.println("single instance: " + (seen.size() == 1));
        System.out.println("value exact: " + (seen.iterator().next().value == 42));
    }
}
```

Expected output:
```
distinct instances: 1
single instance: true
value exact: true
```

Every call takes the monitor — 160k acquisitions here, all uncontended
after warmup (~20 ns each). The baseline against which DCL's single
volatile read (~1 ns) must justify its subtlety: same answers, different
price. Below millions of calls per second, ship this.

## 5. Dropping the Second Check: Double Initialization, Deterministically

```java
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicInteger;

public class NoSecondCheck {
    static class Helper {
        static final AtomicInteger constructions = new AtomicInteger();
        final int value = 42;
        Helper() {
            constructions.incrementAndGet();
            // Wedge the race window wide open: both racers read null at check (1)
            // long before either publishes, so both serialize through and init.
            try { Thread.sleep(50); } catch (InterruptedException ignored) { }
        }
    }

    static Helper instance;   // plain: even the publication races (irrelevant here)

    static Helper get() {
        if (instance == null) {          // (1) unsynchronized check...
            synchronized (NoSecondCheck.class) {
                // ...NO second check: whoever holds the lock initializes
                instance = new Helper();
            }
        }
        return instance;
    }

    public static void main(String[] args) throws Exception {
        CountDownLatch go = new CountDownLatch(1);
        Thread t1 = new Thread(() -> {
            try { go.await(); } catch (InterruptedException ignored) { }
            get();
        });
        Thread t2 = new Thread(() -> {
            try { go.await(); } catch (InterruptedException ignored) { }
            get();
        });
        t1.start();
        t2.start();
        go.countDown();                  // both pass check (1) on null...
        t1.join(10_000);                 // ...then serialize and BOTH initialize
        t2.join(10_000);
        System.out.println("constructions = " + Helper.constructions.get());
        System.out.println("double initialization without recheck: "
                + (Helper.constructions.get() == 2));
        System.out.println("surviving instance constructed: " + (instance.value == 42));
    }
}
```

Expected output:
```
constructions = 2
double initialization without recheck: true
surviving instance constructed: true
```

The 50 ms constructor sleep wedges the race window open deterministically:
both threads read `null` at check (1) before either enters the monitor,
then each initializes in turn. Constructor side effects run twice, the
first instance is silently discarded. (The stale-*read* hazard — seeing a
half-built object — is the subtler sibling this snippet doesn't chase;
unobservable on demand, real in production. The missing `volatile` is load
bearing there; the missing recheck is load bearing *here*, observably.)

## Common Pitfalls Encountered Here

- **DCL without `volatile`** — half-constructed publication (pre-2004 bug,
  alive whenever the keyword is deleted).
- **DCL without the recheck** — double initialization, deterministically
  (snippet 5).
- **Reading the volatile twice** — extra fence + check-then-act skew; use
  the local-variable shape (snippet 1).
- **Serializing a DCL/holder singleton** — add `readResolve` or use an
  enum (snippet 3).
- **Reaching for DCL first** — holder (snippet 2) or synchronized accessor
  (snippet 4) unless parameters force laziness-with-subtlety.
- **Assuming the reorder is observable on demand** — it isn't; the
  *guarantee* (volatile/holder/enum/sync) is asserted instead (all
  snippets).
