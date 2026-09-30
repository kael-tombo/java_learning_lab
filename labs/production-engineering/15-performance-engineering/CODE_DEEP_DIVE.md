# CODE DEEP DIVE: Mechanical Sympathy & Performance Patterns
## Lab 15 | Production Engineering Academy

---

## Pattern 1: Cache-Line Padded Volatile Atomic Counter (Zero False Sharing)

```java
package com.learning.production.lab15;

import java.lang.invoke.MethodHandles;
import java.lang.invoke.VarHandle;

/**
 * Padded counter occupying a minimum of 128 bytes to prevent False Sharing across L1/L2 cache lines.
 */
public class FalseSharingSafeCounter {
    // 56 bytes padding before value (7 * 8 bytes)
    public long p1, p2, p3, p4, p5, p6, p7;

    // Actual hot volatile counter
    public volatile long value = 0L;

    // 56 bytes padding after value
    public long p8, p9, p10, p11, p12, p13, p14;

    private static final VarHandle VALUE_HANDLE;

    static {
        try {
            VALUE_HANDLE = MethodHandles.lookup().findVarHandle(FalseSharingSafeCounter.class, "value", long.class);
        } catch (ReflectiveOperationException e) {
            throw new ExceptionInInitializerError(e);
        }
    }

    public void incrementRelaxed() {
        // Use Opaque or Release semantics when total ordering is not strictly required, avoiding full memory fence
        VALUE_HANDLE.setOpaque(this, (long) VALUE_HANDLE.getOpaque(this) + 1L);
    }

    public void add(long delta) {
        VALUE_HANDLE.getAndAdd(this, delta);
    }

    public long get() {
        return value;
    }
}
```

---

## Pattern 2: JMH (Java Microbenchmark Harness) Production Harness

```java
package com.learning.production.lab15;

import org.openjdk.jmh.annotations.*;
import org.openjdk.jmh.infra.Blackhole;
import org.openjdk.jmh.runner.Runner;
import org.openjdk.jmh.runner.options.Options;
import org.openjdk.jmh.runner.options.OptionsBuilder;

import java.util.concurrent.TimeUnit;

@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.NANOSECONDS)
@Warmup(iterations = 3, time = 1)
@Measurement(iterations = 5, time = 1)
@Fork(1)
@State(Scope.Thread)
public class BenchmarkMemoryAccess {

    private int[] array;

    @Setup
    public void setup() {
        array = new int[1_000_000];
        for (int i = 0; i < array.length; i++) array[i] = i;
    }

    // 1. Sequential Memory Access (CPU hardware prefetcher friendly - fast L1 hit)
    @Benchmark
    public void sequentialScan(Blackhole bh) {
        long sum = 0;
        for (int i = 0; i < array.length; i++) {
            sum += array[i];
        }
        bh.consume(sum);
    }

    // 2. Random Strided Access (Defeats CPU prefetcher - continuous L3/DRAM cache misses)
    @Benchmark
    public void randomStrideScan(Blackhole bh) {
        long sum = 0;
        int length = array.length;
        for (int i = 0; i < length; i++) {
            sum += array[(i * 1021) % length];
        }
        bh.consume(sum);
    }

    public static void main(String[] args) throws Exception {
        Options opt = new OptionsBuilder()
                .include(BenchmarkMemoryAccess.class.getSimpleName())
                .build();
        new Runner(opt).run();
    }
}
```
