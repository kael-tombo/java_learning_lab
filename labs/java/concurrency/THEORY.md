# THEORY — Concurrency Deep Dive (Part 2)

---

## 2. Lock-Free & Wait-Free Algorithms

### CAS Loop Pattern

```java
// Lock-free stack
class LockFreeStack<E> {
    AtomicReference<Node<E>> head = new AtomicReference<>();

    void push(E item) {
        Node<E> newNode = new Node<>(item);
        Node<E> currentHead;
        do {
            currentHead = head.get();
            newNode.next = currentHead;
        } while (!head.compareAndSet(currentHead, newNode));
    }
}
```

### ABA Problem

```java
// ABA: A → B → A, CAS succeeds but state changed
// Solution: AtomicStampedReference
AtomicStampedReference<Node> head = new AtomicStampedReference<>(null, 0);

// In CAS loop:
int[] stamp = {0};
Node expected = head.getReference();
while (!head.compareAndSet(expected, newNode, stamp[0], stamp[0]+1)) {
    expected = head.getReference();
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
            Node<E> tail = tail.get();
            Node<E> next = tail.next.get();
            if (tail == this.tail.get()) {
                if (next == null) {
                    if (tail.next.compareAndSet(null, node)) {
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
    stamp = lock.readLock();
    try {
        data = readData();
    } finally {
        lock.unlockRead(stamp);
    }
}

// Pessimistic read
long stamp = lock.readLock();
try { return data; } finally { lock.unlockRead(stamp); }

// Write lock
long stamp = lock.writeLock();
try { mutate(); } finally { lock.unlockWrite(stamp); }
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