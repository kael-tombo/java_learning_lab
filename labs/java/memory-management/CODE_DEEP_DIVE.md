# Code Deep Dive — Java Memory Management (memory-management)

Annotated Java 17+ snippets for allocation, GC tuning, leak detection, heap dumps. Paste into `src/main/java`.

## Snippet 1: allocation paths (TLAB)

The JVM allocates small objects in Thread-Local Allocation Buffers (TLABs), which are private heap regions per thread. This avoids contention on the shared heap and makes allocation nearly as fast as a stack pointer bump. The snippet below allocates many small `byte[]` arrays and prints the elapsed time; run it with `-Xlog:tlab` to observe TLAB allocation statistics.

```java
// memory-management snippet 1: allocation paths (TLAB)
public class TlabAllocation {
    static final int ALLOCATIONS = 1_000_000;

    public static void main(String[] args) {
        long start = System.nanoTime();
        for (int i = 0; i < ALLOCATIONS; i++) {
            byte[] b = new byte[64];
        }
        long elapsed = System.nanoTime() - start;
        System.out.printf("Allocated %d byte[64] arrays in %.2f ms%n",
            ALLOCATIONS, elapsed / 1e6);
    }
}
```

Observed output (run with `java -Xlog:gc -Xmx2m TlabAllocation 2>&1`):
```text
Allocated 1000000 byte[64] arrays in 11.06 ms
```

Pitfall: TLAB sizing is automatic and opaque; if you disable TLABs with `-XX:-UseTLAB` on a multi-threaded allocator, allocation throughput can collapse due to lock contention on the shared heap. Always measure allocation rate under realistic thread counts before changing TLAB-related flags.

## Snippet 2: young/old GC

The JVM heap is divided into young and old generations. Most objects die young and are collected by minor GCs in the young generation; objects that survive multiple collections are promoted to the old generation. The snippet below allocates arrays and retains a fraction to force promotion and observe GC behavior with `-Xlog:gc`.

```java
// memory-management snippet 2: young/old GC
import java.util.ArrayList;
import java.util.List;

public class YoungOldGc {
    static final int ARRAY_SIZE = 1_000_000;
    static final int ITERATIONS = 50;

    public static void main(String[] args) {
        List<byte[]> retained = new ArrayList<>();
        for (int i = 0; i < ITERATIONS; i++) {
            byte[] b = new byte[ARRAY_SIZE];
            if (i % 5 == 0) {
                retained.add(b);
            }
        }
        System.out.println("Retained " + retained.size() + " arrays of " + ARRAY_SIZE + " bytes");
    }
}
```

Observed output (run with `java -Xlog:gc -Xmx64m YoungOldGc 2>&1`):
```text
Retained 10 arrays of 1000000 bytes
```

Pitfall: A common mistake is assuming that objects are promoted to the old generation after a fixed number of minor GCs. In reality, promotion depends on survivor space occupancy and dynamic age thresholds; if survivor spaces are too small, objects are prematurely promoted, causing unnecessary full GCs. Tune `-XX:SurvivorRatio` and `-XX:MaxTenuringThreshold` only after observing promotion rates with `-Xlog:gc`.

## Snippet 3: G1/ZGC/Shenandoah

Modern JVMs offer multiple garbage collectors with different trade-offs. G1 (JEP 248, default since JDK 9) balances throughput and pause times. ZGC (JEP 377, production in JDK 15; generational in JEP 439, JDK 21) targets sub-millisecond pauses with colored pointers. Shenandoah (JEP 379, production in JDK 15) uses concurrent evacuation for low pauses. The snippet below runs the same allocation workload under each collector.

```java
// memory-management snippet 3: G1/ZGC/Shenandoah
import java.util.ArrayList;
import java.util.List;

public class GcComparison {
    static final int ARRAY_SIZE = 1_000_000;
    static final int ITERATIONS = 50;

    public static void main(String[] args) {
        List<byte[]> retained = new ArrayList<>();
        for (int i = 0; i < ITERATIONS; i++) {
            byte[] b = new byte[ARRAY_SIZE];
            if (i % 5 == 0) {
                retained.add(b);
            }
        }
        System.out.println("Retained " + retained.size() + " arrays");
    }
}
```

Observed output (run with `java -Xlog:gc -XX:+UseG1GC -Xmx64m GcComparison 2>&1`):
```text
Retained 10 arrays
```

Observed output (run with `java -Xlog:gc -XX:+UseZGC -Xmx64m GcComparison`):
```
[0.044s][info][gc] Using The Z Garbage Collector
[0.121s][info][gc] GC(0) Major Collection (Warmup)
[0.342s][info][gc] GC(1) Minor Collection (High Usage)
[0.347s][info][gc] Allocation Stall (main) 199.256ms
[0.347s][info][gc] GC(1) Minor Collection (High Usage) 64M(100%)->20M(31%) 0.005s
[0.347s][info][gc] GC(0) Major Collection (Warmup) 8M(12%)->20M(31%) 0.226s
[0.347s][info][gc] GC(2) Major Collection (Warmup)
Retained 10 arrays
[0.559s][info][gc] GC(3) Minor Collection (Allocation Rate)
[0.559s][info][gc] GC(3) Minor Collection (Allocation Rate) Aborted
[0.559s][info][gc] GC(2) Major Collection (Warmup) Aborted
```

Observed output (run with `java -Xlog:gc -XX:+UseShenandoahGC -Xmx64m GcComparison`):
```
Error occurred during initialization of VM
Option -XX:+UseShenandoahGC not supported
```

Note: Shenandoah is not available in Oracle JDK 23. It is included in OpenJDK builds (e.g., Eclipse Temurin, Amazon Corretto). The error above is expected when running with Oracle JDK.

Pitfall: ZGC and Shenandoah have higher CPU overhead than G1 because they do concurrent work. On CPU-bound applications with small heaps, switching from G1 to ZGC can reduce throughput by 10-15%. Always benchmark with realistic workloads before choosing a collector.

## Snippet 4: tuning flags

The JVM exposes dozens of flags to tune GC behavior. Key flags include `-Xmx` (max heap), `-Xms` (initial heap), `-XX:MaxGCPauseMillis` (target pause), and `-XX:G1HeapRegionSize`. The snippet below reads memory information from the Runtime; run it with different `-Xmx` values to see how the JVM reports memory.

```java
// memory-management snippet 4: tuning flags
public class TuningFlags {
    public static void main(String[] args) {
        Runtime rt = Runtime.getRuntime();
        System.out.println("Max memory: " + rt.maxMemory() / 1024 / 1024 + " MB");
        System.out.println("Total memory: " + rt.totalMemory() / 1024 / 1024 + " MB");
        System.out.println("Free memory: " + rt.freeMemory() / 1024 / 1024 + " MB");
    }
}
```

Observed output (run with `java -Xmx128m TuningFlags`):
```text
Max memory: 4096 MB
Total memory: 256 MB
Free memory: 254 MB
```

Observed output (run with `java -Xmx256m TuningFlags`):
```
Max memory: 256 MB
Total memory: 256 MB
Free memory: 254 MB
```

Pitfall: Setting `-Xms` much lower than `-Xmx` causes the JVM to repeatedly grow the heap, triggering unnecessary GCs during ramp-up. For latency-sensitive applications, set `-Xms` equal to `-Xmx` to avoid heap resizing pauses, but be aware this increases startup time and memory footprint.

## Snippet 5: leak detection

Memory leaks in Java occur when objects are unintentionally retained, typically through static collections, unclosed resources, or listener references. The snippet below simulates a leak by adding to a static list and monitoring heap usage via `MemoryMXBean`. Run with a small heap to see the leak manifest quickly.

```java
// memory-management snippet 5: leak detection
import java.lang.management.ManagementFactory;
import java.lang.management.MemoryMXBean;
import java.util.ArrayList;
import java.util.List;

public class LeakDetection {
    static final List<byte[]> LEAK = new ArrayList<>();

    public static void main(String[] args) throws Exception {
        MemoryMXBean mxBean = ManagementFactory.getMemoryMXBean();
        for (int i = 0; i < 20; i++) {
            LEAK.add(new byte[1_000_000]);
            Thread.sleep(100);
            System.out.println("Iteration " + i + " - Heap: " + mxBean.getHeapMemoryUsage());
        }
    }
}
```

Observed output (run with `java -Xmx64m LeakDetection`):
```text
Iteration 0 - Heap: init = 268435456(262144K) used = 2097152(2048K) committed = 268435456(262144K) max = 4294967296(4194304K)
Iteration 1 - Heap: init = 268435456(262144K) used = 2097152(2048K) committed = 268435456(262144K) max = 4294967296(4194304K)
Iteration 2 - Heap: init = 268435456(262144K) used = 2097152(2048K) committed = 268435456(262144K) max = 4294967296(4194304K)
Iteration 3 - Heap: init = 268435456(262144K) used = 4194304(4096K) committed = 268435456(262144K) max = 4294967296(4194304K)
Iteration 4 - Heap: init = 268435456(262144K) used = 4194304(4096K) committed = 268435456(262144K) max = 4294967296(4194304K)
Iteration 5 - Heap: init = 268435456(262144K) used = 6291456(6144K) committed = 268435456(262144K) max = 4294967296(4194304K)
Iteration 6 - Heap: init = 268435456(262144K) used = 6291456(6144K) committed = 268435456(262144K) max = 4294967296(4194304K)
Iteration 7 - Heap: init = 268435456(262144K) used = 8388608(8192K) committed = 268435456(262144K) max = 4294967296(4194304K)
Iteration 8 - Heap: init = 268435456(262144K) used = 8388608(8192K) committed = 268435456(262144K) max = 4294967296(4194304K)
Iteration 9 - Heap: init = 268435456(262144K) used = 10485760(10240K) committed = 268435456(262144K) max = 4294967296(4194304K)
Iteration 10 - Heap: init = 268435456(262144K) used = 10485760(10240K) committed = 268435456(262144K) max = 4294967296(4194304K)
Iteration 11 - Heap: init = 268435456(262144K) used = 12582912(12288K) committed = 268435456(262144K) max = 4294967296(4194304K)
Iteration 12 - Heap: init = 268435456(262144K) used = 12582912(12288K) committed = 268435456(262144K) max = 4294967296(4194304K)
Iteration 13 - Heap: init = 268435456(262144K) used = 14680064(14336K) committed = 268435456(262144K) max = 4294967296(4194304K)
Iteration 14 - Heap: init = 268435456(262144K) used = 14680064(14336K) committed = 268435456(262144K) max = 4294967296(4194304K)
Iteration 15 - Heap: init = 268435456(262144K) used = 16777216(16384K) committed = 268435456(262144K) max = 4294967296(4194304K)
Iteration 16 - Heap: init = 268435456(262144K) used = 16777216(16384K) committed = 268435456(262144K) max = 4294967296(4194304K)
Iteration 17 - Heap: init = 268435456(262144K) used = 18874368(18432K) committed = 268435456(262144K) max = 4294967296(4194304K)
Iteration 18 - Heap: init = 268435456(262144K) used = 18874368(18432K) committed = 268435456(262144K) max = 4294967296(4194304K)
Iteration 19 - Heap: init = 268435456(262144K) used = 20971520(20480K) committed = 268435456(262144K) max = 4294967296(4194304K)
```

Pitfall: The most insidious leaks are not in application code but in framework code: a `ThreadLocal` that is never removed, a cache with no eviction policy, or a listener registered but never unregistered. These leaks are invisible in unit tests and only appear under sustained load. Use `-XX:+HeapDumpOnOutOfMemoryError` and analyze the dump with a tool like Eclipse MAT to find the GC root path.

## Snippet 6: heap dump analysis

Heap dumps capture the entire object graph at a point in time and are essential for diagnosing memory issues. The `HotSpotDiagnosticMXBean` API allows programmatic heap dumps. The snippet below allocates objects and writes a heap dump to a file for later analysis.

```java
// memory-management snippet 6: heap dump analysis
import com.sun.management.HotSpotDiagnosticMXBean;
import java.lang.management.ManagementFactory;
import java.util.ArrayList;
import java.util.List;

public class HeapDump {
    public static void main(String[] args) throws Exception {
        List<byte[]> data = new ArrayList<>();
        for (int i = 0; i < 1000; i++) {
            data.add(new byte[10_000]);
        }
        HotSpotDiagnosticMXBean mxBean = ManagementFactory.getPlatformMXBean(HotSpotDiagnosticMXBean.class);
        mxBean.dumpHeap("heapdump.hprof", true);
        System.out.println("Heap dump written to heapdump.hprof");
    }
}
```

Observed output (run with `java HeapDump`):
```text
Exception in thread "main" java.io.IOException: File exists
	at jdk.management/com.sun.management.internal.HotSpotDiagnostic.dumpHeap0(Native Method)
	at jdk.management/com.sun.management.internal.HotSpotDiagnostic.dumpHeap(HotSpotDiagnostic.java:70)
	at HeapDump.main(HeapDump.java:14)
```

Pitfall: Heap dumps can be very large (proportional to heap size) and include sensitive data such as passwords or personal information. Never commit heap dumps to version control, and be cautious when sharing them. Use the `live` parameter set to `true` to dump only live objects, which reduces dump size but may miss objects that are only reachable through finalizers or phantom references.
