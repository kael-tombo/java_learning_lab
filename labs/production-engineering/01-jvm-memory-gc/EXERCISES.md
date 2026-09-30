# EXERCISES: JVM Memory & GC Engineering
## Lab 01 | Production Engineering Academy

---

## Exercise 1: Triage and Fix the Leaking Cache (Hands-On Lab)

### Objective
Identify the root cause of a reproducing OutOfMemoryError, extract a heap dump, inspect the Dominator Tree, and refactor the code to production-grade resilience.

### Scenario Code
You are provided with the following service simulating an active order cache:

```java
package com.learning.production.lab01;

import java.util.*;
import java.util.concurrent.*;

public class LeakingOrderService {
    // Problematic structure
    private static final Map<String, List<OrderPayload>> ORDER_HISTORY = new HashMap<>();

    public record OrderPayload(String orderId, byte[] rawPayload, long timestamp) {}

    public synchronized void recordOrder(String customerId, String orderId, byte[] data) {
        List<OrderPayload> orders = ORDER_HISTORY.computeIfAbsent(customerId, k -> new ArrayList<>());
        orders.add(new OrderPayload(orderId, data, System.currentTimeMillis()));
    }

    public static void main(String[] args) throws InterruptedException {
        LeakingOrderService service = new LeakingOrderService();
        System.out.println("Starting workload. Monitor with jcmd or VisualVM...");
        
        Random random = new Random();
        for (long i = 0; i < 10_000_000; i++) {
            String customerId = "CUST-" + (i % 100_000); // 100k distinct customers
            String orderId = UUID.randomUUID().toString();
            byte[] payload = new byte[4096]; // 4 KB payload
            service.recordOrder(customerId, orderId, payload);
            
            if (i % 1000 == 0) {
                Thread.sleep(1);
            }
        }
    }
}
```

### Tasks
1. Run the application with restricted heap:
   ```bash
   java -Xmx256m -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=./leak.hprof com.learning.production.lab01.LeakingOrderService
   ```
2. Observe the crash: note how quickly Eden/Old fills up and examine the generated `leak.hprof`.
3. Use `jcmd <PID> GC.class_histogram` before the crash to identify top retained objects.
4. Refactor `LeakingOrderService` using `Caffeine` with:
   - Maximum size: 10,000 entries.
   - Expiration: Expire after write in 10 minutes.
   - Use soft references for payloads if memory pressure spikes.
5. Re-run and verify that the application runs indefinitely under 256MB heap without OOM.

---

## Exercise 2: GC Comparison Benchmark (G1 vs ZGC)

### Objective
Measure latency and throughput differences between G1GC and Generational ZGC under an allocation-intensive web simulation.

### Benchmark Harness
```java
package com.learning.production.lab01;

import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;

public class GcBenchmarkHarness {
    private static final int THREADS = 8;
    private static final int DURATION_SECONDS = 30;

    public static void main(String[] args) throws Exception {
        ExecutorService executor = Executors.newFixedThreadPool(THREADS);
        AtomicLong allocationCounter = new AtomicLong();
        long deadline = System.currentTimeMillis() + (DURATION_SECONDS * 1000L);

        System.out.println("Running benchmark for " + DURATION_SECONDS + "s...");
        for (int i = 0; i < THREADS; i++) {
            executor.submit(() -> {
                while (System.currentTimeMillis() < deadline) {
                    // Short-lived allocations (95%)
                    byte[] shortLived = new byte[1024]; 
                    // Medium-lived allocations (5%)
                    if (System.nanoTime() % 20 == 0) {
                        byte[] med = new byte[65536];
                    }
                    allocationCounter.incrementAndGet();
                }
            });
        }

        executor.shutdown();
        executor.awaitTermination(40, TimeUnit.SECONDS);
        System.out.printf("Total allocations completed: %,d operations%n", allocationCounter.get());
    }
}
```

### Execution Steps
1. Run with **G1GC** with unified logging:
   ```bash
   java -Xms2g -Xmx2g -XX:+UseG1GC -Xlog:gc*,gc+phases=debug:file=g1-gc.log:time,uptime,pid:filecount=5,filesize=100m com.learning.production.lab01.GcBenchmarkHarness
   ```
2. Run with **Generational ZGC** (Java 21+):
   ```bash
   java -Xms2g -Xmx2g -XX:+UseZGC -XX:+ZGenerational -Xlog:gc*:file=zgc.log:time,uptime,pid:filecount=5,filesize=100m com.learning.production.lab01.GcBenchmarkHarness
   ```
3. Parse the logs:
   - Identify max pause time in `g1-gc.log` vs `zgc.log`.
   - Calculate total pause time (STW duration) across the 30-second run.
   - Compare operations completed per second.

---

## Exercise 3: Direct Memory / Off-Heap Leak Investigation

### Scenario
An application uses Netty `ByteBuf` or `ByteBuffer.allocateDirect()` for gRPC serialization. The JVM crashes with:
`java.lang.OutOfMemoryError: Direct buffer memory`
even though heap utilization is only 15%.

### Tasks
1. Enable Native Memory Tracking (NMT):
   ```bash
   -XX:NativeMemoryTracking=detail
   ```
2. Establish an NMT baseline during warm-up:
   ```bash
   jcmd <PID> VM.native_memory baseline
   ```
3. After 15 minutes of load, run:
   ```bash
   jcmd <PID> VM.native_memory detail.diff
   ```
4. Analyze the diff output:
   - Identify which memory category grew (`Internal`, `Other`, `Arena`, or `Thread`).
   - Pinpoint the exact stack trace allocating native memory.
   - Implement reference tracking to ensure all `ByteBuf` allocations call `ReferenceCountUtil.release()`.
