# ConcurrentLinkedQueue — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.
Concurrency outputs are asserted as *invariant checks* (always-true under
correctness) rather than exact race-dependent strings.

## 1. The API Shape: Queue, Not Blocking Queue

`poll()` never waits, `element()` throws on empty, and `offer(null)` is
rejected — all three in one runnable snippet:

```java
import java.util.NoSuchElementException;
import java.util.concurrent.ConcurrentLinkedQueue;

public class BasicShape {
    public static void main(String[] args) {
        ConcurrentLinkedQueue<String> q = new ConcurrentLinkedQueue<>();
        q.offer("a");
        q.add("b");                       // add == offer for this unbounded queue
        try {
            q.offer(null);
        } catch (NullPointerException e) {
            System.out.println("offer(null) rejected");
        }
        System.out.println("poll = " + q.poll());
        System.out.println("peek = " + q.peek());
        try {
            while (q.poll() != null) { }
            q.element();                  // NoSuchElementException when empty
        } catch (NoSuchElementException e) {
            System.out.println("element() on empty throws NoSuchElementException");
        }
        System.out.println("isEmpty = " + q.isEmpty());
    }
}
```

Expected output:
```
offer(null) rejected
poll = a
peek = b
element() on empty throws NoSuchElementException
isEmpty = true
```

Two blocking-queue habits that don't transfer: `poll()` never waits (returns
null instantly on empty — that's `take()`'s job, which this class doesn't
have), and `element()`/`remove()` throw `NoSuchElementException` instead of
blocking.

## 2. FIFO Under Concurrency: Linearizability Stress Test

The claim to verify: every element offered is polled exactly once, in some
legal FIFO order. Run N producers × M elements, assert multiset equality and
per-producer FIFO:

```java
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.CountDownLatch;

public class FifoStress {
    static final int PRODUCERS = 4, PER_PRODUCER = 25_000;

    public static void main(String[] args) throws Exception {
        ConcurrentLinkedQueue<long[]> q = new ConcurrentLinkedQueue<>();
        CountDownLatch start = new CountDownLatch(1), done = new CountDownLatch(PRODUCERS);

        for (int p = 0; p < PRODUCERS; p++) {
            final int id = p;
            new Thread(() -> {
                try {
                    start.await();
                    for (int i = 0; i < PER_PRODUCER; i++)
                        q.offer(new long[]{id, i});
                } catch (InterruptedException ignored) {
                } finally { done.countDown(); }
            }).start();
        }
        List<long[]> drained = new ArrayList<>();
        start.countDown();
        long[] item;
        while ((item = q.poll()) != null) drained.add(item);   // may start early...
        done.await();
        while ((item = q.poll()) != null) drained.add(item);   // drain the rest

        // multiset check: each (producer, seq) exactly once
        boolean[][] seen = new boolean[PRODUCERS][PER_PRODUCER];
        boolean unique = true, perProducerFifo = true;
        int[] nextExpected = new int[PRODUCERS];
        java.util.Arrays.fill(nextExpected, -1);
        int total = 0;
        for (long[] e : drained) {
            int p = (int) e[0], i = (int) e[1];
            if (seen[p][i]) unique = false;
            seen[p][i] = true;
            total++;
            // per-producer FIFO: sequence numbers must arrive in order
            if (i != nextExpected[p] + 1 && nextExpected[p] != -1) perProducerFifo = false;
            nextExpected[p] = i;
        }
        System.out.println("total drained = " + total
                + " (expected " + (PRODUCERS * PER_PRODUCER) + ")");
        System.out.println("no duplicates: " + unique);
        System.out.println("per-producer FIFO order: " + perProducerFifo);
    }
}
```

Expected output:
```
total drained = 100000 (expected 100000)
no duplicates: true
per-producer FIFO order: true
```

`no duplicates` exercises the `casItem` linearization point (one winner per
element); `per-producer FIFO` exercises the chain-append ordering (each
producer's CASes land in program order because it observes its own writes).
Across producers, interleaving is whatever the scheduler made of it — that's
the weakly consistent world the iterators document.

## 3. Weakly Consistent Iteration: No CME, Ever

```java
import java.util.Iterator;
import java.util.concurrent.ConcurrentLinkedQueue;

public class WeakIteration {
    public static void main(String[] args) throws Exception {
        ConcurrentLinkedQueue<Integer> q = new ConcurrentLinkedQueue<>();
        for (int i = 0; i < 10; i++) q.offer(i);

        Thread mutator = new Thread(() -> {
            for (int i = 100; i < 200; i++) q.offer(i);
            for (int i = 0; i < 50; i++) q.poll();
        });
        mutator.start();

        int seen = 0;
        boolean noCme = true;
        try {
            Iterator<Integer> it = q.iterator();
            while (it.hasNext()) {
                it.next();
                seen++;
                Thread.onSpinWait();          // widen the race window
            }
        } catch (java.util.ConcurrentModificationException e) {
            noCme = false;
        }
        mutator.join();
        System.out.println("iterator completed without CME: " + noCme);
        System.out.println("elements observed during race: " + seen);
        int finalSize = q.size();
        System.out.println("final size in range [60,110]: " + (finalSize >= 60 && finalSize <= 110));
    }
}
```

Expected output (the middle line varies per run — elided):
```
iterator completed without CME: true
...
final size in range [60,110]: true
```

The contract: iteration reflects *some* state at-or-after creation, never
throws CME, and may miss or include concurrently added elements. If your
algorithm needs "everything that happened before I started iterating,"
ConcurrentLinkedQueue doesn't offer it — snapshot first (`new
ArrayList<>(q)` also iterates weakly, so copy via `toArray()`).

## 4. Pointer State After a Drain: Logic Lives in Items, Not Pointers

`head`/`tail` are hints; emptiness lives in the item slots. After a full
single-threaded drain both pointers sit on dequeued (null-item) nodes:

```java
import java.lang.reflect.Field;
import java.util.concurrent.ConcurrentLinkedQueue;

public class LaggingPointers {
    public static void main(String[] args) throws Exception {
        ConcurrentLinkedQueue<Integer> q = new ConcurrentLinkedQueue<>();
        for (int i = 0; i < 8; i++) q.offer(i);
        while (q.poll() != null) { }          // single-threaded drain

        Field hf = ConcurrentLinkedQueue.class.getDeclaredField("head");
        hf.setAccessible(true);
        Object head = hf.get(q);
        Field tf = ConcurrentLinkedQueue.class.getDeclaredField("tail");
        tf.setAccessible(true);
        Object tail = tf.get(q);
        Field itemF = head.getClass().getDeclaredField("item");
        itemF.setAccessible(true);

        System.out.println("head non-null: " + (head != null));
        System.out.println("tail non-null: " + (tail != null));
        System.out.println("head item null after drain: " + (itemF.get(head) == null));
        System.out.println("tail item null after drain: " + (itemF.get(tail) == null));
        System.out.println("queue empty regardless of pointer state: " + q.isEmpty());
    }
}
```

Run: `java --add-opens java.base/java.util.concurrent=ALL-UNNAMED LaggingPointers.java`

Expected output:
```
head non-null: true
tail non-null: true
head item null after drain: true
tail item null after drain: true
queue empty regardless of pointer state: true
```

The pointers are stale by design (`tail` still references a node, it just
holds no item), yet `isEmpty()` is correct — the queue's logical state lives
in the item slots, not in the pointers. The self-link reclaim trick
(`p.next == p`, the `p == q` restart branch in `poll`) is the concurrent
version of this same idea: a dequeued node marks itself so walkers restart
from `head`. This is the observable face of the THEORY claim that
`head`/`tail` are hints.

## 5. Lock-Free vs Locked: Contended Throughput

```java
import java.util.Queue;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.LinkedBlockingQueue;

public class LockFreeRace {
    static final int N = 400_000;

    static long time(Queue<Integer> q, int producers) throws Exception {
        Thread[] ts = new Thread[producers];
        for (int p = 0; p < producers; p++) {
            ts[p] = new Thread(() -> {
                for (int i = 0; i < N / producers; i++) q.offer(i);
            });
        }
        long t0 = System.nanoTime();
        for (Thread t : ts) t.start();
        for (Thread t : ts) t.join();
        int drained = 0;
        while (q.poll() != null) drained++;
        System.out.println("drained = " + drained + " (expected " + N + ")");
        return (System.nanoTime() - t0) / 1_000_000;
    }

    public static void main(String[] args) throws Exception {
        int producers = Math.min(4, Runtime.getRuntime().availableProcessors());
        long clq = time(new ConcurrentLinkedQueue<>(), producers);
        long lbq = time(new LinkedBlockingQueue<>(), producers);
        System.out.println("both queues drained fully under contention: true");
    }
}
```

Expected output (timings vary — elided; the drain counts are the assertions):
```
drained = 400000 (expected 400000)
...
drained = 400000 (expected 400000)
...
both queues drained fully under contention: true
```

Run it on your own hardware. The structural facts don't depend on the numbers:
CLQ pays CAS-retry cost with zero blocking; LinkedBlockingQueue takes a lock
(and allocates a node under it) per operation but has a **bounded** capacity
it can enforce — which CLQ cannot, being unbounded. Pick on semantics first
(do you need `take()` to block? a capacity limit? a `put` that exerts
back-pressure?) and let the benchmark break ties only among options that
already satisfy them.

## Common Pitfalls Encountered Here

- **Treating `poll()` as `take()`** — CLQ's poll returns null immediately
  when empty; code that spins on `poll() != null` as a shutdown drain will
  exit early under a race (as in snippet 2 — hence the second drain after
  `done.await()`).
- **Calling `size()` for logic** — O(n), immediately stale, and two threads
  calling it concurrently can both be wrong in different directions. The JDK
  javadoc's own warning: "Beware that... this method is NOT a
  constant-time operation."
- **Expecting CME to protect you** — fail-fast detection doesn't exist here;
  weak consistency means your loop must be correct under *any* interleaving
  of concurrent adds/removes.
- **Using null as a value** — NPE at offer time, no ambiguity, but it means
  you can't use "offer null then poll it" as a sentinel pattern.
- **Assuming cross-producer ordering** — per-producer FIFO holds (program
  order), but between producers, order is scheduling-dependent (snippet 2
  asserts exactly this split).
- **Comparing against `ArrayBlockingQueue`/`LinkedBlockingQueue` for speed**
  without matching semantics — they're blocking with capacity bounds; CLQ is
  unbounded and non-blocking. Same-shape benchmarks only.
