# Synchronized Internals — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.

## 1. monitorenter/monitorexit in the Bytecode

The compiler — not the programmer — pairs acquisition with release on every
path. This snippet's driver compiles a probe class and inspects it with
`javap`:

```java
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class MonitorBytecode {
    static final String PROBE = """
            public class Probe {
                private final Object lock = new Object();
                int counter;
                public void inc(boolean boom) {
                    synchronized (lock) {
                        counter++;
                        if (boom) throw new RuntimeException("boom");
                    }
                }
            }
            """;

    public static void main(String[] args) throws Exception {
        Path dir = Files.createTempDirectory("mon");
        Path src = dir.resolve("Probe.java");
        Files.writeString(src, PROBE);
        Process javac = new ProcessBuilder("javac", src.toString())
                .redirectErrorStream(true).start();
        String javacOut = new String(javac.getInputStream().readAllBytes());
        System.out.println("probe compiles: " + (javac.waitFor() == 0) + javacOut);

        Process javap = new ProcessBuilder("javap", "-c", "-p",
                dir.resolve("Probe.class").toString())
                .redirectErrorStream(true).start();
        String out = new String(javap.getInputStream().readAllBytes());
        javap.waitFor();

        long enters = out.lines().filter(l -> l.contains("monitorenter")).count();
        long exits = out.lines().filter(l -> l.contains("monitorexit")).count();
        boolean hasExTable = out.contains("Exception table:");
        System.out.println("monitorenter count = " + enters);
        System.out.println("monitorexit count = " + exits);
        System.out.println("has exception table = " + hasExTable);
        System.out.println("one enter, two exits (normal + exceptional): "
                + (enters == 1 && exits == 2 && hasExTable));
    }
}
```

Expected output:
```
probe compiles: true
monitorenter count = 1
monitorexit count = 2
has exception table = true
one enter, two exits (normal + exceptional): true
```

One entry, two releases: the exception table routes the `boom` path through
the second `monitorexit`. "Synchronized always releases" is a compiler
theorem, not a coding convention.

## 2. The Biased-Locking Flag Is Gone

```java
public class NoBiasedLocking {
    public static void main(String[] args) throws Exception {
        Process p = new ProcessBuilder(
                ProcessHandle.current().info().command().orElse("java"),
                "-XX:+UseBiasedLocking", "-version")
                .redirectErrorStream(true).start();
        String out = new String(p.getInputStream().readAllBytes());
        p.waitFor();
        System.out.println("JVM says: " + out.lines()
                .filter(l -> l.contains("UseBiasedLocking")).findFirst().orElse("(no mention)"));
        System.out.println("flag unrecognized (removed, not just off): "
                + out.contains("Unrecognized VM option"));
    }
}
```

Expected output:
```
JVM says: Unrecognized VM option 'UseBiasedLocking'
flag unrecognized (removed, not just off): true
```

Timeline in one line: default-on through 14, disabled + deprecated in 15
(JEP 374), removed in 18 (JDK-8256425) — and on JDK 23 the flag isn't even
parsed. Any tuning guide that mentions it is describing a JVM that no longer
exists.

## 3. wait/notify Demands Ownership + while-Loop Discipline

```java
public class WaitProtocol {
    public static void main(String[] args) throws Exception {
        Object cond = new Object();

        // 1. wait() without the monitor -> IllegalMonitorStateException
        try {
            cond.wait(10);
        } catch (IllegalMonitorStateException e) {
            System.out.println("unowned wait rejected: IllegalMonitorStateException");
        }

        // 2. correct protocol: while-loop + notifyAll, same monitor both sides
        boolean[] ready = {false};
        Thread waiter = new Thread(() -> {
            synchronized (cond) {
                while (!ready[0]) {
                    try {
                        cond.wait();
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        return;
                    }
                }
                System.out.println("waiter proceeded after condition true");
            }
        });
        waiter.start();
        Thread.sleep(100);   // let waiter reach wait()
        synchronized (cond) {
            ready[0] = true;
            cond.notifyAll();
        }
        waiter.join(3000);
        System.out.println("waiter terminated: " + !waiter.isAlive());
    }
}
```

Expected output:
```
unowned wait rejected: IllegalMonitorStateException
waiter proceeded after condition true
waiter terminated: true
```

The ownership check is dynamic — the JVM verifies monitor holdership at the
call. The `while` loop (not `if`) is what makes spurious wakeups and stolen
signals harmless: re-check before proceeding, always.

## 4. Different Monitors Don't Exclude Each Other

```java
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicInteger;

public class WrongMonitor {
    static final int N = 200_000;

    public static void main(String[] args) throws Exception {
        // Warmup: stabilize JIT so both cases measure steady-state code
        Overlap warm = new Overlap();
        warm.instanceWork();
        Overlap.staticWork();

        // Case A: instance method (this) vs static method (Class object) overlap freely
        Overlap o = new Overlap();
        CountDownLatch go = new CountDownLatch(1);
        Thread inst = new Thread(() -> {
            try { go.await(); } catch (InterruptedException ignored) { }
            o.instanceWork();
        });
        Thread stat = new Thread(() -> {
            try { go.await(); } catch (InterruptedException ignored) { }
            Overlap.staticWork();
        });
        long t0 = System.nanoTime();
        inst.start();
        stat.start();
        go.countDown();
        inst.join();
        stat.join();
        long overlappedMs = (System.nanoTime() - t0) / 1_000_000;
        System.out.println("instance+static overlapped ms = " + overlappedMs);

        // Case B: two threads, same instance monitor -> serialized
        Overlap o2 = new Overlap();
        CountDownLatch go2 = new CountDownLatch(1);
        Thread t1 = new Thread(() -> {
            try { go2.await(); } catch (InterruptedException ignored) { }
            o2.instanceWork();
        });
        Thread t2 = new Thread(() -> {
            try { go2.await(); } catch (InterruptedException ignored) { }
            o2.instanceWork();
        });
        t0 = System.nanoTime();
        t1.start();
        t2.start();
        go2.countDown();
        t1.join();
        t2.join();
        long serializedMs = (System.nanoTime() - t0) / 1_000_000;
        System.out.println("same-monitor serialized ms = " + serializedMs);
        System.out.println("same monitor takes ~2x overlapped: "
                + (serializedMs > overlappedMs * 1.5));
    }

    static class Overlap {
        static void burn() {
            long x = 0;
            for (int i = 0; i < 150_000_000; i++) x += i;
            if (x == -1) System.out.print("");
        }
        synchronized void instanceWork() { burn(); }
        static synchronized void staticWork() { burn(); }
    }
}
```

Expected output (timings vary — last line is the assertion):
```
...
same monitor takes ~2x overlapped: true
```

`synchronized` instance method locks `this`; `static synchronized` locks the
`Class` object — disjoint monitors, full overlap. Two instance calls on the
same object serialize (~2×). Every "synchronized isn't working" bug is this
drawing done wrong.

## 5. Uncontended synchronized Costs Nanoseconds

```java
public class UncontendedCost {
    final Object lock = new Object();
    int counter;

    void inc() { synchronized (lock) { counter++; } }

    public static void main(String[] args) {
        UncontendedCost u = new UncontendedCost();
        for (int i = 0; i < 5_000_000; i++) u.inc();      // warmup (JIT, inflation settles)
        long t0 = System.nanoTime();
        int n = 10_000_000;
        for (int i = 0; i < n; i++) u.inc();
        long ns = (System.nanoTime() - t0) / n;
        System.out.println("ns per uncontended synchronized inc = " + ns);
        System.out.println("counter exact: " + (u.counter == n + 5_000_000));
        System.out.println("uncontended lock is nanoseconds, not microseconds: " + (ns < 1000));
    }
}
```

Expected output (first line varies — elided; rest asserted):
```
...
counter exact: true
uncontended lock is nanoseconds, not microseconds: true
```

Single-threaded acquisition stays on the stack-locking fast path (a CAS on
the mark word, no park, no OS call) — tens of nanoseconds after warmup. The
microsecond horror stories are all *contended* acquisitions paying for park
+ OS wakeup. Same keyword, two cost universes.

## Common Pitfalls Encountered Here

- **Assuming biased locking still exists** — tuning flags from pre-18 guides
  are unrecognized options now; uncontended cost is stack-locking, full stop.
- **`if (cond) wait()`** — spurious wakeups and stolen signals demand
  `while`.
- **`notify()` with multiple conditions** — one arbitrary waiter wakes; if it
  can't proceed and no one else is notified, the signal is lost. Default to
  `notifyAll()`.
- **Locking different monitors around shared state** — static vs instance,
  `this` vs private lock object: no shared monitor, no happens-before edge.
- **Holding a monitor during I/O or `sleep`** — turns a nanosecond mechanism
  into a seconds-long BLOCKED queue for everyone else; waiters can't even be
  interrupted out of entry.
- **Calling alien methods under a lock** — overridable methods/callbacks can
  re-enter (reentrancy allows it) and observe half-built invariants the lock
  was supposed to protect.
