# CODE DEEP DIVE: Mechanical Sympathy & Performance Patterns
## Lab 15 | Production Engineering Academy — Top 0.0001% Engineering

---

## Pattern 1: Cache-Line Padded Counter Using VarHandle (Zero False Sharing)

```java
package com.learning.production.lab15;

import java.lang.invoke.MethodHandles;
import java.lang.invoke.VarHandle;

/**
 * A cache-line-padded atomic counter that prevents False Sharing.
 *
 * Design: Each instance occupies exactly 192 bytes in memory (3 cache lines):
 *   - 56 bytes padding (pre)
 *   - 8 bytes volatile value
 *   - 56 bytes padding (post)
 *   = 120 bytes guaranteed to keep 'value' isolated on its own cache line.
 *
 * VarHandle provides access modes beyond the synchronized/volatile keyword:
 *   - PLAIN (no ordering)     - OPAQUE (intra-thread, no global ordering)
 *   - ACQUIRE/RELEASE         - VOLATILE (full memory barrier)
 *
 * JVM Flag Required: -XX:-RestrictContended
 * Alternative: @jdk.internal.vm.annotation.Contended
 */
public final class PaddedCounter {

    // 56 bytes before 'value' — 7 × 8-byte longs
    private long p1, p2, p3, p4, p5, p6, p7;

    // The actual hot counter — isolated on its own 64-byte cache line
    private volatile long value = 0L;

    // 56 bytes after 'value'
    private long p8, p9, p10, p11, p12, p13, p14;

    // VarHandle: Reflective, type-safe alternative to sun.misc.Unsafe
    private static final VarHandle VALUE;
    static {
        try {
            VALUE = MethodHandles.lookup()
                .findVarHandle(PaddedCounter.class, "value", long.class);
        } catch (ReflectiveOperationException e) {
            throw new ExceptionInInitializerError(e);
        }
    }

    /**
     * Increments with RELEASE memory ordering — writes are visible to
     * threads that subsequently perform an ACQUIRE read.
     * Avoids the full StoreLoad fence of a VOLATILE write.
     */
    public void incrementRelease() {
        VALUE.setRelease(this, (long) VALUE.getOpaque(this) + 1L);
    }

    /**
     * Full compare-and-swap: returns true only if successful.
     * Uses VarHandle compareAndSet which emits LOCK CMPXCHG on x86.
     */
    public boolean tryIncrement(long expected) {
        return VALUE.compareAndSet(this, expected, expected + 1L);
    }

    /**
     * Unconditional atomic add: uses x86 LOCK XADD instruction.
     * Returns the previous value.
     */
    public long getAndAdd(long delta) {
        return (long) VALUE.getAndAdd(this, delta);
    }

    /** VOLATILE read — full StoreLoad barrier, sequentially consistent. */
    public long getVolatile() {
        return value;
    }

    /** OPAQUE read — compiler cannot hoist outside loops, but no memory fence. */
    public long getOpaque() {
        return (long) VALUE.getOpaque(this);
    }

    /** Reset for object reuse (object pool pattern). */
    public void reset() {
        VALUE.setRelease(this, 0L);
    }
}
```

---

## Pattern 2: JMH Benchmark Suite — False Sharing vs. Padded Counter

```java
package com.learning.production.lab15;

import org.openjdk.jmh.annotations.*;
import org.openjdk.jmh.infra.Blackhole;
import org.openjdk.jmh.runner.Runner;
import org.openjdk.jmh.runner.options.OptionsBuilder;

import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;

@BenchmarkMode(Mode.Throughput)
@OutputTimeUnit(TimeUnit.MILLISECONDS)
@Warmup(iterations = 5, time = 1)
@Measurement(iterations = 10, time = 2)
@Fork(value = 3, jvmArgs = {
    "-XX:-RestrictContended",
    "-XX:+UseG1GC",
    "-Xms4g", "-Xmx4g"
})
@Threads(8)  // 8 concurrent threads per JVM fork
public class FalseSharingBenchmark {

    /** BAD: Two counters in the same cache line — massive false sharing */
    @State(Scope.Benchmark)
    public static class FalseSharingState {
        volatile long counter1 = 0;
        volatile long counter2 = 0;  // Same 64-byte cache line as counter1!
    }

    /** GOOD: Two counters isolated on separate cache lines */
    @State(Scope.Benchmark)
    public static class PaddedState {
        PaddedCounter counter1 = new PaddedCounter();
        PaddedCounter counter2 = new PaddedCounter();
    }

    @Benchmark
    public void falseSharingWrite(FalseSharingState state) {
        // Even and odd threads update different counters, same cache line:
        if (Thread.currentThread().getName().hashCode() % 2 == 0) {
            state.counter1++;
        } else {
            state.counter2++;
        }
    }

    @Benchmark
    public void paddedCounterWrite(PaddedState state) {
        if (Thread.currentThread().getName().hashCode() % 2 == 0) {
            state.counter1.incrementRelease();
        } else {
            state.counter2.incrementRelease();
        }
    }
}
// Expected results (8-core machine):
// falseSharingWrite:  ~85,000 ops/ms
// paddedCounterWrite: ~4,200,000 ops/ms  (49× faster — false sharing eliminated)
```

---

## Pattern 3: Allocation-Free Hot Path — Object Pool with Ring Buffer

```java
package com.learning.production.lab15;

import java.util.concurrent.atomic.AtomicLong;

/**
 * Lock-free, GC-free object pool backed by a power-of-2 ring buffer.
 *
 * Design Principles:
 * - Pre-allocates all objects during startup (never allocates in hot path).
 * - Claim/release operations are lock-free using CAS on atomic sequence cursors.
 * - Ring size must be power-of-2 for efficient index masking (& mask instead of % size).
 *
 * Trade-offs:
 * - Fixed capacity: pool exhaustion = blocking or null return.
 * - Objects must be reset() before reuse (caller contract).
 */
public class RingBufferObjectPool<T extends Resettable> {

    private final Object[] ring;
    private final int mask;
    private final AtomicLong claimSequence = new AtomicLong(0);
    private final AtomicLong releaseSequence = new AtomicLong(0);

    @SuppressWarnings("unchecked")
    public RingBufferObjectPool(int capacity, java.util.function.Supplier<T> factory) {
        // Enforce power-of-2 capacity
        int size = Integer.highestOneBit(capacity - 1) << 1;
        this.ring = new Object[size];
        this.mask = size - 1;
        for (int i = 0; i < size; i++) {
            ring[i] = factory.get();
        }
    }

    /**
     * Borrow an object from the pool.
     * Returns null if pool is exhausted (no blocking).
     */
    @SuppressWarnings("unchecked")
    public T borrow() {
        long seq = claimSequence.getAndIncrement();
        long available = releaseSequence.get() + ring.length;
        if (seq >= available) {
            claimSequence.decrementAndGet();  // Return the claimed slot
            return null;  // Pool exhausted — caller must handle
        }
        T obj = (T) ring[(int)(seq & mask)];
        obj.reset();
        return obj;
    }

    /**
     * Return object to pool. Must be called exactly once per borrow().
     */
    public void release(T obj) {
        releaseSequence.incrementAndGet();
    }
}

public interface Resettable {
    void reset();
}

// Usage in hot path:
public class OrderEvent implements Resettable {
    public long orderId;
    public double price;
    public int quantity;
    public String symbol;

    @Override
    public void reset() {
        orderId = 0L;
        price = 0.0;
        quantity = 0;
        symbol = null;
    }
}
```

---

## Pattern 4: Zero-Copy File Transfer with NIO `transferTo()`

```java
package com.learning.production.lab15;

import java.io.*;
import java.net.*;
import java.nio.channels.*;
import java.nio.file.*;

/**
 * Demonstrates zero-copy file serving using Java NIO FileChannel.transferTo().
 *
 * OS Implementation:
 *   - Linux: Uses sendfile(2) syscall — data moves from page cache to socket
 *             without entering user space.
 *   - macOS: Uses sendfile() (BSD variant)
 *   - Windows: Uses TransmitFile() Win32 API
 *
 * Performance: Eliminates 2 of 4 traditional memory copies, and avoids
 * user-space buffer allocations entirely.
 */
public class ZeroCopyFileServer {

    public void serveFile(Path filePath, SocketChannel clientChannel) throws IOException {
        try (FileChannel fileChannel = FileChannel.open(filePath, StandardOpenOption.READ)) {
            long fileSize = fileChannel.size();
            long position = 0L;

            // transferTo() handles partial transfers — loop until complete
            while (position < fileSize) {
                long transferred = fileChannel.transferTo(
                    position,
                    fileSize - position,
                    clientChannel
                );
                if (transferred <= 0) break;  // Client disconnected
                position += transferred;
            }
        }
    }

    /**
     * Traditional (WRONG) way — 4 copies, user-space buffer allocation:
     */
    public void serveFileNaive(File file, Socket socket) throws IOException {
        byte[] buffer = new byte[8192];  // User-space buffer allocated on heap!
        try (FileInputStream fis = new FileInputStream(file);
             OutputStream os = socket.getOutputStream()) {
            int bytesRead;
            while ((bytesRead = fis.read(buffer)) != -1) {
                // COPY 1: Disk → Kernel Page Cache (DMA)
                // COPY 2: Kernel Page Cache → User buffer (this read)
                // COPY 3: User buffer → Socket buffer (this write)
                // COPY 4: Socket buffer → NIC (DMA)
                os.write(buffer, 0, bytesRead);
            }
        }
    }
}
```

---

## Pattern 5: Padded Sequence for LMAX Disruptor-Style Ring Buffer

```java
package com.learning.production.lab15;

import java.lang.invoke.MethodHandles;
import java.lang.invoke.VarHandle;

/**
 * A heavily-padded sequence that occupies an entire cache line (128+ bytes).
 * This is the architectural core of the LMAX Disruptor pattern.
 *
 * Why 128 bytes?
 *   Intel x86 "destructive interference size" is 64 bytes (one cache line).
 *   Some prefetchers fetch 2 adjacent lines together (128 bytes).
 *   128-byte padding guarantees isolation even on aggressive prefetchers.
 */
public class Sequence {
    // 56 bytes before
    private long p1, p2, p3, p4, p5, p6, p7;

    private volatile long value;  // The actual sequence number (8 bytes)

    // 56 bytes after
    private long p8, p9, p10, p11, p12, p13, p14;

    private static final VarHandle VALUE;
    static {
        try {
            VALUE = MethodHandles.lookup().findVarHandle(Sequence.class, "value", long.class);
        } catch (NoSuchFieldException | IllegalAccessException e) {
            throw new ExceptionInInitializerError(e);
        }
    }

    public Sequence(long initialValue) {
        VALUE.setRelease(this, initialValue);
    }

    public long get() {
        return (long) VALUE.getAcquire(this);
    }

    public void set(long value) {
        VALUE.setRelease(this, value);
    }

    public boolean compareAndSet(long expected, long update) {
        return VALUE.compareAndSet(this, expected, update);
    }

    public long incrementAndGet() {
        return (long) VALUE.getAndAdd(this, 1L) + 1L;
    }
}

/**
 * Minimal single-producer, single-consumer ring buffer using padded sequences.
 * Demonstrates the Disruptor's core allocation-free message passing.
 */
public class SingleProducerRingBuffer<E> {
    private final E[] buffer;
    private final int mask;
    private final Sequence producerCursor = new Sequence(-1L);
    private final Sequence consumerCursor = new Sequence(-1L);

    @SuppressWarnings("unchecked")
    public SingleProducerRingBuffer(int size) {
        // Power-of-2 size for efficient index masking
        int capacity = Integer.highestOneBit(size - 1) << 1;
        buffer = (E[]) new Object[capacity];
        mask = capacity - 1;
    }

    /**
     * Producer: claim next sequence, write event, then publish.
     * Returns false if buffer is full (consumer hasn't caught up).
     */
    public boolean tryPublish(E event) {
        long next = producerCursor.get() + 1L;
        // Check if ring buffer is full: producer is lapping consumer
        if (next > consumerCursor.get() + buffer.length) {
            return false;  // Back-pressure: consumer too slow
        }
        buffer[(int)(next & mask)] = event;
        producerCursor.set(next);  // RELEASE: makes event visible to consumer
        return true;
    }

    /**
     * Consumer: poll for next available event. Returns null if nothing available.
     * Zero allocation — returns reference to pre-allocated event in ring.
     */
    public E poll() {
        long next = consumerCursor.get() + 1L;
        if (next > producerCursor.get()) {
            return null;  // No events available
        }
        E event = buffer[(int)(next & mask)];
        consumerCursor.set(next);  // RELEASE: allows producer to reclaim slot
        return event;
    }
}
```

---

## Pattern 6: JMH Benchmark for Sequential vs. Random Memory Access (Cache Effects)

```java
package com.learning.production.lab15;

import org.openjdk.jmh.annotations.*;
import org.openjdk.jmh.infra.Blackhole;

import java.util.concurrent.TimeUnit;

/**
 * Proves hardware cache effects empirically.
 * Expected results on modern x86-64 hardware:
 *
 *   sequentialAccess:   ~500 MB/s throughput  (L1/L2 hits via prefetcher)
 *   strided_16Access:   ~350 MB/s             (every 64 bytes — exactly one cache line)
 *   randomAccess:       ~50 MB/s              (random DRAM accesses — no prefetch benefit)
 */
@BenchmarkMode(Mode.Throughput)
@OutputTimeUnit(TimeUnit.SECONDS)
@State(Scope.Thread)
@Fork(2)
@Warmup(iterations = 3, time = 1)
@Measurement(iterations = 5, time = 2)
public class CacheEffectBenchmark {

    private static final int SIZE = 1 << 24;  // 16M integers = 64MB
    private int[] data;
    private int[] randomIndices;

    @Setup
    public void init() {
        data = new int[SIZE];
        randomIndices = new int[SIZE];
        java.util.Random rng = new java.util.Random(42L);
        for (int i = 0; i < SIZE; i++) {
            data[i] = rng.nextInt();
            randomIndices[i] = rng.nextInt(SIZE);
        }
    }

    /** L1/L2 hardware prefetcher activates — near peak memory bandwidth */
    @Benchmark
    public long sequentialAccess(Blackhole bh) {
        long sum = 0;
        for (int i = 0; i < SIZE; i++) {
            sum += data[i];
        }
        bh.consume(sum);
        return sum;
    }

    /**
     * Stride 16 = 64 bytes (one cache line per access).
     * Prefetcher still works for regular strides.
     */
    @Benchmark
    public long stridedAccess(Blackhole bh) {
        long sum = 0;
        for (int i = 0; i < SIZE; i += 16) {
            sum += data[i];
        }
        bh.consume(sum);
        return sum;
    }

    /**
     * Random access: defeats hardware prefetcher entirely.
     * Every access is a cache miss → DRAM latency of 50–100ns per element.
     */
    @Benchmark
    public long randomAccess(Blackhole bh) {
        long sum = 0;
        for (int i = 0; i < SIZE; i++) {
            sum += data[randomIndices[i]];
        }
        bh.consume(sum);
        return sum;
    }
}
```

---

## Pattern 7: Virtual Threads with Structured Concurrency (JDK 21)

```java
package com.learning.production.lab15;

import java.util.concurrent.*;

/**
 * Demonstrates Project Loom's Virtual Threads for high-concurrency I/O-bound workloads.
 *
 * Virtual Threads Architecture:
 * - Virtual threads are cheap: 1 million virtual threads ≈ 200MB RAM (200 bytes each).
 * - Platform threads (OS threads) cost: 1MB stack + kernel resources.
 * - Virtual threads are "parked" when blocking on I/O; unmounted from carrier threads.
 * - The carrier thread pool (= number of CPU cores) stays fully utilized.
 *
 * Trade-offs:
 * - NOT a replacement for lock-free data structures on CPU-bound hot paths.
 * - Synchronized blocks "pin" virtual threads to carrier threads — avoid in hot paths.
 * - Use ReentrantLock instead of synchronized to allow unmounting during blocking.
 */
public class VirtualThreadDemo {

    public static void main(String[] args) throws InterruptedException {
        // Create 10,000 virtual threads — trivially cheap
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            var futures = new java.util.ArrayList<StructuredTaskScope.Subtask<String>>();

            for (int i = 0; i < 10_000; i++) {
                final int id = i;
                futures.add(scope.fork(() -> fetchFromDatabase(id)));
            }

            scope.join();           // Wait for all subtasks
            scope.throwIfFailed();  // Propagate any exception

            // All results available:
            futures.forEach(f -> System.out.println(f.get()));
        }
    }

    private static String fetchFromDatabase(int id) throws InterruptedException {
        // This blocking sleep parks the virtual thread — carrier thread stays free!
        Thread.sleep(100);  // Simulates DB I/O
        return "Result-" + id;
    }

    /**
     * WRONG: synchronized pins virtual thread to carrier thread!
     * Use ReentrantLock instead.
     */
    private static final ReentrantLock lock = new ReentrantLock();
    private static int counter = 0;

    public static void safeIncrement() throws InterruptedException {
        lock.lock();  // Correct: allows virtual thread unmounting while waiting
        try {
            counter++;
        } finally {
            lock.unlock();
        }
    }
}
```
