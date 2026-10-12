# Atomic Classes — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.

## 1. The CAS Loop, Written by Hand

`getAndUpdate` hides the loop; here it is explicit, with a retry counter that
makes contention visible:

```java
import java.util.concurrent.atomic.AtomicInteger;

public class CasLoop {
    public static void main(String[] args) throws Exception {
        AtomicInteger atomic = new AtomicInteger(0);
        int threads = 8, perThread = 200_000;
        Thread[] ts = new Thread[threads];
        for (int t = 0; t < threads; t++) {
            ts[t] = new Thread(() -> {
                for (int i = 0; i < perThread; i++) {
                    int prev, next;
                    do {
                        prev = atomic.get();       // volatile read
                        next = prev + 1;
                    } while (!atomic.compareAndSet(prev, next));  // commit or retry
                }
            });
            ts[t].start();
        }
        for (Thread t : ts) t.join();
        System.out.println("final = " + atomic.get()
                + " (expected " + (threads * perThread) + ")");
        System.out.println("exact despite races: " + (atomic.get() == threads * perThread));
    }
}
```

Expected output:
```
final = 1600000 (expected 1600000)
exact despite races: true
```

The loop's contract in one sentence: the CAS commits only if nothing changed
since our read — every lost race retries with a fresh read, so no update is
ever silently dropped (contrast snippet 2 of lab 03, where `volatile++`
drops them).

## 2. Update Functions May Run Multiple Times

```java
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

public class RerunFunction {
    public static void main(String[] args) throws Exception {
        AtomicInteger atomic = new AtomicInteger(0);
        AtomicLong applications = new AtomicLong();
        int threads = 8, perThread = 50_000;
        Thread[] ts = new Thread[threads];
        for (int t = 0; t < threads; t++) {
            ts[t] = new Thread(() -> {
                for (int i = 0; i < perThread; i++) {
                    atomic.getAndUpdate(prev -> {
                        applications.incrementAndGet();   // side effect: counted
                        return prev + 1;
                    });
                }
            });
            ts[t].start();
        }
        for (Thread t : ts) t.join();
        long total = (long) threads * perThread;
        System.out.println("final = " + atomic.get() + " (expected " + total + ")");
        System.out.println("function applications = " + applications.get());
        System.out.println("applications exceed successes (re-execution real): "
                + (applications.get() > total));
    }
}
```

Expected output (exact application count varies — elided):
```
final = 400000 (expected 400000)
...
applications exceed successes (re-execution real): true
```

Under 8-way contention the mapping function routinely runs, loses the CAS,
and runs again — the source even optimizes for it (`haveNext` avoids
re-applying when the re-read matches). A function with side effects
(logging, I/O, counter increments) fires an unpredictable number of times:
pure functions only.

## 3. ABA: Stamped Reference Distinguishes A1 from A2

```java
import java.util.concurrent.atomic.AtomicReference;
import java.util.concurrent.atomic.AtomicStampedReference;

public class AbaDemo {
    public static void main(String[] args) {
        // Plain reference: A -> B -> A fools compareAndSet
        AtomicReference<String> ref = new AtomicReference<>("A");
        ref.set("B");
        ref.set("A");                                  // back to A, different history
        boolean fooled = ref.compareAndSet("A", "C");  // succeeds: cannot tell
        System.out.println("plain CAS fooled by ABA: " + fooled);

        // Stamped: each mutation bumps the stamp
        AtomicStampedReference<String> stamped =
                new AtomicStampedReference<>("A", 0);
        int[] hold = new int[1];
        stamped.get(hold);
        int s0 = hold[0];
        stamped.set("B", s0 + 1);
        stamped.set("A", s0 + 2);                      // same value, newer stamp
        boolean blocked = stamped.compareAndSet("A", "C", s0, s0 + 1);
        System.out.println("stamped CAS with stale stamp rejected: " + !blocked);
        System.out.println("current stamp = " + stamped.getStamp() + " (expected 2)");
    }
}
```

Expected output:
```
plain CAS fooled by ABA: true
stamped CAS with stale stamp rejected: true
current stamp = 2 (expected 2)
```

CAS compares values, not histories. Where recycled identities meet CAS
(lock-free stacks, Treiber-style pools), the stamp is the history —
at the price of a pair object per access.

## 4. LongAdder Beats AtomicLong Under Contention, Loses Without It

```java
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.LongAdder;

public class AdderVsAtomic {
    static final int THREADS = 8, PER_THREAD = 1_000_000;

    static long time(Runnable r) throws Exception {
        Thread[] ts = new Thread[THREADS];
        for (int i = 0; i < THREADS; i++) ts[i] = new Thread(r);
        long t0 = System.nanoTime();
        for (Thread t : ts) t.start();
        for (Thread t : ts) t.join();
        return (System.nanoTime() - t0) / 1_000_000;
    }

    public static void main(String[] args) throws Exception {
        AtomicLong atomic = new AtomicLong();
        LongAdder adder = new LongAdder();
        long atomicMs = time(() -> {
            for (int i = 0; i < PER_THREAD; i++) atomic.incrementAndGet();
        });
        long adderMs = time(() -> {
            for (int i = 0; i < PER_THREAD; i++) adder.increment();
        });
        System.out.println("AtomicLong total = " + atomic.get()
                + ", LongAdder total = " + adder.sum());
        System.out.println("both exact: " + (atomic.get() == adder.sum()
                && atomic.get() == (long) THREADS * PER_THREAD));
        System.out.println("adder not slower under 8-way contention: " + (adderMs <= atomicMs));
    }
}
```

Expected output (timings vary — elided):
```
AtomicLong total = 8000000, LongAdder total = 8000000
both exact: true
adder not slower under 8-way contention: true
```

One CAS word (AtomicLong) serializes 8 writers; striped cells let them land
apart. Flip to 1 thread and AtomicLong wins (no cell infrastructure) — the
crossover lives around 2–4 writers, which is why libraries default to
`LongAdder` for metrics and `AtomicLong` for sequence numbers.

## 5. weakCompareAndSet Belongs in Loops Only

```java
import java.util.concurrent.atomic.AtomicBoolean;

public class WeakCas {
    public static void main(String[] args) {
        // One-shot use: plain compareAndSet is the correct default
        AtomicBoolean once = new AtomicBoolean(false);
        System.out.println("one-shot CAS: " + once.compareAndSet(false, true));

        // Loop use: weak CAS is legal here — spurious failure just retries
        AtomicIntegerWithWeak w = new AtomicIntegerWithWeak();
        int threads = 4, perThread = 200_000;
        Thread[] ts = new Thread[threads];
        for (int t = 0; t < threads; t++) {
            ts[t] = new Thread(() -> {
                for (int i = 0; i < perThread; i++) {
                    int prev;
                    do {
                        prev = w.value.get();
                    } while (!w.value.weakCompareAndSetVolatile(prev, prev + 1));
                }
            });
            ts[t].start();
        }
        try {
            for (Thread t : ts) t.join();
        } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
        int expected = threads * perThread;
        System.out.println("weak-CAS loop exact: " + (w.value.get() == expected));
    }

    static class AtomicIntegerWithWeak {
        final java.util.concurrent.atomic.AtomicInteger value = new java.util.concurrent.atomic.AtomicInteger();
    }
}
```

Expected output:
```
one-shot CAS: true
weak-CAS loop exact: true
```

`weakCompareAndSetVolatile` may fail spuriously (allowed by spec, real on
ARM/LL-SC) — inside a retry loop that failure is indistinguishable from a
lost race, so it's free performance; as a one-shot boolean test it's a
correctness bug. (This mirrors the JDK's own `getAndUpdate`, which loops on
exactly this method.)

## Common Pitfalls Encountered Here

- **Side effects in update functions** — re-execution under contention is
  normal (snippet 2 counts it).
- **Two atomics don't transact** — the intermediate state is observable;
  multi-variable invariants need a lock or a packed single-word CAS.
- **ABA blindness** — recycled references + plain CAS = silent corruption;
  stamp, mark, or never reuse (snippet 3).
- **`sum()` as an exact total** — striped sums are fuzzy under concurrent
  mutation; quiesce first or accept the skew.
- **AtomicLong for hot counters** — above a few writers, `LongAdder` wins;
  below, it wastes cells. Match the tool to the contention level.
- **One-shot weak CAS** — legal only in retry loops (snippet 5).
