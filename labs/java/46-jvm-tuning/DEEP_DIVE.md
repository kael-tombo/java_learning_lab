# Deep Dive: JVM Tuning

## 1. Heap Sizing Formulas

The JVM heap is divided into generations with complex sizing relationships.

### Heap Layout

```
Heap (Xms = initial, Xmx = maximum)
├── Young Generation (NewRatio = 2 → 1/3 of heap)
│   ├── Eden (SurvivorRatio = 8 → 8/10 of young)
│   ├── Survivor From (1/10 of young)
│   └── Survivor To (1/10 of young)
└── Old Generation (Tenured) (2/3 of heap with NewRatio=2)
```

```java
// Key heap sizing parameters:
// -Xms4g -Xmx4g              // Fixed heap (no resize)
// -Xmn1g                       // Explicit young gen size
// -XX:NewRatio=2              // Old:Young = 2:1
// -XX:SurvivorRatio=8         // Eden:Survivor = 8:1
// -XX:MaxNewSize=512m         // Max young gen
// -XX:+UseAdaptiveSizePolicy  // Auto-sizing (default for Parallel GC)
// -XX:-UseAdaptiveSizePolicy  // Manual sizing (G1 ignores this)

public class HeapSizingFormulas {
    // Survival space sizing formula:
    // survivor_size = young_size / (survivor_ratio + 2)
    // 
    // Example: young=1024m, SurvivorRatio=8
    // survivor = 1024 / (8 + 2) = ~102m per survivor
    // eden = 1024 - 2*102 = 820m
    
    // Promotion rate:
    // rate = (young_used_before_gc - young_used_after_gc - survivor_used_after_gc) / gc_interval
    // If rate > old_gen_free / max_gc_interval → promotion failure risk
    
    // Optimal Eden size:
    // Should hold ~2x the allocation between minor GCs
    // allocation_per_second * gc_interval * 2 = eden_size
    // This gives ~50% eden occupancy at GC time (balanced)
    
    // -XX:TargetSurvivorRatio=50 (default 50%)
    // Target occupancy of survivor spaces after aging
    // Too high: objects promoted before they're truly tenured
    // Too low: survivor space wasted
    
    // -XX:MaxTenuringThreshold=15 (default 15 for G1, 6 for Parallel)
    // If SurvivorRatio and MaxTenuringThreshold are balanced:
    // Average age of death = < 2 × MaxTenuringThreshold × survivor_ratio / (1 + survivor_ratio)
}
```

### Ergonomics

JVM ergonomics automatically select GC, heap size, and compiler based on hardware:

```java
// Default ergonomic selections:
// - GC: G1 (since Java 9)
// - Heap: 1/4 of physical RAM (MinRAMFraction=2) or 1GB (server)
// - Young gen: 1/3 of heap (NewRatio=2 for Parallel, G1 uses adaptive)
// - Compiler: C1 + C2 (tiered compilation)
// - Thread stack: 1024KB (varies by platform)
// 
// -XX:MinRAMFraction=2 (minimum heap = RAM/2)
// -XX:MaxRAMFraction=4 (max heap = RAM/4) [deprecated, use MaxRAMPercentage]
// -XX:MaxRAMPercentage=25.0 (since Java 8u191, recommended)
// -XX:InitialRAMPercentage=12.5
// -XX:MinRAMPercentage=50.0

public class ErgonomicsExample {
    public static void main(String[] args) {
        // -XX:+PrintFlagsFinal shows all ergonomic settings
        // -XX:+PrintCommandLineFlags shows effective flags
        
        Runtime rt = Runtime.getRuntime();
        System.out.printf("Processors: %d%n", rt.availableProcessors());
        System.out.printf("Max memory: %d MB%n", rt.maxMemory() / 1024 / 1024);
        System.out.printf("Total memory: %d MB%n", rt.totalMemory() / 1024 / 1024);
        System.out.printf("Free memory: %d MB%n", rt.freeMemory() / 1024 / 1024);
    }
}
```

## 2. Survivor Space Sizing

### The Survivor Space Balancing Act

```java
// Survivor space sizing is critical for GC efficiency:
// 
// Too small:
// - Objects promoted prematurely to old gen
// - More old gen GCs
// - Worse throughput (promotion is more expensive than copying)
//
// Too large:
// - Wasted space (Eden is smaller)
// - More young GC work (scanning more survivor space)
// - Longer pauses
//
// The ideal: survivor space is sized so that ~50% of objects
// from Eden are promoted after MaxTenuringThreshold GCs
//
// jstat -gcutil <pid> 1s shows survivor utilization
// -XX:+PrintTenuringDistribution shows age histograms

public class SurvivorOptimization {
    public static void main(String[] args) {
        // Check survivor utilization with:
        // jstat -gc <pid> 1000
        
        // -XX:+PrintTenuringDistribution output:
        // Desired survivor size 48234496 bytes, new threshold 15 (max 15)
        // - age   1:   12345678 bytes,   12345678 total
        // - age   2:    5432109 bytes,   17777787 total
        // - age   3:    2109876 bytes,   19887663 total
        // ...
        // If total at age 2 > desired_threshold × TargetSurvivorRatio
        // → threshold lowered, objects promoted
    }
}
```

### Automatic Survivor Sizing

```java
// Adaptive sizing adjusts survivor spaces:
// -XX:+UseAdaptiveSizePolicy (Parallel GC)
// -XX:AdaptiveSizeThroughPutWeight=0.1
// -XX:AdaptiveSizePausePolicy=1
// 
// The policy monitors:
// - GC pause time vs -XX:MaxGCPauseMillis target
// - Throughput (time spent in GC vs application)
// - Survivor overflow (promotion rate)
//
// Adjustments:
// - Increase survivor: if overflow detected
// - Decrease survivor: if always under TargetSurvivorRatio
// - Adjust eden/survivor ratio: if pause time targets missed
}
```

## 3. TLAB (Thread-Local Allocation Buffer) Sizing

TLABs give each thread a dedicated Eden region for lock-free allocation:

```java
// TLAB parameters:
// -XX:+UseTLAB (default: true)
// -XX:TLABSize=0 (0 = ergonomic default)
// -XX:TLABRefillWasteFraction=64 (1/64 wasted per refill)
// -XX:TLABWasteTargetPercent=1 (1% waste target)
// -XX:+PrintTLAB (shows TLAB utilization)
// -XX:TLABAllocationWeight=100

// TLAB sizing formula:
// Initial TLAB size = shared Eden size × TLABWasteTargetPercent / 100 / threads
// Each thread gets: min(~100KB, eden/threads ÷ TLABWasteTargetPercent)
//
// When TLAB runs out:
// 1. Try to allocate a new TLAB (if eden has room)
// 2. If waste would exceed limit, allocate directly in Eden (slow path)
// 3. If Eden is full → trigger young GC

public class TLABCosting {
    private static final int ITERATIONS = 10_000_000;
    private static final int ALLOC_SIZE = 64; // bytes per object
    
    public static void main(String[] args) {
        // Run with: -XX:+PrintTLAB -XX:+UnlockDiagnosticVMOptions
        // 
        // TLAB usage per thread:
        // Thread: main (0x00000123456789)
        //   TLAB: 1024K [0x00000000F8800000, 0x00000000F8800000, 0x00000000F8900000]
        //   alloc: 5120 / 10240 blocks, 512M / 1024M
        //   min: 64K, avg: 128K, max: 1024K
        //   waste: 2K (0.2%)
        //
        // TLAB resizing:
        // Small TLAB → frequent refill (more expensive)
        // Large TLAB → more waste (fragmentation)
        
        // -XX:+UseTLAB -XX:-ResizeTLAB (disable resizing for predictability)
        // -XX:TLABRefillWasteFraction=32 (allow more waste, fewer refills)
        
        byte[][] data = new byte[ITERATIONS][];
        long t0 = System.nanoTime();
        for (int i = 0; i < ITERATIONS; i++) {
            data[i] = new byte[ALLOC_SIZE]; // TLAB allocation (fast)
        }
        long elapsed = System.nanoTime() - t0;
        System.out.printf("Allocated %dMB in %dms (%d ns/alloc)%n",
            ITERATIONS * ALLOC_SIZE / 1024 / 1024,
            elapsed / 1_000_000,
            elapsed / ITERATIONS);
    }
}
```

### TLAB Performance Impact

```java
// TLAB allocation path (fast):
// 1. Load TLAB end pointer
// 2. Bump-allocate: current + size > end? → slow path
// 3. Write allocation address
// 4. Clear memory (stores zeros)
// Total: ~10 instructions, ~5 ns on modern hardware
//
// Without TLAB (slow path):
// 1. Synchronized Eden allocation
// 2. CAS on Eden top pointer (contention!)
// 3. GC safe point check
// 4. Array clearing
// Total: ~100-500 ns (10-100x slower)
```

## 4. Code Cache Sizing

The code cache stores JIT-compiled native code:

```java
// Code cache sizing:
// -XX:ReservedCodeCacheSize=256m   (max size, default 256m)
// -XX:InitialCodeCacheSize=64m    (initial size)
// -XX:CodeCacheExpansionSize=64k  (expansion size)
// -XX:+UseCodeCacheFlushing       (flush old code when full)

// Code cache segments (since Java 9 with tiered compilation):
// - Non-nmethod code: ~5MB (runtime stubs, adapters)
// - Profiled code (C1): ~140MB
// - Non-profiled code (C2): ~120MB
// 
// Total default: 256MB (set by -XX:ReservedCodeCacheSize)
//
// Code cache full → stop compilation
// Warning in logs: "CodeCache is full. Compiler has been disabled."
// Performance drops because:
// - No new JIT compilation
// - Methods revert to interpreted mode
// - Already compiled methods still run (but can't be recompiled)

public class CodeCacheMonitor {
    public static void main(String[] args) {
        // Monitor with:
        // jcmd <pid> Compiler.codecache
        //
        // Or via JMX:
        java.lang.management.ManagementFactory.getPlatformMBeanServer();
        // java.lang:type=MemoryPool,name=CodeHeap 'non-nmethods'
        // java.lang:type=MemoryPool,name=CodeHeap 'profiled-nmethods'
        // java.lang:type=MemoryPool,name=CodeHeap 'non-profiled-nmethods'
        
        // -XX:+PrintCodeCache shows usage after each GC
        // -XX:+PrintCodeCacheOnCompilation shows on each compile
        
        // Code cache sizing guidelines:
        // Small app (<1000 methods): 64MB
        // Medium app (1000-5000 methods): 128MB
        // Large app (5000-20000 methods): 256MB
        // Very large (>20000 methods): 512MB+
    }
}
```

## 5. Metaspace Reclamation

```java
// Metaspace parameters:
// -XX:MetaspaceSize=256m        (first GC threshold)
// -XX:MaxMetaspaceSize=512m     (hard limit)
// -XX:CompressedClassSpaceSize=1g (class pointer storage)
// -XX:MinMetaspaceExpansion=256k
// -XX:MaxMetaspaceExpansion=8m
// -XX:+UseContainerSupport      (respect cgroups, default since Java 10)
//
// Metaspace reclamation:
// 1. Class unloading happens when a ClassLoader dies
// 2. GC detects unreachable class loaders
// 3. -XX:+UnsyncloadClass (loading class in parallel)
// 4. -XX:+AlwaysPreTouch (commit pages immediately)
//
// Common Metaspace issues:
// - ClassLoader leak: frameworks that create many class loaders
// - Large generated classes: proxy classes, lambda expressions
// - Reflection-heavy code: generated accessor classes
//
// Diagnosis:
// jcmd <pid> VM.metaspace (shows usage by class loader)
// -XX:+PrintMetaspaceStatisticsAtExit

public class MetaspaceDeepDive {
    public static void main(String[] args) throws Exception {
        // 1000 loaders, each defining one uniquely named minimal class built
        // in memory — real generate-and-define, no filesystem involved.
        for (int i = 0; i < 1000; i++) {
            new CustomClassLoader().defineOne("com.example.GeneratedClass" + i);
        }
        // If class loaders are not released, Metaspace grows indefinitely;
        // hold a reference to the List<CustomClassLoader> and the growth is
        // permanent until that List itself becomes unreachable.
        System.out.println("defined 1000 unique classes; watch with jcmd VM.metaspace");
        // jcmd <pid> GC.run() - forces GC (may unload classes)
        // -XX:+TraceClassUnloading shows when classes are unloaded
    }

    static class CustomClassLoader extends ClassLoader {
        /** Defines a minimal but VALID class file named `name` (no members). */
        void defineOne(String name) {
            try {
                byte[] b = minimalClassFile(name);
                // cross-check the hex constant pool really contains the name
                if (!new String(b, "ISO-8859-1").contains(
                        name.replace('.', '/'))) {
                    throw new IllegalStateException("name missing from bytes");
                }
                defineClass(name, b, 0, b.length);
                } catch (java.io.UnsupportedEncodingException e) {
                throw new IllegalStateException(e);
            }
        }
    }

    /** Assembles a valid class file: CP[name(Utf8), super(Utf8)] and CP entries. */
    static byte[] minimalClassFile(String name) {
        String bin = name.replace('.', '/');
        byte[] n = bin.getBytes(), s = "java/lang/Object".getBytes();
        java.io.ByteArrayOutputStream o = new java.io.ByteArrayOutputStream();
        // header: magic + version 52.0 (Java 8 target, loadable anywhere)
        u4(o, 0xCAFEBABEL); u2(o, 0); u2(o, 52);
        // constant pool: #1 name utf8, #2 name class, #3 Object utf8, #4 Object class
        u2(o, 5);
        u1(o, 1); u2(o, n.length); o.write(n, 0, n.length);
        u1(o, 7); u2(o, 1);
        u1(o, 1); u2(o, s.length); o.write(s, 0, s.length);
        u1(o, 7); u2(o, 3);
        // access_flags public super, this #2, super #4, no interfaces/fields
        u2(o, 0x0021); u2(o, 2); u2(o, 4); u2(o, 0); u2(o, 0); u2(o, 0);
        u2(o, 0);  // class-level attributes count (none — the file is complete)
        return o.toByteArray();
    }

    static void u1(java.io.ByteArrayOutputStream o, int v) { o.write(v & 0xFF); }
    static void u2(java.io.ByteArrayOutputStream o, int v) {
        u1(o, v >> 8); u1(o, v);
    }
    static void u4(java.io.ByteArrayOutputStream o, long v) {
        u2(o, (int) (v >>> 16)); u2(o, (int) v);
    }
}
```

## 6. Compressed OOPs with Heaps >32GB

Compressed OOPs (Ordinary Object Pointers) use 32-bit references instead of 64-bit, reducing object header size:

```java
// With Compressed OOPs (-XX:+UseCompressedOops, default):
// - Object references: 4 bytes instead of 8
// - Klass pointer: 4 bytes (with UseCompressedClassPointers)
// - Object header: 12 bytes (8 mark + 4 klass)
// - Max heap: ~32GB (theoretical limit of 32-bit address × 8-byte granularity)
//
// Without Compressed OOPs:
// - Object references: 8 bytes
// - Klass pointer: 8 bytes
// - Object header: 16 bytes (8 mark + 8 klass)
// - Heap limited only by physical memory
//
// When heap > 32GB, you have options:
// Option 1: Use -XX:-UseCompressedOops (all references 64-bit)
//   - Extra 4 bytes per reference (significant overhead)
//   - Large heap regression: ~10-20% more memory usage
//
// Option 2: Use -XX:ObjectAlignmentInBytes=16 (16-byte alignment)
//   - Compressed OOPs scale: heap = 32GB × (alignment / 8)
//   - With 16-byte alignment: max heap = 64GB
//   - With 32-byte alignment: max heap = 128GB
//   - Cost: internal fragmentation (objects round up to 16/32 bytes)
//   - -XX:ObjectAlignmentInBytes=16 (also requires large page support)
//   - Useful: large heaps (64-128GB) with many small objects

public class CompressedOopsAnalysis {
    // To check if compressed OOPs are enabled:
    // java -XX:+PrintCommandLineFlags -version
    // -XX:+UseCompressedOops -XX:+UseCompressedClassPointers
    
    // Object header comparison:
    // 64-bit heap < 32GB:  12 bytes header (8 mark + 4 klass)
    // 64-bit heap > 32GB:  16 bytes header (8 mark + 8 klass)
    // 64-bit heap + 16-byte alignment: 12 bytes header, 16-byte aligned
    
    // Best practice: keep heap < 32GB if possible to use compressed OOPs
    // If heap > 32GB required, consider:
    // 1. Splitting into multiple JVMs (each < 32GB)
    // 2. Using object alignment (XX:ObjectAlignmentInBytes=16)
    // 3. Accept 10-20% memory overhead
}
```

## 7. Large Page Support

```java
// Large pages improve TLB (Translation Lookaside Buffer) coverage:
// - Standard page: 4KB
// - Large page (HugeTLB): 2MB on Linux, 4MB on Windows
// - Transparent HugePages (THP): Linux kernel feature
//
// -XX:+UseLargePages (enable large pages)
// -XX:LargePageSizeInBytes=2m (default: auto)
// -XX:+UseTransparentHugePages (Linux only, transparent)
//
// Performance impact:
// - TLB miss rate reduces by 10-100x
// - GC scanning is faster (fewer page walks)
// - Allocation at startup is slower (pages committed immediately)
// - Overall throughput improvement: 5-15% (GC-heavy apps)
// - Latency improvement: 10-30% for GC pauses
//
// Without large pages:
// - 4KB pages: 262144 TLB entries needed for 1GB heap
// - TLB has ~64 entries → massive TLB thrashing
//
// With 2MB pages:
// - 512 TLB entries needed for 1GB heap
// - Most mappings fit in L1/L2 TLB

public class LargePageConfig {
    // Linux setup:
    // echo 2048 > /proc/sys/vm/nr_hugepages
    // mount -t hugetlbfs hugetlbfs /dev/hugepages
    // java -XX:+UseLargePages -Xmx4g
    
    // Windows setup:
    // Requires "Lock pages in memory" privilege for user
    // secedit /configure /db secedit.sdb /cfg hugetlb.inf
    
    // Verify large pages are in use:
    // -XX:+PrintFlagsFinal | grep LargePage
    // /proc/meminfo | grep HugePages (Linux)
    
    public static void main(String[] args) {
        long totalPages = Runtime.getRuntime().maxMemory() / (2 * 1024 * 1024);
        System.out.println("Approximate " + totalPages + " large pages needed");
    }
}
```

## 8. Biased Locking (Removed in Java 21)

Biased locking was a controversial optimization that assumed locks were mostly contended by a single thread:

```java
// Biased locking history:
// - Introduced in Java 6
// - Biased lock: mark word stores thread ID, no CAS needed for lock
// - Revocation: if another thread tries to acquire, bias must be revoked
//   (safepoint operation, expensive)
// - Disabled by default in Java 15
// - Removed in Java 21 (JDK-8201734)
//
// Why it was removed:
// - High complexity in the JVM implementation
// - Revocation required a safepoint
// - Modern lock contention patterns rarely benefit
// - Java 21+ virtual threads use different synchronization
// - 1-2% performance cost to maintain (not worth it)
//
// Effect of removal:
// - Mark word no longer has biased locking bits (simplifies header)
// - Locks always start as thin locks (CAS-based)
// - No safepoints for bias revocation
// - Slightly faster single-threaded lock acquisition in some cases

public class BiasedLockingHistory {
    // Pre-Java 21:
    // Object locked: [thread_id | epoch | age | 1 | 01]
    //                (biased_lock=1, pattern=01)
    // 
    // Java 21+:
    // Object locked: [hash | age | 0 | 00]  → thin lock
    //                (no bias pattern, directly use CAS on mark word)
    
    // Biased locking was disabled via:
    // -XX:+UseBiasedLocking (removed in Java 21, flag ignored)
    // -XX:BiasedLockingStartupDelay=4000 (delay before enabling)
}
```

## 9. Comprehensive Tuning Checklist

```java
public class JVMTuningChecklist {
    // PRODUCTION JVM TUNING CHECKLIST:
    //
    // [ ] Heap sizing
    //     -Xms = -Xmx (fixed heap, avoid resize)
    //     MaxRAMPercentage=75.0 (container: 75% of container limit)
    //
    // [ ] GC selection
    //     -XX:+UseG1GC (default, good for most)
    //     -XX:+UseZGC (low latency, modern apps)
    //     -XX:MaxGCPauseMillis=100 (G1 target)
    //
    // [ ] GC tuning
    //     -XX:ConcGCThreads=4
    //     -XX:ParallelGCThreads=8
    //     -Xlog:gc*:file=gc.log
    //
    // [ ] Memory
    //     -XX:+AlwaysPreTouch (commit all pages at startup)
    //     -XX:+UseLargePages (if available)
    //     -XX:MetaspaceSize=256m
    //     -XX:MaxMetaspaceSize=512m
    //
    // [ ] Code cache
    //     -XX:ReservedCodeCacheSize=512m
    //     -XX:+UseCodeCacheFlushing
    //
    // [ ] JIT
    //     -XX:CompileThreshold=10000 (C2 threshold)
    //     -XX:TieredCompilation (default)
    //
    // [ ] Diagnostics
    //     -XX:+PrintCommandLineFlags
    //     -XX:+HeapDumpOnOutOfMemoryError
    //     -XX:HeapDumpPath=/dumps
    //     -XX:+ExitOnOutOfMemoryError
    //
    // [ ] Container-aware
    //     -XX:+UseContainerSupport (since Java 10)
    //     -XX:ActiveProcessorCount=4
    //
    // [ ] Tuning by workload:
    //     Throughput: ParallelGC, larger heap, less GC
    //     Latency: ZGC, G1 with tight pause target
    //     Batch: Serial or Parallel, no pause target
    //     Real-time: ZGC, Shenandoah
}
```

## 10. A Complete JVM Tuning Example

```java
// Example command for a latency-sensitive microservice:
// java -Xms8g -Xmx8g \
//      -XX:+UseZGC \
//      -XX:+ZGenerational \
//      -XX:ConcGCThreads=4 \
//      -XX:ParallelGCThreads=8 \
//      -XX:MaxRAMPercentage=75.0 \
//      -XX:+AlwaysPreTouch \
//      -XX:+UseContainerSupport \
//      -XX:ActiveProcessorCount=8 \
//      -XX:ReservedCodeCacheSize=512m \
//      -XX:+ExitOnOutOfMemoryError \
//      -XX:+HeapDumpOnOutOfMemoryError \
//      -XX:HeapDumpPath=/var/dumps \
//      -Xlog:gc*:file=/var/log/gc.log:time,uptime,level,tags \
//      -Xlog:gc+safepoint=debug:file=/var/log/safepoint.log \
//      -jar myapp.jar
//
// For throughput-optimized batch:
// java -Xms32g -Xmx32g \
//      -XX:+UseParallelGC \
//      -XX:ParallelGCThreads=16 \
//      -XX:MaxGCPauseMillis=500 \
//      -XX:+UseAdaptiveSizePolicy \
//      -jar batch-processor.jar
```

Tuning is iterative. Every change should be validated with GC logs, JFR recording, and application-level metrics. There are no universal "best" settings — only settings that work for your specific workload.
