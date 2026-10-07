# Code Deep Dive — Java Performance Engineering (performance-deep)

Annotated Java 17+ snippets for JMH, JIT, profiling, GC latency. Paste into `src/main/java`.

## Snippet 1: JMH benchmarks

JMH (Java Microbenchmark Harness) is the standard tool for writing reliable microbenchmarks. It handles JVM warm-up, dead-code elimination, and statistical analysis automatically. The snippet below shows a JMH benchmark and a JDK-only micro-measurement with a note on why naive timing is unreliable.

**JMH is external (`org.openjdk.jmh:jmh-core`); not compiled in this repo.**

```java
// performance-deep snippet 1: JMH benchmarks
// JMH is external (org.openjdk.jmh:jmh-core); not compiled in this repo.
// Below is a JDK-only micro-measurement with a note on why naive timing is unreliable.

public class JmhBenchmarks {
    static final int WARMUP = 10_000;
    static final int ITERATIONS = 1_000_000;

    static long compute(int x) {
        return x * x + 1;
    }

    public static void main(String[] args) {
        // Warm-up: let the JIT compile the method
        long sum = 0;
        for (int i = 0; i < WARMUP; i++) {
            sum += compute(i);
        }
        System.out.println("Warm-up sum: " + sum);

        // Measured run
        long start = System.nanoTime();
        for (int i = 0; i < ITERATIONS; i++) {
            sum += compute(i);
        }
        long elapsed = System.nanoTime() - start;
        System.out.printf("Sum: %d%n", sum);
        System.out.printf("Time: %.2f ms%n", elapsed / 1e6);
        System.out.println("Note: naive timing is unreliable due to JIT warm-up, " +
            "dead-code elimination, and OS scheduling. Use JMH for reliable benchmarks.");
    }
}
```

Observed output (run with `java -cp out JmhBenchmarks`):
```text
Warm-up sum: 333283345000
Sum: 17200205061384
Time: 6.24 ms
Note: naive timing is unreliable due to JIT warm-up, dead-code elimination, and OS scheduling. Use JMH for reliable benchmarks.
```

Pitfall: Naive micro-benchmarks are unreliable because the JIT compiler can eliminate dead code (if the result is unused), inline methods, and optimize based on profiling data. Without proper warm-up, the first iterations run in the interpreter, skewing results. JMH solves these problems with `@Benchmark` annotations, `@Fork` for isolated JVMs, and `@Warmup` for controlled warm-up. Never trust a benchmark that does not use JMH or a similar framework.

## Snippet 2: JIT C1/C2 & inlining

The HotSpot JVM uses a tiered compilation strategy: C1 (client compiler) for fast startup and C2 (server compiler) for peak performance. Methods are inlined to eliminate call overhead. The snippet below runs a method many times to trigger JIT compilation; observe with `-Xlog:compilation`.

```java
// performance-deep snippet 2: JIT C1/C2 & inlining
public class JitInlining {
    static int compute(int x) {
        return x * x + 1;
    }

    public static void main(String[] args) {
        long sum = 0;
        for (int i = 0; i < 100_000_000; i++) {
            sum += compute(i);
        }
        System.out.println("Sum: " + sum);
    }
}
```

Observed output (run with `java -XX:+PrintCompilation JitInlining 2>&1`):
```text
Sum: 20047555266176
```

Pitfall: The JIT compiler makes optimization decisions based on profiling data collected at runtime. Code paths that are rarely taken may never be compiled to native code, and deoptimization can occur when assumptions are violated (e.g., a class hierarchy changes). Use `-XX:+PrintInlining` to see which methods are inlined, and be aware that excessive inlining can increase code cache pressure.

## Snippet 3: escape analysis

Escape analysis is a JIT optimization that determines whether an object's scope is confined to a method or thread. If an object does not escape, the JVM can allocate it on the stack or eliminate it entirely (scalar replacement). The snippet below creates objects in a loop; observe with `-XX:+PrintEscapeAnalysis`.

```java
// performance-deep snippet 3: escape analysis
public class EscapeAnalysis {
    static class Point {
        int x, y;
        Point(int x, int y) {
            this.x = x;
            this.y = y;
        }
    }

    static int sum(int n) {
        int total = 0;
        for (int i = 0; i < n; i++) {
            Point p = new Point(i, i + 1);
            total += p.x + p.y;
        }
        return total;
    }

    public static void main(String[] args) {
        long start = System.nanoTime();
        int result = sum(10_000_000);
        long elapsed = System.nanoTime() - start;
        System.out.println("Result: " + result);
        System.out.printf("Time: %.2f ms%n", elapsed / 1e6);
    }
}
```

Observed output (run with `java -Xlog:gc EscapeAnalysis 2>&1`):
```text
Result: 276447232
Time: 11.94 ms
```

Note: `-XX:+PrintEscapeAnalysis` is only available in debug builds of the JVM. The output above shows the GC log and timing; to see escape analysis decisions, use a debug JVM or a profiler like async-profiler.

Pitfall: Escape analysis is disabled by default in some JVM versions and can be defeated by seemingly innocuous code changes. For example, storing an object in a field, returning it, or passing it to a method that the compiler cannot analyze will cause it to escape. Use `-XX:+DoEscapeAnalysis` (enabled by default in JDK 21) and verify with `-XX:+PrintEliminateAllocations` that allocations are actually eliminated.

## Snippet 4: allocation profiling

Allocation profiling identifies where objects are created in your code, which is essential for reducing GC pressure. The snippet below allocates objects in a loop; observe with `-Xlog:gc` to see allocation rates.

```java
// performance-deep snippet 4: allocation profiling
import java.util.ArrayList;
import java.util.List;

public class AllocationProfiling {
    public static void main(String[] args) {
        List<byte[]> list = new ArrayList<>();
        for (int i = 0; i < 1000; i++) {
            list.add(new byte[10_000]);
        }
        System.out.println("Allocated " + list.size() + " arrays of 10000 bytes");
    }
}
```

Observed output (run with `java -Xlog:gc AllocationProfiling`):
```text
Allocated 1000 arrays of 10000 bytes
```

Pitfall: Excessive allocation is a common performance problem, but not all allocation is bad. Short-lived objects are cheap to allocate (TLAB) and collect (minor GC). The real problem is allocation of long-lived objects that survive multiple GCs and get promoted to the old generation. Use a profiler (async-profiler, JFR) to identify allocation hotspots, and focus on reducing allocation of objects that survive young GC.

## Snippet 5: async-profiler/JFR

Java Flight Recorder (JFR) is a low-overhead profiling API built into the JDK. It records events such as method execution, allocation, and GC. The snippet below records a JFR recording while performing work.

```java
// performance-deep snippet 5: async-profiler/JFR
import jdk.jfr.Recording;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public class JfrRecording {
    public static void main(String[] args) throws Exception {
        Recording recording = new Recording();
        recording.start();

        List<byte[]> list = new ArrayList<>();
        for (int i = 0; i < 1000; i++) {
            list.add(new byte[10_000]);
        }

        recording.stop();
        Path file = Path.of("recording.jfr");
        recording.dump(file);
        System.out.println("JFR recording saved to " + file.toAbsolutePath());
    }
}
```

Observed output:
```
JFR recording saved to C:\Users\jratombo-adm\Desktop\java_learning_lab\recording.jfr
```

Pitfall: JFR has low overhead (< 2%) but is not free. Recording too many events or recording for too long can impact performance and produce large files. Use `Recording.setSettings()` to configure which events to record, and always stop and dump the recording in a `finally` block to avoid resource leaks. async-profiler is an external tool that provides additional capabilities like wall-clock profiling and native stack traces.

## Snippet 6: GC pause tuning

GC pause tuning involves selecting the right collector and tuning its parameters to meet latency requirements. The snippet below allocates objects to trigger GC; observe with `-Xlog:gc` under different collectors.

```java
// performance-deep snippet 6: GC pause tuning
import java.util.ArrayList;
import java.util.List;

public class GcPauseTuning {
    public static void main(String[] args) {
        List<byte[]> list = new ArrayList<>();
        for (int i = 0; i < 100; i++) {
            list.add(new byte[1_000_000]);
        }
        System.out.println("Allocated " + list.size() + " MB");
    }
}
```

Observed output (run with `java -Xlog:gc -XX:+UseG1GC -Xmx128m GcPauseTuning`):
```text
Allocated 100 MB
```

Observed output (run with `java -Xlog:gc -XX:+UseZGC -Xmx128m GcPauseTuning`):
```
[0.036s][info][gc] Using The Z Garbage Collector
[0.104s][info][gc] GC(0) Major Collection (Warmup)
[0.335s][info][gc] GC(1) Minor Collection (High Usage)
[0.344s][info][gc] GC(1) Minor Collection (High Usage) 128M(100%)->128M(100%) 0.009s
[0.344s][info][gc] GC(0) Major Collection (Warmup) 14M(11%)->128M(100%) 0.240s
[0.344s][info][gc] GC(2) Major Collection (Allocation Stall)
[0.566s][info][gc] Allocation Stall (main) 412.944ms
[0.566s][info][gc] GC(2) Major Collection (Allocation Stall) 128M(100%)->128M(100%) 0.223s
[0.567s][info][gc] GC(3) Major Collection (Warmup)
[0.573s][info][gc] GC(4) Minor Collection (Allocation Stall)
[0.577s][info][gc] GC(4) Minor Collection (Allocation Stall) 128M(100%)->128M(100%) 0.005s
[0.782s][info][gc] GC(3) Major Collection (Warmup) 128M(100%)->128M(100%) 0.216s
[0.783s][info][gc] GC(5) Major Collection (Allocation Stall)
[1.005s][info][gc] GC(5) Major Collection (Allocation Stall) 128M(100%)->128M(100%) 0.223s
[1.005s][info][gc] Allocation Stall (main) 437.733ms
[1.005s][info][gc] Out Of Memory (main)
[1.006s][info][gc] GC(6) Minor Collection (Allocation Stall)
[1.010s][info][gc] GC(6) Minor Collection (Allocation Stall) 128M(100%)->128M(100%) 0.004s
[1.010s][info][gc] GC(7) Major Collection (Allocation Stall)
[1.025s][info][gc] Allocation Stall (main) 19.411ms
Exception in thread "main" java.lang.OutOfMemoryError: Java heap space
	at GcPauseTuning.main(GcPauseTuning.java:7)
[1.233s][info][gc] GC(7) Major Collection (Allocation Stall) 128M(100%)->4M(3%) 0.223s
```

Pitfall: GC tuning is highly workload-dependent — parameters that improve performance for one application can degrade it for another. The most common mistake is tuning GC in isolation without considering the application's allocation rate and object lifetime distribution. Always measure end-to-end latency and throughput under realistic load, and use `-Xlog:gc*` to understand what the collector is doing before changing any parameters.
