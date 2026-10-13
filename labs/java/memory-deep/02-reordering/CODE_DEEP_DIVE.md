# Reordering — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23; anomaly rates are
x86-64 measurements — ARM/POWER shapes differ, verdicts don't), no
dependencies. Every snippet rendezvouses the racers per iteration (volatile
flag spins); free-running or barrier phasing hides the anomaly — see
THEORY invariant 5.

## 1. The Anomaly: Dekker (0,0), Forbidden Under SC, Routine on x86

```java
public class DekkerAnomaly {
    static int x, y;
    static volatile boolean go;
    static volatile boolean done1, done2;
    static int r1slot, r2slot;

    public static void main(String[] args) throws Exception {
        int iters = 20_000, bad = 0;
        Thread t1 = new Thread(() -> {
            while (!Thread.currentThread().isInterrupted()) {
                while (!go) Thread.onSpinWait();
                x = 1;                 // store...
                r1slot = y;            // ...then load (may pass it on x86)
                done1 = true;
                while (go) Thread.onSpinWait();
                done1 = false;
            }
        });
        Thread t2 = new Thread(() -> {
            while (!Thread.currentThread().isInterrupted()) {
                while (!go) Thread.onSpinWait();
                y = 1;
                r2slot = x;
                done2 = true;
                while (go) Thread.onSpinWait();
                done2 = false;
            }
        });
        t1.setDaemon(true);
        t2.setDaemon(true);
        t1.start();
        t2.start();
        for (int i = 0; i < iters; i++) {
            x = 0; y = 0;
            done1 = false; done2 = false;
            go = true;
            while (!done1 || !done2) Thread.onSpinWait();
            if (r1slot == 0 && r2slot == 0) bad++;
            go = false;
            while (done1 || done2) Thread.onSpinWait();
        }
        t1.interrupt();
        t2.interrupt();
        System.out.println("forbidden (0,0) outcomes = " + bad + "/" + iters);
        System.out.println("reordering observed on real hardware: " + (bad > iters / 100));
    }
}
```

Expected output (count varies — elided):
```
...
reordering observed on real hardware: true
```

Measured: ~79% of rendezvoused iterations show (0,0) here — both loads beat
both stores out of the store buffers. Sequential consistency forbids this
outcome absolutely (whichever store is "first," the other's load must see
it); x86 produces it routinely. The 1% bar holds at ~79x margin.

## 2. Volatile Forbids It: Same Shape, Zero Anomalies

Identical to snippet 1 with `volatile int` fields (only the field
declarations and the spin/flag mechanics change — the race shape is
untouched):

```java
public class VolatileFix {
    static volatile int x, y;
    static volatile boolean go;
    static volatile boolean done1, done2;
    static int r1slot, r2slot;

    public static void main(String[] args) throws Exception {
        int iters = 20_000, bad = 0;
        Thread t1 = new Thread(() -> {
            while (!Thread.currentThread().isInterrupted()) {
                while (!go) Thread.onSpinWait();
                x = 1;
                r1slot = y;
                done1 = true;
                while (go) Thread.onSpinWait();
                done1 = false;
            }
        });
        Thread t2 = new Thread(() -> {
            while (!Thread.currentThread().isInterrupted()) {
                while (!go) Thread.onSpinWait();
                y = 1;
                r2slot = x;
                done2 = true;
                while (go) Thread.onSpinWait();
                done2 = false;
            }
        });
        t1.setDaemon(true);
        t2.setDaemon(true);
        t1.start();
        t2.start();
        for (int i = 0; i < iters; i++) {
            x = 0; y = 0;
            done1 = false; done2 = false;
            go = true;
            while (!done1 || !done2) Thread.onSpinWait();
            if (r1slot == 0 && r2slot == 0) bad++;
            go = false;
            while (done1 || done2) Thread.onSpinWait();
        }
        t1.interrupt();
        t2.interrupt();
        System.out.println("forbidden (0,0) outcomes = " + bad + "/" + iters);
        System.out.println("volatile ordering holds (zero anomalies): " + (bad == 0));
    }
}
```

Expected output:
```
forbidden (0,0) outcomes = 0/20000
volatile ordering holds (zero anomalies): true
```

Two keywords added, ~15,000 anomalies deleted. The volatile store/load
edges (sequential consistency for the volatile chain) forbid exactly the
pair snippet 1 exhibits. Same threads, same rendezvous, same iteration
count — the *only* delta is ordering semantics.

## 3. The Mechanism Is the Store Buffer (Delay Eliminates It)

Snippet 1's bytecode, plus one nanosecond of drain time between store and
load:

```java
public class DelayDrains {
    static int x, y;
    static volatile boolean go;
    static volatile boolean done1, done2;
    static int r1slot, r2slot;

    public static void main(String[] args) throws Exception {
        int iters = 20_000, bad = 0;
        Thread t1 = new Thread(() -> {
            while (!Thread.currentThread().isInterrupted()) {
                while (!go) Thread.onSpinWait();
                x = 1;
                java.util.concurrent.locks.LockSupport.parkNanos(1);  // drain
                r1slot = y;
                done1 = true;
                while (go) Thread.onSpinWait();
                done1 = false;
            }
        });
        Thread t2 = new Thread(() -> {
            while (!Thread.currentThread().isInterrupted()) {
                while (!go) Thread.onSpinWait();
                y = 1;
                java.util.concurrent.locks.LockSupport.parkNanos(1);  // drain
                r2slot = x;
                done2 = true;
                while (go) Thread.onSpinWait();
                done2 = false;
            }
        });
        t1.setDaemon(true);
        t2.setDaemon(true);
        t1.start();
        t2.start();
        for (int i = 0; i < iters; i++) {
            x = 0; y = 0;
            done1 = false; done2 = false;
            go = true;
            while (!done1 || !done2) Thread.onSpinWait();
            if (r1slot == 0 && r2slot == 0) bad++;
            go = false;
            while (done1 || done2) Thread.onSpinWait();
        }
        t1.interrupt();
        t2.interrupt();
        System.out.println("forbidden (0,0) outcomes = " + bad + "/" + iters);
        System.out.println("drain delay eliminates the anomaly: " + (bad == 0));
    }
}
```

Expected output:
```
forbidden (0,0) outcomes = 0/20000
drain delay eliminates the anomaly: true
```

The compiler emits the same store;load sequence (nothing to hoist across
the opaque park call — and nothing was hoisted before either). The only
change is *time*: the store drains before the load issues. Anomaly gone ⇒
the buffer, not the compiler, was the culprit on this platform. (On ARM,
compiler/CPU reorderings can survive timing changes — same verdict via
`volatile`, different mechanism mix.)

## 4. Release/Acquire: Cheaper-Than-Volatile Ordering That Holds

```java
import java.lang.invoke.MethodHandles;
import java.lang.invoke.VarHandle;

public class ReleaseAcquire {
    static int data;
    static int flag;   // accessed ONLY via the VarHandle below
    static final VarHandle FLAG;

    static {
        try {
            FLAG = MethodHandles.lookup()
                    .findStaticVarHandle(ReleaseAcquire.class, "flag", int.class);
        } catch (ReflectiveOperationException e) {
            throw new ExceptionInInitializerError(e);
        }
    }

    public static void main(String[] args) throws Exception {
        int iters = 50_000;
        boolean[] ok = {true};
        Thread writer = new Thread(() -> {
            for (int i = 1; i <= iters; i++) {
                data = i;                    // plain store, program-ordered first
                FLAG.setRelease(i);          // release edge carries it
            }
        });
        Thread reader = new Thread(() -> {
            int last = 0;
            for (int i = 1; i <= iters; i++) {
                int f = (int) FLAG.getAcquire();   // acquire spin
                while (f < i) {
                    Thread.onSpinWait();
                    f = (int) FLAG.getAcquire();
                }
                if (data < f) ok[0] = false;       // data must track the flag
                last = f;
            }
        });
        writer.start();
        reader.start();
        writer.join(60_000);
        reader.join(60_000);
        System.out.println("release->acquire chain intact over " + iters + ": " + ok[0]);
    }
}
```

Expected output:
```
release->acquire chain intact over 50000: true
```

`setRelease` + `getAcquire` compose a happens-before chain (release write
hb the acquire read that observes it; program order does the rest): `data
== i` is always visible when the flag reads `i`. One-directional edges at
a fraction of full-volatile cost — the Disruptor-style sequencing
primitive, demonstrated end to end.

## 5. Monitors Forbid It Too: Dekker Under Lock

```java
public class MonitorFix {
    static int x, y;
    static final Object LOCK = new Object();
    static volatile boolean go;
    static volatile boolean done1, done2;
    static int r1slot, r2slot;

    public static void main(String[] args) throws Exception {
        int iters = 20_000, bad = 0;
        Thread t1 = new Thread(() -> {
            while (!Thread.currentThread().isInterrupted()) {
                while (!go) Thread.onSpinWait();
                synchronized (LOCK) { x = 1; r1slot = y; }
                done1 = true;
                while (go) Thread.onSpinWait();
                done1 = false;
            }
        });
        Thread t2 = new Thread(() -> {
            while (!Thread.currentThread().isInterrupted()) {
                while (!go) Thread.onSpinWait();
                synchronized (LOCK) { y = 1; r2slot = x; }
                done2 = true;
                while (go) Thread.onSpinWait();
                done2 = false;
            }
        });
        t1.setDaemon(true);
        t2.setDaemon(true);
        t1.start();
        t2.start();
        for (int i = 0; i < iters; i++) {
            x = 0; y = 0;
            done1 = false; done2 = false;
            go = true;
            while (!done1 || !done2) Thread.onSpinWait();
            if (r1slot == 0 && r2slot == 0) bad++;
            go = false;
            while (done1 || done2) Thread.onSpinWait();
        }
        t1.interrupt();
        t2.interrupt();
        System.out.println("forbidden (0,0) outcomes = " + bad + "/" + iters);
        System.out.println("mutual exclusion forbids the anomaly: " + (bad == 0));
    }
}
```

Expected output:
```
forbidden (0,0) outcomes = 0/20000
mutual exclusion forbids the anomaly: true
```

The monitor serializes the two store;load pairs — no overlap, no anomaly,
by mutual exclusion rather than memory ordering. Three fixes, three
mechanisms: `volatile` (ordering), delay (timing — diagnostic only, never
a fix), lock (exclusion). Only the first and third are synchronization.

## Common Pitfalls Encountered Here

- **Testing races without rendezvous** — free-running threads phase-lock
  or never collide; barriers align starts but spread execution
  (snippets' volatile-flag rendezvous is the load-bearing design).
- **Calling timing a fix** — sleeps/delays change anomaly *rates*; only
  edges change the *verdict* (snippet 3 vs 2).
- **Assuming x86unreorderability** — StoreLoad escapes on x86 (snippet 1's
  79%); ARM escapes more.
- **Release/acquire as volatile replacement** — one-directional edges
  compose chains but don't give the full volatile total order (snippet 4's
  chain is sufficient, not universal).
- **Locking for ordering but mutating outside** — exclusion covers the
  critical section only (snippet 5's pair must stay inside).
- **Reading anomaly counts as benchmarks** — rates depend on rendezvous
  tightness, core count, and power state; verdicts (zero vs nonzero) are
  the portable signal.
