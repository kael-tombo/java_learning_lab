# THEORY — Memory Deep Dive

## Overview

Advanced JVM memory management: heap structure, allocation, GC algorithms, memory leaks, and profiling.

---

## Heap Organization

### Generational Layout

```
Heap
├── Young Generation
│   ├── Eden Space (80-90% of young)
│   ├── Survivor 0 (S0) - "From"
│   └── Survivor 1 (S1) - "To"
└── Old Generation (Tenured)
    └── Humongous Objects (G1/ZGC)
```

### Object Aging

```
New Object → Eden
    │ Minor GC: survive → S0 (age=1)
    │ Minor GC: survive → S1 (age=2)
    │ Minor GC: survive → S0 (age=3)
    │ ...
    │ Age ≥ MaxTenuringThreshold → Old Gen
    ▼
Old Generation
```

### Humongous Objects

- G1: Objects > 50% region size
- ZGC: Objects > 256KB (configurable)
- Allocated directly in old generation
- Special handling during GC

---

## Allocation

### Thread-Local Allocation Buffers (TLABs)

```
Thread 1: [TLAB: Eden chunk] → allocate fast (bump pointer)
Thread 2: [TLAB: Eden chunk] → allocate fast
Thread 3: [TLAB: Eden chunk] → allocate fast

When TLAB full → request new TLAB or slow path
```

### Allocation Fast Path

```c
// Pseudocode for bump pointer allocation
void* allocate(size_t size) {
    void* result = thread->tlab_top;
    thread->tlab_top += size;
    if (thread->tlab_top > thread->tlab_limit) {
        return allocate_slow(size);  // Refill TLAB or slow path
    }
    return result;
}
```

### Allocation Flags

```bash
# TLAB
-XX:+UseTLAB                    # Enable (default)
-XX:TLABSize=1m                 # Initial TLAB size
-XX:MinTLABSize=1k              # Minimum
-XX:+ResizeTLAB                 # Dynamic sizing

# Fast path
-XX:+UseFastAllocation          # Enable (default)
```

---

## GC Algorithms Deep Dive

### G1 GC Phases

```
1. Young GC (STW)
   ├── Root scanning
   ├── Remembered set scan (old→young refs)
   ├── Copy live: Eden+S0 → S1/Old
   └── Update refs

2. Concurrent Marking
   ├── Initial Mark (STW, piggyback on young GC)
   ├── Root Region Scan (STW)
   ├── Concurrent Mark (parallel)
   ├── Remark (STW)
   └── Cleanup (STW, reclaim empty regions)

3. Mixed GC (STW)
   ├── Young + selected Old regions
   ├── Evacuation
   └── Compaction
```

### ZGC Phases

```
1. Pause Mark Start (STW) - root marking
2. Concurrent Mark - traverse object graph
3. Pause Mark End (STW) - finalize marking
4. Concurrent Prepare for Relocate - select regions
5. Pause Relocate Start (STW) - start relocation
6. Concurrent Relocate - move objects, fix refs
7. Pause Relocate End (STW) - finalize
```

### GC Comparison

| Aspect | G1 | ZGC | Shenandoah |
|--------|-----|-----|------------|
| Max Heap | ~64TB | 16TB | 64TB |
| Pause Target | 200ms | <1ms | <10ms |
| Compaction | Mixed GC | Concurrent | Concurrent |
| Barriers | SATB (write) | Load/Store | Brooks (read) |
| Generational | Yes | No (21+) | No |
| Heap Regions | Fixed (1-32MB) | Dynamic | Dynamic |

---

## Memory Leaks

### Common Patterns

```java
// 1. Static collections
static Map<String, Object> cache = new HashMap<>(); // Never cleared

// 2. Listeners not removed
button.addListener(e -> doSomething()); // Anonymous class holds outer ref

// 3. ThreadLocal in thread pools
ThreadLocal<Connection> tl = ThreadLocal.withInitial(() -> pool.get());
// Thread reused → connection never released

// 4. Unclosed resources
// Files, sockets, streams, DB connections

// 5. Cache without eviction
Map<K, V> cache = new ConcurrentHashMap<>(); // Grows unbounded

// 6. String interning
String s = new String("huge").intern(); // PermGen/Metaspace leak (pre-8)
```

### Detection

```bash
# Heap dump
jcmd <pid> GC.heap_dump /tmp/heap.hprof

# Analyze with Eclipse MAT
# 1. Histogram → Group by class → Retained size
# 2. Dominator tree → Path to GC roots
# 3. Leak suspects report

# JFR
-XX:StartFlightRecording=event=jdk.OldObjectSample,filename=leak.jfr
```

---

## Native Memory

### Categories

| Category | Description | Tracking |
|----------|-------------|----------|
| Heap | Java objects | GC |
| Metaspace | Class metadata | Metaspace GC |
| Code Cache | JIT code | CodeCache GC |
| Thread Stacks | Per-thread | OS |
| Direct Buffers | `ByteBuffer.allocateDirect` | Cleaner/Reference |
| Mapped Files | `FileChannel.map` | Cleaner/Reference |
| JNI | Native allocations | Manual |
| GC Structures | Card tables, remembered sets | GC |

### Tracking

```bash
# Native Memory Tracking (NMT)
-XX:NativeMemoryTracking=summary  # or detail
jcmd <pid> VM.native_memory summary
jcmd <pid> VM.native_memory detail

# Output:
# Total: reserved=4.2GB, committed=2.1GB
# - Java Heap: reserved=2GB, committed=2GB
# - Class: reserved=1GB, committed=200MB
# - Thread: reserved=200MB, committed=50MB
# - Code: reserved=256MB, committed=100MB
# - GC: reserved=200MB, committed=150MB
# - Internal: reserved=50MB, committed=30MB
# - Symbol: reserved=50MB, committed=20MB
# - Native Memory Tracking: reserved=10MB, committed=5MB
```

### Off-Heap Allocation

```java
// Direct buffer
ByteBuffer buf = ByteBuffer.allocateDirect(1024 * 1024);
// Cleaned by Cleaner (phantom reference)
// Or manually:
((DirectBuffer) buf).cleaner().clean();

// Unsafe (internal)
Unsafe unsafe = Unsafe.getUnsafe();
long addr = unsafe.allocateMemory(size);
unsafe.freeMemory(addr);

// Foreign Memory API (Java 22+)
try (Arena arena = Arena.ofConfined()) {
    MemorySegment segment = arena.allocate(1024);
    // Auto-free on close
}
```

---

## Performance Tuning

### Heap Sizing Strategy

```
1. Start with -Xms = -Xmx (fixed heap)
2. Set NewRatio for generational (2-3 typical)
3. Monitor GC logs for:
   - Promotion rate
   - Old gen occupancy trend
   - GC frequency vs pause time
4. Adjust:
   - High promotion → larger young gen
   - Long old GC → larger heap or different collector
   - Frequent young GC → larger young gen
```

### GC Log Analysis

```bash
# Unified logging (Java 9+)
-Xlog:gc*:file=gc.log:time,uptime,level,tags:filecount=10,filesize=50m

# Key metrics:
# - GC pause time (p99, max)
# - Throughput: (app time) / (app + GC time)
# - Allocation rate (MB/s)
# - Promotion rate (MB/s)
# - Heap occupancy after GC
```

### ZGC Tuning

```bash
-XX:+UseZGC
-XX:ZCollectionInterval=10          # Min interval between GCs (ms)
-XX:ZAllocationSpikeTolerance=2.0   # Heap headroom factor
-XX:ZProactive=                     # Proactive compaction
-XX:+ZGenerational                  # Java 21+ generational ZGC
```

---

## Tools

| Tool | Purpose |
|------|---------|
| `jcmd GC.heap_info` | Heap summary |
| `jcmd GC.class_histogram` | Live object counts |
| `jmap -histo:live <pid>` | Live objects (triggers GC) |
| `jmap -dump:live,file=heap.hprof <pid>` | Heap dump |
| Eclipse MAT | Heap analysis |
| JFR + JMC | Allocation profiling |
| async-profiler `-e alloc` | Allocation sites |
| VisualVM | GUI heap analysis |