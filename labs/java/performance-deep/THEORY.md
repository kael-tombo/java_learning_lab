# THEORY — Performance Deep Dive

## Overview

Java performance engineering: profiling, JIT optimization, GC tuning, concurrency, and benchmarking.

---

## Profiling Methodology

### USE Method (Utilization, Saturation, Errors)

```
Utilization: % resource busy (CPU, disk, network)
Saturation:  Queue length, wait time (GC pause, lock contention)
Errors:      Error rate (exceptions, timeouts, retries)
```

### RED Method (Rate, Errors, Duration)

```
Rate:        Requests per second
Errors:      Failed requests per second
Duration:    Latency distribution (p50, p95, p99, max)
```

---

## CPU Profiling

### Sampling vs Instrumentation

| Aspect | Sampling (async-profiler) | Instrumentation (JFR) |
|--------|---------------------------|----------------------|
| Overhead | ~1-2% | ~5-15% |
| Accuracy | Statistical | Exact |
| Safe points | Not required | Required |
| Production | Yes | Yes (with care) |

### async-profiler

```bash
# CPU profiling (perf events)
./profiler.sh -d 60 -f cpu.html <pid>

# Allocation profiling
./profiler.sh -d 60 -e alloc -f alloc.html <pid>

# Lock contention
./profiler.sh -d 60 -e lock -f lock.html <pid>

# Wall clock (includes blocked)
./profiler.sh -d 60 -e wall -f wall.html <pid>
```

### JFR (Java Flight Recorder)

```bash
# Continuous recording
-XX:StartFlightRecording=maxsize=250m,maxage=1d,name=continuous,settings=profile

# Event-specific
-XX:StartFlightRecording=duration=60s,filename=recording.jfr,settings=profile
```

### Key JFR Events

| Event | Purpose |
|-------|---------|
| `jdk.CPULoad` | CPU utilization |
| `jdk.ThreadSleep` | Thread blocking |
| `jdk.MonitorEnter` | Lock contention |
| `jdk.JavaMonitorEnter` | synchronized contention |
| `jdk.GCPhasePause` | GC pauses |
| `jdk.ObjectAllocationInNewTLAB` | Allocation sites |

---

## JIT Optimization

### Tiered Compilation

```
Tier 0: Interpreter (profiling)
    ↓ ~1000 invocations
Tier 1: C1 (client) - simple opts
    ↓ ~5000 invocations  
Tier 2: C1 + profiling
    ↓ ~10000 invocations
Tier 3: C2 (server) - aggressive opts
    ↓ ~15000 invocations
Tier 4: C2 + profiling
```

### Key Optimizations

```bash
# Inlining
-XX:MaxInlineSize=35          # Bytecode size limit
-XX:FreqInlineSize=325        # Hot method limit
-XX:MaxRecursiveInlineLevel=1
-XX:MaxInlineLevel=9

# Escape Analysis
-XX:+DoEscapeAnalysis         # Enable (default)
-XX:+EliminateLocks           # Lock elision
-XX:+EliminateAllocations     # Scalar replacement

# Loop Optimizations
-XX:+UseLoopPredication
-XX:+RangeCheckElimination

# Deoptimization
-XX:+PrintDeoptimizationDetails
```

### Inlining Decision

```
Monomorphic call site → Inline
Bimorphic (2 targets) → Inline both with guard
Megamorphic (3+) → No inline (invokeinterface)
```

### Profile Pollution

```java
// Bad: Megamorphic call site
interface Processor { void process(Data d); }
class JsonProcessor implements Processor { ... }
class XmlProcessor implements Processor { ... }
class CsvProcessor implements Processor { ... }

Processor p = getProcessor(); // Many implementations
p.process(data); // Megamorphic

// Better: Separate methods or visitor pattern
void processJson(JsonData d) { ... }
void processXml(XmlData d) { ... }
```

---

## GC Tuning

### Choosing Collector

| Workload | Collector |
|----------|-----------|
| Batch, throughput | Parallel |
| Low latency, < 4GB | G1 |
| Low latency, > 4GB | ZGC |
| Low latency, huge heap | Shenandoah |
| Predictable pauses | ZGC/Shenandoah |

### G1 Tuning

```bash
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200        # Pause target
-XX:G1HeapRegionSize=16m        # Region size (1-32MB)
-XX:InitiatingHeapOccupancyPercent=45  # Concurrent mark trigger
-XX:G1MixedGCCountTarget=8      # Mixed GCs per cycle
-XX:G1MixedGCLiveThresholdPercent=85  # Region liveness threshold
```

### ZGC Tuning

```bash
-XX:+UseZGC
-XX:ZCollectionInterval=10      # Min interval (ms)
-XX:ZAllocationSpikeTolerance=2.0  # Headroom factor
-XX:+ZGenerational              # Java 21+ generational
```

### GC Logging

```bash
# Unified logging (Java 9+)
-Xlog:gc*:file=gc.log:time,uptime,level,tags:filecount=10,filesize=50m

# Key tags: gc, gc+heap, gc+phases, gc+ref, gc+age
```

---

## Concurrency Performance

### Lock Contention

```java
// Reduce lock scope
synchronized(lock) {
    // Minimal work
}

// Use striped locks
Striped<Lock> stripes = Striped.lazyWeakLock(32);
Lock lock = stripes.get(key);
lock.lock();
try { ... } finally { lock.unlock(); }

// Use ConcurrentHashMap
ConcurrentHashMap<K, V> map = new ConcurrentHashMap<>();
map.computeIfAbsent(key, k -> expensiveCompute(k));

// Use LongAdder for counters
LongAdder counter = new LongAdder();
counter.increment();
```

### Thread Pools

```java
// CPU-bound: fixed size = cores
ExecutorService cpuPool = Executors.newFixedThreadPool(
    Runtime.getRuntime().availableProcessors()
);

// I/O-bound: virtual threads (Java 21+)
ExecutorService ioPool = Executors.newVirtualThreadPerTaskExecutor();

// Custom
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    coreSize, maxSize, 60L, TimeUnit.SECONDS,
    new LinkedBlockingQueue<>(),
    new ThreadFactoryBuilder().setNameFormat("worker-%d").build(),
    new ThreadPoolExecutor.AbortPolicy()
);
```

### False Sharing

```java
// Bad: Adjacent fields on same cache line
class Counter {
    volatile long count1;
    volatile long count2; // False sharing with count1
}

// Good: Padding
class Counter {
    volatile long count1;
    long p1, p2, p3, p4, p5, p6, p7; // 56 bytes padding
    volatile long count2;
}

// Or @Contended (JDK internal)
@jdk.internal.vm.annotation.Contended
class Counter {
    volatile long count1;
    volatile long count2;
}
```

---

## Benchmarking (JMH)

### Setup

```xml
<dependency>
    <groupId>org.openjdk.jmh</groupId>
    <artifactId>jmh-core</artifactId>
    <version>1.37</version>
</dependency>
<dependency>
    <groupId>org.openjdk.jmh</groupId>
    <artifactId>jmh-generator-annprocess</artifactId>
    <version>1.37</version>
</dependency>
```

### Benchmark Template

```java
@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.NANOSECONDS)
@Warmup(iterations = 3, time = 1, timeUnit = TimeUnit.SECONDS)
@Measurement(iterations = 5, time = 1, timeUnit = TimeUnit.SECONDS)
@Fork(value = 3, jvmArgs = {"-Xms2g", "-Xmx2g"})
@State(Scope.Benchmark)
public class MyBenchmark {
    
    @Param({"100", "1000", "10000"})
    int size;
    
    List<String> data;
    
    @Setup
    public void setup() {
        data = generateData(size);
    }
    
    @Benchmark
    public int baseline(Blackhole bh) {
        int sum = 0;
        for (String s : data) {
            sum += s.length();
        }
        bh.consume(sum);
        return sum;
    }
    
    @Benchmark
    public int stream(Blackhole bh) {
        int sum = data.stream().mapToInt(String::length).sum();
        bh.consume(sum);
        return sum;
    }
}
```

### Running

```bash
# Compile
mvn clean install

# Run
java -jar target/benchmarks.jar "MyBenchmark.*" -prof gc

# With async-profiler
java -jar target/benchmarks.jar "MyBenchmark.*" -prof "org.openjdk.jmh.profile.AsyncProfiler"
```

---

## Memory Optimization

### Object Layout

```java
// Compact fields
class Good {
    long id;       // 8 bytes
    int status;    // 4 bytes
    short type;    // 2 bytes
    byte flags;    // 1 byte
    // Total: 16 bytes (with padding)
}

class Bad {
    byte flags;    // 1 byte
    long id;       // 8 bytes (alignment padding before)
    int status;    // 4 bytes
    short type;    // 2 bytes
    // Total: 24 bytes
}
```

### String Deduplication

```bash
-XX:+UseStringDeduplication
-XX:StringDeduplicationAgeThreshold=3
```

### Escape Analysis

```java
// Allocation eliminated if doesn't escape
public void method() {
    Point p = new Point(x, y); // Scalar replaced
    use(p.x, p.y);
}
```

---

## Tools Summary

| Category | Tools |
|----------|-------|
| CPU Profiling | async-profiler, JFR, VisualVM, JMC |
| Memory | jmap, jcmd, Eclipse MAT, JFR, async-profiler |
| GC | jstat, jcmd, GC logs, G1/ZGC logs |
| Locks | async-profiler (-e lock), JFR, jstack |
| Benchmarking | JMH |
| System | perf, bpftrace, eBPF |