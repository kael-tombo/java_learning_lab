# ANTI-PATTERNS: High-Performance Java Engineering
## Lab 15 | Production Engineering Academy — Top 0.0001% Engineering

---

## Anti-Pattern 1: Naive Microbenchmarking Without JMH

### The Mistake
```java
long start = System.currentTimeMillis();
for (int i = 0; i < 1_000_000; i++) {
    myMethod();
}
long elapsed = System.currentTimeMillis() - start;
System.out.println("Time: " + elapsed + "ms");
```

### Why It Fails (3 Silent Killers)
1. **Dead Code Elimination (DCE)**: The JIT compiler detects that `myMethod()`'s return value is never consumed. The entire loop is **silently compiled away to zero instructions**. You are measuring the overhead of an empty loop.
2. **No JIT Warmup**: The first few hundred invocations run in the interpreter (Tier 0). Thousands of invocations are needed before C1 → C2 compilation occurs. Including cold-start time in measurements produces results that are $3–10\times$ slower than steady-state production throughput.
3. **System Clock Granularity**: `currentTimeMillis()` has 1–15ms OS scheduler granularity. Operations taking nanoseconds cannot be measured with a millisecond-resolution clock.
4. **Single JVM Instance**: JVM ergonomic differences, GC timing jitter, OS scheduler preemption, and NUMA topology all cause measurement noise that is not averaged out across a single-run benchmark.

### The Correct Production Fix
Use **JMH (Java Microbenchmark Harness)** — the industry standard tool endorsed by the OpenJDK team:
```java
@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.NANOSECONDS)
@Warmup(iterations = 5, time = 1, timeUnit = TimeUnit.SECONDS)
@Measurement(iterations = 10, time = 1, timeUnit = TimeUnit.SECONDS)
@Fork(value = 3)  // 3 separate forked JVM processes eliminates JVM startup bias
@State(Scope.Thread)
public class MyBenchmark {

    @Benchmark
    public long testMyMethod(Blackhole bh) {  // Blackhole prevents DCE
        long result = myMethod();
        bh.consume(result);  // Forces JIT to treat result as "used"
        return result;
    }
}
```

---

## Anti-Pattern 2: Pointer Chasing — LinkedList vs. Array-Backed Collections

### The Mistake
```java
// Using LinkedList because it has O(1) add/remove at head
List<Order> pendingOrders = new LinkedList<>();

// Processing hot path:
for (Order order : pendingOrders) {
    process(order);
}
```

### Why It Fails (Hardware Physics)
A `LinkedList` node (`Node<E>`) contains:
- `E item` — actual data
- `Node<E> next` — a pointer (reference) to the next node in heap memory

The critical problem: each `Node` is independently allocated somewhere in the heap. After millions of allocations and GC cycles, nodes scatter across **random DRAM addresses**. Traversing the list means:
```
Node@0x7f2a_0000  →  Node@0x7f91_8040  →  Node@0x7f12_c000  ...
     (L1 hit)           (L3 miss! → DRAM)    (L3 miss! → DRAM)
```

Every node reference is a **guaranteed L3/DRAM cache miss** — a $50–100\text{ ns}$ penalty per node!

**An `ArrayList` by contrast**:
```
int[] array = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15...]
              ◄──────────── 64-byte cache line: 16 ints in one load ────────────►
```
The CPU hardware prefetcher detects sequential memory access and pre-loads subsequent cache lines before the CPU even requests them. This makes `ArrayList` iteration effectively **memory-bandwidth-bound** rather than latency-bound.

**Benchmark comparison** (JMH, 10M elements):
| Collection | Throughput (ops/ms) | Relative |
|---|---|---|
| `int[]` primitive array | 3,850 ops/ms | **1.0× (baseline)** |
| `ArrayList<Integer>` | 2,100 ops/ms | 0.55× |
| `LinkedList<Integer>` | 38 ops/ms | **0.01× — 100× slower!** |

### The Correct Production Fix
- Use `ArrayList` for random-access iteration.
- Use `ArrayDeque` (array-backed) as a `Deque`/`Queue` replacement for `LinkedList`.
- For primitive-heavy hot paths, use **EclipseCollections** (`IntList`, `LongList`) or **HPPC** to eliminate `Integer` boxing overhead entirely.

---

## Anti-Pattern 3: Synchronizing on a Shared Lock (Thundering Herd on Mutex)

### The Mistake
```java
public class OrderBook {
    private final List<Order> orders = new ArrayList<>();

    public synchronized void addOrder(Order o) {
        orders.add(o);
    }

    public synchronized List<Order> getOrders() {
        return new ArrayList<>(orders);
    }
}
```

### Why It Fails
`synchronized` acquires a JVM monitor lock, backed by a kernel futex. Under contention:
1. Thread 2 attempts to acquire the lock held by Thread 1.
2. Thread 2 is suspended via `futex_wait()` — a **context switch into kernel mode** ($2–10\mu\text{s}$).
3. Thread 1 releases, `futex_wake()` wakes Thread 2 — another **context switch back**.
4. Under 32 threads: each context switch is $5\mu\text{s}$; at 100,000 ops/sec, this burns $5\mu\text{s} \times 100{,}000 = 500\text{ ms/sec}$ — **50% of total CPU time** on lock overhead alone!

### Failure Amplifiers
- **Lock Convoy**: All threads pile up behind a hot lock. Even when Thread 1 releases, Thread 2 acquires but immediately contends with Thread 3. The queue never drains.
- **Priority Inversion**: A low-priority GC thread holds a lock needed by a high-priority request handler.

### The Correct Production Fix
Replace with a `ReadWriteLock` or `StampedLock` for read-heavy workloads:
```java
private final StampedLock lock = new StampedLock();

// Optimistic read — zero blocking, zero kernel call for read-mostly data:
public List<Order> getOrders() {
    long stamp = lock.tryOptimisticRead();
    List<Order> result = new ArrayList<>(orders);
    if (!lock.validate(stamp)) {
        // Data changed during read — upgrade to pessimistic read
        stamp = lock.readLock();
        try {
            result = new ArrayList<>(orders);
        } finally {
            lock.unlockRead(stamp);
        }
    }
    return result;
}

public void addOrder(Order o) {
    long stamp = lock.writeLock();
    try {
        orders.add(o);
    } finally {
        lock.unlockWrite(stamp);
    }
}
```
`StampedLock` optimistic reads: **zero blocking, zero memory fence** for the 90% case where no concurrent writer exists.

---

## Anti-Pattern 4: Excessive Object Allocation in Hot Paths (GC Churn)

### The Mistake
```java
// Called 1 million times per second in the trading engine hot path:
public OrderResult processOrder(long price, int quantity, String symbol) {
    // Allocates a new String for every call:
    String key = symbol + "-" + price + "-" + quantity;
    // Allocates a new OrderResult wrapper:
    return new OrderResult(key, System.currentTimeMillis());
}
```

### Why It Fails
At 1 million calls/second:
- 1 `String` allocation × ~48 bytes = 48 MB/sec of Eden allocation rate.
- 1 `OrderResult` × ~32 bytes = 32 MB/sec.
- **Total**: 80 MB/sec of short-lived object churn.
- Eden space (default 512 MB) fills in $512 / 80 = 6.4$ seconds → **Minor GC every 6.4 seconds**.
- Each Minor GC: 5–50ms stop-the-world → **P99 latency spike every 6 seconds**.

### The Correct Production Fix
**Object Pooling** (for reusable objects):
```java
// Apache Commons Pool2 or custom ring-buffer object pool:
private final ObjectPool<OrderResult> resultPool = new GenericObjectPool<>(new OrderResultFactory());

public OrderResult processOrder(long price, int quantity, String symbol) {
    OrderResult result = resultPool.borrowObject();
    result.reset(symbol, price, quantity, System.nanoTime());
    return result;  // Caller must return to pool after use!
}
```

**Interned Strings / Symbol tables** (for repeated string keys):
```java
private final Map<String, String> symbolCache = new ConcurrentHashMap<>();
// Intern once, reuse identity reference:
private String intern(String symbol) {
    return symbolCache.computeIfAbsent(symbol, Function.identity());
}
```

**Primitive specialization** (eliminate boxing entirely):
```java
// Replace Map<Long, OrderResult> (boxes Long) with HPPC:
LongObjectMap<OrderResult> orderMap = new LongObjectHashMap<>();
orderMap.put(orderId, result);  // Zero boxing, zero GC churn
```

---

## Anti-Pattern 5: Megamorphic Virtual Dispatch (Polymorphism at Scale)

### The Mistake
```java
interface PaymentProcessor {
    ProcessingResult process(Payment payment);
}

// Many implementations registered at runtime:
// StripeProcessor, AdyenProcessor, PayPalProcessor,
// BraintreeProcessor, SquareProcessor, WorldpayProcessor...

void handlePayment(PaymentProcessor processor, Payment p) {
    processor.process(p);  // Megamorphic call site
}
```

### Why It Fails
HotSpot C2 JIT specializes call sites into three categories:
| Call Site Type | Implementations | JIT Optimization | Latency |
|---|---|---|---|
| **Monomorphic** | 1 | Full inline, no dispatch | $0.5\text{ ns}$ |
| **Bimorphic** | 2 | Two-branch inline check | $1\text{ ns}$ |
| **Megamorphic** | 3+ | **Full vtable dispatch, no inlining** | $5–20\text{ ns}$ |

At a megamorphic call site, C2 must look up the vtable for every call, defeating all method inlining. At 1M calls/sec, that's 20ms/sec of unnecessary vtable overhead fleet-wide.

### The Correct Production Fix
Isolate the hot path to a **single concrete type** where possible. Use a routing layer to separate megamorphic dispatch from high-frequency processing:
```java
// Hot path is always Stripe (99% of traffic) — monomorphic!
if (processor instanceof StripeProcessor stripe) {
    stripe.processDirectly(payment);  // JIT can fully inline this
} else {
    processor.process(payment);  // Slow path for other processors
}
```

Or use sealed interfaces + pattern matching to help C2 enumerate and inline all implementations:
```java
sealed interface PaymentProcessor permits StripeProcessor, AdyenProcessor {}
```

---

## Anti-Pattern 6: Using `ThreadLocal` Without Cleanup (Memory Leak in Executors)

### The Mistake
```java
private static final ThreadLocal<DateFormat> DATE_FORMAT =
    ThreadLocal.withInitial(() -> new SimpleDateFormat("yyyy-MM-dd"));
```

### Why It Fails
In a thread-pool executor (Tomcat, Netty, virtual threads carrier threads):
- `ThreadLocal` values are stored in a map keyed by the **thread object**, not the task.
- When a task completes, the thread returns to the pool — **the ThreadLocal value is never cleared**.
- Across millions of requests: each thread holds a `SimpleDateFormat` instance (plus its internal `Calendar`, `TimeZone`, `Locale`): ~2KB each.
- On a 500-thread pool: 500 × 2KB = **1MB of leaked state per ThreadLocal**.
- Worse: leaked state from previous tasks **bleeds into the next task** on the same thread!

### The Correct Production Fix
1. Use `DateTimeFormatter` (thread-safe, no thread-local needed).
2. Always clean up `ThreadLocal` in a `try-finally`:
```java
try {
    DATE_FORMAT.set(new SimpleDateFormat("yyyy-MM-dd"));
    // ... use it ...
} finally {
    DATE_FORMAT.remove();  // MANDATORY cleanup
}
```
3. Or use Scoped Values (JDK 21 preview, JDK 23 final) which are automatically scoped to a task lifecycle.
