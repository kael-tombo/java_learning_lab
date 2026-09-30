# THEORY: JVM Memory Architecture & Garbage Collection
## Lab 01 | Production Engineering Academy

---

## 1. JVM Memory Architecture

### 1.1 The Big Picture

```
┌────────────────────────────────────────────────────────────┐
│                       JVM Process                          │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    Heap Memory                       │  │
│  │                                                      │  │
│  │  ┌─────────────┐  ┌────────────────────────────────┐ │  │
│  │  │   Young Gen  │  │          Old Gen               │ │  │
│  │  │             │  │                                │ │  │
│  │  │ ┌───┐ ┌───┐ │  │  Long-lived objects live here  │ │  │
│  │  │ │ E │ │S0 │ │  │  Full GC sweeps this region    │ │  │
│  │  │ │ d │ │   │ │  │                                │ │  │
│  │  │ │ e │ │S1 │ │  │  Target: < 30% occupancy       │ │  │
│  │  │ │ n │ └───┘ │  │                                │ │  │
│  │  │ └───┘       │  └────────────────────────────────┘ │  │
│  │  └─────────────┘                                     │  │
│  │                                                      │  │
│  │  ┌───────────────────────────────────────────────┐   │  │
│  │  │  Metaspace (off-heap, grows dynamically)      │   │  │
│  │  │  Class metadata, method bytecode, interned    │   │  │
│  │  │  strings (Java 8+), runtime constants         │   │  │
│  │  └───────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌────────────────────────────────────────────────────┐    │
│  │            Non-Heap / Off-Heap Memory              │    │
│  │  Code Cache | Direct Buffers | JVM internals       │    │
│  └────────────────────────────────────────────────────┘    │
│                                                            │
│  ┌─────┐  Per-thread stack  │  Holds stack frames,        │
│  │Stack│  (512KB–1MB each)  │  local vars, references     │
│  └─────┘                                                   │
└────────────────────────────────────────────────────────────┘
```

### 1.2 Object Lifecycle in the Heap

```
new MyObject()
     │
     ▼
┌─────────────────┐
│  Eden Space     │  ← Objects born here (TLAB allocation)
│  (Young Gen)    │
└────────┬────────┘
         │ Minor GC triggers when Eden is full
         ▼
┌─────────────────┐
│  Survivor S0/S1 │  ← Survives 1+ minor GC → age++
│  (Young Gen)    │
└────────┬────────┘
         │ age >= MaxTenuringThreshold (default 15)
         │ OR object too large for Young Gen
         ▼
┌─────────────────┐
│   Old Gen       │  ← Tenured objects; cleaned by Major/Full GC
│                 │
└─────────────────┘
```

### 1.3 TLAB (Thread-Local Allocation Buffers)

Each thread has its own private slice of Eden. This enables lock-free object allocation — critical for throughput.

```
Eden Space
├── Thread-1 TLAB: [obj1][obj2][obj3][...........]
├── Thread-2 TLAB: [obj4][obj5][...................]
├── Thread-3 TLAB: [obj6][obj7][obj8][obj9][.......]
└── Shared rest: [large objects allocated here w/ lock]
```

**Key insight**: Most Java objects are born and die in Eden. This is the "generational hypothesis" — young objects die young.

---

## 2. Garbage Collection Algorithms

### 2.1 G1GC (Garbage-First) — Default since Java 9

**How it works**:
```
Heap = N regions of equal size (1MB–32MB each)
Each region dynamically assigned: Eden | Survivor | Old | Humongous
```

G1 builds a "remembered set" for each region (which other regions point into it). During collection, it picks regions with the most garbage ("Garbage-First").

**GC Phases**:
1. **Minor GC (Young-only)**: Collect Eden + Survivors. Stop-the-world (STW), but short (~5-50ms)
2. **Concurrent Marking**: Mark live objects in Old Gen while app runs (concurrent!)
3. **Mixed GC**: Collect Young + subset of Old regions with most garbage
4. **Full GC**: Emergency — all regions, all threads stop. Usually a sign of trouble

**Best for**: Most applications. Balances throughput vs pause time. Target: < 200ms pauses.

```
Key Flags:
-XX:+UseG1GC                    # Enable (default Java 9+)
-XX:MaxGCPauseMillis=200        # Target pause goal (not a hard limit!)
-XX:G1HeapRegionSize=8m         # Region size (power of 2, 1-32m)
-XX:G1NewSizePercent=5          # Min young gen %
-XX:G1MaxNewSizePercent=60      # Max young gen %
-XX:G1MixedGCCountTarget=8      # Mixed GC cycles per marking
-XX:InitiatingHeapOccupancyPercent=45  # When to start concurrent mark
```

### 2.2 ZGC — The Low-Latency Champion (Java 15+, production-ready)

**Pause times**: < 1ms (yes, sub-millisecond!) regardless of heap size (multi-TB heaps!)

**How it works**:
- Concurrent relocation using "colored pointers" (load barriers)
- Reference coloring: pointer bits encode GC state
- Almost all work done concurrently with application

```
Key Flags:
-XX:+UseZGC                     # Enable ZGC
-XX:ZCollectionInterval=2       # Force GC every 2 seconds
-XX:SoftMaxHeapSize=16g         # ZGC target heap size
-XX:+ZGenerational              # Java 21+: Generational ZGC (much better!)
```

**When to use ZGC**:
- Latency-sensitive services (trading systems, gaming, real-time APIs)
- Large heaps (> 8GB)
- You can afford higher CPU overhead

### 2.3 Shenandoah — Red Hat's Ultra-Low-Latency GC

Similar to ZGC but uses "Brooks pointers" (forwarding pointers). Available in OpenJDK.

```
Key Flags:
-XX:+UseShenandoahGC
-XX:ShenandoahGCHeuristics=adaptive  # adaptive|static|compact|aggressive
```

### 2.4 Parallel GC — Throughput King

Old school but still valid for batch processing. All GC threads run in parallel during STW.

```
Key Flags:
-XX:+UseParallelGC
-XX:ParallelGCThreads=8
```

**Use when**: Offline batch jobs, ETL, where throughput > latency.

---

## 3. GC Log Analysis

### 3.1 Enable Unified GC Logging (Java 9+)

```bash
-Xlog:gc*:file=gc.log:time,uptime,level,tags:filecount=10,filesize=50m
```

### 3.2 Reading G1GC Logs

```
[2026-09-30T03:42:11.000+0000][5.234s][info][gc,start] GC(42) Pause Young (Normal) (G1 Evacuation Pause)
[2026-09-30T03:42:11.000+0000][5.234s][info][gc,task ] GC(42) Using 8 workers of 8 for evacuation
[2026-09-30T03:42:11.056s    ][5.290s][info][gc,heap ] GC(42) Eden regions: 512->0(470)   ← Eden cleared
[2026-09-30T03:42:11.056s    ][5.290s][info][gc,heap ] GC(42) Survivor regions: 15->18(65) ← Survivors updated
[2026-09-30T03:42:11.056s    ][5.290s][info][gc,heap ] GC(42) Old regions: 127->127        ← Old untouched
[2026-09-30T03:42:11.056s    ][5.290s][info][gc,heap ] GC(42) Humongous regions: 3->3      ← Large objects
[2026-09-30T03:42:11.056s    ][5.290s][info][gc      ] GC(42) Pause Young (Normal) 4152M->1321M(8192M) 56.231ms
                                                                                                ↑ Duration: 56ms
```

**Key metrics to watch**:
- **Pause duration**: How long the STW pause lasted
- **Heap before/after**: `4152M->1321M(8192M)` = 4.1GB before, 1.3GB after, 8GB max
- **Eden cleared**: Good — objects died in Eden (young death)
- **Old region growth**: Increasing over time = promotion pressure = potential Full GC

### 3.3 Danger Signs in GC Logs

```
# DANGER: Full GC happening
GC(523) Pause Full (Allocation Failure)  ← BAD! App is freezing

# DANGER: Old Gen filling up
Old regions: 1800->1850(2048)  ← Only 198 regions free!

# DANGER: Humongous allocations
Humongous regions: 12->15  ← Objects > region_size/2 bypass young gen

# DANGER: GC overhead limit approaching
[gc] GC overhead limit exceeded  ← Will throw OOM if not fixed
```

---

## 4. Memory Sizing for Production

### 4.1 The Sizing Formula

```
Total JVM Memory = Heap + Metaspace + Code Cache + Thread Stacks + Direct Buffers + GC overhead

Container Memory Limit = Total JVM Memory + OS overhead (100-200MB)
```

**Never set -Xmx = container limit!** Leave headroom for off-heap.

### 4.2 Heap Sizing Guidelines

| Workload | Xms | Xmx | Young Gen % | Notes |
|----------|-----|-----|-------------|-------|
| API service (low latency) | = Xmx | 2-4G | 40-60% | Short-lived objects |
| High-throughput API | = Xmx | 4-8G | 30-40% | Balance |
| Data processing | = Xmx | 8-32G | 20-30% | Long-lived data |
| Batch ETL | 1G | 16-64G | varies | Throughput matters |

**Always set -Xms = -Xmx**: Prevents heap resizing overhead in production.

### 4.3 Metaspace Sizing

```bash
-XX:MetaspaceSize=256m          # Initial Metaspace (prevents early resizing)
-XX:MaxMetaspaceSize=512m       # Cap Metaspace (prevent runaway class loading)
```

**Metaspace OOM** usually means:
- Class loader leak (common in hot-reload, OSGi, app servers)
- Too many dynamically generated classes (Spring proxies, Hibernate bytecode)
- Excessive reflection with ClassInfo caching

---

## 5. Object Allocation Patterns That Kill Performance

### 5.1 String Concatenation in Loops

```java
// BAD — creates N intermediate String objects
String result = "";
for (Item item : items) {
    result += item.getName() + ",";  // Each += = new String!
}

// GOOD — StringBuilder reuses buffer
StringBuilder sb = new StringBuilder(items.size() * 20);
for (Item item : items) {
    sb.append(item.getName()).append(',');
}
String result = sb.toString();
```

### 5.2 Autoboxing in Hot Paths

```java
// BAD — Integer objects created in each iteration
Map<String, Integer> counts = new HashMap<>();
for (String word : words) {
    counts.merge(word, 1, Integer::sum);  // Boxing int→Integer
}

// GOOD — use primitive-specialized map (Eclipse Collections / Trove)
MutableObjectIntMap<String> counts = ObjectIntMaps.mutable.empty();
for (String word : words) {
    counts.addToValue(word, 1);  // No boxing!
}
```

### 5.3 Humongous Object Allocations

Objects > G1RegionSize/2 bypass young gen entirely and go straight to Old Gen.

```java
// BAD — 2MB byte array goes straight to Old Gen with G1 default 8MB regions
byte[] buffer = new byte[4 * 1024 * 1024];  // 4MB — HUMONGOUS

// GOOD — use pooled buffers
ByteBuffer buffer = bufferPool.acquire();  // Reuse from pool
try {
    // use buffer
} finally {
    bufferPool.release(buffer);
}
```

---

## 6. GC Tuning Decision Tree

```
Is GC causing problems?
│
├── High pause times (> SLO)
│   ├── Pauses > 200ms regularly → Switch to ZGC/Shenandoah
│   ├── Occasional Full GC → Increase heap, tune G1 IHOP
│   └── Mixed GC long → Increase G1MixedGCCountTarget
│
├── High GC frequency (GC every second)
│   ├── Eden too small → Increase G1NewSizePercent
│   ├── Many short-lived objects → Profile allocation sites
│   └── Memory leak in Old Gen → Heap dump analysis
│
├── OOM: Java heap space
│   ├── Actual leak → Heap dump, MAT analysis
│   ├── Heap too small → Increase -Xmx (if affordable)
│   └── Humongous objects → Pool them
│
├── OOM: Metaspace
│   ├── Class loader leak → Find the leaking CL
│   └── MaxMetaspaceSize too small → Increase it (carefully)
│
└── OOM: Direct buffer memory
    ├── Netty / NIO buffers not released → Fix lifecycle
    └── MaxDirectMemorySize too small → Increase it
```

---

## 7. Key JVM Internals: Safepoints

A **safepoint** is a point where JVM can stop all application threads safely for GC.

```
App threads reach safepoint when:
- At method return
- At backward branch (loop back-edge)
- After unchecked array access (JVM inserts polls)

GC needs safepoint → JVM sets safepoint flag → threads check flag at polls
→ All threads reach safepoint → GC runs → Threads resume
```

**Why this matters**: Long-running native code or tight loops without safepoint polls = long TTSP (Time To Safepoint) = your GC pause looks long even though GC itself was fast.

```
-XX:+PrintSafepointStatistics   # Show safepoint times
-XX:PrintSafepointStatisticsCount=1
```

**Safepoint problem signs in GC logs**:
```
[safepoint] Application time: 0.0001234 seconds  ← Normal
[safepoint] Total time for which application threads were stopped: 3.456 seconds  ← PROBLEM
# 3.4s pause but GC itself was 50ms = 3.35s spent waiting for safepoint!
```

---

## 8. Summary: The GC Cheat Sheet

| Question | Answer |
|----------|--------|
| Default GC (Java 9+)? | G1GC |
| Lowest latency? | ZGC (Java 21: Generational ZGC) |
| Highest throughput? | ParallelGC |
| Full GC is always bad? | Yes — it's a production incident |
| Should -Xms = -Xmx? | Yes, in production |
| Where to set -Xmx? | 70-80% of container memory limit |
| How often to GC log? | Always — disk is cheap, downtime isn't |
| Best tool for heap analysis? | Eclipse MAT / JDK Mission Control |
