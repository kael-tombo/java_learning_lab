# Mock Interview: Concurrent Data Structures

## Q1 — ConcurrentHashMap Atomic Updates

**Problem.** Count word frequencies from parallel threads without explicit locks.

**Key insight.** `merge`/`compute` run atomically per bin, so read-modify-write cannot interleave. Iterators are weakly consistent: they tolerate concurrent modification instead of throwing.

**Complexity.** Expected O(1) ops; scalability comes from striped locking, not a single monitor.

```java
import java.util.concurrent.ConcurrentHashMap;

public class ConcurrentQ1 {
    public static void main(String[] args) throws Exception {
        ConcurrentHashMap<String, Integer> m = new ConcurrentHashMap<>();
        Thread t1 = new Thread(() -> {
            for (int i = 0; i < 1000; i++) m.merge("hits", 1, Integer::sum);
        });
        Thread t2 = new Thread(() -> {
            for (int i = 0; i < 1000; i++) m.merge("hits", 1, Integer::sum);
        });
        t1.start(); t2.start();
        t1.join(); t2.join();
        System.out.println(m.get("hits"));
    }
}
```

Output:

```
2000
```

## Q2 — Producer-Consumer with BlockingQueue

**Problem.** Hand items from producers to consumers with backpressure.

**Key insight.** A bounded BlockingQueue blocks producers when full and consumers when empty, so no busy-wait or manual wait/notify is needed. Poison-pill sentinels shut consumers down cleanly.

**Complexity.** O(1) put/take amortized; blocking is a feature, not overhead.

```java
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;

public class ConcurrentQ2 {
    public static void main(String[] args) throws Exception {
        BlockingQueue<Integer> q = new ArrayBlockingQueue<>(4);
        q.put(1); q.put(2); q.put(3);
        int sum = q.take() + q.take() + q.take();
        System.out.println(sum);
        System.out.println(q.remainingCapacity());
    }
}
```

Output:

```
6
4
```

## Q3 — LongAdder vs AtomicLong under Contention

**Problem.** Why does a metrics counter use LongAdder instead of AtomicLong?

**Key insight.** AtomicLong funnels all increments through one CAS location; LongAdder stripes increments across cells and sums them on read. Writes scale, reads cost O(cells).

**Complexity.** Increment expected O(1) with far less contention; sum is O(cells).

```java
import java.util.concurrent.atomic.LongAdder;

public class ConcurrentQ3 {
    public static void main(String[] args) throws Exception {
        LongAdder adder = new LongAdder();
        Thread[] ts = new Thread[4];
        for (int k = 0; k < 4; k++) {
            ts[k] = new Thread(() -> {
                for (int i = 0; i < 2500; i++) adder.increment();
            });
            ts[k].start();
        }
        for (Thread t : ts) t.join();
        System.out.println(adder.sum());
    }
}
```

Output:

```
10000
```
