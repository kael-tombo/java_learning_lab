# HANDS-ON LAB EXERCISES: Production Diagnostics & Profiling
## Lab 03 | Production Engineering Academy — Top 0.0001% Engineering

---

## Exercise 1: Pinpoint the Catastrophic Regex Backtracking 100% CPU Bug

### Objective
Diagnose a CPU spike causing 100% core saturation in a web worker using native thread IDs (`TID`), hexadecimal conversion, `jcmd Thread.print`, and flamegraphs.

### The Broken Code
```java
package com.learning.production.lab03;

import java.util.regex.Pattern;

public class RegexCpuSpikeSimulator {
    // Evil Regex: Nested quantifiers cause 2^N catastrophic backtracking
    private static final Pattern EVIL_REGEX = Pattern.compile("^([a-zA-Z0-9]+)+$");

    public static void main(String[] args) {
        long pid = ProcessHandle.current().pid();
        System.out.println(">>> Starting Regex CPU Spike Simulator. PID: " + pid);

        // A 32-character string ending in an invalid character '!' forces the NFA engine
        // to evaluate billions of permutation branches before failing:
        String maliciousPayload = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!";

        Runnable task = () -> {
            System.out.println("Executing regex validation on thread: " + Thread.currentThread().getName());
            boolean matches = EVIL_REGEX.matcher(maliciousPayload).matches();
            System.out.println("Result: " + matches);
        };

        Thread thread = new Thread(task, "worker-regex-validator-01");
        thread.start();
    }
}
```

### Lab Instructions & Step-by-Step Triage
1. **Run the Simulator**:
   ```bash
   java -cp target/classes com.learning.production.lab03.RegexCpuSpikeSimulator
   ```
   Notice that one CPU core immediately locks at $100\%$ utilization.
2. **Find the Offending Thread in Another Terminal**:
   ```bash
   PID=$(pgrep -f RegexCpuSpikeSimulator)
   top -b -n 1 -H -p $PID | head -n 15
   ```
   Note the `TID` with $99.9\%$ CPU.
3. **Convert TID to Hexadecimal**:
   ```bash
   printf "0x%x\n" <TID>
   ```
4. **Capture Thread Dump and Locate the Culprit**:
   ```bash
   jcmd $PID Thread.print > /tmp/threaddump.txt
   grep -A 25 "nid=0x<hex_tid>" /tmp/threaddump.txt
   ```
   *Observation*: The stack trace points directly to `java.util.regex.Pattern$GroupCurly.match0()`.
5. **Implement the Fix**:
   Replace nested quantifiers with possessive quantifiers (`++`) or non-backtracking DFA engines (Google Re2j):
   ```java
   private static final Pattern SAFE_REGEX = Pattern.compile("^[a-zA-Z0-9]++$");
   ```
6. **Re-run the Benchmark**: Verify execution completes in $< 1\text{ms}$.

---

## Exercise 2: Flamegraph Analysis of Lock Contention

### Objective
Measure severe thread lock contention under 64 concurrent threads using `async-profiler`'s `-e lock` mode, and eliminate the bottleneck using atomic striping.

### The Broken Lock Contention Harness
```java
package com.learning.production.lab03;

import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;

public class LockContentionHarness {
    private static final Object GLOBAL_MONITOR = new Object();
    private static long globalCounter = 0;

    // The Contended Method
    public static void incrementShared() {
        synchronized (GLOBAL_MONITOR) {
            // Simulated micro-work
            globalCounter++;
            try {
                Thread.sleep(0, 1000); // 1 microsecond wait inside critical section
            } catch (InterruptedException ignored) {}
        }
    }

    public static void main(String[] args) throws Exception {
        int threads = 64;
        ExecutorService executor = Executors.newFixedThreadPool(threads);
        System.out.println("Running Lock Contention Harness. PID: " + ProcessHandle.current().pid());

        for (int i = 0; i < threads; i++) {
            executor.submit(() -> {
                while (!Thread.currentThread().isInterrupted()) {
                    incrementShared();
                }
            });
        }
    }
}
```

### Lab Instructions:
1. Start `LockContentionHarness`.
2. Attach `async-profiler` to capture lock wait events:
   ```bash
   asprof -e lock -d 15 -f /tmp/lock_contention.html $(pgrep -f LockContentionHarness)
   ```
3. Open `/tmp/lock_contention.html` in a web browser. Observe the massive flame plateau on `LockContentionHarness.incrementShared`.
4. Refactor `globalCounter` to use `java.util.concurrent.atomic.LongAdder`:
   ```java
   private static final LongAdder modernCounter = new LongAdder();
   public static void incrementOptimized() {
       modernCounter.increment();
   }
   ```
5. Re-profile: Verify lock contention drops to **0.00%**, and throughput increases by $> 50\times$.

---

## Exercise 3: Off-Heap DirectByteBuffer Leak Diagnosis with NMT

### Objective
Simulate a native off-heap memory leak that bypasses JVM garbage collection, and track its exact allocation source using Native Memory Tracking (NMT) baselining.

### The Leaking Off-Heap Simulator
```java
package com.learning.production.lab03;

import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.List;

public class OffHeapLeakSimulator {
    // Retaining direct byte buffers off-heap
    private static final List<ByteBuffer> LEAKED_BUFFERS = new ArrayList<>();

    public static void main(String[] args) throws Exception {
        System.out.println("Off-Heap Leak Simulator running. PID: " + ProcessHandle.current().pid());

        while (true) {
            // Allocate 10MB of native off-heap memory per second
            ByteBuffer directBuffer = ByteBuffer.allocateDirect(10 * 1024 * 1024);
            LEAKED_BUFFERS.add(directBuffer);
            Thread.sleep(1000);
        }
    }
}
```

### Lab Instructions:
1. Run with NMT enabled:
   ```bash
   java -XX:NativeMemoryTracking=detail -XX:MaxDirectMemorySize=2g \
        -cp target/classes com.learning.production.lab03.OffHeapLeakSimulator
   ```
2. Establish NMT baseline after 5 seconds:
   ```bash
   PID=$(pgrep -f OffHeapLeakSimulator)
   jcmd $PID VM.native_memory baseline
   ```
3. Wait 30 seconds for 300MB of native allocations, then run NMT diff:
   ```bash
   jcmd $PID VM.native_memory detail.diff
   ```
4. **Analyze Output**:
   Observe the `Internal` section showing:
   ```
   -                    Internal (reserved=312450KB +307200KB, committed=312450KB +307200KB)
                                (malloc=312450KB #30 +30)
   ```
   This proves the leak is native `DirectByteBuffer` rather than Java heap!

---

## Exercise 4: Safepoint Time-To-Safepoint (TTSP) Stall Reproduction

### Objective
Demonstrate how an unrolled counted loop without safepoints stalls the entire JVM during garbage collection or thread dumps, and fix it using safepoint compiler flags.

### The Code
```java
package com.learning.production.lab03;

public class SafepointStallSimulator {
    public static void main(String[] args) {
        System.out.println("Safepoint Stall Simulator running. PID: " + ProcessHandle.current().pid());

        // Worker thread executing an uncounted loop that C2 JIT compiles without safepoints
        new Thread(() -> {
            long sum = 0;
            while (true) {
                // Counted loop that JIT C2 unrolls without safepoint checks
                for (int i = 0; i < Integer.MAX_VALUE; i++) {
                    sum += i;
                }
            }
        }, "long-loop-worker").start();

        // Harmless reporter thread trying to print timestamp
        new Thread(() -> {
            while (true) {
                try {
                    Thread.sleep(1000);
                    System.out.println("Heartbeat: " + System.currentTimeMillis());
                } catch (InterruptedException ignored) {}
            }
        }, "heartbeat-worker").start();
    }
}
```

### Lab Instructions:
1. Run with safepoint logging enabled:
   ```bash
   java -Xlog:safepoint=debug -cp target/classes com.learning.production.lab03.SafepointStallSimulator
   ```
2. In another terminal, trigger a thread dump via `jcmd <PID> Thread.print`.
3. Notice that `Thread.print` stalls for several seconds, and check `safepoint=debug` output:
   - Observe `Time to safepoint: 2480 ms` (TTSP stall).
4. Restart with:
   ```bash
   java -XX:+UseCountedLoopSafepoints -Xlog:safepoint=debug ...
   ```
5. Re-run `jcmd <PID> Thread.print`: Observe TTSP immediately drops to $< 5\text{ms}$.
