# THEORY — Concurrency Deep Dive

## Overview

Advanced concurrency patterns, JVM internals, and performance optimization techniques for building high-throughput, low-latency concurrent systems.

---

## 1. Java Memory Model (JMM)

### Happens-Before Relationship

The JMM defines a partial ordering called **happens-before** that guarantees visibility of writes across threads:

| Rule | Description |
|------|-------------|
| Program Order | Actions in a single thread happen in program order |
| Monitor Lock | Unlock happens-before subsequent lock |
| Volatile Write | Write to volatile happens-before subsequent read |
| Thread Start | `Thread.start()` happens-before thread's first action |
| Thread Join | Thread termination happens-before `join()` returns |
| Transitivity | If A hb B and B hb C, then A hb C |

### Data Races

Two conflicting accesses (at least one write) without happens-before ordering = **data race**.
JMM guarantees **DRF (Data Race Free) guarantee**: programs without data races exhibit sequential consistency.

---

## 2. Lock Implementations

### synchronized vs ReentrantLock

| Aspect | `synchronized` | `ReentrantLock` |
|--------|----------------|-----------------|
| Fairness | Unfair (barging) | Optional fair mode |
| Interruptibility | No | `lockInterruptibly()` |
| Timeout | No | `tryLock(timeout)` |
| Conditions | Single `wait/notify` | Multiple `Condition` objects |
| Performance | Good (biased locking) | Better under high contention |

### StampedLock (Java 8+)

```java
StampedLock lock = new StampedLock();

// Optimistic read (fast path)
long stamp = lock.tryOptimisticRead();
Data data = readData();
if (!lock.validate(stamp)) {
    // Fallback to pessimistic
    long stamp = lock.readLock();
    try { return readData(); } finally { lock.unlockRead(stamp); }
}

// Pessimistic read
long stamp = lock.readLock();
try { return readData(); } finally { lock.unlockRead(stamp); }

// Write lock
long stamp = lock.writeLock();
try { mutate(); } finally { lock.unlockWrite(stamp); }
```

**Key advantage**: Optimistic reads don't block writers. Use `validate()` to check if write occurred during read.

---

## 2. Lock-Free Programming

### CAS (Compare-And-Swap)

```java
AtomicInteger counter = new AtomicInteger(0);

// Simple increment
counter.incrementAndGet();

// CAS loop pattern
void increment(AtomicInteger counter) {
    while (true) {
        int current = counter.get();
        int next = current + 1;
        if (counter.compareAndSet(current, next)) return;
        // retry on contention
    }
}
```

### ABA Problem

```
Thread 1: reads A
Thread 2: changes A → B → A
Thread 1: CAS succeeds (sees A), but state changed!
```

**Solution**: `AtomicStampedReference` or `AtomicMarkableReference`

```java
AtomicStampedReference<Node> head = new AtomicStampedReference<>(null, 0);

// In CAS loop:
int[] stamp = {0};
Node expected = head.getReference();
while (!head.compareAndSet(expected, newNode, stamp[0], stamp[0]+1)) {
    expected = head.getReference();
    stamp[0] = head.getStamp();
}
```

---

## 2. Lock-Free Data Structures

### Michael-Scott Lock-Free Queue

```java
class LockFreeQueue<E> {
    static class Node<E> {
        final E item;
        final AtomicReference<Node<E>> next = new AtomicReference<>();
    }

    final AtomicReference<Node<E>> head = new AtomicReference<>(new Node<>(null));
    final AtomicReference<Node<E>> tail = new AtomicReference<>(head.get());

    void enqueue(E item) {
        Node<E> node = new Node<>(item);
        while (true) {
            Node<E> tail = this.tail.get();
            Node<E> next = tail.next.get();
            if (tail == this.tail.get()) {
                if (next == null) {
                    if (tail.next.compareAndSet(null, newNode)) {
                        tail.compareAndSet(tail, node);
                        return;
                    }
                } else {
                    tail.compareAndSet(tail, next);
                }
            }
        }
    }
}
```

---

## 3. StampedLock (Java 8+)

### Optimistic Read Lock

```java
StampedLock lock = new StampedLock();

// Optimistic read (fast path)
long stamp = lock.tryOptimisticRead();
Data data = readData();
if (!lock.validate(stamp)) {
    // Fallback to pessimistic
    long stamp = lock.readLock();
    try { return readData(); } finally { lock.unlockRead(stamp); }
}
```

### When to Use

| Scenario | Lock Choice |
|----------|-------------|
| Read-heavy, rare writes | StampedLock (optimistic) |
| Write-heavy | ReentrantReadWriteLock |
| High contention | StampedLock optimistic |
| Simple cases | ReentrantLock / synchronized |

---

## 3. ForkJoinPool & Parallelism

### ForkJoinPool Mechanics

```java
ForkJoinPool pool = new ForkJoinPool(
    Runtime.getRuntime().availableProcessors(),
    ForkJoinPool.defaultForkJoinWorkerThreadFactory,
    null, true);

pool.submit(() -> {
    // ForkJoinTask
}).join();
```

### Work Stealing

```
Thread 1: [Task A] → steal from Q2
Thread 2: [Task B, Task C] → steal from Q3
Thread 3: [Task D]
```

### RecursiveTask

```java
class SumTask extends RecursiveTask<Long> {
    static final int THRESHOLD = 10000;
    final long[] array;
    final int lo, hi;

    SumTask(long[] a, int lo, int hi) { this.array = a; this.lo = lo; this.hi = hi; }

    @Override
    protected Long compute() {
        if (hi - lo <= THRESHOLD) return sumSequentially();
        int mid = (lo + hi) >>> 1;
        SumTask left = new SumTask(array, lo, mid);
        SumTask right = new SumTask(array, mid, hi);
        left.fork();
        long rightResult = right.compute();
        long leftResult = left.join();
        return leftResult + rightResult;
    }
}
```

---

## 4. Reactive Streams & Backpressure

### Reactive Streams Spec

```
Publisher → Subscriber
    subscribe(Subscriber)
    → onSubscribe(Subscription)
    → onNext(T) × N
    → onComplete() / onError(Throwable)

Subscription:
  request(n)  // demand
  cancel()    // cancel
```

### Reactive Streams Operators

| Operator | Backpressure |
|----------|--------------|
| `map` | Transforms, passes demand |
| `filter` | Drops, passes demand |
| `flatMap` | Concat/merge, request management |
| `buffer` | Buffers, requests in chunks |
| `flatMapSequential` | Ordered, backpressure-aware |

---

## 4. Reactive Streams Backpressure

### Flow Control

```
Publisher → Subscriber
    subscribe(Subscriber)
    → onSubscribe(Subscription)
    → onNext(T) × N
    → onComplete() / onError(Throwable)

Subscription:
  request(n)  // demand
  cancel()    // cancel
```

### Backpressure Strategies

| Strategy | Behavior |
|----------|----------|
| Buffer | Unbounded (OOM risk) |
| Drop | Drop new/old |
| Error | Signal error |
| Latest | Keep latest only |

---

## 5. Structured Concurrency (Java 21+)

### StructuredTaskScope

```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    var f1 = scope.fork(() -> serviceA.call());
    var f2 = scope.fork(() -> serviceB.call());
    
    scope.join();           // Wait for all
    scope.throwIfFailed();  // Propagate first exception
    
    Result r1 = f1.get();
    Result r2 = f2.get();
}
```

### Benefits

- Automatic error propagation
- Automatic cancellation on failure
- No thread leaks
- Clear ownership hierarchy

---

## 5. Virtual Threads (Java 21+)

### Lightweight Threads

```java
// Platform threads: ~1MB stack, ~1ms start
// Virtual threads: ~1KB stack, ~1μs start

ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();
executor.submit(() -> blockingIoCall());
```

### Pinning

```java
// Pinning: VT blocks carrier thread
// Causes: synchronized, native calls, Foreign Function Interface

// Fix: ReentrantLock instead of synchronized
ReentrantLock lock = new ReentrantLock();
lock.lock();
try { ... } finally { lock.unlock(); }
```

---

## 7. Performance Anti-Patterns

| Anti-Pattern | Fix |
|------------|-----|
| Synchronized on long ops | Move I/O outside lock |
| Spin loops | Use Condition/LockSupport |
| ThreadLocal leaks | Remove in finally / use WeakReference |
| ThreadLocal in pools | Clear in finally |
| Excessive synchronization | Lock striping, ConcurrentHashMap |

---

## 8. Testing Concurrency

### jcstress

```java
@JCStressTest
@Outcome(id = "TERMINATED", expect = Expect.ACCEPTABLE)
@State
class CounterTest {
    AtomicInteger counter = new AtomicInteger();
    
    @Actor
    void increment() { counter.incrementAndGet(); }
    
    @Arbiter
    void check(IntResult r) { r.r1 = counter.get(); }
}
```

### Stress Testing

```bash
java -jar jcstress.jar -t MyTest -v
```

### ThreadSanitizer (TSan)

```bash
clang -fsanitize=thread -O1 -g -o test test.c
./test
```