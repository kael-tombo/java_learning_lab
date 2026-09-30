# INTERVIEW QUESTIONS: JVM Memory & GC
## Lab 01 | Senior/Staff/Principal Java Architect Level

> These are real questions asked at FAANG, fintech, and cloud companies for senior/staff/principal roles.

---

## Tier 1: Senior Java Engineer (5+ years)

**Q1**: Walk me through what happens when you call `new ArrayList<>(1000)` in Java.

**Expected Answer**:
- JVM checks thread's TLAB for space
- If TLAB has room: bump pointer, object allocated lock-free
- If TLAB full: JVM either gets a new TLAB from Eden, or allocates directly in Eden with CAS
- Object header written (mark word + class pointer)
- Constructor called, `Object[]` backing array allocated (same process, size 1000 × 8 bytes = 8KB)
- If Eden full: Minor GC triggered before allocation can complete
- Object's initial age = 0 (in Eden)

---

**Q2**: What is the difference between `-Xmx8g` and `-XX:MaxHeapSize=8g`?

**Expected Answer**: They are identical — `-Xmx` is shorthand for `-XX:MaxHeapSize`. Same effect.

---

**Q3**: Your service has 8GB heap but keeps getting `OOM: Java heap space`. Adding more heap doesn't help. What do you suspect?

**Expected Answer**:
1. Memory leak — objects accumulating in Old Gen, never becoming unreachable
2. GC not being triggered fast enough (but more heap should help this... unless allocation rate > GC throughput)
3. Large objects being allocated faster than GC can free them
4. The heap IS being reclaimed but some non-heap area is leaking (native, Metaspace, Direct)
*Investigation steps: heap dump → Eclipse MAT → find large retained objects → find who's holding references*

---

**Q4**: What causes a `ConcurrentModeFailure` in G1GC?

**Expected Answer**: G1's concurrent marking cycle couldn't complete fast enough before Old Gen filled up, forcing a Full GC. Causes: IHOP threshold too high, Old Gen growing faster than marking can reclaim, short GC intervals not allowing marking to finish. Fix: lower IHOP, increase heap, fix memory leak.

---

## Tier 2: Staff Engineer / Tech Lead

**Q5**: Explain the difference between ZGC and G1GC's approach to relocation.

**Expected Answer**:
- **G1**: Stop-the-world evacuation — all live objects in a region are copied to new regions while app threads are stopped. App cannot run during this.
- **ZGC**: Concurrent relocation — uses load barriers. When app thread reads a reference, the load barrier checks if the object is being/has been relocated. If so, the barrier updates the pointer. App and GC run concurrently. Cost: every heap read has a tiny barrier overhead (~1-5ns). Benefit: no STW during relocation, just very short STW for root scanning.

---

**Q6**: You're seeing 500ms GC pauses in G1GC logs, but your application's SLO shows 800ms latency spikes. Explain the discrepancy.

**Expected Answer**: Several possible causes:
1. **Safepoint delays** — threads take time to reach safepoint before GC can start. Total pause = TTSP + GC pause. Enable `-XX:+PrintSafepointStatistics`.
2. **Post-GC reference processing** — SoftReferences, WeakReferences, finalizers processed after GC in another STW.
3. **Other STW operations** — deoptimizations, code cache flushing, class loading can trigger safepoints.
4. **Application-level effects** — threads blocked waiting for connections that timed out during GC, downstream cascades.

---

**Q7**: Design a production JVM configuration for a low-latency payment API processing 10,000 TPS with p99 < 20ms latency requirement. Container has 8GB RAM.

**Expected Answer**:
```bash
# Container: 8GB RAM, 8 vCPUs
# JVM gets ~6.5GB total (leave ~1.5GB for OS + other processes)

-Xmx5g -Xms5g                           # 5GB heap, no resizing
-XX:+UseZGC                              # Sub-ms GC pauses
-XX:+ZGenerational                       # Java 21: much better ZGC
-XX:MaxGCPauseMillis=10                  # Target 10ms (ZGC hint)
-XX:SoftMaxHeapSize=4g                   # ZGC target, grows if needed
-XX:ConcGCThreads=4                      # 50% cores for GC (rest for app)
-XX:+AlwaysPreTouch                      # Pre-zero pages at startup
-XX:+DisableExplicitGC                   # Ignore System.gc() calls
-Xss512k                                 # 512KB stack (vs 1MB default)
-XX:MetaspaceSize=256m                   # Avoid early metaspace resizing
-XX:MaxMetaspaceSize=512m
-XX:MaxDirectMemorySize=512m             # Cap direct buffer allocation
-Xlog:gc*:file=gc.log:time,uptime:filecount=5,filesize=100m  # GC logging
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/log/app/
-XX:+ExitOnOutOfMemoryError             # Fast fail on OOM (K8s will restart)
```
*Note*: Would also move session state to Redis, use pooled HTTP clients, avoid finalizers.

---

**Q8**: What is the "remembered set" in G1GC and why does it matter?

**Expected Answer**: A remembered set (RSet) is a data structure maintained per region that records which other regions contain pointers into this region. During GC, when evacuating a region, G1 needs to know all incoming references. Without RSets, it would scan the entire heap (like CMS did with card tables). RSets allow G1 to do efficient incremental collection — only scan relevant regions. Tradeoff: RSets consume memory (~2-5% of heap) and maintaining them during object writes adds write barrier overhead.

---

## Tier 3: Principal Engineer / Architect

**Q9**: How would you design an application to minimize GC pressure at 100k req/s?

**Expected Answer** (comprehensive):
1. **Object pooling**: Pool expensive objects (parsers, serializers, buffers)
2. **Value-oriented design**: Use Java records, primitive arrays, avoid boxing
3. **Arena allocation**: Allocate objects for a request in a pre-allocated arena, free the whole arena at end of request (bypasses GC entirely)
4. **Off-heap for large data**: Store large caches in direct ByteBuffers or file-mapped memory
5. **Minimize inter-region references**: Keep related objects in same region to reduce RSet pressure
6. **Immutability**: Immutable objects create write barriers only at construction
7. **Avoid finalizers/cleaners**: They add pressure to reference processing queues
8. **Profile first**: Use async-profiler allocation profiler to find hot allocation sites

---

**Q10**: You're the architect for a new 20-service microservices system. Each service runs in a 2GB container. How do you set GC policy across services?

**Expected Answer**:
- Not one-size-fits-all; categorize services:
  - **Stateless request handlers** (APIs): G1GC or ZGC, -Xmx1g -Xms1g, maximize Eden
  - **Caching services**: ZGC (large heaps of long-lived objects), -Xmx1.5g
  - **Batch processors**: ParallelGC (throughput > latency), -Xmx1.5g
  - **Stream processors** (Kafka consumers): G1GC, tune for steady-state
- Enforce GC logging in all services (centralized, structured)
- Alert on: GC > 5% of time, Full GC events, heap > 80%, promotion failures
- Set `-XX:+ExitOnOutOfMemoryError` everywhere — restart is better than limping

---

## Quickfire Round (10 questions, 30 seconds each)

1. What is TLAB? — Thread-Local Allocation Buffer; per-thread private Eden slice for lock-free allocation
2. When is `System.gc()` actually dangerous? — In production; can trigger Full GC unexpectedly; disable with `-XX:+DisableExplicitGC`
3. What is "stop-the-world"? — All application threads are paused so GC can safely inspect/move objects
4. Difference between Minor and Full GC? — Minor: young gen only, fast. Full: entire heap, slow, emergency
5. What is IHOP in G1? — `InitiatingHeapOccupancyPercent`: when Old Gen hits this %, concurrent marking starts
6. When to use ZGC vs G1? — ZGC for p99 < 10ms SLOs or heaps > 8GB; G1 for general workloads
7. What causes memory leak in Java? — Strong references held to objects no longer needed (e.g., static collections, listener registrations)
8. What is escape analysis? — JIT optimization: if object provably doesn't escape method, allocate on stack instead of heap
9. What does `-XX:+AlwaysPreTouch` do? — Forces JVM to access all heap pages at startup, avoiding OS page-fault overhead during runtime
10. How to read a heap dump? — Eclipse MAT: look at "Leak Suspects", "Dominator Tree" for large retained object graphs
